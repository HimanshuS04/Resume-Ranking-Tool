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
