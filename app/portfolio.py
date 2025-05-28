import pandas as pd
import chromadb
import uuid
import os
import tempfile
import streamlit as st
from chromadb.config import Settings


class Portfolio:
    def __init__(self, file_path=None, csv_data=None):
        self.file_path = file_path
        self.csv_data = csv_data
        self.data = None
        
        # Create a temporary directory for ChromaDB that works on Render
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            # Use in-memory client for cloud deployments
            self.chroma_client = chromadb.EphemeralClient()
            self.collection = self.chroma_client.get_or_create_collection(name="personal_projects")
        except Exception as e:
            st.error(f"ChromaDB initialization failed: {e}")
            # Fallback to simple in-memory storage
            self.collection = None
            self.projects_cache = []
        
        if csv_data is not None:
            self.data = csv_data
        elif file_path and os.path.exists(file_path):
            try:
                self.data = pd.read_csv(file_path)
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
                self.data = pd.DataFrame(columns=['Project_Name', 'Description', 'Tech_Stack', 'Links', 'GitHub', 'Demo_Link'])
        else:
            self.data = pd.DataFrame(columns=['Project_Name', 'Description', 'Tech_Stack', 'Links', 'GitHub', 'Demo_Link'])

    def load_portfolio(self, force_reload=False):
        if self.data is None or len(self.data) == 0:
            return False
        
        try:
            if self.collection is not None:
                # Use ChromaDB if available
                if force_reload:
                    try:
                        self.chroma_client.delete_collection(name="personal_projects")
                    except:
                        pass
                    self.collection = self.chroma_client.get_or_create_collection(name="personal_projects")
                
                if not self.collection.count() or force_reload:
                    for idx, row in self.data.iterrows():
                        project_text = f"{row.get('Project_Name', '')} {row.get('Description', '')} {row.get('Tech_Stack', '')}"
                        
                        self.collection.add(
                            documents=project_text,
                            metadatas={
                                "project_name": str(row.get("Project_Name", "")),
                                "description": str(row.get("Description", "")),
                                "tech_stack": str(row.get("Tech_Stack", "")),
                                "links": str(row.get("Links", "")),
                                "github": str(row.get("GitHub", "")),
                                "demo": str(row.get("Demo_Link", ""))
                            },
                            ids=[str(uuid.uuid4())]
                        )
            else:
                # Fallback to simple caching
                self.projects_cache = []
                for _, row in self.data.iterrows():
                    project_info = {
                        'name': str(row.get('Project_Name', 'Unknown Project')),
                        'description': str(row.get('Description', '')),
                        'tech_stack': str(row.get('Tech_Stack', '')),
                        'links': str(row.get('Links', '')),
                        'github': str(row.get('GitHub', '')),
                        'demo': str(row.get('Demo_Link', ''))
                    }
                    self.projects_cache.append(project_info)
            
            return True
            
        except Exception as e:
            st.error(f"Error loading portfolio: {e}")
            return False

    def query_links(self, skills):
        if not skills:
            return []
        
        try:
            if self.collection is not None:
                # Use ChromaDB query
                if isinstance(skills, list):
                    query_text = " ".join(str(skill) for skill in skills)
                else:
                    query_text = str(skills)
                
                results = self.collection.query(query_texts=[query_text], n_results=3)
                
                formatted_projects = []
                metadatas = results.get('metadatas', [])
                
                for metadata_list in metadatas:
                    for metadata in metadata_list:
                        project_info = {
                            'name': metadata.get('project_name', 'Unknown Project'),
                            'description': metadata.get('description', ''),
                            'tech_stack': metadata.get('tech_stack', ''),
                            'links': metadata.get('links', ''),
                            'github': metadata.get('github', ''),
                            'demo': metadata.get('demo', '')
                        }
                        formatted_projects.append(project_info)
                
                return formatted_projects
            else:
                # Fallback to simple matching
                if isinstance(skills, list):
                    skills_lower = [str(skill).lower() for skill in skills]
                else:
                    skills_lower = [str(skills).lower()]
                
                matched_projects = []
                for project in self.projects_cache:
                    tech_stack_lower = project['tech_stack'].lower()
                    description_lower = project['description'].lower()
                    
                    # Simple keyword matching
                    match_score = 0
                    for skill in skills_lower:
                        if skill in tech_stack_lower or skill in description_lower:
                            match_score += 1
                    
                    if match_score > 0:
                        matched_projects.append((project, match_score))
                
                # Sort by match score and return top 3
                matched_projects.sort(key=lambda x: x[1], reverse=True)
                return [project for project, _ in matched_projects[:3]]
                
        except Exception as e:
            st.error(f"Error querying projects: {e}")
            return []

    def update_data(self, new_data):
        try:
            self.data = new_data
            return self.load_portfolio(force_reload=True)
        except Exception as e:
            st.error(f"Error updating data: {e}")
            return False
    
    def get_projects_count(self):
        try:
            return len(self.data) if self.data is not None else 0
        except:
            return 0
    
    def get_project_names(self):
        try:
            if self.data is not None and not self.data.empty:
                return self.data['Project_Name'].tolist()
            return []
        except Exception as e:
            st.error(f"Error getting project names: {e}")
            return []

    def __del__(self):
        # Cleanup temporary directory
        try:
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass