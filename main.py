import streamlit as st
import fitz  # PyMuPDF
from langchain.llms import Ollama

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text.strip()

# Mistral parsing
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

# Extract experience section
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


# 🚀 Streamlit App
st.set_page_config(page_title="📄 Resume Parser", layout="centered")
st.title("📄 AI Resume Parser using Mistral")
st.markdown("Upload a resume PDF, and let the AI extract key information.")

uploaded_file = st.file_uploader("Choose a resume PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    st.success("✅ Resume text extracted!")

    # ✅ Store raw experience section
    st.session_state.raw_experience = extract_job_history_section(resume_text)

    # 🧠 Parse with Mistral
    if st.button("🧠 Parse Resume with Mistral"):
        with st.spinner("Parsing resume with Mistral..."):
            parsed_output = parse_resume_with_mistral(resume_text)

        st.session_state.parsed_output = parsed_output  # Store in session

# ✅ Show Mistral output if available
if "parsed_output" in st.session_state:
    st.subheader("📋 Parsed Resume Data (JSON)")
    st.code(st.session_state.parsed_output, language="json")

# ✅ Keyword Search — always below parsed result
if "raw_experience" in st.session_state:
    st.subheader("🔍 Search Your Keywords in Experience Section")
    search_input = st.text_input("Enter comma-separated keywords (e.g., Python, Django, ML)")

    if search_input:
        # Process keywords
        search_words = [word.strip().lower() for word in search_input.split(",") if word.strip()]
        experience_text = st.session_state.raw_experience.lower()

        matched_words = [word for word in search_words if word in experience_text]

        if matched_words:
            st.success(f"✅ Matched Keywords: {', '.join(matched_words)}")
        else:
            st.warning("⚠️ No keywords matched in the experience section.")
