import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time

# Configure page settings for a modern look
st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
BACKEND_API_URL = "http://localhost:8000"

# Function to check if the backend server is running
def is_backend_available():
    try:
        response = requests.get(f"{BACKEND_API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Custom CSS for modern design
st.markdown("""
<style>
    /* Modern color palette */
    :root {
        --primary: #6C63FF;
        --secondary: #4CAF50;
        --background: #F9FAFB;
        --text: #333;
        --card: #FFFFFF;
        --accent: #FF5252;
    }
    
    /* Main background */
    .stApp {
        background-color: var(--background);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--primary);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main title */
    .main-title {
        font-size: 2.5rem !important;
        padding: 1rem 0 !important;
        background: linear-gradient(90deg, #6C63FF 0%, #4CAF50 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Cards */
    .css-1r6slb0.e1tzin5v2 {
        background-color: var(--card);
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #5652cc;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    /* Upload button */
    .css-1offfwp {
        border-radius: 5px !important;
    }
    
    /* Success messages */
    .st-bd {
        border-radius: 5px;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: var(--primary);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px 5px 0px 0px;
        color: var(--text);
        font-weight: 400;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--card);
        color: var(--primary) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--primary);
    }
    
    /* Card elements */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-right: 0.3rem;
        margin-bottom: 0.3rem;
    }
    .badge-primary {
        background-color: #6C63FF;
        color: white;
    }
    .badge-secondary {
        background-color: #4CAF50;
        color: white;
    }
    .badge-info {
        background-color: #03A9F4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown("<h1 class='main-title'>TalentMatch AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; margin-bottom: 2rem;'>Intelligent HR Recruitment Assistant</p>", unsafe_allow_html=True)

# Create sidebar for navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/artificial-intelligence.png", width=80)
    st.markdown("## Navigation")
    
    # Check backend connection status
    backend_available = is_backend_available()
    if not backend_available:
        st.error("⚠️ Backend server is not available. Please make sure it's running.")
        st.info("""
        To start the backend server, open a terminal and run:
        ```
        cd backend
        python main.py
        ```
        """)
    
    nav_selection = st.radio(
        "",
        ["Dashboard", "Resume Upload", "Job Management", "Candidate Search", "Career Insights"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("#### Powered by Gemini AI")
    st.markdown("Need help? [Contact Support](mailto:support@talentmatchai.com)")
    
    # Display backend status
    if backend_available:
        st.success("✅ Backend connected")
    else:
        st.error("❌ Backend not connected")

# Wrapper function for API calls with proper error handling
def api_call(method, endpoint, **kwargs):
    try:
        if method.lower() == "get":
            response = requests.get(f"{BACKEND_API_URL}{endpoint}", timeout=10, **kwargs)
        elif method.lower() == "post":
            response = requests.post(f"{BACKEND_API_URL}{endpoint}", timeout=10, **kwargs)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}
        
        return {
            "success": response.ok,
            "status_code": response.status_code,
            "data": response.json() if response.ok else None,
            "error": None if response.ok else f"Server error: {response.status_code}"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to the backend server. Please make sure it's running."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False, 
            "error": "Request timed out. The server might be overloaded."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Dashboard Section
if nav_selection == "Dashboard":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;'>
            <h3 style='color: #6C63FF;'>Resumes</h3>
            <h2 style='font-size: 2.5rem;'>{}</h2>
        </div>
        """.format(len(resumes) if 'resumes' in locals() else 0), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;'>
            <h3 style='color: #4CAF50;'>Jobs</h3>
            <h2 style='font-size: 2.5rem;'>{}</h2>
        </div>
        """.format(len(jobs) if 'jobs' in locals() else 0), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;'>
            <h3 style='color: #FF5252;'>Matches</h3>
            <h2 style='font-size: 2.5rem;'>0</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sample data for visualization
    st.markdown("### Recent Activities")
    
    activities = [
        {"activity": "Resume uploaded", "timestamp": "2023-10-25 14:30:22"},
        {"activity": "New job posted: Data Scientist", "timestamp": "2023-10-25 13:15:45"},
        {"activity": "Candidate matched with job", "timestamp": "2023-10-25 12:05:10"},
        {"activity": "Career insights generated", "timestamp": "2023-10-25 11:20:33"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div style='display: flex; align-items: center; background-color: white; padding: 10px 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
            <div style='background-color: #F2F3FF; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; margin-right: 15px;'>
                <span style='color: #6C63FF; font-size: 1.2rem;'>✓</span>
            </div>
            <div>
                <p style='margin: 0; font-weight: 500;'>{activity["activity"]}</p>
                <p style='margin: 0; color: #777; font-size: 0.8rem;'>{activity["timestamp"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Resume Upload Section
elif nav_selection == "Resume Upload":
    st.markdown("## Resume Upload")
    
    with st.container():
        st.markdown("""
        <div style='background-color: #F2F3FF; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>
            <h4 style='color: #6C63FF; margin-top: 0;'>Instructions</h4>
            <p>Upload a candidate's resume in PDF or TXT format. Our AI will analyze the document to extract key information.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader("", type=["pdf", "txt"])
            
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if uploaded_file:
                st.markdown(f"Selected file: **{uploaded_file.name}**")
                
                if st.button("Process Resume", key="process_resume"):
                    with st.spinner("Analyzing resume with AI..."):
                        # Simulate progress
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        # Make API call
                        result = api_call(
                            "post", 
                            "/upload-resume/", 
                            files={"file": uploaded_file}
                        )
                        
                        if result["success"]:
                            candidate_id = result["data"].get('candidate_id')
                            st.success(f"Resume processed successfully!")
                            
                            # Store in session state for later use
                            if 'processed_resumes' not in st.session_state:
                                st.session_state.processed_resumes = []
                            
                            st.session_state.processed_resumes.append({
                                'id': candidate_id,
                                'name': uploaded_file.name,
                                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            
                            st.markdown(f"""
                            <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                                <h4 style='color: #4CAF50; margin-top: 0;'>✓ Success</h4>
                                <p><strong>Candidate ID:</strong> {candidate_id}</p>
                                <p>You can now search for this candidate or get career insights using the ID.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"Failed to process resume: {result['error']}")
                            if "Cannot connect" in result['error']:
                                st.info("Please make sure the backend server is running.")
    
    # Show previously processed resumes
    if 'processed_resumes' in st.session_state and st.session_state.processed_resumes:
        st.markdown("### Previously Processed Resumes")
        
        df = pd.DataFrame(st.session_state.processed_resumes)
        df.columns = ["Candidate ID", "File Name", "Processing Date"]
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Candidate ID": st.column_config.TextColumn("Candidate ID", width="medium"),
                "File Name": st.column_config.TextColumn("File Name", width="large"),
                "Processing Date": st.column_config.TextColumn("Processing Date", width="medium"),
            }
        )

# Job Management Section
elif nav_selection == "Job Management":
    st.markdown("## Job Management")
    
    job_tabs = st.tabs(["Add New Job", "View Jobs"])
    
    with job_tabs[0]:
        st.markdown("""
        <div style='background-color: #F2F3FF; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>
            <h4 style='color: #6C63FF; margin-top: 0;'>Instructions</h4>
            <p>Create a new job posting with the required skills and experience level.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("job_form"):
            job_title = st.text_input("Job Title", placeholder="e.g., Senior Software Engineer")
            
            col1, col2 = st.columns(2)
            with col1:
                required_skills = st.text_area(
                    "Required Skills (comma-separated)", 
                    placeholder="e.g., Python, TensorFlow, SQL"
                )
            with col2:
                experience_level = st.selectbox(
                    "Experience Level", 
                    ["Entry", "Mid", "Senior"]
                )
            
            description = st.text_area(
                "Job Description", 
                placeholder="Enter a detailed job description..."
            )
            
            submit_job = st.form_submit_button("Add Job Posting")
        
        if submit_job:
            if job_title and required_skills and description:
                with st.spinner("Adding job posting..."):
                    job_data = {
                        "job_title": job_title,
                        "required_skills": [skill.strip() for skill in required_skills.split(",")],
                        "description": description,
                        "experience_level": experience_level
                    }
                    
                    result = api_call("post", "/add-job/", json=job_data)
                    
                    if result["success"]:
                        job_id = result["data"].get('job_id')
                        
                        # Store in session state
                        if 'job_postings' not in st.session_state:
                            st.session_state.job_postings = []
                        
                        st.session_state.job_postings.append({
                            'id': job_id,
                            'title': job_title,
                            'skills': required_skills,
                            'level': experience_level,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        
                        st.success(f"Job added successfully!")
                    else:
                        st.error(f"Failed to add job posting: {result['error']}")
                        if "Cannot connect" in result['error']:
                            st.info("Please make sure the backend server is running.")
            else:
                st.warning("Please fill all required fields.")
    
    with job_tabs[1]:
        if 'job_postings' in st.session_state and st.session_state.job_postings:
            for job in st.session_state.job_postings:
                with st.container():
                    st.markdown(f"""
                    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <h3 style='margin-top: 0; color: #333;'>{job['title']}</h3>
                            <span style='background-color: #6C63FF; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem;'>{job['level']}</span>
                        </div>
                        <p style='color: #777; font-size: 0.9rem;'>Posted: {job['date']}</p>
                        <p style='margin-bottom: 10px;'>Skills: {job['skills']}</p>
                        <p style='color: #666; font-size: 0.9rem;'>ID: {job['id']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No job postings yet. Add a job posting to see it here.")

# Candidate Search Section
elif nav_selection == "Candidate Search":
    st.markdown("## Candidate Search")
    
    st.markdown("""
    <div style='background-color: #F2F3FF; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>
        <h4 style='color: #6C63FF; margin-top: 0;'>Instructions</h4>
        <p>Search for candidates matching specific skills and experience level.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_skills = st.text_input("Skills", placeholder="e.g., Python, Data Science, SQL")
    with col2:
        search_experience = st.selectbox("Experience Level", ["Entry", "Mid", "Senior"])
    
    if st.button("Search Candidates", key="search_button"):
        if search_skills:
            with st.spinner("Searching for matching candidates..."):
                # Simulate a bit of processing time
                time.sleep(1)
                
                query = {
                    "skills": [skill.strip() for skill in search_skills.split(",")],
                    "experience_level": search_experience
                }
                
                result = api_call("post", "/search-candidates/", json=query)
                
                if result["success"]:
                    candidates = result["data"].get("candidates", [])
                    
                    if candidates:
                        st.markdown(f"### Found {len(candidates)} Matching Candidates")
                        
                        for candidate in candidates:
                            cid = candidate.get("candidate_id")
                            details = candidate.get("details", {})
                            
                            st.markdown(f"""
                            <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <h3 style='margin-top: 0; color: #333;'>{details.get('name', 'Candidate')}</h3>
                                    <span style='background-color: #4CAF50; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem;'>{details.get('experience_level', 'Unknown')}</span>
                                </div>
                                <p style='color: #777; font-size: 0.9rem;'>Experience: {details.get('experience', 'Not specified')}</p>
                                <p style='color: #777; font-size: 0.9rem;'>Education: {details.get('education', 'Not specified')}</p>
                                <div style='margin: 10px 0;'>
                                    <p style='margin-bottom: 5px;'>Skills:</p>
                                    {''.join([f"<span class='badge badge-primary'>{skill}</span>" for skill in details.get('skills', [])])}
                                </div>
                                <p style='color: #666; font-size: 0.9rem;'>ID: {cid}</p>
                                <a href="?candidate_id={cid}" target="_blank" style='color: #6C63FF; text-decoration: none;'>View Career Insights →</a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No candidates found matching your search criteria.")
                else:
                    st.error(f"Failed to search candidates: {result['error']}")
                    if "Cannot connect" in result['error']:
                        st.info("Please make sure the backend server is running.")
        else:
            st.warning("Please enter at least one skill to search.")

# Career Insights Section
elif nav_selection == "Career Insights":
    st.markdown("## Career Insights")
    
    st.markdown("""
    <div style='background-color: #F2F3FF; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>
        <h4 style='color: #6C63FF; margin-top: 0;'>Instructions</h4>
        <p>Get AI-powered career insights for a candidate based on their ID.</p>
    </div>
    """, unsafe_allow_html=True)
    
    candidate_id = st.text_input("Candidate ID", placeholder="Enter candidate ID")
    
    if st.button("Get Career Insights", key="insights_button"):
        if candidate_id:
            with st.spinner("Generating AI insights..."):
                # Add a little delay for UX
                time.sleep(1)
                
                result = api_call("get", f"/career-insights/{candidate_id}")
                
                if result["success"]:
                    insights = result["data"].get("insights", "")
                    
                    # Display insights in a nice formatted way
                    st.markdown("""
                    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <h3 style='color: #6C63FF; margin-top: 0;'>AI Career Insights</h3>
                        <hr style='margin: 10px 0 20px 0;'>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(insights)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    error_msg = "Failed to retrieve insights"
                    if result.get("status_code") == 404:
                        error_msg = "Candidate not found. Check if the ID is correct."
                    elif "Cannot connect" in result['error']:
                        error_msg = "Cannot connect to backend server. Please make sure it's running."
                    st.error(error_msg)
        else:
            st.warning("Please enter a candidate ID.")
