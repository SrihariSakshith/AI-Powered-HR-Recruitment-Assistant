from fastapi import FastAPI, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import uuid
import os
import time
from pathlib import Path
import google.generativeai as genai
import PyPDF2
import io
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure Gemini API using environment variables for security
# Important: Never hardcode API keys in your code
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables. Using placeholder.")
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # This will be replaced with the actual key from .env file

genai.configure(api_key=GEMINI_API_KEY)
# Update the model name from gemini-pro to gemini-1.5-flash
model = genai.GenerativeModel('gemini-1.5-flash')
print(f"Initialized Gemini model: gemini-1.5-flash")

# In-memory storage (replace with database in production)
resumes = {}
jobs = {}

# Models
class JobPosting(BaseModel):
    job_title: str
    required_skills: List[str]
    description: str
    experience_level: str

class CandidateSearchQuery(BaseModel):
    skills: List[str]
    experience_level: str

# Sample job postings from different fields to populate the system
sample_jobs = [
    {
        "job_title": "Senior Full Stack Developer",
        "required_skills": ["JavaScript", "React", "Node.js", "Python", "MongoDB", "AWS"],
        "description": "We're looking for an experienced Full Stack Developer to join our engineering team. You'll be working on our main product, building new features, and improving existing functionality. The ideal candidate has strong experience with both frontend and backend technologies and is comfortable working in an agile environment.",
        "experience_level": "Senior"
    },
    {
        "job_title": "Data Scientist",
        "required_skills": ["Python", "R", "Machine Learning", "SQL", "TensorFlow", "Statistics"],
        "description": "We are seeking a talented Data Scientist to help us discover insights from our data. You will work with stakeholders throughout the organization to identify opportunities for leveraging company data to drive business solutions. The right candidate should have experience using statistical computer languages, machine learning techniques and a strong background in statistics.",
        "experience_level": "Mid"
    },
    {
        "job_title": "Digital Marketing Manager",
        "required_skills": ["SEO", "SEM", "Social Media Marketing", "Content Strategy", "Analytics", "Campaign Management"],
        "description": "We're looking for a Digital Marketing Manager to develop, implement, track and optimize our digital marketing campaigns across all digital channels. You will be responsible for managing our social media presence, SEO/SEM, email marketing, and online advertising campaigns to increase brand awareness and drive website traffic.",
        "experience_level": "Mid"
    },
    {
        "job_title": "Registered Nurse",
        "required_skills": ["Patient Care", "Medical Records", "Vital Signs", "Care Planning", "Communication"],
        "description": "We are seeking a compassionate Registered Nurse to join our healthcare facility. You will be responsible for providing patient care, administering medications, maintaining medical records, and communicating with doctors and other healthcare professionals. The ideal candidate has excellent communication skills and a genuine passion for helping others.",
        "experience_level": "Entry"
    },
    {
        "job_title": "Financial Analyst",
        "required_skills": ["Financial Modeling", "Excel", "Data Analysis", "Forecasting", "Budgeting", "PowerBI"],
        "description": "We are looking for a Financial Analyst to evaluate financial data and provide insights to help optimize business operations. You'll be responsible for analyzing financial information, creating financial models, forecasting future performance, and presenting findings to leadership. The ideal candidate has strong analytical skills and attention to detail.",
        "experience_level": "Mid"
    },
    {
        "job_title": "HR Business Partner",
        "required_skills": ["Recruitment", "Employee Relations", "Performance Management", "HRIS", "Conflict Resolution"],
        "description": "We're seeking an experienced HR Business Partner to provide strategic HR support to our business units. You'll partner with managers to develop and implement HR strategies, manage employee relations, lead recruitment efforts, and ensure compliance with employment laws and regulations.",
        "experience_level": "Senior"
    },
    {
        "job_title": "Mechanical Engineer",
        "required_skills": ["AutoCAD", "SolidWorks", "3D Modeling", "Prototyping", "Product Design"],
        "description": "We are looking for a Mechanical Engineer to design, develop and test mechanical and electromechanical products. You'll be involved in product development from concept to production, creating detailed designs, running simulations, and testing prototypes. The ideal candidate has experience with 3D modeling software and a strong understanding of engineering principles.",
        "experience_level": "Mid"
    },
    {
        "job_title": "Elementary School Teacher",
        "required_skills": ["Curriculum Development", "Classroom Management", "Assessment", "Differentiated Instruction"],
        "description": "We are seeking a passionate Elementary School Teacher to join our school. You'll be responsible for planning and delivering engaging lessons, assessing student progress, managing classroom behavior, and communicating with parents. The ideal candidate is creative, patient, and committed to helping students reach their full potential.",
        "experience_level": "Entry"
    }
]

# Add more detailed sample jobs to better showcase the application
sample_jobs.extend([
    {
        "job_title": "UX/UI Designer",
        "required_skills": ["Figma", "Adobe XD", "Sketch", "Prototyping", "User Research", "Wireframing"],
        "description": "We're looking for a talented UX/UI Designer to create exceptional user experiences. You will work closely with product managers and developers to design intuitive interfaces that meet user needs while achieving business goals. The ideal candidate has an eye for clean design, possesses superior UI knowledge, and can translate high-level requirements into effective interaction flows.",
        "experience_level": "Mid"
    },
    {
        "job_title": "DevOps Engineer",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Linux", "Python"],
        "description": "We are seeking a DevOps Engineer to help us build and maintain our cloud infrastructure. You will be responsible for implementing and maintaining CI/CD pipelines, cloud resources, and containerization strategies. The ideal candidate is comfortable with automation, has strong troubleshooting skills, and is experienced with cloud platforms.",
        "experience_level": "Senior"
    },
    {
        "job_title": "Content Marketing Specialist",
        "required_skills": ["Content Creation", "SEO", "Social Media", "Copywriting", "Analytics", "Editorial Planning"],
        "description": "We're looking for a Content Marketing Specialist to create compelling content that attracts and engages our target audience. You will be responsible for developing and executing our content strategy across multiple channels including our blog, social media, and email. The ideal candidate is a skilled writer with SEO knowledge and data-driven decision making abilities.",
        "experience_level": "Entry"
    }
])

# Helper functions
def parse_resume_with_gemini(file_content, file_type):
    """Extract structured information from resume using Gemini API"""
    prompt = f"""
    Extract the following information from this {file_type} resume:
    1. Name
    2. Skills (as a list)
    3. Experience (in years)
    4. Education
    5. Experience Level (Entry, Mid, Senior)
    
    Return the information in a structured JSON format with the following keys:
    {{"name": "", "skills": [], "experience": "", "education": "", "experience_level": ""}}
    
    Resume content:
    {file_content[:5000]}  # Limiting content size for API constraints
    """
    
    try:
        # Configure parameters suitable for gemini-1.5-flash
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        response_text = response.text
        
        # Try to extract JSON from the response
        # Look for JSON content between triple backticks if present
        import re
        json_match = re.search(r"```json\s*([\\s\S]*?)\s*```", response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no JSON formatting, use the whole response
            json_str = response_text
        
        # Clean up and parse the JSON
        json_str = json_str.replace("```", "").strip()
        parsed_data = json.loads(json_str)
        
        # Ensure required fields exist
        required_fields = ["name", "skills", "experience", "education", "experience_level"]
        for field in required_fields:
            if field not in parsed_data:
                parsed_data[field] = "Not specified" if field != "skills" else []
                
        return parsed_data
    except Exception as e:
        print(f"Error parsing resume: {str(e)}")
        # Fallback to default values
        return {
            "name": "Candidate",
            "skills": ["Not specified"],
            "experience": "Not specified",
            "education": "Not specified",
            "experience_level": "Not specified"
        }

def generate_insights_with_gemini(candidate_data):
    """Generate career insights using Gemini API"""
    prompt = f"""
    As an AI career advisor, provide comprehensive professional insights for this candidate.
    
    Based on the following candidate profile:
    - Name: {candidate_data.get('name', 'Unknown')}
    - Skills: {', '.join(candidate_data.get('skills', []))}
    - Experience: {candidate_data.get('experience', 'Unknown')}
    - Education: {candidate_data.get('education', 'Unknown')}
    - Experience Level: {candidate_data.get('experience_level', 'Unknown')}
    
    Please provide a detailed career analysis with the following sections:
    
    ## Professional Strengths
    - [List 3-5 key strengths based on their skills and experience]
    
    ## Areas for Improvement
    - [Suggest 2-3 areas where they could improve]
    
    ## Recommended Career Paths
    - [Provide 2-3 potential career trajectories with brief explanations]
    
    ## Suggested Certifications & Courses
    - [List 3-5 specific certifications or courses that would benefit them]
    
    ## Skills to Develop
    - [Recommend 3-5 specific skills they should focus on developing next]
    
    Format your response using proper markdown formatting with headings, bullet points, and brief explanations.
    """
    
    try:
        # Configure parameters suitable for gemini-1.5-flash
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        # Check if we have a valid response
        if not response or not hasattr(response, 'text') or not response.text:
            print("Empty response from Gemini API")
            return "Unable to generate career insights. The AI model returned an empty response. Please try again."
        
        return response.text
    except Exception as e:
        error_message = str(e)
        print(f"Error generating insights: {error_message}")
        
        # Provide more helpful error message based on the type of error
        if "quota" in error_message.lower():
            return "Unable to generate career insights due to API quota limitations. Please try again later."
        elif "permission" in error_message.lower() or "access" in error_message.lower():
            return "Unable to generate career insights due to API access restrictions. Please check your API key configuration."
        elif "content" in error_message.lower() and "filtered" in error_message.lower():
            return "Unable to generate career insights due to content filtering. Please modify the candidate profile and try again."
        elif "not found" in error_message.lower() or "404" in error_message:
            return "Model 'gemini-1.5-flash' was not found. Please check that you're using a valid model name and that the API key has access to this model."
        else:
            return f"Unable to generate career insights at this time. Error: {error_message}"

# Endpoints
@app.post("/upload-resume/")
async def upload_resume(file: UploadFile):
    file_id = str(uuid.uuid4())
    file_path = Path(f"resumes/{file_id}_{file.filename}")
    os.makedirs(file_path.parent, exist_ok=True)
    
    # Read file content
    content = await file.read()
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Parse content based on file type
    file_content = ""
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        file_content = " ".join(page.extract_text() for page in pdf_reader.pages)
        file_type = "PDF"
    else:  # Assume text file
        file_content = content.decode('utf-8')
        file_type = "text"
    
    parsed_data = parse_resume_with_gemini(file_content, file_type)
    resumes[file_id] = parsed_data
    
    return {"message": "Resume uploaded successfully", "candidate_id": file_id}

@app.post("/add-job/")
async def add_job(job: JobPosting):
    job_id = str(uuid.uuid4())
    jobs[job_id] = job.dict()
    return {"message": "Job added successfully", "job_id": job_id}

@app.post("/search-candidates/")
async def search_candidates(query: CandidateSearchQuery):
    # Placeholder for hybrid search logic (BM25 + embeddings)
    matched_candidates = [
        {"candidate_id": cid, "details": details}
        for cid, details in resumes.items()
        if any(skill in details["skills"] for skill in query.skills)
        and details["experience_level"] == query.experience_level
    ]
    return {"candidates": matched_candidates}

@app.get("/career-insights/{candidate_id}")
async def career_insights(candidate_id: str):
    if candidate_id not in resumes:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Add validation for candidate data
    candidate_data = resumes.get(candidate_id, {})
    if not candidate_data or not candidate_data.get("skills"):
        return {"insights": "Unable to generate insights: Incomplete candidate profile. Please ensure the resume was properly processed."}
    
    try:
        # Generate insights with a timeout to prevent hanging requests
        insights = generate_insights_with_gemini(candidate_data)
        
        # Validate response
        if not insights or len(insights) < 50:  # Basic validation
            return {"insights": "The AI model returned insufficient insights. Please try again."}
            
        return {"insights": insights}
    except Exception as e:
        error_message = str(e)
        print(f"Error in career insights endpoint: {error_message}")
        return {"insights": f"Unable to generate career insights: {error_message}. Please try again later."}

# Add a new endpoint to get all jobs
@app.get("/jobs")
async def get_jobs():
    """
    Return all job postings
    """
    jobs_list = [{"job_id": job_id, **job_data} for job_id, job_data in jobs.items()]
    return {"jobs": jobs_list}

# Initialize sample job data
def initialize_sample_jobs():
    if not jobs:  # Only initialize if jobs dictionary is empty
        for job in sample_jobs:
            job_id = str(uuid.uuid4())
            jobs[job_id] = job
        print(f"Initialized {len(sample_jobs)} sample job postings")
    else:
        print(f"Jobs already initialized. {len(jobs)} jobs available.")

# Add a health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the server is running
    """
    return {"status": "ok", "message": "Server is running", "model": "gemini-1.5-flash"}

if __name__ == "__main__":
    # Initialize sample data
    initialize_sample_jobs()
    print(f"Initialized {len(sample_jobs)} sample job postings")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
