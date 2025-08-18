from openai import OpenAI
import os
import PyPDF2
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.dirname(BASE_DIR)

upload_folder = os.path.join(BASE_DIR, "uploads")

# easier than hardcoding paths :o
resume = os.path.join(upload_folder, "resume.pdf")
jd = os.path.join(upload_folder, "job_description.txt")

def extract_text_from_pdf():
   resume_text = ""
   with open(resume, "rb") as pdf_file:
      pdf_reader = PyPDF2.PdfReader(pdf_file)
      num_pages = len(pdf_reader.pages)
      for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        resume_text += page.extract_text()
      return resume_text
  
def extract_text_from_txt():
   jd_text = ""
   with open(jd, 'r') as txt_file:
      jd_text += txt_file.read()
      return jd_text
    

def evaluate_resume_match():
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

  instructions = """
                      
                      Goal: Evaluate how well the candidate’s resume matches the job description (JD). Be strict, evidence-based, and transparent.

                      How to read the files:
                        Extract key JD requirements first (must-haves vs nice-to-haves). Quote or cite the exact JD bullet/line when you use it.
                        Parse the resume for: titles, employers, dates, skills/tech stack, certifications, education, locations, work authorization/clearance, and measurable outcomes.

                      Definitions:
                        Must-have: explicitly required items (e.g., “3+ years of Python,” “active TS/SCI,” “must be onsite in Austin”).
                        Dealbreaker: a must-have the resume clearly lacks or contradicts.
                        Gap: anything the JD prefers or implies that the resume doesn’t show strongly enough.
                        Strength: a concrete match supported by resume evidence (title, bullet, metric, project, certification).
                      
                      Normalization & inference rules:
                        Map synonyms (e.g., “JS” → “JavaScript”; “SDE” → “Software Engineer”).
                        Seniority: infer from titles + years in role (e.g., “Senior,” “Lead,” “Manager”) but never inflate.
                        Dates: convert ranges to YYYY-MM and compute approximate years per skill/role if possible. Treat missing dates as unknown.
                        Recency matters: favor experience within the last 5 years; older experience counts half unless the JD accepts legacy tech.
                        Location/onsite: if JD requires onsite/hybrid in a city and the resume shows a different location with no relocation note, mark as a risk.
                        Authorization/clearance: if JD requires something and resume is silent, mark as unknown (not a dealbreaker unless JD says “required”).
                        Education/certs: if JD says “BS required” and resume lacks any degree signal, mark as dealbreaker. If “preferred,” mark as gap.
                        Quantifiable impact: prioritize bullets with metrics (%, $, time saved).

                      Evidence style:
                        When you claim a match, include a short parenthetical citation like: (JD: “3+ yrs Python”; Resume: “Python 2019–present, data pipelines at X Corp”).
                        Scoring (0–100): Compute a weighted score; if input is missing/unclear, use the Unknown handling below.

                      Must-haves (40 pts):
                        Fully satisfied: +10 each (cap 40).
                        Partially satisfied (near-match/ambiguous): +5.
                        Missing: 0 and record a dealbreaker.

                      Core skills & tools (20 pts):
                        Build a skill list from JD core stack; award up to 20 total.
                        Exact matches with recent use: +2; older use: +1; related/transferable: +0.5.

                      Role & domain fit (15 pts):
                        Title seniority alignment (IC vs Manager, level): up to +8.
                        Industry/domain/regulatory context (e.g., fintech, healthcare, embedded): up to +7.

                      Experience depth (years/scope) (10 pts):
                        Meets/exceeds JD years-in-role or years-with-tech: up to +10.

                      Impact & outcomes (10 pts):
                        Evidence of measurable results, ownership, scale, or leadership: up to +10.

                      Education & certifications (5 pts):
                        Required degree/cert met: +5; preferred: +2–3.

                      Deductions (apply after subtotal):
                        Dealbreakers present: if any hard must-have is missing, cap final score at 49.
                        Red flags/instability: unexplained multi-year gaps, frequent <12-month hops without reason, or contradictions: −0 to −10.
                        Location/onsite risk: −0 to −5 if JD is strict and resume conflicts.
                        Authorization/clearance unknown when required: cap at 59 unless resume clearly satisfies it.

                      Unknown handling:
                        If the resume is silent on a requirement that is marked “required” in the JD, treat as not met for scoring and list as a dealbreaker.
                        If the JD is ambiguous (e.g., “experience with cloud”), match any major provider (AWS/Azure/GCP) unless it names one.

                      Output requirements:
                        Be concise but specific. Use direct quotes sparingly in the evidence fields.

                      What to return:
                        match_score: (0–100 integer after deductions/caps).
                        strengths[]: bullet points with brief evidence citations.
                        gaps[]: non-fatal mismatches or weak signals, each with a suggested question to probe.
                        dealbreakers[]: only hard must-haves that are missing/contradicted; cite the JD bullet.
                        must_haves_assessed[]: each required item with status: "met" | "partial" | "missing" | "unknown".
                        skills: matched[] (exact or close matches), related[] (transferable/adjacent), missing[] (explicitly required but absent)
                        experience_summary: years_overall (float, best estimate), years_in_role_or_level (float), 
                        constraints: location_match ("yes"|"risk"|"no"|"unknown"), work_auth_match ("yes"|"risk"|"no"|"unknown"), clearance_match ("yes"|"no"|"unknown")
                        education_fit ("required_met"|"preferred_met"|"not_met"|"unknown")
                        improvements_to_make[] (3–5 crisp pointers on how to improve resume)
                        summary (3–5 sentences, neutral, evidence-based).

                      Tone:
                        Neutral, recruiter-friendly, and specific. No speculation without labeling it as such.


                      """
  resume_text = extract_text_from_pdf()
  jd_text = extract_text_from_txt()

  user_payload = (
    instructions
    + "\n\n---\nJob Description (text):\n"
    + jd_text
    + "\n\n---\nResume (text):\n"
    + resume_text
  )

  response = client.chat.completions.create(
      model="gpt-5-nano",
      messages=[
            {"role": "system", "content": "You are a strict, evidence-based recruiter tool."},
            {"role": "user", "content":  user_payload}
        ],
    response_format={
          "type": "json_schema",
          "json_schema": {
            "name": "candidate_job_fit",
            "schema": {
              "type": "object",
              "properties": {
                "match_score": { "type": "integer", "minimum": 0, "maximum": 100 },
                "strengths": { "type": "array", "items": { "type": "string" } },
                "gaps": { "type": "array", "items": { "type": "string" } },
                "dealbreakers": { "type": "array", "items": { "type": "string" } },
                "must_haves_assessed": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "requirement": { "type": "string" },
                      "status": { "type": "string", "enum": ["Met","Partial","Missing","Unknown"] },
                      "evidence": { "type": "string" }
                    },
                    "required": ["requirement","status"]
                  }
                },
                "skills": {
                  "type": "object",
                  "properties": {
                    "matched": { "type": "array", "items": { "type": "string" } },
                    "related": { "type": "array", "items": { "type": "string" } },
                    "missing": { "type": "array", "items": { "type": "string" } }
                  },
                  "required": ["matched","missing"]
                },
                "experience_summary": {
                  "type": "object",
                  "properties": {
                    "years_overall": { "type": "number" },
                    "years_in_role_or_level": { "type": "number" }
                  }
                },
                "constraints": {
                  "type": "object",
                  "properties": {
                    "location_match": { "type": "string", "enum": ["Yes","Risk","No","Unknown"] },
                    "work_auth_match": { "type": "string", "enum": ["Yes","Risk","No","Unknown"] },
                    "clearance_match": { "type": "string", "enum": ["Yes","No","Unknown"] }
                  }
                },
                "education_fit": { "type": "string", "enum": ["Required Met","Preferred Met","Not Met","Unknown"] },
                "improvements_to_make": { "type": "array", "items": { "type": "string" }, "minItems": 3, "maxItems": 5 },
                "summary": { "type": "string" }
              },
              "required": ["match_score","strengths","gaps","summary","skills","must_haves_assessed","education_fit","improvements_to_make"]
            }
    }
  }

  )
  # returns a dict which allows evaluate() in app.py to function
  raw = response.choices[0].message.content
  data = json.loads(raw)
  return data