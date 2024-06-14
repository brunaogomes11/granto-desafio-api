import fitz  # PyMuPDF
import re

def remove_line_breaks(text):
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove space before punctuation
    text = re.sub(r'\s+([.,?!;:])', r'\1', text)
    # Ensure space after punctuation if not already present
    text = re.sub(r'([.,?!;:])(\S)', r'\1 \2', text)
    return text.strip()

def extract_text_without_line_breaks(pdf_path):
    # Open the PDF file
    document = fitz.open(pdf_path)
    all_text = ""
    
    for page_num in range(len(document)):
        page = document[page_num]
        # Extract text with simple layout
        text = page.get_text("text")
        # Process text to remove line breaks while preserving format
        text = remove_line_breaks(text)
        all_text += text + " "  # Add a space between page contents

    document.close()
    return all_text.strip()

# Example usage
pdf_path = "./test/data/minuta2.pdf"
text = extract_text_without_line_breaks(pdf_path)
print(text)