import pdfplumber
from pathlib import Path
import io
    
#===============================================================================
def extract_text_from_pdf(file_path:str) -> str: # used this definition to input string and output string

    path = Path(file_path)
    extracted_pages = []

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text.strip())

    if not extracted_pages:
        raise ValueError(
            "No text could be extracted from this PDF. NOOOOOOOOOOOOOOOOO"
        )

    return "\n\n".join(extracted_pages)
#===============================================================================
'''
If i would upload pdf through UI  with a build api using FastAPI 
you can use the `extract_text_from_bytes` function to handle the uploaded file as bytes. 
This function reads the PDF content directly from the byte stream, 
allowing me to extract text without needing to save the file to disk first.
'''
def extract_text_from_bytes(file_bytes: bytes) -> str:
    extracted_pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_pages.append(text.strip())

    if not extracted_pages:
        raise ValueError("No text could be extracted from the uploaded PDF.")

    return "\n\n".join(extracted_pages)

#===============================================================================
'''
Main function is build to test the code and see if it works well
'''
# def main():
#     pdf_path = r"./Input_files/student_answer.pdf"  # put your PDF file here

#     try:
#         text = extract_text_from_pdf(pdf_path)
#         print(text[:1000])  # print first 1000 characters
#     except Exception as e:
#         print(f"Error: {e}")


# if __name__ == "__main__":
#     main()