import fitz  # PyMuPDF
from langchain.llms import Ollama
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_resume_file():
    Tk().withdraw()  # hide GUI window
    file_path = askopenfilename(
        title="Select Resume PDF", filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def call_mistral_resume_parser(resume_text):
    llm = Ollama(model="mistral")

    prompt = f"""
You are a professional resume parser. Extract the following details in JSON format from the given resume text:
- Full Name
- Total Experience (in years and months)
- Skills
- Job History: (Company, Role, Start Date, End Date)(include previous roles also)

Resume:
\"\"\"{resume_text}\"\"\"
"""
    result = llm.invoke(prompt)
    return result

if __name__ == "__main__":
    print("📄 Please select a resume PDF...")
    resume_path = select_resume_file()
    
    if resume_path:
        print(f"✅ Selected file: {resume_path}")
        resume_text = extract_text_from_pdf(resume_path)
        print("🧠 Parsing with Mistral...")
        parsed_output = call_mistral_resume_parser(resume_text)
        print("\n📋 Parsed Resume Data:\n")
        print(parsed_output)
    else:
        print("❌ No file selected.")
