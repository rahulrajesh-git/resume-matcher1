import sqlite3
import os
from datetime import datetime
import sys
import traceback

# --- CONFIG ---
project_dir = "resumematcher"  # directory to hold DB file
# Ensure the folder exists (create it if needed)
try:
    os.makedirs(project_dir, exist_ok=True)
except Exception as e:
    print(f"ERROR: Could not create directory '{project_dir}': {e}")
    raise

# Use an absolute path for debugging clarity
DATABASE_NAME = os.path.abspath(os.path.join(project_dir, 'match_results.db'))

def connect_db():
    """Connect to the SQLite DB and return connection. Raises exception on failure."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except Exception:
        print("Failed to open SQLite database file.")
        print("DB absolute path:", DATABASE_NAME)
        print("Current working directory:", os.getcwd())
        print("Dir exists and writable?:", os.path.isdir(project_dir), os.access(project_dir, os.W_OK))
        traceback.print_exc()
        raise

def create_match_results_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            resume_filename TEXT NOT NULL,
            match_score REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_job_descriptions_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            job_id TEXT PRIMARY KEY,
            recruiter_email TEXT NOT NULL,
            job_title TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            upload_timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

def create_aspirant_submissions_table():
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS aspirant_submissions (
            submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            aspirant_name TEXT NOT NULL,
            aspirant_email TEXT NOT NULL,
            resume_filename TEXT NOT NULL,
            submission_timestamp TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id)
        )
    """)
    conn.commit()
    conn.close()

def save_job_description_meta(job_id, original_filename):
    conn = connect_db()
    c = conn.cursor()
    upload_timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO job_descriptions (job_id, recruiter_email, job_title, original_filename, upload_timestamp) VALUES (?, ?, ?, ?, ?)",
              (job_id, '', '', original_filename, upload_timestamp))
    conn.commit()
    conn.close()

def get_all_job_descriptions():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT job_id, recruiter_email, job_title, original_filename, upload_timestamp, status FROM job_descriptions ORDER BY upload_timestamp DESC")
    jobs = c.fetchall()
    conn.close()
    return [{'job_id': row[0], 'recruiter_email': row[1], 'job_title': row[2], 'original_filename': row[3], 'upload_timestamp': row[4], 'status': row[5]} for row in jobs]

def save_results(job_id, ranked_resumes):
    conn = connect_db()
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    for resume_filename, match_score in ranked_resumes:
        c.execute("INSERT INTO match_results (job_id, resume_filename, match_score, timestamp) VALUES (?, ?, ?, ?)",
                  (job_id, resume_filename, match_score, timestamp))
    conn.commit()
    conn.close()

def get_results(job_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT resume_filename, match_score, timestamp FROM match_results WHERE job_id=? ORDER BY match_score DESC", (job_id,))
    results = c.fetchall()
    conn.close()
    return results

def delete_job_description(job_id):
    conn = connect_db()
    c = conn.cursor()
    # Delete from match_results table
    c.execute("DELETE FROM match_results WHERE job_id=?", (job_id,))
    # Delete from aspirant_submissions table
    c.execute("DELETE FROM aspirant_submissions WHERE job_id=?", (job_id,))
    # Delete from job_descriptions table
    c.execute("DELETE FROM job_descriptions WHERE job_id=?", (job_id,))
    conn.commit()
    conn.close()

def save_aspirant_submission(job_id, aspirant_name, aspirant_email, resume_filename):
    conn = connect_db()
    c = conn.cursor()
    submission_timestamp = datetime.now().isoformat()
    c.execute("INSERT INTO aspirant_submissions (job_id, aspirant_name, aspirant_email, resume_filename, submission_timestamp) VALUES (?, ?, ?, ?, ?)",
              (job_id, aspirant_name, aspirant_email, resume_filename, submission_timestamp))
    conn.commit()
    conn.close()

def get_aspirant_submissions(job_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT submission_id, aspirant_name, aspirant_email, resume_filename, submission_timestamp FROM aspirant_submissions WHERE job_id=? ORDER BY submission_timestamp DESC", (job_id,))
    submissions = c.fetchall()
    conn.close()
    return submissions

def update_job_description_meta(job_id, recruiter_email, job_title):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE job_descriptions SET recruiter_email=?, job_title=? WHERE job_id=?",
              (recruiter_email, job_title, job_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing DB. Will use:", DATABASE_NAME)
    create_match_results_table()
    create_job_descriptions_table()
    create_aspirant_submissions_table()
    print(f"Database tables initialized in {DATABASE_NAME}.")
