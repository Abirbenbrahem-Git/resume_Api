import re
import fitz
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def extract_emails_from_pdf(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()

    return text

import re

def extract_mobile_number(text):
    phone = re.findall(r'\b\d{8}\b', text)

    if phone:
        number = ''.join(phone[0])
        return number
    else:
        return None

import spacy
from spacy.matcher import Matcher
import fitz  # PyMuPDF

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

def extract_name_from_pdf(pdf_file_path):
    # Extract text from PDF
    with fitz.open(pdf_file_path) as doc:
        pdf_text = ""
        for page_number in range(doc.page_count):
            page = doc[page_number]
            pdf_text += page.get_text()

    return extract_name(pdf_text)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

    matcher.add('NAME', patterns=[pattern])

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

import spacy
import json
from PyPDF2 import PdfReader

class EntityGenerator:
    def __init__(self, text=None):
        self.text = text

    def get(self):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(self.text)
        entities = {"EDUCATION": [], "EXPERIENCE": [], "SKILLS": []}

        # Mots-clés pour identifier les sections
        education_keywords = ["education", "formation", "diplôme", "études"]
        experience_keywords = ["experience", "expérience", "emploi", "travail"]
        skills_keywords = ["skills", "compétences", "aptitudes"]

        current_section = None
        current_phrase = []

        for token in doc:
            if token.text.lower() in education_keywords:
                current_section = "EDUCATION"
            elif token.text.lower() in experience_keywords:
                current_section = "EXPERIENCE"
            elif token.text.lower() in skills_keywords:
                current_section = "SKILLS"
            elif current_section is not None:
                current_phrase.append(token.text)
                if token.is_punct or token.is_space:
                    sentence = " ".join(current_phrase).strip()
                    if current_section == "SKILLS":
                        # Extract skills as a comma-separated list
                        entities["SKILLS"].extend(sentence.split(','))
                    else:
                        entities[current_section].append(sentence)
                    current_phrase = []

        # Remove empty strings from the skills list
        entities["SKILLS"] = list(filter(None, entities["SKILLS"]))

        return entities


if __name__ == "__main__":
    pdf_file_path = "C:\\Users\\LENOVO\\PycharmProjects\\pythonProject1\\data\\2.pdf"
    pdf_text = extract_emails_from_pdf(pdf_file_path)

    # Assuming the PDF contains email addresses, you can split the text into lines
    lines = pdf_text.split('\n')

    # Extract emails from each line and print the results
    for line in lines:
        extracted_email = extract_email(line)
        extracted_phone = extract_mobile_number(line)
        if extracted_email:
            print(f"Extracted email: {extracted_email}")
        if extracted_phone:
            print(f"Extracted phone: {extracted_phone}")
    # Extract name from PDF
    # extracted_name = extract_name_from_pdf(pdf_file_path)

    # Print the extracted name
    # print("Extracted Name:", extracted_name)

    extracted_name = extract_name_from_pdf(pdf_file_path)
    print("Prénom:", extracted_name.split()[0])
    print("Nom :", extracted_name.split()[1])


class Resume:
    def __init__(self, filename=None):
        self.filename = filename

    def get_text_from_pdf(self):
        with open(self.filename, 'rb') as file:
            pdf_reader = PdfReader(file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text.replace('\n', ' ')  # Remplacer les caractères de nouvelle ligne par un espace


# Example Usage
resume = Resume(filename="C:\\Users\\LENOVO\\PycharmProjects\\pythonProject1\\data\\abir ben brahem.pdf")
resume_text = resume.get_text_from_pdf()

if resume_text:
    entity_generator = EntityGenerator(text=resume_text)
    entities = entity_generator.get()

    # Remove sentences starting with "\u25cb" from the EXPERIENCE section
    entities["EXPERIENCE"] = [sentence for sentence in entities["EXPERIENCE"] if not sentence.startswith("\u25cb")]
    entities["EDUCATION"] = [sentence for sentence in entities["EDUCATION"] if not sentence.startswith("\u25cb")]

    # Print the extracted entities including SKILLS
    print(json.dumps(entities, indent=3))
else:
    print("Error: No text extracted from the resume.")




from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get_results')
def get_results():
    pdf_file_path = "C:\\Users\\LENOVO\\PycharmProjects\\pythonProject1\\data\\abir ben brahem.pdf"
    pdf_text = extract_emails_from_pdf(pdf_file_path)

    # Assuming the PDF contains email addresses, you can split the text into lines
    lines = pdf_text.split('\n')

    extracted_info = {"phone": None, "email": None, "first_name": None, "last_name": None}

    # Extract emails from each line and print the results
    for line in lines:
        extracted_email = extract_email(line)
        extracted_phone = extract_mobile_number(line)
        if extracted_email:
            extracted_info["email"] = extracted_email
        if extracted_phone:
            extracted_info["phone"] = extracted_phone

    # Extract name from PDF
    extracted_name = extract_name_from_pdf(pdf_file_path)
    if extracted_name:
        extracted_info["first_name"] = extracted_name.split()[0]
        extracted_info["last_name"] = extracted_name.split()[1]

    resume = Resume(filename="C:\\Users\\LENOVO\\PycharmProjects\\pythonProject1\\data\\abir ben brahem.pdf")
    resume_text = resume.get_text_from_pdf()

    if resume_text:
        entity_generator = EntityGenerator(text=resume_text)
        entities = entity_generator.get()

        # Remove sentences starting with "\u25cb" from the EXPERIENCE section
        entities["EXPERIENCE"] = [sentence for sentence in entities["EXPERIENCE"] if not sentence.startswith("\u25cb")]
        entities["EDUCATION"] = [sentence for sentence in entities["EDUCATION"] if not sentence.startswith("\u25cb")]

        # Add the extracted info to the entities JSON
        entities.update(extracted_info)

        # Print the extracted entities including SKILLS and the additional info
        return jsonify(entities)
    else:
        return jsonify({"error": "No text extracted from the resume."})

if __name__ == '__main__':
    app.run(debug=True)


#http://127.0.0.1:5000/get_results
