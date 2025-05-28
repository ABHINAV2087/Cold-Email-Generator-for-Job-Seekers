import pandas as pd
import streamlit as st
import uuid
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle
import tempfile

class Portfolio:
    def __init__(self, file_path=None, csv_data=None):
        self.file_path = file_path
        self.csv_data = csv_data
        self.data = None
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.project_vectors = None
        self.project_texts = []
        
        # Use session state for persistence instead of ChromaDB
        if 'portfolio_data' not in st.session_state:
            st.session_state.portfolio_data = None
        if 'portfolio_vectors' not in st.session_state:
            st.session_state.portfolio_vectors = None
        if 'portfolio_texts' not in st.session_state:
            st.session_state.portfolio_texts = []
        
        if csv_data is not None:
            self.data = csv_data
        elif file_path and os.path.exists(file_path):
            self.data = pd.read_csv(file_path)
        else:
            self.data = pd.DataFrame(columns=['Project_Name', 'Description', 'Tech_Stack', 'Links', 'GitHub', 'Demo_Link'])

    def load_portfolio(self, force_reload=False):
        """Load portfolio data and create vectors for similarity search"""
        if self.data is None or len(self.data) == 0:
            return False
        
        # Check if we need to reload
        if not force_reload and st.session_state.portfolio_data is not None:
            if len(st.session_state.portfolio_data) == len(self.data):
                return True
        
        # Store data in session state
        st.session_state.portfolio_data = self.data.copy()
        
        # Create text representations for vectorization
        project_texts = []
        for _, row in self.data.iterrows():
            text = f"{row.get('Project_Name', '')} {row.get('Description', '')} {row.get('Tech_Stack', '')}"
            project_texts.append(text)
        
        if project_texts:
            try:
                # Create TF-IDF vectors
                self.project_vectors = self.vectorizer.fit_transform(project_texts)
                st.session_state.portfolio_vectors = self.project_vectors
                st.session_state.portfolio_texts = project_texts
                self.project_texts = project_texts
                return True
            except Exception as e:
                st.error(f"Error creating portfolio vectors: {str(e)}")
                return False
        
        return False

    def query_links(self, skills, n_results=3):
        """Query similar projects using TF-IDF and cosine similarity"""
        if not skills:
            return []
        
        # Use session state data
        if st.session_state.portfolio_data is None or st.session_state.portfolio_vectors is None:
            return []
        
        try:
            # Prepare query text
            if isinstance(skills, list):
                query_text = " ".join(str(skill) for skill in skills)
            else:
                query_text = str(skills)
            
            # Transform query using the same vectorizer
            query_vector = self.vectorizer.transform([query_text])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, st.session_state.portfolio_vectors).flatten()
            
            # Get top n_results
            if len(similarities) == 0:
                return []
            
            # Get indices of top similar projects
            top_indices = np.argsort(similarities)[::-1][:min(n_results, len(similarities))]
            
            # Filter out very low similarity scores
            top_indices = [idx for idx in top_indices if similarities[idx] > 0.1]
            
            formatted_projects = []
            portfolio_data = st.session_state.portfolio_data
            
            for idx in top_indices:
                if idx < len(portfolio_data):
                    row = portfolio_data.iloc[idx]
                    project_info = {
                        'name': row.get('Project_Name', 'Unknown Project'),
                        'description': row.get('Description', ''),
                        'tech_stack': row.get('Tech_Stack', ''),
                        'links': row.get('Links', ''),
                        'github': row.get('GitHub', ''),
                        'demo': row.get('Demo_Link', ''),
                        'similarity_score': float(similarities[idx])
                    }
                    formatted_projects.append(project_info)
            
            return formatted_projects
            
        except Exception as e:
            st.error(f"Error querying projects: {str(e)}")
            return []

    def update_data(self, new_data):
        """Update portfolio data and reload vectors"""
        self.data = new_data
        return self.load_portfolio(force_reload=True)
    
    def get_projects_count(self):
        """Get number of projects in portfolio"""
        if st.session_state.portfolio_data is not None:
            return len(st.session_state.portfolio_data)
        return len(self.data) if self.data is not None else 0
    
    def get_project_names(self):
        """Get list of project names"""
        if st.session_state.portfolio_data is not None and not st.session_state.portfolio_data.empty:
            return st.session_state.portfolio_data['Project_Name'].tolist()
        elif self.data is not None and not self.data.empty:
            return self.data['Project_Name'].tolist()
        return []
    
    def reset_portfolio(self):
        """Reset portfolio data in session state"""
        st.session_state.portfolio_data = None
        st.session_state.portfolio_vectors = None
        st.session_state.portfolio_texts = []
        self.project_vectors = None
        self.project_texts = []
    
    def export_portfolio_state(self):
        """Export current portfolio state for debugging"""
        if st.session_state.portfolio_data is not None:
            return {
                'data_shape': st.session_state.portfolio_data.shape,
                'project_names': self.get_project_names()[:3],  # First 3 names
                'has_vectors': st.session_state.portfolio_vectors is not None,
                'vector_shape': st.session_state.portfolio_vectors.shape if st.session_state.portfolio_vectors is not None else None
            }
        return {'status': 'No data loaded'}