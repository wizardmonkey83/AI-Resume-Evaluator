from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from utils import evaluate_resume_match
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.dirname(BASE_DIR)        
# loads the .env file (for gpt) so that api key can be kept secret           
load_dotenv(os.path.join(PROJECT_ROOT, ".gitignore/.env"))

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")
# to limit the size of the resume 
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf'}

# render_function takes the name of the HTML file and returns the file as a string. 
# when the user navigates to the home page, Flask will return this string, and the browser will render it as HTML
@app.route("/")
def home():
    return render_template("index.html")

def allowed_file(filename):
    # checks to see if the file contains an extension, if so it splits the filename to the right at the dot, takes the second half of the split and checks to see if its a valid extension
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/index", methods = ["POST"])
def upload_file():
    # checks to see if the user uploaded content
    if "resume" in request.files and "job_description" in request.form:
    
        job_desc = request.form["job_description"]
        resume = request.files["resume"]
        if resume and allowed_file(resume.filename):
            # secures the filename before using it as it may not be a safe/valid filename
            filename = secure_filename(resume.filename)
    
            try:
                # saves text input outside of the uploads folder. need to troubleshoot.
                with open(os.path.join(app.config['UPLOAD_FOLDER'], "job_description.txt"), "w") as desc_file:
                    desc_file.write(job_desc)
                # need to change how file gets renamed so that "secure_filename" actually does something
                filename = "resume.pdf"
                resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # once user uploaded files are saved, the api logic gets called 
                return redirect(url_for("evaluate"))
            
            except Exception as e:
                return f"Error saving file: {str(e)}", 500
        
        elif resume and not allowed_file(resume.filename):
            return "No selected file", 400
        
        elif resume.filename == "":
            return "No selected file", 400
        
    elif "resume" not in request.files:
        return "No file part in this request", 400


@app.route("/result", methods = ["GET"])
def evaluate():
    # get the evaluation from open ai api
    data = evaluate_resume_match()
    ## pass it to the frontend
    return render_template("result.html", **data)
        

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return "File too large", 413


if __name__ == '__main__':
    app.run(debug=True)
