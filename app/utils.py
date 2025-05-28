import re
import streamlit as st
from typing import List, Dict, Any
import validators


def clean_text(text):
    text = re.sub(r'<[^>]*?>', '', text)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip()
    text = ' '.join(text.split())
    return text


def clean_resume_text(text):
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\t+', ' ', text)
    text = re.sub(r'[•▸▪▫◦‣⁃]', '-', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'©.*?\d{4}', '', text)
    return text.strip()


def extract_contact_info(text):
    contact_info = {}
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    contact_info['email'] = emails[0] if emails else None
    
    phone_patterns = [
        r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
        r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        phone_numbers.extend(phones)
    
    contact_info['phone'] = phone_numbers[0] if phone_numbers else None
    
    linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
    linkedin_matches = re.findall(linkedin_pattern, text)
    contact_info['linkedin'] = f"https://{linkedin_matches[0]}" if linkedin_matches else None
    
    return contact_info


def validate_file_type(file, allowed_types=['pdf', 'docx', 'txt']):
    if file is None:
        return False, "No file uploaded"
    
    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in allowed_types:
        return False, f"File type '{file_extension}' not supported. Allowed types: {', '.join(allowed_types)}"
    
    return True, "File type valid"


def validate_url(url):
    if not url:
        return False, "URL cannot be empty"
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if validators.url(url):
        return True, url
    else:
        return False, "Invalid URL format"


def format_skills_list(skills):
    if isinstance(skills, str):
        skills = re.split(r'[,;|\n]', skills)
    
    if isinstance(skills, list):
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1:
                cleaned_skills.append(skill)
        return cleaned_skills
    
    return skills


def extract_years_of_experience(text):
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
        r'experience:?\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:field|industry)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            return int(matches[0])
    
    return None


def chunk_text(text, chunk_size=4000, overlap=200):
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        break_point = text.rfind('.', start, end)
        if break_point == -1:
            break_point = text.rfind(' ', start, end)
        if break_point == -1:
            break_point = end
        
        chunks.append(text[start:break_point])
        start = break_point - overlap
    
    return chunks


def format_project_links(projects):
    if not projects:
        return "No relevant projects found."
    
    formatted_links = []
    for project in projects:
        if isinstance(project, dict):
            name = project.get('name', 'Unnamed Project')
            github = project.get('github', '')
            demo = project.get('demo', '')
            description = project.get('description', '')
            
            project_text = f"• **{name}**"
            if description:
                project_text += f": {description[:100]}..."
            
            links = []
            if github:
                links.append(f"[GitHub]({github})")
            if demo:
                links.append(f"[Demo]({demo})")
            
            if links:
                project_text += f" ({' | '.join(links)})"
            
            formatted_links.append(project_text)
    
    return '\n'.join(formatted_links)


def display_success_message(message, duration=3):
    success_placeholder = st.empty()
    with success_placeholder.container():
        st.success(message)
    
    import time
    time.sleep(duration)
    success_placeholder.empty()


def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    parts = filename.split('.')
    if len(parts) > 2:
        filename = '_'.join(parts[:-1]) + '.' + parts[-1]
    return filename


def extract_company_from_url(url):
    try:
        patterns = [
            r'(?:https?://)?(?:www\.)?([^./]+)\.com',
            r'(?:https?://)?(?:careers\.|jobs\.)?([^./]+)\.',
            r'(?:https?://)?([^./]+)\.(?:com|org|net)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url.lower())
            if match:
                company = match.group(1)
                company = re.sub(r'^(jobs|careers|www)', '', company)
                return company.capitalize()
        
        return "Company"
    except:
        return "Company"


def validate_resume_content(resume_text):
    if not resume_text or len(resume_text.strip()) < 100:
        return False, "Resume content is too short or empty"
    
    resume_keywords = [
        'experience', 'education', 'skills', 'work', 'employment',
        'university', 'college', 'degree', 'certification', 'project',
        'responsibilities', 'achievements', 'objective', 'summary'
    ]
    
    text_lower = resume_text.lower()
    keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    if keyword_count < 3:
        return False, "Content doesn't appear to be a resume"
    
    return True, "Resume content validated"


def format_email_for_display(email_content):
    formatted_email = email_content.replace('\n\n', '\n\n---\n\n')
    
    if email_content.startswith('Subject:'):
        lines = email_content.split('\n')
        lines[0] = f"**{lines[0]}**"
        formatted_email = '\n'.join(lines)
    
    return formatted_email


def validate_csv_structure(df):
    required_columns = ['Project_Name', 'Description', 'Tech_Stack']
    optional_columns = ['Links', 'GitHub', 'Demo_Link']
    
    if df.empty:
        return False, "CSV file is empty"
    
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        return False, f"Missing required columns: {', '.join(missing_required)}"
    
    for col in required_columns:
        if df[col].isna().all():
            return False, f"Column '{col}' has no data"
    
    for col in optional_columns:
        if col not in df.columns:
            df[col] = ""
    
    return True, "CSV structure is valid"


def display_csv_template():
    st.markdown("### 📋 CSV Template")
    st.markdown("Your CSV file should have the following columns:")
    
    template_data = {
        'Project_Name': ['My Awesome Project', 'Another Cool App'],
        'Description': ['Brief description of the project', 'What this project does'],
        'Tech_Stack': ['React, Node.js, MongoDB', 'Python, Django, PostgreSQL'],
        'Links': ['https://portfolio.com/project1', 'https://portfolio.com/project2'],
        'GitHub': ['https://github.com/user/project1', 'https://github.com/user/project2'],
        'Demo_Link': ['https://demo1.com', 'https://demo2.com']
    }
    
    template_df = pd.DataFrame(template_data)
    st.dataframe(template_df, use_container_width=True)
    
    csv_template = template_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Template",
        data=csv_template,
        file_name="portfolio_template.csv",
        mime="text/csv"
    )
    
    st.markdown("""
    **Required Columns:**
    - `Project_Name`: Name of your project
    - `Description`: Brief description of what the project does
    - `Tech_Stack`: Technologies used (comma-separated)
    
    **Optional Columns:**
    - `Links`: Portfolio or project page link
    - `GitHub`: GitHub repository link
    - `Demo_Link`: Live demo link
    """)


def process_uploaded_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        
        is_valid, message = validate_csv_structure(df)
        
        if not is_valid:
            return None, message
        
        df = df.fillna("")
        
        string_columns = ['Project_Name', 'Description', 'Tech_Stack', 'Links', 'GitHub', 'Demo_Link']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df, f"Successfully processed {len(df)} projects"
        
    except Exception as e:
        return None, f"Error processing CSV: {str(e)}"