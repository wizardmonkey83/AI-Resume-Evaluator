# AI Resume Evaluator
A full-stack web application meant to assess resume alignment with job descriptions using OpenAI’s GPT API

## Features
- Upload a Resume (pdf) and paste a Job Description
- AI-Powered evaluator with:
- Match Score (0-100)
- Strengths and Gaps
- Must Haves & Dealbreakers
- Skills (matched, related, missing)
- Experience summary
- Education & constraints (location, clearance, etc.)
- Suggested improvements

## File Structure
```bash
project-root/
│── .env # stores your API key (ignored by Git)
│── requirements.txt # Python dependencies
│── app.py # Flask app and routes
│── utils.py # Resume/JobDescription parsing + OpenAI API logic
│── templates/
│ ├── index.html # upload form
│ └── result.html # evaluation results page
│── static/
│ └── style.css # styling for frontend
│── uploads/ # temporary uploaded files (resume, job_description.txt)
```

## Setup and Installation

### 1. Clone the Repo
```bash 
git clone https://github.com/wizardmonkey83/AI-Resume-Evaluator
cd ai-resume-evaluator
```

### 2. Create a virtual Environment
In the terminal paste:
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```


### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your .env
- Create a file called .env in your project root. 
- Inside of it paste: ```OPENAI_API_KEY=sk-yourkeyhere```
- Make sure .env is in .gitignore (never push it to GitHub)

### 5. Run the app
Navigate to the app.py file
```bash
python app.py
```
This app will be available at: http://127.0.0.1:5000

## Usage
- Open the app in your browser
- Paste a job description into the textarea
- Upload your resume (.pdf)
- Click Submit
- The AI will analyze and generate results, shown in the results page

## Security Notes
- Never commit your .env or API key
- If you accidentally pushed your key, rotate it immediately in the OpenAI dashboard.
- The uploads/ folder is temporary storage and should be cleaned regularly or ignored in production.

## Other

- Feel free to alter the prompt in utils.py to better match your career field


