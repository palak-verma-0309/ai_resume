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
4. Job History: List of dictionaries with Company, Role, Start Date, End Date (include previous roles also)
Resume:
\"\"\"{resume_text}\"\"\"
"""
    response = llm.invoke(prompt)
    return response

# ✅ Improved Function to extract experience section
def extract_job_history_section(resume_text):
    stop_headings = [
        'education', 'projects', 'certifications', 'skills',
        'achievements', 'personal', 'languages', 'contact',
        'summary', 'objective', 'hobbies', 'interests'
    ]

    lines = resume_text.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]
    exp_start = None
    exp_end = None

    # Find a proper heading like 'Experience' or 'Work Experience'
    for i, line in enumerate(clean_lines):
        line_lower = line.lower()
        if line_lower in ['experience', 'work experience', 'professional experience']:
            exp_start = i
            break

    if exp_start is not None:
        for j in range(exp_start + 1, len(clean_lines)):
            if any(stop in clean_lines[j].lower() for stop in stop_headings):
                exp_end = j
                break
        if exp_end is None:
            exp_end = len(clean_lines)

        experience_lines = clean_lines[exp_start:exp_end]
        return "\n".join(experience_lines).strip()

    return "❌ Could not find 'Experience' section as a proper heading."


# Streamlit UI
st.set_page_config(page_title="📄 Resume Parser", layout="centered")
st.title("📄 AI Resume Parser using Mistral")
st.markdown("Upload a resume PDF, and let the AI extract key information.")

uploaded_file = st.file_uploader("Choose a resume PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.success("✅ Resume text extracted!")

    # Optional Debug (see headings) – uncomment if needed
    # st.write("🪵 Possible Headings Found:")
    # for line in resume_text.splitlines():
    #     if line.strip() and len(line.strip().split()) <= 5 and line.strip().istitle():
    #         st.write(f"👉 {line.strip()}")

    # 🔍 Show raw Experience section
    st.subheader("📜 Raw Experience Section from Resume")
    experience_section = extract_job_history_section(resume_text)
    st.text_area("🔍 Extracted Experience Section", experience_section, height=300)

    # 🧠 Parse with Mistral
    if st.button("🧠 Parse Resume with Mistral"):
        with st.spinner("Parsing resume with Mistral..."):
            parsed_output = parse_resume_with_mistral(resume_text)

        st.subheader("📋 Parsed Resume Data (JSON)")
        st.code(parsed_output, language="json")
