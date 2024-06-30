import fitz
import docx

import pytesseract
from PIL import Image

import re
from spacy import load
from unidecode import unidecode

import io
from concurrent.futures import ThreadPoolExecutor, as_completed


class ReadDocument:
    def __init__(self):
        self.doc = None
        self.__cl_model = load("./app/document_reader/models/cl-v2_1")

        self.__min_row_len = 75
        self.__initial_key = "preambulo"
        self.__remove_index_pattern = r"\b\d{1,2}\.\d{1,2}(\.\d{1,2})*\b"


    def read_document(self, path: str) -> dict:
        file_ext = path.split(".")[-1]
        document = []      

        if file_ext == "pdf":
            document = self.read_from_pdf(path)
        elif file_ext == "docx":
            document = self.read_from_docx(path)
        elif file_ext == "txt":
            document = self.read_from_txt(path)
        else:
            raise Exception("Document type not supported")

        return self.__find_doc_keys(document)


    def read_from_pdf(self, path: str) -> list:
        self.doc = fitz.open(path)
        text_chunks = self.__get_chuncks_from_pdf()        

        if len(text_chunks) == 0:
            print("Scanned Document")
            text_chunks = self.__get_chuncks_from_scanned_doc()
        # self.debug(text_chunks)

        self.doc.close()
        return text_chunks


    def read_from_docx(self, path: str) -> list:
        return [p.text for p in docx.Document(path).paragraphs]


    def read_from_txt(self, path: str) -> list:
        with open(path, mode="r", encoding="UTF-8") as txt_file:
            txt_paragraphs = txt_file.read().split("\n")
            text_list = [text for text in txt_paragraphs if text.strip() != ""]
        
        return text_list


    def __get_chuncks_from_pdf(self) -> list:
        text_list, paragraph = [], ""
        
        for page in self.doc:
            blocks = page.get_text("blocks")

            for block in blocks:
                row = block[4].replace("\n", " ")
                text_list, paragraph = self.__is_paragraph(text_list, paragraph, row)

        return text_list


    def __get_chuncks_from_scanned_doc(self) -> list:
        images = self.__get_scanned_images()
        return self.__process_images_concurrently(images)


    def __get_scanned_images(self):
        images = []
        for page in self.doc:
            # Extract images from the page
            for img in page.get_images(full=True):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Load image with PIL
                im = Image.open(io.BytesIO(image_bytes))

                # Reduce the image resolution
                # (width, height) = (im.width // 2, im.height // 2)
                # im = im.resize((width, height))
                images.append(im)

        return images


    def __process_image(self, image) -> list:
        text_list, paragraph = [], ""

        page_text = pytesseract.image_to_string(image, lang="por")

        for row in page_text.split("\n"):
            text_list, paragraph = self.__is_paragraph(text_list, paragraph, row.strip())

        if paragraph.strip() != "":
            text_list.append(paragraph)

        return text_list


    def __process_images_concurrently(self, images: Image, max_workers = 1) -> list:
        results = []
    
        with ThreadPoolExecutor(max_workers = max_workers) as executor:
            future_to_image = {executor.submit(self.__process_image, image): image for image in images}
            
            for i, future in enumerate(as_completed(future_to_image)):
                # text_list = future_to_image[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Error processing index:{i + 1}: {e}")
        
        return [text for page in results for text in page]

    
    def __is_paragraph(self, text_list: list, paragraph: str, row: str):
        if len(row) < self.__min_row_len or row.strip()[-1] in [".", ";", ":"]: 
            paragraph += f" {row}"

            if paragraph.strip() != "" and len(paragraph) > 5:
                text_list.append(re.sub(self.__remove_index_pattern, "", paragraph).strip())

            paragraph = ""
        else:
            paragraph += f" {row}"

        return text_list, paragraph
    
    
    def __find_doc_keys(self, list: list) -> dict:
        key = self.__initial_key
        doc_dict = {}
        all_text = []

        for row in list:
            row = row.strip()
            doc = self.__cl_model(row).cats # Verify if is a title
            

            if doc["Clausula"] >= 0.95 or "CLAUSULA" in unidecode(row[:16]).upper(): # Intervalo arbitrário
                if  len(row) > 120: # Número arbitrário
                    row = row.split("-")[0]
                    row = row.split("–")[0]
                    print(row)
                
                new_key = self.__clean_key(row)

                if len(all_text) != 0:
                    doc_dict[key] = all_text

                key = new_key
                all_text = []

            else:
                all_text.append(row)

        if len(all_text) != 0:
            doc_dict[key] = all_text
            
        return doc_dict


    def __clean_key(self, row: str) -> str:
        new_key = unidecode(row) # Removes accent from string
        new_key = new_key.lower()
        # new_key = "".join([i for i in new_key if not i.isdigit()])
        new_key = new_key.replace("-", "")
        new_key = new_key.replace("\\", "")
        new_key = new_key.replace("/", "")
        new_key = new_key.replace(".", "")
        new_key = new_key.replace(",", "")
        new_key = new_key.strip()
        new_key = new_key.replace("  ", "_")
        new_key = new_key.replace(" ", "_")
        return new_key

    def debug(self, text_chunks):
        with open("./app/document_reader/test/data/result.txt", mode='w') as txt:
            txt.write("")
        
        with open("./app/document_reader/test/data/result.txt", mode='a', encoding='UTF-8') as txt:
            for line in text_chunks:
                txt.write(line + "\n")