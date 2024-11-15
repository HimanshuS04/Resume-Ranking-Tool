import os
from PyPDF2 import PdfReader
import docx
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from nltk.tokenize import word_tokenize
import string
from itertools import chain

# Ensure you have the required nltk data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')


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
  x=[]
  tokens=word_tokenize(text)
  tok=[w.lower() for w in tokens]
  table=str.maketrans('','',string.punctuation)
  strpp=[w.translate(table) for w in tok]
  words=[word for word in strpp if word.isalpha()]
  stop_words=set(stopwords.words('english'))
  words=[w for w in words if not w in stop_words]
  x.append(words)
  res=" ".join(chain.from_iterable(x))
  return res



def score_resume(resume_path, job_description):
    # Extract text from the resume based on file type
    if resume_path.endswith('.pdf'):
        text = extract_text_from_pdf(resume_path)
    elif resume_path.endswith('.docx'):
        text = extract_text_from_docx(resume_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .pdf or .docx file.")

    # Preprocess the extracted text and job description
    processed_resume_text = [preprocess_text(text)]
    processed_job_description = [preprocess_text(job_description)]

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit the vectorizer on both resume and job description
    resume_tfidf = vectorizer.fit_transform(processed_resume_text)
    job_description_tfidf = vectorizer.transform(processed_job_description)

    # Compute the dot product
    dot_product = np.dot(resume_tfidf, job_description_tfidf.T).toarray().flatten()[0]

    # Compute the norms (magnitudes) of the vectors
    resume_norm = np.linalg.norm(resume_tfidf.toarray())
    job_description_norm = np.linalg.norm(job_description_tfidf.toarray())

    # Calculate cosine similarity
    cosine_similarity = dot_product / (resume_norm * job_description_norm)

    # Convert the similarity to a percentage
    score_percentage = int(cosine_similarity * 100)

    return score_percentage
