import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import PyPDF2
import docx
import pandas as pd
from io import BytesIO

from chains import Chain
from portfolio import Portfolio
from utils import clean_text, validate_csv_structure


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(docx_file):
    doc = docx.Document(BytesIO(docx_file.read()))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def add_custom_css():
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
    
    .generate-container {
        text-align: center;
        margin: 3rem 0 2rem 0;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 0.7rem;
        margin: -0.5rem 0;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex;
        justify-content:center;
        align-items: center;
    }
    
    .sidebar-header {
        font-size: 1.7rem;
        font-weight: 600;
        color: #1e293b;
        letter-spacing:2px;
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
        margin-top:50px;
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
    
    .status-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .status-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .portfolio-option {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        border: 2px solid #e2e8f0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .portfolio-option:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
    }
    
    .portfolio-option.selected {
        border-color: #3b82f6;
        background: #eff6ff;
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
    
    .progress-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .progress-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #cbd5e1;
    }
    
    .progress-dot.active {
        background: #10b981;
    }
    
    .progress-dot.complete {
        background: #3b82f6;
    }
    
    @media (max-width: 768px) {
        .main-container {
            padding: 0.5rem;
        }
        .step-container {
            padding: 0.8rem;
        }
        .step-header {
            font-size: 1.1rem;
            margin: 1rem 0 0.5rem 0;
        }
        .sidebar-section {
            padding: 0.8rem;
        }
        .sidebar-header {
            font-size: 1.3rem;
        }
        .sidebar-subheader {
            font-size: 0.9rem;
        }
        .instruction-text {
            font-size: 0.8rem;
        }
        .generate-container {
            padding: 1rem;
            margin: 1.5rem 0;
        }
        .status-number {
            font-size: 1.2rem;
        }
        .status-label {
            font-size: 0.75rem;
        }
        .portfolio-option {
            padding: 0.8rem;
            margin: 0.5rem 0;
        }
        .upload-area {
            padding: 1rem;
        }
        .stTextArea textarea, .stTextInput input {
            font-size: 0.9rem !important;
        }
        .stRadio > div {
            gap: 0.3rem;
        }
        .stFileUploader > label {
            font-size: 0.9rem !important;
        }
    }
    
    @media (prefers-color-scheme: dark) {
        .step-container {
            background: #1e293b;
            border-color: #475569;
        }
        .step-header {
            color: #60a5fa;
        }
        .sidebar-section {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-color: #475569;
        }
        .sidebar-header {
            color: #71C0BB;
        }
        .status-card {
            background: #334155;
            color: #e2e8f0;
        }
        .portfolio-option {
            background: #334155;
            border-color: #475569;
            color: #e2e8f0;
        }
    }
    
    .stRadio > div {
        gap: 0.5rem;
    }
    
    .stFileUploader > div > div {
        background: transparent;
    }
    
    .stExpander > div > div > div {
        background: rgba(255,255,255,0.5);
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def create_sidebar_content(portfolio):
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header " style="color: #71C0BB;text-align:center;">
            Portfolio 
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    project_count = portfolio.get_projects_count()
    
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
                    portfolio.update_data(projects_df)
                    st.success(f"✅ Successfully loaded {len(projects_df)} projects!")
                    
                    with st.expander("📊 Project Preview", expanded=False):
                        preview_df = projects_df[['Project_Name', 'Tech_Stack']].head(3)
                        st.dataframe(preview_df, use_container_width=True, hide_index=True)
                        if len(projects_df) > 3:
                            st.caption(f"... and {len(projects_df) - 3} more projects")
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
        st.markdown('<div class="sidebar-subheader">Sample Portfolio Loaded</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Load Sample Projects", use_container_width=True):
            sample_data = create_sample_portfolio_data()
            portfolio.update_data(sample_data)
            st.success(f"✅ Loaded {len(sample_data)} sample projects!")
            st.rerun()
        
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
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-header">
            💡 Quick Tips
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("🎯 Portfolio Tips", expanded=False):
        st.markdown("""
        **For better email generation:**
        
        • Include 3-5 of your best projects \n
        • Use specific tech stack details\n
        • Add live demo links when possible\n
        • Highlight diverse skills and technologies\n
        • Keep descriptions concise but informative\n
        """)
    
    with st.expander("📧 Email Tips", expanded=False):
        st.markdown("""
        **For effective cold emails:**
        
        • Use the complete job description \n
        • Include company name and role title \n
        • Mention specific requirements from the posting \n
        • Keep your resume updated and relevant \n
        • Review the generated email before sending \n
        """)
    
    with st.expander("📝 CSV Format Guide", expanded=False):
        st.markdown("""
        **Required CSV columns:**
        
        • **Project_Name** - Name of your project \n
        • **Description** - Brief project description \n
        • **Tech_Stack** - Technologies used \n
        • **Links** - Live demo URL (optional) \n
        • **GitHub** - Repository URL (optional) \n
        
        Make sure your CSV file includes these columns with the exact names shown above.
        """)
    
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 2rem;">
        Cold Email Generator v2.0<br>
        <small>Powered by AI • Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


def create_streamlit_app(llm, portfolio, clean_text):
    add_custom_css()
    
    st.title(" Cold Email Generator for Job Seekers")
    st.markdown("**Generate personalized cold emails for job applications with AI**")
    
    with st.sidebar:
        create_sidebar_content(portfolio)
    
    with st.container():
        st.markdown('<div class="step-header">📄 Step 1: Upload Your Resume</div>', unsafe_allow_html=True)
        
        st.markdown(
                """
                <style>
                div[data-testid="stCheckbox"][key="mobile_check"] {
                display: none;
                }
                </style>
                """,
         unsafe_allow_html=True
        )
        is_mobile = st.checkbox("Is mobile", value=False, key="mobile_check", disabled=True, label_visibility="hidden")
        
        if is_mobile:
            uploaded_file = st.file_uploader(
                "",
                type=['pdf', 'docx', 'txt'],
                help="Upload your resume file",
                label_visibility="collapsed"
            )
            st.markdown('<p class="instruction-text">📎 Drag and drop or browse. Accepts PDF, DOCX, TXT • Max size: 200MB</p>', unsafe_allow_html=True)
            
            if uploaded_file is not None:
                st.success("✅ File uploaded!")
                st.info(f"📋 **{uploaded_file.name}**  \n🗂️ {uploaded_file.type}")
        else:
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
    
    st.markdown('<div class="step-header">💼 Step 2: Enter Job Information</div>', unsafe_allow_html=True)
    
    with st.container():
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
                placeholder="Copy and paste the job description here...\n\nInclude details like :\n\n•  Job title and company\n•  Required skills and qualifications\n•  Job responsibilities\n•  Company culture information",
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
    
    generate_button = st.button(
        "🚀 Generate Cold Email",
        type="primary",
        use_container_width=True,
        disabled=not ready_to_generate,
        help="Generate a personalized cold email based on your resume and the job posting"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

    if generate_button:
        try:
            with st.spinner("🔄 Processing your information and generating personalized email..."):
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    resume_text = extract_text_from_docx(uploaded_file)
                else:
                    resume_text = str(uploaded_file.read(), "utf-8")
                
                resume_info = llm.extract_resume_info(resume_text)
                
                if "Text" in input_method:
                    job_data = llm.parse_job_description(job_input)
                    jobs = [job_data] if not isinstance(job_data, list) else job_data
                else:
                    loader = WebBaseLoader([job_input])
                    data = clean_text(loader.load().pop().page_content)
                    jobs = llm.extract_jobs(data)
                
                portfolio.load_portfolio()
            
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
            
            st.header("📧 Generated Cold Email(s)")
            
            for i, job in enumerate(jobs):
                    job_skills = job.get('skills', [])

                    # Convert job_skills to a list regardless of its type
                    if isinstance(job_skills, dict):
                   # If it's a dict, extract values and flatten them
                        job_skills = []
                    for value in job.get('skills', {}).values():
                        if isinstance(value, list):
                          job_skills.extend(value)
                        elif isinstance(value, str):
                          job_skills.append(value)
                        elif isinstance(job_skills, str):
                         # If it's a string, make it a list
                          job_skills = [job_skills]
                        elif not isinstance(job_skills, list):
                          # If it's neither dict, string, nor list, default to empty list
                        job_skills = []

# Ensure resume_info skills is also a list
resume_skills = resume_info.get('skills', [])
if not isinstance(resume_skills, list):
    resume_skills = []

# Now safely combine the lists
all_skills = job_skills + resume_skills
relevant_projects = portfolio.query_links(all_skills)
                if len(jobs) > 1:
                    st.subheader(f"📧 Email {i+1}: {job.get('role', 'Unknown Role')}")
                
                st.markdown("### 📝 Your Personalized Cold Email:")
                st.code(email, language='text')
                
                if relevant_projects:
                    with st.expander(f"🔗 Relevant Projects Used ({len(relevant_projects)} found)"):
                        for project in relevant_projects:
                            if isinstance(project, dict) and 'links' in project:
                                st.markdown(f"• **{project.get('name', 'Project')}**: {project['links']}")
                
                if i < len(jobs) - 1:
                    st.markdown("---")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again. Make sure your resume file is readable and job information is complete.")


def create_sample_portfolio_data():
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


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(
        layout="wide", 
        page_title="Cold Email Generator for Job Seekers", 
        page_icon="📧",
        initial_sidebar_state="expanded"
    )
    create_streamlit_app(chain, portfolio, clean_text)