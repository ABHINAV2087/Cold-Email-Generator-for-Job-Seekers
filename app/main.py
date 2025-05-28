import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import PyPDF2
import docx
import pandas as pd
from io import BytesIO
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from chains import Chain
from portfolio import Portfolio  # Updated portfolio class
from utils import clean_text, validate_csv_structure


def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""


def extract_text_from_docx(docx_file):
    """Extract text from uploaded DOCX file"""
    try:
        doc = docx.Document(BytesIO(docx_file.read()))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""


def add_custom_css():
    """Add custom CSS styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .step-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 2rem 0 1rem 0;
        padding: 1rem 0 0.5rem 0;
        border-bottom: 2px solid #e5e7eb;
        font-family: 'Inter', sans-serif;
    }
    
    .step-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0 2rem 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .instruction-text {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 0.7rem;
        margin: -0.5rem 0;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .sidebar-header {
        font-size: 1.7rem;
        font-weight: 600;
        color: #1e293b;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar-subheader {                
        font-size: 1.05rem;
        font-weight: 500;
        color: white;
        margin: 1rem 0 0.5rem 0;
        font-family: 'Inter', sans-serif;
        margin-top: 50px;
    }
    
    .status-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .status-card.warning {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .status-card.success {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .upload-area {
        background: white;
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: #f8fafc;
    }
    
    .error-message {
        color: #dc2626;
        background: #fee2e2;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #dc2626;
    }
    
    .success-message {
        color: #059669;
        background: #d1fae5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #059669;
    }
    </style>
    """, unsafe_allow_html=True)


def create_sidebar_content(portfolio):
    """Create sidebar content with portfolio management"""
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header" style="color: #71C0BB;text-align:center;">
            Portfolio 
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-subheader"><i>• Choose Data Source</i></div>', unsafe_allow_html=True)
    
    portfolio_option = st.radio(
        "",
        ["📤 Upload CSV File", "🎯 Use Sample Data"],
        help="Select how you want to manage your project portfolio",
        label_visibility="collapsed"
    )
    
    if "Upload CSV" in portfolio_option:
        st.markdown('<div class="sidebar-subheader"><i> • Upload Your Portfolio</i></div>', unsafe_allow_html=True)
        
        uploaded_csv = st.file_uploader(
            "",
            type=['csv'],
            help="Upload a CSV file with your personal projects",
            label_visibility="collapsed"
        )
        
        if uploaded_csv is not None:
            try:
                projects_df = pd.read_csv(uploaded_csv)
                is_valid, message = validate_csv_structure(projects_df)
                
                if is_valid:
                    success = portfolio.update_data(projects_df)
                    if success:
                        st.success(f"✅ Successfully loaded {len(projects_df)} projects!")
                        
                        with st.expander("📊 Project Preview", expanded=False):
                            preview_df = projects_df[['Project_Name', 'Tech_Stack']].head(3)
                            st.dataframe(preview_df, use_container_width=True, hide_index=True)
                            if len(projects_df) > 3:
                                st.caption(f"... and {len(projects_df) - 3} more projects")
                    else:
                        st.error("❌ Failed to process portfolio data")
                else:
                    st.error(f"❌ Invalid CSV format: {message}")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
        else:
            st.markdown("""
            <div class="upload-area">
                <div style="color: #64748b; font-size: 0.9rem;">
                    📎 Drop your CSV file here<br>
                    <small>or use the browse button above</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif "Sample Data" in portfolio_option:
        st.markdown('<div class="sidebar-subheader">Sample Portfolio</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Load Sample Projects", use_container_width=True):
            sample_data = create_sample_portfolio_data()
            success = portfolio.update_data(sample_data)
            if success:
                st.success(f"✅ Loaded {len(sample_data)} sample projects!")
                st.rerun()
            else:
                st.error("❌ Failed to load sample data")
        
        st.markdown("""
        <div style="background: #eff6ff; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <div style="font-size: 0.85rem; color: #1e40af;">
                💡 <strong>Sample includes:</strong><br>
                • E-commerce Platform<br>
                • Task Management App<br>
                • Data Analytics Dashboard<br>
                • ML Stock Predictor<br>
                • Weather Mobile App
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display current portfolio status
    project_count = portfolio.get_projects_count()
    if project_count > 0:
        st.markdown(f"""
        <div class="success-message">
            📊 <strong>{project_count} projects loaded</strong><br>
            Ready to generate emails!
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick tips section
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">
            💡 Quick Tips
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 CSV Format Guide", expanded=False):
        st.markdown("""
        **Required CSV columns:**
        
        • **Project_Name** - Name of your project  
        • **Description** - Brief project description  
        • **Tech_Stack** - Technologies used  
        • **Links** - Live demo URL (optional)  
        • **GitHub** - Repository URL (optional)  
        
        Make sure your CSV file includes these columns with the exact names shown above.
        """)


def create_sample_portfolio_data():
    """Create sample portfolio data for demonstration"""
    sample_projects = {
        'Project_Name': [
            'E-commerce Platform',
            'Task Management App',
            'Data Analytics Dashboard',
            'Machine Learning Predictor',
            'Mobile Weather App'
        ],
        'Description': [
            'Full-stack e-commerce application with user authentication, product catalog, shopping cart, and payment integration',
            'Real-time collaborative task management tool with drag-and-drop functionality, team collaboration features, and notifications',
            'Interactive dashboard for visualizing sales and customer data with real-time updates and customizable charts',
            'ML model for predicting stock prices using historical data, with web interface for visualization and predictions',
            'Cross-platform mobile app providing weather forecasts with location-based services and offline capabilities'
        ],
        'Tech_Stack': [
            'React, Node.js, Express, MongoDB, Stripe API, JWT',
            'Vue.js, Firebase, Socket.io, Vuetify, PWA',
            'Python, Django, PostgreSQL, D3.js, Chart.js, Redis',
            'Python, Scikit-learn, TensorFlow, Flask, Pandas, NumPy',
            'React Native, Redux, AsyncStorage, OpenWeatherMap API'
        ],
        'Links': [
            'https://portfolio.com/ecommerce',
            'https://portfolio.com/taskmanager',
            'https://portfolio.com/analytics',
            'https://portfolio.com/ml-predictor',
            'https://portfolio.com/weather-app'
        ],
        'GitHub': [
            'https://github.com/user/ecommerce-app',
            'https://github.com/user/task-manager',
            'https://github.com/user/analytics-dashboard',
            'https://github.com/user/ml-stock-predictor',
            'https://github.com/user/weather-mobile'
        ],
        'Demo_Link': [
            'https://ecommerce-demo.herokuapp.com',
            'https://taskmanager-live.netlify.app',
            'https://analytics-demo.vercel.app',
            'https://ml-predictor.streamlit.app',
            'https://expo.dev/@user/weather-app'
        ]
    }
    return pd.DataFrame(sample_projects)


def main():
    """Main application function"""
    # Set page config
    st.set_page_config(
        layout="wide", 
        page_title="Cold Email Generator for Job Seekers", 
        page_icon="📧",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    add_custom_css()
    
    # Initialize components
    try:
        chain = Chain()
        portfolio = Portfolio()
    except Exception as e:
        st.error(f"❌ Error initializing application: {str(e)}")
        st.stop()
    
    # Main app title
    st.title("📧 Cold Email Generator for Job Seekers")
    st.markdown("**Generate personalized cold emails for job applications with AI**")
    
    # Sidebar
    with st.sidebar:
        create_sidebar_content(portfolio)
    
    # Step 1: Resume Upload
    st.markdown('<div class="step-header">📄 Step 1: Upload Your Resume</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "",
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume file",
            label_visibility="collapsed"
        )
        st.markdown('<p class="instruction-text">📎 Drag and drop or browse. Accepts PDF, DOCX, TXT • Max size: 200MB</p>', unsafe_allow_html=True)
    
    with col2:
        if uploaded_file is not None:
            st.success("✅ File uploaded!")
            st.info(f"📋 **{uploaded_file.name}**  \n🗂️ {uploaded_file.type}")
    
    # Step 2: Job Information
    st.markdown('<div class="step-header">💼 Step 2: Enter Job Information</div>', unsafe_allow_html=True)
    
    input_method = st.radio(
        "How would you like to provide job details?",
        ["📝 Job Description (Text)", "🔗 Company Careers Page URL"],
        horizontal=True,
        help="Choose your preferred method to input job information"
    )
    
    if "Text" in input_method:
        job_input = st.text_area(
            "Paste the complete job description:",
            height=200,
            placeholder="Copy and paste the job description here...\n\nInclude details like:\n\n• Job title and company\n• Required skills and qualifications\n• Job responsibilities\n• Company culture information",
            help="The more detailed the job description, the better the personalized email"
        )
        st.markdown('<p class="instruction-text">💡 Tip: Include job title, required skills, and company information for best results</p>', unsafe_allow_html=True)
    else:
        job_input = st.text_input(
            "Enter the company's job posting URL:",
            placeholder="https://jobs.company.com/job/position-123456",
            help="Direct link to the job posting page"
        )
        st.markdown('<p class="instruction-text">🌐 Example: https://jobs.nike.com/job/R-33460 or similar career page URLs</p>', unsafe_allow_html=True)
    
    # Check if ready to generate
    ready_to_generate = bool(uploaded_file and job_input.strip() and portfolio.get_projects_count() > 0)
    
    if not ready_to_generate:
        missing_items = []
        if not uploaded_file:
            missing_items.append("Resume file")
        if not job_input.strip():
            missing_items.append("Job information")
        if portfolio.get_projects_count() == 0:
            missing_items.append("Portfolio data")
        
        st.warning(f"⚠️ Please complete: {', '.join(missing_items)}")
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Cold Email",
        type="primary",
        use_container_width=True,
        disabled=not ready_to_generate,
        help="Generate a personalized cold email based on your resume and the job posting"
    )
    
    # Email generation logic
    if generate_button:
        try:
            with st.spinner("🔄 Processing your information and generating personalized email..."):
                # Extract resume text
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    resume_text = extract_text_from_docx(uploaded_file)
                else:
                    resume_text = str(uploaded_file.read(), "utf-8")
                
                if not resume_text.strip():
                    st.error("❌ Could not extract text from resume. Please try a different file.")
                    st.stop()
                
                # Extract resume information
                resume_info = chain.extract_resume_info(resume_text)
                
                # Process job information
                if "Text" in input_method:
                    job_data = chain.parse_job_description(job_input)
                    jobs = [job_data] if not isinstance(job_data, list) else job_data
                else:
                    try:
                        loader = WebBaseLoader([job_input])
                        data = clean_text(loader.load().pop().page_content)
                        jobs = chain.extract_jobs(data)
                    except Exception as e:
                        st.error(f"❌ Error loading URL: {str(e)}")
                        st.stop()
                
                # Load portfolio
                portfolio.load_portfolio()
            
            # Display results
            st.markdown("---")
            st.header("📊 Analysis Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("📄 Your Resume Analysis", expanded=False):
                    st.json(resume_info)
            
            with col2:
                with st.expander("💼 Job Analysis", expanded=False):
                    for i, job in enumerate(jobs):
                        if len(jobs) > 1:
                            st.subheader(f"Job {i+1}")
                        st.json(job)
            
            # Generate emails
            st.header("📧 Generated Cold Email(s)")
            
            for i, job in enumerate(jobs):
                job_skills = job.get('skills', [])
                if isinstance(job_skills, str):
                    job_skills = [job_skills]
                
                relevant_projects = portfolio.query_links(job_skills + resume_info.get('skills', []))
                
                email = chain.write_candidate_email(job, resume_info, relevant_projects)
                
                if len(jobs) > 1:
                    st.subheader(f"📧 Email {i+1}: {job.get('role', 'Unknown Role')}")
                
                st.markdown("### 📝 Your Personalized Cold Email:")
                st.code(email, language='text')
                
                if relevant_projects:
                    with st.expander(f"🔗 Relevant Projects Used ({len(relevant_projects)} found)"):
                        for project in relevant_projects:
                            if isinstance(project, dict):
                                name = project.get('name', 'Project')
                                links = project.get('links', '')
                                github = project.get('github', '')
                                demo = project.get('demo', '')
                                
                                project_links = []
                                if links:
                                    project_links.append(f"[Portfolio]({links})")
                                if github:
                                    project_links.append(f"[GitHub]({github})")
                                if demo:
                                    project_links.append(f"[Demo]({demo})")
                                
                                link_text = " | ".join(project_links) if project_links else "No links available"
                                st.markdown(f"• **{name}**: {link_text}")
                
                if i < len(jobs) - 1:
                    st.markdown("---")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again. Make sure your resume file is readable and job information is complete.")
            
            # Debug information
            with st.expander("🔧 Debug Information", expanded=False):
                st.write("Error details:", str(e))
                st.write("Portfolio status:", portfolio.export_portfolio_state())


if __name__ == "__main__":
    main()