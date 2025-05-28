import pandas as pd
import chromadb
import uuid
import os


class Portfolio:
    def __init__(self, file_path=None, csv_data=None):
        self.file_path = file_path
        self.csv_data = csv_data
        self.data = None
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="personal_projects")
        
        if csv_data is not None:
            self.data = csv_data
        elif file_path and os.path.exists(file_path):
            self.data = pd.read_csv(file_path)
        else:
            self.data = pd.DataFrame(columns=['Project_Name', 'Description', 'Tech_Stack', 'Links', 'GitHub', 'Demo_Link'])

    def load_portfolio(self, force_reload=False):
        if force_reload or self.collection.count() == 0:
            try:
                self.chroma_client.delete_collection(name="personal_projects")
            except:
                pass
            self.collection = self.chroma_client.get_or_create_collection(name="personal_projects")
        
        if self.data is None or len(self.data) == 0:
            return False
            
        if not self.collection.count() or force_reload:
            for _, row in self.data.iterrows():
                project_text = f"{row.get('Project_Name', '')} {row.get('Description', '')} {row.get('Tech_Stack', '')}"
                
                self.collection.add(
                    documents=project_text,
                    metadatas={
                        "project_name": row.get("Project_Name", ""),
                        "description": row.get("Description", ""),
                        "tech_stack": row.get("Tech_Stack", ""),
                        "links": row.get("Links", ""),
                        "github": row.get("GitHub", ""),
                        "demo": row.get("Demo_Link", "")
                    },
                    ids=[str(uuid.uuid4())]
                )
        return True

    def query_links(self, skills):
        if not skills:
            return []
        
        if isinstance(skills, list):
            query_text = " ".join(skills)
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

    def update_data(self, new_data):
        self.data = new_data
        return self.load_portfolio(force_reload=True)
    
    def get_projects_count(self):
        return len(self.data) if self.data is not None else 0
    
    def get_project_names(self):
        if self.data is not None and not self.data.empty:
            return self.data['Project_Name'].tolist()
        return []