from fastapi import FastAPI, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import uuid
import os
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
model = genai.GenerativeModel('gemini-pro')

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
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Try to extract JSON from the response
        # Look for JSON content between triple backticks if present
        import re
        json_match = re.search(r"```json\s*([\s\S]*?)\s*```", response_text)
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
    Based on the following candidate information:
    - Name: {candidate_data.get('name', 'Unknown')}
    - Skills: {', '.join(candidate_data.get('skills', []))}
    - Experience: {candidate_data.get('experience', 'Unknown')}
    - Education: {candidate_data.get('education', 'Unknown')}
    - Experience Level: {candidate_data.get('experience_level', 'Unknown')}
    
    Please provide:
    1. Strengths and improvement areas
    2. Suggested career paths
    3. Potential certifications or courses that would help advance their career
    4. Skills they should develop next
    
    Format your response in markdown with appropriate headings and bullet points.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        return "Unable to generate career insights at this time. Please try again later."

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
    
    insights = generate_insights_with_gemini(resumes[candidate_id])
    return {"insights": insights}

# Add a health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the server is running
    """
    return {"status": "ok", "message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
