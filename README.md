# AI-Powered HR Recruitment Assistant

An AI-driven application that helps HR professionals automate resume screening, perform job-candidate matching, and generate career insights.

## Features

- Real-time resume upload and parsing
- Job posting management
- Candidate-job matching using hybrid search
- AI-powered resume insights using Google Gemini API
- User-friendly Streamlit interface

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd AI-Powered-HR-Recruitment-Assistant
```

### 2. Set up the backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the backend directory:
```bash
# On Windows
copy .env.example .env

# On Linux/Mac
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

**Important:** Never commit your API keys to version control. The `.env` file is included in `.gitignore` to prevent this.

### 4. Set up the frontend
```bash
cd ../frontend
pip install -r requirements.txt
```

### 5. Run the application
In one terminal:
```bash
cd backend
python main.py
```

In another terminal:
```bash
cd frontend
streamlit run app.py
```

## Usage

1. Open the application in your browser at http://localhost:8501
2. Upload candidate resumes in PDF or text format
3. Add job postings with required skills and descriptions
4. Search for candidates matching specific skills and experience
5. Get AI-generated career insights for candidates

## Technologies Used

- FastAPI (Backend API)
- Streamlit (Frontend UI)
- Google Gemini API (AI model)
- PyPDF2 (PDF parsing)
