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

# Function to parse resume with Mistral
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

# Function to extract experience section only
def extract_experience_section(resume_text):
    stop_headings = [
        'education', 'projects', 'certifications', 'skills',
        'achievements', 'personal', 'languages', 'contact',
        'summary', 'objective', 'hobbies', 'interests'
    ]
    lines = resume_text.splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]
    exp_start, exp_end = None, None

    for i, line in enumerate(clean_lines):
        if line.lower() in ['experience', 'work experience', 'professional experience']:
            exp_start = i
            break
    if exp_start is not None:
        for j in range(exp_start + 1, len(clean_lines)):
            if any(stop in clean_lines[j].lower() for stop in stop_headings):
                exp_end = j
                break
        if exp_end is None:
            exp_end = len(clean_lines)
        return "\n".join(clean_lines[exp_start:exp_end]).strip()
    return ""

# App UI
st.set_page_config(page_title="📄 Multi Resume Parser", layout="wide")
st.title("📄 Upload Multiple Resumes and Parse as Needed")

uploaded_files = st.file_uploader("Upload multiple resume PDFs", type=["pdf"], accept_multiple_files=True)

# 🔍 Input once from user
search_input = st.text_input("🔍 Enter comma-separated keywords to search in all resumes")

# Main logic after upload
if uploaded_files:
    if "all_data" not in st.session_state:
        st.session_state.all_data = {}

    for idx, uploaded_file in enumerate(uploaded_files):
        file_key = f"resume_{idx}"

        if file_key not in st.session_state.all_data:
            with st.spinner(f"Reading {uploaded_file.name}..."):
                text = extract_text_from_pdf(uploaded_file)
                exp = extract_experience_section(text)
                st.session_state.all_data[file_key] = {
                    "name": uploaded_file.name,
                    "text": text,
                    "experience": exp,
                    "parsed": None
                }

        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"📄 **{uploaded_file.name}**")
        with col2:
            if st.button(f"🧠 Parse {uploaded_file.name}", key=f"btn_{idx}"):
                with st.spinner("Parsing with Mistral..."):
                    result = parse_resume_with_mistral(st.session_state.all_data[file_key]["text"])
                    st.session_state.all_data[file_key]["parsed"] = result

        # Show parsed JSON if available
        if st.session_state.all_data[file_key]["parsed"]:
            st.code(st.session_state.all_data[file_key]["parsed"], language="json")

    # 🔍 Keyword Search across all resumes
    if search_input:
        st.markdown("---")
        st.subheader("🔎 Keyword Match Results")

        keywords = [k.strip().lower() for k in search_input.split(",") if k.strip()]
        for data in st.session_state.all_data.values():
            matches = [kw for kw in keywords if kw in data["experience"].lower()]
            if matches:
                st.success(f"✅ **{data['name']}** matched: {', '.join(matches)}")
            else:
                st.info(f"❌ **{data['name']}** matched: None")
