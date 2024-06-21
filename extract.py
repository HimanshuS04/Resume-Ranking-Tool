import os
from PyPDF2 import PdfReader
import docx
import nltk
from nltk.corpus import stopwords
from collections import Counter

# Ensure you have the required nltk data


STOPWORDS = set(stopwords.words('english'))

# Define constants
NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

EDUCATION = [
    'BE','B.E.', 'B.E', 'BS', 'B.S', 'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'BTECH', 'MTECH',
    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'
NUMBER = r'\d+'
MONTHS_SHORT = r'(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)|(aug)|(sep)|(oct)|(nov)|(dec)'
MONTHS_LONG = r'(january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december)'
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'

RESUME_SECTIONS = [
    'accomplishments',
    'experience',
    'education',
    'interests',
    'projects',
    'professional experience',
    'publications',
    'skills',
]

COMPETENCIES = {
    'teamwork': [
        'supervised', 'facilitated', 'planned', 'plan', 'served', 'serve', 'project lead', 'managing', 'managed', 'lead ',
        'project team', 'team', 'conducted', 'worked', 'gathered', 'organized', 'mentored', 'assist', 'review', 'help',
        'involve', 'share', 'support', 'coordinate', 'cooperate', 'contributed'
    ],
    'communication': [
        'addressed', 'collaborated', 'conveyed', 'enlivened', 'instructed', 'performed', 'presented', 'spoke', 'trained',
        'author', 'communicate', 'define', 'influence', 'negotiated', 'outline', 'proposed', 'persuaded', 'edit', 
        'interviewed', 'summarize', 'translate', 'write', 'wrote', 'project plan', 'business case', 'proposal', 'writeup'
    ],
    'analytical': [
        'process improvement', 'competitive analysis', 'aligned', 'strategic planning', 'cost savings', 'researched ',
        'identified', 'created', 'led', 'measure', 'program', 'quantify', 'forecast', 'estimate', 'analyzed', 'survey',
        'reduced', 'cut cost', 'conserved', 'budget', 'balanced', 'allocate', 'adjust', 'launched', 'hired', 'spedup',
        'speedup', 'ran', 'run', 'enhanced', 'developed'
    ],
    'result_driven': [
        'cut', 'decrease', 'eliminate', 'increase', 'lower', 'maximize', 'raise', 'reduce', 'accelerate', 'accomplish',
        'advance', 'boost', 'change', 'improve', 'saved', 'save', 'solve', 'solved', 'upgrade', 'fix', 'fixed', 
        'correct', 'achieve'
    ],
    'leadership': [
        'advise', 'coach', 'guide', 'influence', 'inspire', 'instruct', 'teach', 'authorized', 'chair', 'control',
        'establish', 'execute', 'hire', 'multi-task', 'oversee', 'navigate', 'prioritize', 'approve', 'administer',
        'preside', 'enforce', 'delegate', 'coordinate', 'streamlined', 'produce', 'review', 'supervise', 'terminate',
        'found', 'set up', 'spearhead', 'originate', 'innovate', 'implement', 'design', 'launch', 'pioneer', 'institute'
    ]
}

MEASURABLE_RESULTS = {
    'metrics': [
        'saved', 'increased', '$ ', '%', 'percent', 'upgraded', 'fundraised ', 'millions', 'thousands', 'hundreds',
        'reduced annual expenses ', 'profits', 'growth', 'sales', 'volume', 'revenue', 'reduce cost', 'cut cost',
        'forecast', 'increase in page views', 'user engagement', 'donations', 'number of cases closed', 'customer ratings',
        'client retention', 'tickets closed', 'response time', 'average', 'reduced customer complaints', 'managed budget',
        'numeric_value'
    ],
    'action_words': [
        'developed', 'led', 'analyzed', 'collaborated', 'conducted', 'performed', 'recruited', 'improved', 'founded',
        'transformed', 'composed', 'conceived', 'designed', 'devised', 'established', 'generated', 'implemented', 'initiated',
        'instituted', 'introduced', 'launched', 'opened', 'originated', 'pioneered', 'planned', 'prepared', 'produced',
        'promoted', 'started', 'released', 'administered', 'assigned', 'chaired', 'consolidated', 'contracted', 'co-ordinated',
        'delegated', 'directed', 'evaluated', 'executed', 'organized', 'oversaw', 'prioritized', 'recommended', 'reorganized',
        'reviewed', 'scheduled', 'supervised', 'guided', 'advised', 'coached', 'demonstrated', 'illustrated', 'presented',
        'taught', 'trained', 'mentored', 'spearheaded', 'authored', 'accelerated', 'achieved', 'allocated', 'completed',
        'awarded', 'persuaded', 'revamped', 'influenced', 'assessed', 'clarified', 'counseled', 'diagnosed', 'educated',
        'facilitated', 'familiarized', 'motivated', 'participated', 'provided', 'referred', 'rehabilitated', 'reinforced',
        'represented', 'moderated', 'verified', 'adapted', 'coordinated', 'enabled', 'encouraged', 'explained', 'informed',
        'instructed', 'lectured', 'stimulated', 'classified', 'collated', 'defined', 'forecasted', 'identified', 'interviewed',
        'investigated', 'researched', 'tested', 'traced', 'interpreted', 'uncovered', 'collected', 'critiqued', 'examined',
        'extracted', 'inspected', 'inspired', 'summarized', 'surveyed', 'systemized', 'arranged', 'budgeted', 'controlled',
        'eliminated', 'itemised', 'modernised', 'operated', 'organised', 'processed', 'redesigned', 'reduced', 'refined',
        'resolved', 'revised', 'simplified', 'solved', 'streamlined', 'appraised', 'audited', 'balanced', 'calculated',
        'computed', 'projected', 'restructured', 'modelled', 'customized', 'fashioned', 'integrated', 'proved', 'revitalized',
        'set up', 'shaped', 'structured', 'tabulated', 'validated', 'approved', 'catalogued', 'compiled', 'dispatched',
        'filed', 'monitored', 'ordered', 'purchased', 'recorded', 'retrieved', 'screened', 'specified', 'systematized',
        'conceptualized', 'brainstormed', 'tasked', 'supported', 'proposed', 'boosted', 'earned', 'negotiated', 'navigated',
        'updated', 'utilized'
    ],
    'weak_words': [
        'i', 'got', 'i\'ve', 'because', 'our', 'me', 'he', 'her', 'him', 'she', 'helped', 'familiar', 'assisted', 'like',
        'enjoy', 'love', 'did', 'tried', 'attempted', 'worked', 'approximately', 'managed', 'manage', 'create', 'created'
    ]
}

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
    return tokens

# Function to rank resumes based on keywords and competencies
def rank_resumes(resume_texts, keywords, competencies):
    keyword_set = set(keywords)
    scores = []
    for resume in resume_texts:
        tokens = preprocess_text(resume)
        counter = Counter(tokens)
        score = sum(counter[keyword] for keyword in keyword_set if keyword in counter)
        score += sum(counter[word] for comp in competencies.values() for word in comp if word in counter)
        scores.append(score)
    return scores

# Main function to extract and rank resumes
def main(resume_folder, keywords, competencies):
    resume_texts = []
    for file_name in os.listdir(resume_folder):
        file_path = os.path.join(resume_folder, file_name)
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            continue
        resume_texts.append(text)

    scores = rank_resumes(resume_texts, keywords, competencies)
    ranked_resumes = sorted(zip(os.listdir(resume_folder), scores), key=lambda x: x[1], reverse=True)

    for rank, (file_name, score) in enumerate(ranked_resumes, start=1):
        print(f"Rank {rank}: {file_name} with score {score}")

# Example usage

  # Replace with the path to your resume folder
text="Job Title: Software Developer Company: [Company Name] Location: [Specify Location, e.g., San Francisco, CA] Job Summary: We are seeking a talented Software Developer to join our dynamic team. As a Software Developer, you will be responsible for designing, developing, and implementing software solutions to address complex business issues. You will work closely with product managers and engineers to deliver high-quality code and contribute to the overall success of our projects. Key Responsibilities: Design, develop, and maintain software applications and solutions. Collaborate with cross-functional teams to define, design, and ship new features. Write clean, scalable, and maintainable code that meets coding standards. Conduct thorough testing and debugging to ensure software functionality and performance. Troubleshoot and resolve issues reported by users or team members. Stay updated with the latest technologies and industry trends in software development. Participate in code reviews and provide constructive feedback to peers. Required Qualifications: Bachelor’s degree in Computer Science, Engineering, or a related field. Proven experience as a Software Developer or Software Engineer. Strong proficiency in one or more programming languages such as Java, Python, C++, JavaScript, etc. Experience with software development methodologies (Agile, Scrum, etc.). Familiarity with relational databases and SQL. Ability to work independently and as part of a team in a fast-paced environment. Excellent problem-solving and analytical skills. Preferred Qualifications: Master’s degree in Computer Science, Engineering, or a related field. Experience with web development frameworks (e.g., Django, Spring, React, Angular). Knowledge of cloud computing platforms (AWS, Azure, Google Cloud). Familiarity with version control systems (Git, SVN). Experience in mobile application development (iOS, Android)."


if __name__ == "__main__":
    resume_folder = 'uploads'
    keywords = preprocess_text(text)  # Replace with your desired keywords
    main(resume_folder, keywords, COMPETENCIES)
