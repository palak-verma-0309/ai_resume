import spacy
import os
import docx2txt
import fitz  # PyMuPDF
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Load SpaCy NER model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(path):
    text = ""
    pdf = fitz.open(path)
    for page in pdf:
        text += page.get_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(path):
    return docx2txt.process(path)

# Function to extract name using SpaCy
def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Name not found"

# GUI to select file
def select_file():
    Tk().withdraw()  # Hide root window
    file_path = askopenfilename(title="Select Resume (PDF or DOCX)")
    return file_path

# Main logic
if __name__ == "__main__":
    file_path = select_file()

    if not file_path:
        print("❌ No file selected.")
        exit()

    ext = os.path.splitext(file_path)[1].lower()

    print(f"📄 Selected File: {file_path}")

    if ext == ".pdf":
        resume_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        resume_text = extract_text_from_docx(file_path)
    else:
        print("❌ Unsupported file type. Please upload a PDF or DOCX.")
        exit()

    # Extract and display name
    name = extract_name(resume_text)
    print(f"✅ Extracted Name: {name}")
