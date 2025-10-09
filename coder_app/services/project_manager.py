"""
Project management service for survey coding projects.
Handles project CRUD operations and coordinates with database.
"""

import pandas as pd
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.survey_models import ProjectMetadata, Codebook, ClassificationResult
from ..storage.database import db, Project


class ProjectManager:
    """Manages survey coding projects with persistent storage."""
    
    def __init__(self):
        self.db = db
    
    def create_project(self, name: str, description: str = "", 
                      question_text: str = "", column_to_code: str = "") -> ProjectMetadata:
        """Create a new project.
        
        Args:
            name: Project name (must be unique)
            description: Optional project description
            question_text: The survey question being coded
            column_to_code: Name of the column containing responses
            
        Returns:
            ProjectMetadata: Created project metadata
        """
        try:
            project = self.db.create_project(
                name=name,
                description=description,
                question_text=question_text,
                column_to_code=column_to_code
            )
            return self._project_to_metadata(project)
        except Exception as e:
            raise ValueError(f"Failed to create project '{name}': {e}")
    
    def get_project(self, name: str) -> Optional[ProjectMetadata]:
        """Get project by name.
        
        Args:
            name: Project name
            
        Returns:
            ProjectMetadata or None if not found
        """
        project = self.db.get_project(name)
        return self._project_to_metadata(project) if project else None
    
    def list_projects(self) -> List[ProjectMetadata]:
        """List all projects.
        
        Returns:
            List of ProjectMetadata objects
        """
        projects = self.db.list_projects()
        return [self._project_to_metadata(p) for p in projects]
    
    def update_project(self, name: str, **kwargs) -> Optional[ProjectMetadata]:
        """Update project fields.
        
        Args:
            name: Project name
            **kwargs: Fields to update
            
        Returns:
            Updated ProjectMetadata or None if not found
        """
        project = self.db.update_project(name, **kwargs)
        return self._project_to_metadata(project) if project else None
    
    def delete_project(self, name: str) -> bool:
        """Delete a project.
        
        Args:
            name: Project name
            
        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_project(name)
    
    def load_data(self, project_name: str, file_path: str) -> pd.DataFrame:
        """Load data file for a project.
        
        Args:
            project_name: Project name
            file_path: Path to CSV or Excel file
            
        Returns:
            Loaded DataFrame
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='latin1')
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel files.")
            
            # Store data location in project metadata (could be improved)
            self.update_project(project_name, description=f"Data loaded from {file_path}")
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to load data: {e}")
    
    def save_codebook(self, project_name: str, codebook: Codebook) -> int:
        """Save a codebook for a project.
        
        Args:
            project_name: Project name
            codebook: Codebook to save
            
        Returns:
            Version number of saved codebook
        """
        project = self.db.get_project(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        codebook_data = codebook.model_dump()
        codebook_version = self.db.save_codebook(project.id, codebook_data)
        return codebook_version.version
    
    def get_latest_codebook(self, project_name: str) -> Optional[Codebook]:
        """Get the latest codebook for a project.
        
        Args:
            project_name: Project name
            
        Returns:
            Codebook or None if not found
        """
        project = self.db.get_project(project_name)
        if not project:
            return None
        
        codebook_version = self.db.get_latest_codebook(project.id)
        if not codebook_version:
            return None
        
        return Codebook.model_validate(codebook_version.data)
    
    def save_classification_results(self, project_name: str, results: List[Dict[str, Any]]) -> int:
        """Save classification results for a project.
        
        Args:
            project_name: Project name
            results: List of classification results
            
        Returns:
            Number of results saved
        """
        project = self.db.get_project(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        # Get the latest codebook for reference
        latest_codebook = self.db.get_latest_codebook(project.id)
        codebook_id = latest_codebook.id if latest_codebook else None
        
        saved_count = 0
        for result in results:
            try:
                self.db.save_classification(
                    project_id=project.id,
                    codebook_id=codebook_id,
                    response_text=result.get('response_text', ''),
                    assigned_codes=result.get('assigned_codes', []),
                    details=result.get('details', [])
                )
                saved_count += 1
            except Exception as e:
                print(f"Failed to save classification result: {e}")
        
        return saved_count
    
    def get_project_results(self, project_name: str) -> pd.DataFrame:
        """Get all classification results for a project as DataFrame.
        
        Args:
            project_name: Project name
            
        Returns:
            DataFrame with classification results
        """
        project = self.db.get_project(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        classifications = self.db.get_project_classifications(project.id)
        
        if not classifications:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for c in classifications:
            assigned_codes_str = " | ".join(c.assigned_codes) if c.assigned_codes else "No Code Applied"
            data.append({
                'response_text': c.response_text,
                'assigned_codes': assigned_codes_str,
                'details': json.dumps(c.details) if c.details else '',
                'created_at': c.created_at.isoformat() if c.created_at else ''
            })
        
        return pd.DataFrame(data)
    
    def export_project_data(self, project_name: str, format: str = 'json') -> str:
        """Export project data.
        
        Args:
            project_name: Project name
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        project_meta = self.get_project(project_name)
        if not project_meta:
            raise ValueError(f"Project '{project_name}' not found")
        
        codebook = self.get_latest_codebook(project_name)
        results_df = self.get_project_results(project_name)
        
        export_data = {
            'project': project_meta.model_dump(),
            'codebook': codebook.model_dump() if codebook else None,
            'results': results_df.to_dict('records') if not results_df.empty else []
        }
        
        if format.lower() == 'json':
            return json.dumps(export_data, indent=2, default=str)
        elif format.lower() == 'csv':
            # For CSV, just export the results
            if not results_df.empty:
                return results_df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError("Format must be 'json' or 'csv'")
    
    def _project_to_metadata(self, project: Project) -> ProjectMetadata:
        """Convert database Project to ProjectMetadata.
        
        Args:
            project: Database project object
            
        Returns:
            ProjectMetadata object
        """
        return ProjectMetadata(
            name=project.name,
            description=project.description,
            question_text=project.question_text,
            column_to_code=project.column_to_code,
            created_at=project.created_at.isoformat() if project.created_at else None,
            last_modified=project.last_modified.isoformat() if project.last_modified else None
        )


# Global project manager instance
project_manager = ProjectManager()