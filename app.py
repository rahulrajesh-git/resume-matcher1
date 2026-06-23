from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import glob
import uuid
from matcher_logic import match_resumes # Import the matching logic
from database import (save_results, get_results, save_job_description_meta, get_all_job_descriptions, 
                      delete_job_description, save_aspirant_submission, get_aspirant_submissions, 
                      update_job_description_meta, create_match_results_table, create_job_descriptions_table, 
                      create_aspirant_submissions_table) # Import database functions

app = Flask(__name__)
app.config['UPLOAD_FOLDER_JOB_DESC'] = 'resumematcher/job_descriptions'
app.config['UPLOAD_FOLDER_RESUMES'] = 'resumematcher/resumes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
app.static_folder = os.path.join(app.root_path, 'job_descriptions')
app.static_url_path = '/static/job_descriptions' # Set a URL prefix for static files served from this folder

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER_JOB_DESC'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER_RESUMES'], exist_ok=True)

# Initialize database tables
create_match_results_table()
create_job_descriptions_table()
create_aspirant_submissions_table()

# Root route redirects to the recruiter dashboard
@app.route('/')
def index():
    return redirect(url_for('recruiter_dashboard'))

# Recruiter Dashboard
@app.route('/recruiter')
def recruiter_dashboard():
    job_descriptions = get_all_job_descriptions()
    return render_template('recruiter_dashboard.html', job_descriptions=job_descriptions)

@app.route('/upload_job_description', methods=['GET', 'POST'])
def upload_job_description():
    if request.method == 'POST':
        if 'job_description_file' not in request.files:
            return redirect(request.url)
        file = request.files['job_description_file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            recruiter_email = request.form.get('recruiter_email', '')
            job_title = request.form.get('job_title', '')
            original_filename = secure_filename(file.filename)
            job_id = str(uuid.uuid4()) # Generate a unique Job ID
            
            # Save job description file with job_id.txt as filename
            job_desc_filepath = os.path.join(app.config['UPLOAD_FOLDER_JOB_DESC'], job_id + '.txt') 
            file.save(job_desc_filepath)
            
            # Save metadata to database
            save_job_description_meta(job_id, original_filename)
            update_job_description_meta(job_id, recruiter_email, job_title)
            
            return redirect(url_for('job_form_details', job_id=job_id))
    return render_template('upload_job_description.html')

@app.route('/job_form_details/<job_id>')
def job_form_details(job_id):
    job_desc_filename = os.path.join(app.config['UPLOAD_FOLDER_JOB_DESC'], job_id + '.txt')
    if not os.path.exists(job_desc_filename):
        return f"Job Description for ID {job_id} not found.", 404
    
    aspirant_form_url = url_for('aspirant_upload_form', job_id=job_id, _external=True)
    return render_template('job_form_details.html', job_id=job_id, aspirant_form_url=aspirant_form_url)

@app.route('/upload_resume/<job_id>', methods=['GET', 'POST'])
def upload_resume(job_id):
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            return redirect(request.url)
        file = request.files['resume_file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Create a job_id specific subdirectory for resumes
            job_resumes_dir = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], job_id)
            os.makedirs(job_resumes_dir, exist_ok=True)

            filename = secure_filename(file.filename)
            file.save(os.path.join(job_resumes_dir, filename))
            return redirect(request.url)  # Redirect to refresh the page
    return render_template('upload_resume.html', job_id=job_id)

@app.route('/aspirant/<job_id>', methods=['GET', 'POST'])
def aspirant_upload_form(job_id):
    """Form for aspirants to upload their resume"""
    if request.method == 'POST':
        if 'resume_file' not in request.files:
            return redirect(request.url)
        file = request.files['resume_file']
        if file.filename == '':
            return redirect(request.url)
        
        aspirant_name = request.form.get('aspirant_name', '')
        aspirant_email = request.form.get('aspirant_email', '')
        
        if file and aspirant_name and aspirant_email:
            # Create a job_id specific subdirectory for resumes
            job_resumes_dir = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], job_id)
            os.makedirs(job_resumes_dir, exist_ok=True)

            # Save resume with a unique identifier
            original_filename = secure_filename(file.filename)
            timestamp = str(uuid.uuid4())[:8]
            filename = f"{aspirant_name.replace(' ', '_')}_{timestamp}_{original_filename}"
            file_path = os.path.join(job_resumes_dir, filename)
            file.save(file_path)
            
            # Save submission to database
            save_aspirant_submission(job_id, aspirant_name, aspirant_email, filename)
            
            return render_template('submission_success.html', aspirant_name=aspirant_name)
    
    return render_template('aspirant_form.html', job_id=job_id)

@app.route('/match_resumes/<job_id>')
def match_resumes_route(job_id):
    # Job description filename now uses job_id
    job_desc_filename = os.path.join(app.config['UPLOAD_FOLDER_JOB_DESC'], job_id + '.txt') 
    if not os.path.exists(job_desc_filename):
        return f"Job Description for ID {job_id} not found.", 404 

    with open(job_desc_filename, 'r', encoding='utf-8') as f:
        job_desc_text = f.read()

    job_resumes_dir = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], job_id)
    if not os.path.exists(job_resumes_dir):
        return f"No resumes uploaded for Job ID {job_id}.", 404 

    resume_data = []
    # Look for all text files in the directory
    for resume_file_path in glob.glob(os.path.join(job_resumes_dir, '*.*')):
        try:
            with open(resume_file_path, 'r', encoding='utf-8') as f:
                resume_filename = os.path.basename(resume_file_path)
                resume_data.append((resume_filename, f.read()))
        except Exception as e:
            print(f"Error reading file {resume_file_path}: {e}")
            continue

    if not resume_data:
        return f"No resumes found for Job ID {job_id} in {job_resumes_dir}.", 404 

    ranked_resumes = match_resumes(job_desc_text, resume_data)
    save_results(job_id, ranked_resumes) # Save results to the database

    return redirect(url_for('view_results', job_id=job_id))

@app.route('/view_results/<job_id>')
def view_results(job_id):
    results = get_results(job_id)
    aspirant_submissions = get_aspirant_submissions(job_id)
    return render_template('view_results.html', job_id=job_id, results=results, aspirant_submissions=aspirant_submissions)

@app.route('/view_job_description/<job_id>')
def view_job_description(job_id):
    job_desc_filename = os.path.join(app.config['UPLOAD_FOLDER_JOB_DESC'], job_id + '.txt')
    if not os.path.exists(job_desc_filename):
        return f"Job Description for ID {job_id} not found.", 404
    with open(job_desc_filename, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"<pre>{content}</pre>"

@app.route('/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id):
    # Delete job description file
    job_desc_filepath = os.path.join(app.config['UPLOAD_FOLDER_JOB_DESC'], job_id + '.txt')
    if os.path.exists(job_desc_filepath):
        os.remove(job_desc_filepath)
    
    # Delete resumes directory
    job_resumes_dir = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], job_id)
    if os.path.exists(job_resumes_dir):
        import shutil
        shutil.rmtree(job_resumes_dir)
    
    # Delete from database - job description metadata and match results
    delete_job_description(job_id)
    
    return redirect(url_for('recruiter_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)