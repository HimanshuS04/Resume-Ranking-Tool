import os
from PyPDF2 import PdfReader
import docx
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Ensure you have the required nltk data
nltk.download('stopwords')
nltk.download('punkt')

STOPWORDS = set(stopwords.words('english'))


# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Function to preprocess text
def preprocess_text(text):
    tokens = nltk.word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha() and word.lower() not in STOPWORDS]
    return ' '.join(tokens)

# Function to rank resumes based on TF-IDF scores
def rank_resumes(resume_texts, job_description):
    vectorizer = TfidfVectorizer(stop_words='english')
    resume_tfidf = vectorizer.fit_transform(resume_texts)
    job_description_tfidf = vectorizer.transform([job_description])

    scores = np.dot(resume_tfidf, job_description_tfidf.T).toarray().flatten()
    return scores

# Main function to extract and rank resumes
def main(resume_folder, job_description):
    resume_texts = []
    for file_name in os.listdir(resume_folder):
        file_path = os.path.join(resume_folder, file_name)
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            continue
        resume_texts.append(preprocess_text(text))

    scores = rank_resumes(resume_texts, preprocess_text(job_description))
    scores = (scores * 100).astype(int)
    ranked_resumes = sorted(zip(os.listdir(resume_folder), scores), key=lambda x: x[1], reverse=True)
    

    return ranked_resumes


