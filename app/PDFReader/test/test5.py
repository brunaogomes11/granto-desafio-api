import fitz  # PyMuPDF

def extract_text_with_paragraph_breaks(pdf_path):
    document = fitz.open(pdf_path)
    all_text = ""

    for page_num in range(len(document)):
        page = document[page_num]
        blocks = page.get_text("blocks")  # Get text blocks including positions

        previous_bottom = None
        paragraph = ""

        for block in blocks:
            x0, y0, x1, y1, text, block_type, _ = block
            if block_type == 0:  # Only process text blocks
                text = text.split('\n')

                current_top = y0
                print(text)

                if previous_bottom is not None and current_top - previous_bottom > 10:
                    # Consider it a paragraph break if there's a significant vertical gap
                    all_text += paragraph.strip() + "\n\n"
                    paragraph = ""

                paragraph += " " + text.strip()
                previous_bottom = y1

        if paragraph:
            all_text += paragraph.strip() + "\n\n"

    document.close()
    return all_text.strip()

# Example usage
pdf_path = "./test/data/minuta2.pdf"

text = extract_text_with_paragraph_breaks(pdf_path)
print(text)
