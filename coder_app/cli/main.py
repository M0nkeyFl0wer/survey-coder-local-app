"""
Command-line interface for the Survey Coder application.
Provides persistent, local project management capabilities.
"""

import click
import os
import json
from typing import Optional
import pandas as pd

from ..services.project_manager import project_manager
from ..models.survey_models import Codebook, Code


@click.group()
@click.version_option()
def cli():
    """Survey Coder - AI-powered survey data analysis with persistent local storage."""
    pass


@cli.group()
def project():
    """Project management commands."""
    pass


@project.command()
@click.option('--name', '-n', required=True, help='Project name')
@click.option('--description', '-d', default='', help='Project description')
@click.option('--question', '-q', default='', help='Survey question text')
@click.option('--column', '-c', default='', help='Column name to code')
def init(name: str, description: str, question: str, column: str):
    """Initialize a new project."""
    try:
        project_meta = project_manager.create_project(
            name=name,
            description=description,
            question_text=question,
            column_to_code=column
        )
        click.echo(f"✅ Created project '{name}'")
        click.echo(f"📅 Created: {project_meta.created_at}")
        if description:
            click.echo(f"📝 Description: {description}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@project.command()
def list():
    """List all projects."""
    projects = project_manager.list_projects()
    if not projects:
        click.echo("No projects found. Create one with 'coder project init'.")
        return
    
    click.echo(f"\n📂 Found {len(projects)} project(s):\n")
    for p in projects:
        click.echo(f"  • {p.name}")
        if p.description:
            click.echo(f"    📝 {p.description}")
        if p.question_text:
            click.echo(f"    ❓ {p.question_text}")
        click.echo(f"    📅 Modified: {p.last_modified}")
        click.echo()


@project.command()
@click.option('--name', '-n', required=True, help='Project name')
def show(name: str):
    """Show project details."""
    project_meta = project_manager.get_project(name)
    if not project_meta:
        click.echo(f"❌ Project '{name}' not found", err=True)
        raise click.Abort()
    
    click.echo(f"\n📂 Project: {project_meta.name}")
    click.echo(f"📝 Description: {project_meta.description or 'None'}")
    click.echo(f"❓ Question: {project_meta.question_text or 'None'}")
    click.echo(f"📊 Column: {project_meta.column_to_code or 'None'}")
    click.echo(f"📅 Created: {project_meta.created_at}")
    click.echo(f"🕐 Modified: {project_meta.last_modified}")
    
    # Show codebook info
    codebook = project_manager.get_latest_codebook(name)
    if codebook:
        click.echo(f"\n📚 Codebook: {len(codebook.codes)} codes")
        for i, code in enumerate(codebook.codes[:5]):  # Show first 5
            click.echo(f"  {i+1}. {code.code}: {code.description}")
        if len(codebook.codes) > 5:
            click.echo(f"  ... and {len(codebook.codes) - 5} more")
    else:
        click.echo(f"\n📚 Codebook: Not created yet")
    
    # Show results info
    results_df = project_manager.get_project_results(name)
    if not results_df.empty:
        click.echo(f"\n📊 Results: {len(results_df)} classifications")
    else:
        click.echo(f"\n📊 Results: No classifications yet")


@project.command()
@click.option('--name', '-n', required=True, help='Project name')
@click.confirmation_option(prompt='Are you sure you want to delete this project?')
def delete(name: str):
    """Delete a project."""
    if project_manager.delete_project(name):
        click.echo(f"✅ Deleted project '{name}'")
    else:
        click.echo(f"❌ Project '{name}' not found", err=True)


@project.command()
@click.option('--name', '-n', required=True, help='Project name')
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Data file (CSV or Excel)')
def load_data(name: str, file: str):
    """Load data file for a project."""
    try:
        df = project_manager.load_data(name, file)
        click.echo(f"✅ Loaded {len(df)} rows from {file}")
        click.echo(f"📊 Columns: {', '.join(df.columns.tolist())}")
        
        # Show valid text columns
        valid_columns = []
        for col in df.columns:
            try:
                if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                    series = df[col].dropna().astype(str).str.strip()
                    unique_count = series[series != ""].nunique()
                    if unique_count > 50:
                        valid_columns.append(f"{col} ({unique_count} unique)")
            except Exception:
                continue
        
        if valid_columns:
            click.echo(f"📝 Text columns suitable for coding:")
            for col in valid_columns:
                click.echo(f"  • {col}")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def codebook():
    """Codebook management commands."""
    pass


@codebook.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--file', '-f', required=True, type=click.Path(exists=True), help='Codebook file (JSON or CSV)')
def import_codebook(project: str, file: str):
    """Import a codebook from file."""
    try:
        # Read and parse codebook file
        with open(file, 'r') as f:
            if file.endswith('.json'):
                data = json.load(f)
                codebook = Codebook.model_validate(data)
            elif file.endswith('.csv'):
                df = pd.read_csv(file)
                codes = []
                for _, row in df.iterrows():
                    code_text = str(row.get('code', '') or '').strip()
                    desc_text = str(row.get('description', '') or '').strip()
                    examples = []
                    if 'examples' in row:
                        try:
                            examples = json.loads(str(row['examples']))
                        except:
                            examples = [str(row['examples'])] if str(row['examples']).strip() else []
                    
                    if code_text:
                        codes.append(Code(code=code_text, description=desc_text, examples=examples))
                
                codebook = Codebook(codes=codes)
            else:
                raise ValueError("Unsupported file format. Use JSON or CSV.")
        
        version = project_manager.save_codebook(project, codebook)
        click.echo(f"✅ Imported codebook with {len(codebook.codes)} codes")
        click.echo(f"📝 Saved as version {version}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@codebook.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json', help='Export format')
def export(project: str, output: str, format: str):
    """Export project codebook."""
    try:
        codebook = project_manager.get_latest_codebook(project)
        if not codebook:
            click.echo(f"❌ No codebook found for project '{project}'", err=True)
            raise click.Abort()
        
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(codebook.model_dump(), f, indent=2)
        elif format == 'csv':
            data = []
            for code in codebook.codes:
                data.append({
                    'code': code.code,
                    'description': code.description,
                    'examples': json.dumps(code.examples) if code.examples else ''
                })
            df = pd.DataFrame(data)
            df.to_csv(output, index=False)
        
        click.echo(f"✅ Exported codebook to {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def export():
    """Export commands."""
    pass


@export.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json', help='Export format')
def project_data(project: str, output: str, format: str):
    """Export complete project data."""
    try:
        data = project_manager.export_project_data(project, format)
        with open(output, 'w') as f:
            f.write(data)
        click.echo(f"✅ Exported project data to {output}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.group()
def ide():
    """IDE integration commands."""
    pass


@ide.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--text', '-t', required=True, help='Text to classify')
@click.option('--output-format', '-f', type=click.Choice(['json', 'table']), default='json', help='Output format')
def classify_text(project: str, text: str, output_format: str):
    """Classify text using project codebook (IDE-friendly output)."""
    try:
        codebook = project_manager.get_latest_codebook(project)
        if not codebook:
            click.echo(json.dumps({"error": f"No codebook found for project '{project}'"}), err=True)
            raise click.Abort()
        
        # Mock classification for now (would integrate with ClassificationService)
        result = {
            "project": project,
            "text": text,
            "classification": "Mock classification - integrate with API",
            "confidence": 0.85,
            "timestamp": click.DateTime().today().isoformat()
        }
        
        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Project: {result['project']}")
            click.echo(f"Text: {result['text']}")
            click.echo(f"Classification: {result['classification']}")
            click.echo(f"Confidence: {result['confidence']}")
        
    except Exception as e:
        error_result = {"error": str(e)}
        click.echo(json.dumps(error_result), err=True)
        raise click.Abort()


@ide.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--input-file', '-i', type=click.Path(exists=True), help='Input file with text selections')
@click.option('--output-file', '-o', help='Output file for results')
def batch_classify(project: str, input_file: str, output_file: str):
    """Batch classify text selections from IDE."""
    try:
        codebook = project_manager.get_latest_codebook(project)
        if not codebook:
            click.echo(json.dumps({"error": f"No codebook found for project '{project}'"}), err=True)
            raise click.Abort()
        
        # Read input file
        with open(input_file, 'r') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        # Mock batch classification
        results = []
        for i, text in enumerate(texts):
            results.append({
                "index": i,
                "text": text,
                "classification": f"Mock classification for text {i+1}",
                "confidence": 0.8 + (i * 0.01)  # Mock varying confidence
            })
        
        output_data = {
            "project": project,
            "processed_count": len(results),
            "results": results,
            "timestamp": click.DateTime().today().isoformat()
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"Results saved to {output_file}")
        else:
            click.echo(json.dumps(output_data, indent=2))
        
    except Exception as e:
        click.echo(json.dumps({"error": str(e)}), err=True)
        raise click.Abort()


@ide.command()
@click.option('--project', '-p', required=True, help='Project name')
@click.option('--output-format', '-f', type=click.Choice(['json', 'vscode-snippets']), default='json', help='Output format')
def export_codebook_for_ide(project: str, output_format: str):
    """Export codebook in IDE-friendly format."""
    try:
        codebook = project_manager.get_latest_codebook(project)
        if not codebook:
            click.echo(json.dumps({"error": f"No codebook found for project '{project}'"}), err=True)
            raise click.Abort()
        
        if output_format == 'vscode-snippets':
            # Generate VS Code snippets for each code
            snippets = {}
            for i, code in enumerate(codebook.codes):
                snippet_key = f"survey-code-{code.code.lower().replace(' ', '-')}"
                snippets[snippet_key] = {
                    "prefix": f"sc-{code.code.lower()}",
                    "body": [
                        f"Code: {code.code}",
                        f"Description: {code.description}",
                        "Examples:",
                        *[f"  - {example}" for example in code.examples[:3]]
                    ],
                    "description": f"Survey code: {code.code}"
                }
            
            click.echo(json.dumps(snippets, indent=2))
        else:
            # Standard JSON format
            ide_format = {
                "project": project,
                "codebook": {
                    "total_codes": len(codebook.codes),
                    "codes": [{
                        "id": i,
                        "code": code.code,
                        "description": code.description,
                        "examples_count": len(code.examples),
                        "examples": code.examples
                    } for i, code in enumerate(codebook.codes)]
                },
                "timestamp": click.DateTime().today().isoformat()
            }
            click.echo(json.dumps(ide_format, indent=2))
        
    except Exception as e:
        click.echo(json.dumps({"error": str(e)}), err=True)
        raise click.Abort()


@cli.command()
def status():
    """Show application status."""
    # Check database
    try:
        projects = project_manager.list_projects()
        db_status = "✅ Connected"
        project_count = len(projects)
    except Exception as e:
        db_status = f"❌ Error: {e}"
        project_count = 0
    
    click.echo("🚀 Survey Coder Status")
    click.echo("=" * 25)
    click.echo(f"Database: {db_status}")
    click.echo(f"Projects: {project_count}")
    click.echo(f"Data directory: ~/.coder_app")
    
    if project_count > 0:
        click.echo("\nRecent projects:")
        for p in projects[-3:]:  # Show last 3
            click.echo(f"  • {p.name} (modified: {p.last_modified})")


if __name__ == '__main__':
    cli()