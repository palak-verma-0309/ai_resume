import os
from pyresparser import ResumeParser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_resume():
    Tk().withdraw()  # Hide the GUI window
    file_path = askopenfilename(title="Select Resume (PDF or DOCX)", filetypes=[("PDF files", "*.pdf"), ("Word Documents", "*.docx")])
    return file_path

def main():
    file_path = select_resume()
    
    if not file_path:
        print("❌ No file selected.")
        return
    
    print(f"📄 Processing: {file_path}")
    
    try:
        data = ResumeParser(file_path).get_extracted_data()
        
        print("\n✅ Resume Data Extracted:")
        print("👤 Name:", data.get("name", "Not Found"))
    except Exception as e:
        print("❌ Error while parsing resume:", str(e))

if __name__ == "__main__":
    main()
