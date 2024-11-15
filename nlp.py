import os
import docx
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from itertools import chain
from nltk.stem import WordNetLemmatizer
from transformers import BertTokenizer, BertModel
import torch

# Ensure you have the required nltk data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Initialize Lemmatizer and BERT tokenizer and model
lemmatizer = WordNetLemmatizer()
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ' '.join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Function to preprocess text
def preprocess_text(text):
    # Tokenize and lemmatize
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens]  # Lemmatize words
    # Remove punctuation and stopwords
    table = str.maketrans('', '', string.punctuation)
    tokens = [w.translate(table) for w in tokens if w.isalpha()]
    stop_words = set(stopwords.words('english'))
    tokens = [w for w in tokens if w not in stop_words]
    # Return preprocessed text as a single string
    return " ".join(tokens)

# Function to get BERT embeddings for a given text
def get_bert_embeddings(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the [CLS] token's embedding (first token's embedding)
    return outputs.last_hidden_state[:, 0, :].numpy()

# Function to calculate cosine similarity between resume and job description using BERT
def score_resume(resume_path, job_description):
    # Extract text from the resume based on file type
    if resume_path.endswith('.pdf'):
        text = extract_text_from_pdf(resume_path)
    elif resume_path.endswith('.docx'):
        text = extract_text_from_docx(resume_path)
    else:
        raise ValueError("Unsupported file type. Please provide a .pdf or .docx file.")

    # Preprocess the extracted text and job description
    processed_resume_text = preprocess_text(text)
    processed_job_description = preprocess_text(job_description)

    # Get BERT embeddings for the resume and job description
    resume_embedding = get_bert_embeddings(processed_resume_text)
    job_description_embedding = get_bert_embeddings(processed_job_description)

    # Compute the dot product
    dot_product = np.dot(resume_embedding, job_description_embedding.T).flatten()[0]

    # Compute the norms (magnitudes) of the vectors
    resume_norm = np.linalg.norm(resume_embedding)
    job_description_norm = np.linalg.norm(job_description_embedding)

    # Calculate cosine similarity
    if resume_norm == 0 or job_description_norm == 0:
        return 0  # Avoid division by zero (in case of empty or invalid documents)
    cosine_similarity = dot_product / (resume_norm * job_description_norm)

    # Convert the similarity to a percentage
    score_percentage = int(cosine_similarity * 100)

    return score_percentage