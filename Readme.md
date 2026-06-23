# Resume Matcher

A Flask-based Resume Matching System that compares candidate resumes with job descriptions using Natural Language Processing (NLP) techniques.

## Overview

This application helps recruiters identify suitable candidates by calculating the similarity between resumes and job descriptions. The system ranks resumes based on their relevance to the job requirements.

## Features

- Upload job descriptions
- Upload candidate resumes
- Automatic resume-job matching
- Similarity score calculation
- Recruiter dashboard
- Candidate ranking
- SQLite database integration

## Technologies Used

- Python
- Flask
- SQLite
- Scikit-learn
- NumPy
- HTML/CSS

## NLP Techniques Used

### TF-IDF (Term Frequency–Inverse Document Frequency)

Converts textual data into numerical vectors while emphasizing important keywords and reducing the impact of common words.

### Cosine Similarity

Measures the similarity between resume and job description vectors to generate a match score.

## Project Structure

```text
Resume-Matcher/
│
├── templates/
├── resumes/
├── job_descriptions/
├── app.py
├── database.py
├── matcher_logic.py
└── requirements.txt
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/rahulrajesh-git/resume-matcher.git
cd resume-matcher
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

## Workflow

1. Recruiter uploads a job description.
2. Candidates upload their resumes.
3. Text is extracted and preprocessed.
4. TF-IDF vectorization is performed.
5. Cosine similarity is calculated.
6. Candidates are ranked based on match scores.

## Future Enhancements

- BERT-based semantic matching
- Skill extraction using NLP
- Resume parsing automation
- PDF report generation
- Advanced recruiter analytics

## Author

Rahul Rajesh