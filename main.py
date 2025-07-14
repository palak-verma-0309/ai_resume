import streamlit as st
import fitz  # PyMuPDF
from langchain.llms import Ollama

# Function to extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text.strip()

# Function to call Mistral model from Ollama
def parse_resume_with_mistral(resume_text):
    llm = Ollama(model="mistral")

    prompt = f"""
You are a professional resume parser.

From the resume below, extract the following information in JSON format:
1. Full Name
2. Total Work Experience (calculate based on job start and end dates if needed)
3. Skills
4. Job History: List of dictionaries with Company, Role, Start Date, End Date(include previous roles also)

Resume:
\"\"\"{resume_text}\"\"\"
"""
    response = llm.invoke(prompt)
    return response

# Streamlit UI
st.set_page_config(page_title="📄 Resume Parser", layout="centered")
st.title("📄 AI Resume Parser using Mistral")
st.markdown("Upload a resume PDF, and let the AI extract key information.")

uploaded_file = st.file_uploader("Choose a resume PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.success("✅ Resume text extracted!")
    
    if st.button("🔍 Parse Resume with Mistral"):
        with st.spinner("Parsing resume with Mistral..."):
            parsed_output = parse_resume_with_mistral(resume_text)
        
        st.subheader("📋 Parsed Resume Data")
        st.code(parsed_output, language="json")
