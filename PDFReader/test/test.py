import fitz  # PyMuPDF
import easyocr
from PIL import Image
import io
import numpy as np

# Function to convert PDF pages to images
def pdf_page_to_image(pdf_path, dpi=300):
    # Open the PDF file
    document = fitz.open(pdf_path)
    images = []
    
    # Iterate through each page

    # Loop through each page
    for page in document:
        # Extract images from the page
        images = page.get_images(full=True)
        
        for img in images:
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image['image']
            # image_ext = base_image['ext']

        image = Image.open(io.BytesIO(image_bytes))
        images.append(image)
    
    return images

# Function to extract text from images using EasyOCR
def extract_text_from_images(images):
    reader = easyocr.Reader(['pt'], gpu=False)  # Set gpu=True if you have a GPU
    texts = []
    
    for image in images:
        # Convert PIL Image to numpy array
        image_np = np.array(image)
        result = reader.readtext(image_np)
        
        # Extract and concatenate the text
        page_text = ' '.join([item[1] for item in result])
        texts.append(page_text)
    
    return texts

# Example usage
pdf_path = './test/data/minuta4.pdf'

# Convert PDF pages to images
images = pdf_page_to_image(pdf_path)

# Extract text from the images
texts = extract_text_from_images(images)

# Combine and print all text
full_text = "\n".join(texts)
print(full_text)
