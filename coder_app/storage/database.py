"""
Database models and connection management using SQLAlchemy.
Implements persistent storage for survey coding projects.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os
from typing import Optional, List

Base = declarative_base()


class Project(Base):
    """Database model for survey coding projects."""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    question_text = Column(Text)
    column_to_code = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    codebooks = relationship("CodebookVersion", back_populates="project")
    classifications = relationship("Classification", back_populates="project")


class CodebookVersion(Base):
    """Database model for codebook versions."""
    __tablename__ = 'codebooks'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    version = Column(Integer, nullable=False)
    data = Column(JSON, nullable=False)  # Stores the Codebook pydantic model as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="codebooks")
    classifications = relationship("Classification", back_populates="codebook")


class Classification(Base):
    """Database model for classification results."""
    __tablename__ = 'classifications'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    codebook_id = Column(Integer, ForeignKey('codebooks.id'))
    response_text = Column(Text, nullable=False)
    assigned_codes = Column(JSON)  # List of assigned code labels
    details = Column(JSON)  # List of ClassificationEvidence objects
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="classifications")
    codebook = relationship("CodebookVersion", back_populates="classifications")


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Create data directory in user's home
            data_dir = os.path.expanduser("~/.coder_app")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "projects.db")
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def create_project(self, name: str, description: str = "", question_text: str = "", 
                      column_to_code: str = "") -> Project:
        """Create a new project."""
        with self.get_session() as session:
            project = Project(
                name=name,
                description=description,
                question_text=question_text,
                column_to_code=column_to_code
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return project
    
    def get_project(self, name: str) -> Optional[Project]:
        """Get project by name."""
        with self.get_session() as session:
            return session.query(Project).filter(Project.name == name).first()
    
    def list_projects(self) -> List[Project]:
        """List all projects."""
        with self.get_session() as session:
            return session.query(Project).all()
    
    def update_project(self, name: str, **kwargs) -> Optional[Project]:
        """Update project fields."""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.name == name).first()
            if project:
                for key, value in kwargs.items():
                    if hasattr(project, key):
                        setattr(project, key, value)
                project.last_modified = datetime.utcnow()
                session.commit()
                session.refresh(project)
            return project
    
    def delete_project(self, name: str) -> bool:
        """Delete a project and all associated data."""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.name == name).first()
            if project:
                session.delete(project)
                session.commit()
                return True
            return False
    
    def save_codebook(self, project_id: int, codebook_data: dict) -> CodebookVersion:
        """Save a codebook version for a project."""
        with self.get_session() as session:
            # Get the next version number
            latest_version = session.query(CodebookVersion)\
                .filter(CodebookVersion.project_id == project_id)\
                .order_by(CodebookVersion.version.desc()).first()
            
            next_version = (latest_version.version + 1) if latest_version else 1
            
            codebook = CodebookVersion(
                project_id=project_id,
                version=next_version,
                data=codebook_data
            )
            session.add(codebook)
            session.commit()
            session.refresh(codebook)
            return codebook
    
    def get_latest_codebook(self, project_id: int) -> Optional[CodebookVersion]:
        """Get the latest codebook version for a project."""
        with self.get_session() as session:
            return session.query(CodebookVersion)\
                .filter(CodebookVersion.project_id == project_id)\
                .order_by(CodebookVersion.version.desc()).first()
    
    def save_classification(self, project_id: int, codebook_id: int, 
                          response_text: str, assigned_codes: List[str], 
                          details: List[dict]) -> Classification:
        """Save a classification result."""
        with self.get_session() as session:
            classification = Classification(
                project_id=project_id,
                codebook_id=codebook_id,
                response_text=response_text,
                assigned_codes=assigned_codes,
                details=details
            )
            session.add(classification)
            session.commit()
            session.refresh(classification)
            return classification
    
    def get_project_classifications(self, project_id: int) -> List[Classification]:
        """Get all classifications for a project."""
        with self.get_session() as session:
            return session.query(Classification)\
                .filter(Classification.project_id == project_id)\
                .order_by(Classification.created_at.desc()).all()


# Global database manager instance
db = DatabaseManager()