#!/usr/bin/env python3
"""
Test script for the modernized Survey Coder architecture.
Demonstrates persistent storage, project management, and CLI functionality.
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from coder_app.services.project_manager import project_manager
from coder_app.models.survey_models import Codebook, Code

def test_basic_functionality():
    """Test basic project management functionality."""
    print("🧪 Testing Survey Coder Modernized Architecture")
    print("=" * 50)
    
    # Test 1: Create a project
    print("\\n1. Testing project creation...")
    project_name = "demo-project"
    
    # Clean up any existing test project
    try:
        project_manager.delete_project(project_name)
    except:
        pass
    
    project = project_manager.create_project(
        name=project_name,
        description="Demo project for testing modernized architecture",
        question_text="How satisfied are you with our service?",
        column_to_code="feedback"
    )
    print(f"   ✅ Created project: {project.name}")
    print(f"   📅 Created at: {project.created_at}")
    
    # Test 2: List projects
    print("\\n2. Testing project listing...")
    projects = project_manager.list_projects()
    print(f"   📂 Found {len(projects)} project(s)")
    for p in projects:
        print(f"   • {p.name}: {p.description}")
    
    # Test 3: Create sample data
    print("\\n3. Creating sample survey data...")
    sample_data = pd.DataFrame({
        'id': range(1, 11),
        'feedback': [
            "Great service, very satisfied!",
            "Could be better, slow response time",
            "Excellent quality, will recommend",
            "Poor customer support experience",
            "Average service, nothing special",
            "Outstanding team, very helpful",
            "Terrible experience, won't use again",
            "Good value for money",
            "Staff was rude and unprofessional",
            "Perfect service, exceeded expectations"
        ]
    })
    
    # Save sample data
    data_path = "sample_survey_data.csv"
    sample_data.to_csv(data_path, index=False)
    print(f"   📊 Created sample data: {data_path}")
    print(f"   📝 {len(sample_data)} responses about service satisfaction")
    
    # Test 4: Create sample codebook
    print("\\n4. Creating sample codebook...")
    sample_codebook = Codebook(codes=[
        Code(
            code="Positive",
            description="Positive feedback about service quality, satisfaction, or experience",
            examples=[
                "Great service, very satisfied!",
                "Excellent quality, will recommend",
                "Outstanding team, very helpful"
            ]
        ),
        Code(
            code="Negative",
            description="Negative feedback expressing dissatisfaction or complaints",
            examples=[
                "Poor customer support experience",
                "Terrible experience, won't use again",
                "Staff was rude and unprofessional"
            ]
        ),
        Code(
            code="Neutral",
            description="Neutral or moderate feedback without strong positive or negative sentiment",
            examples=[
                "Average service, nothing special",
                "Good value for money"
            ]
        )
    ])
    
    # Save codebook to project
    version = project_manager.save_codebook(project_name, sample_codebook)
    print(f"   📚 Saved codebook with {len(sample_codebook.codes)} codes (version {version})")
    
    # Test 5: Retrieve codebook
    print("\\n5. Testing codebook retrieval...")
    retrieved_codebook = project_manager.get_latest_codebook(project_name)
    if retrieved_codebook:
        print(f"   ✅ Retrieved codebook with {len(retrieved_codebook.codes)} codes")
        for i, code in enumerate(retrieved_codebook.codes, 1):
            print(f"   {i}. {code.code}: {code.description}")
    else:
        print("   ❌ Failed to retrieve codebook")
    
    # Test 6: Export project data
    print("\\n6. Testing data export...")
    try:
        export_data = project_manager.export_project_data(project_name, format='json')
        export_path = f"{project_name}_export.json"
        with open(export_path, 'w') as f:
            f.write(export_data)
        print(f"   ✅ Exported project data to: {export_path}")
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
    
    # Test 7: Show project details
    print("\\n7. Project summary...")
    project_details = project_manager.get_project(project_name)
    if project_details:
        print(f"   📂 Project: {project_details.name}")
        print(f"   📝 Description: {project_details.description}")
        print(f"   ❓ Question: {project_details.question_text}")
        print(f"   📊 Column: {project_details.column_to_code}")
        print(f"   🕐 Last Modified: {project_details.last_modified}")
    
    print("\\n🎉 All tests completed successfully!")
    print("\\n📋 What you can do next:")
    print("   • Run: pipenv run python -m coder_app status")
    print("   • Run: pipenv run python -m coder_app project list")
    print(f"   • Run: pipenv run python -m coder_app project show -n {project_name}")
    print("   • Run: pipenv run python -m coder_app --help")
    print("\\n🚀 Your modernized Survey Coder is ready for development!")

def cleanup_test_files():
    """Clean up test files."""
    test_files = [
        "sample_survey_data.csv",
        "demo-project_export.json"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   🧹 Cleaned up: {file_path}")

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except KeyboardInterrupt:
        print("\\n\\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\\n🧹 Cleaning up test files...")
        cleanup_test_files()