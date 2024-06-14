import fitz
import pytesseract
from PIL import Image
import io

import re
from spacy import load
from unidecode import unidecode


class ReadDocument():
    def __init__(self, doc_path: str):
        # Open the PDF file
        self.doc = fitz.open(doc_path)

        self.__cl_model = load('app/PDFReader/models/cl_model')
        self.__initial_key = 'preambulo'
        self.__min_row_len = 75
        self.__remove_index_pattern = r'\b\d{1,2}\.\d{1,2}(\.\d{1,2})*\b'


    def get_text_dict_from_pdf(self) -> dict:
        all_text = self.__get_chuncks()

        if len(all_text) == 0:
            print('Scanned Document')
            all_text = self.__get_chuncks_from_scanned_doc()

        self.debug(all_text)

        self.doc.close()

        return self.__find_doc_keys(all_text)


    def __get_chuncks(self) -> list:
        all_text = []
        paragraph = ''
        
        for page in self.doc:
            blocks = page.get_text('blocks')
            # rect = page.rect
            # footer_rect = fitz.Rect(rect.x0, rect.y1 - 50, rect.x1, rect.y1)

            # # Define the area to ignore (the footer)
            # footer_rect = fitz.Rect(rect.x0, rect.y1 - 50, rect.x1, rect.y1)

            for block in blocks:
                # if footer_rect.intersects(fitz.Rect(block[:4])):
                #     continue

                row = block[4].replace('\n', ' ')

                if len(row) < self.__min_row_len or row.strip()[-1] in ['.', ':']:
                    paragraph += row

                    if paragraph != '' and len(paragraph) > 5:
                        all_text.append(re.sub(self.__remove_index_pattern, '', paragraph).strip())

                    paragraph = ''
                else:
                    paragraph += row

        return all_text


    def __get_chuncks_from_scanned_doc(self) -> list:
        all_text = []
        paragraph = ''

        # Loop through each page
        for page in self.doc:
            # Extract images from the page
            images = page.get_images(full=True)
            
            for img in images:
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image['image']
                
                # Load image with PIL
                im = Image.open(io.BytesIO(image_bytes))
                # (width, height) = (im.width // 2, im.height // 2)
                # im = im.resize((width, height))
                
                # Apply OCR to the image
                page_text = pytesseract.image_to_string(im, lang='por')

                for row in page_text.split('\n'):
                    row = row.strip()

                    if len(row) < self.__min_row_len or row[-1] in ['.']:
                        paragraph += ' ' + row

                        if paragraph.strip() != '' and len(paragraph) > 5:
                            all_text.append(re.sub(self.__remove_index_pattern, '', paragraph).strip())

                        paragraph = ''
                    else:
                        paragraph += ' ' + row

        return all_text
    
    
    def __find_doc_keys(self, list: list) -> dict:
        key = self.__initial_key
        doc_dict = {}
        all_text = []

        for row in list:
            row = row.strip()
            doc = self.__cl_model(row).cats # Verify if is a title

            if doc['Clausula'] >= 0.95:
                print(row)
                new_key = self.clean_key(row)

                if len(all_text) != 0:
                    doc_dict[key] = all_text

                key = new_key
                all_text = []
            else:
                all_text.append(row)

        if len(all_text) != 0:
            doc_dict[key] = all_text
            
        return doc_dict

    def clean_key(self, row: str) -> str:
        new_key = unidecode(row) # Removes accent from string
        new_key = new_key.lower()
        # new_key = ''.join([i for i in new_key if not i.isdigit()])
        new_key = new_key.replace('-', '')
        new_key = new_key.replace('\\', '')
        new_key = new_key.replace('/', '')
        new_key = new_key.replace('.', '')
        new_key = new_key.replace(',', '')
        new_key = new_key.strip()
        new_key = new_key.replace('  ', '_')
        new_key = new_key.replace(' ', '_')

        return new_key

    def debug(self, list):
        with open('app/PDFReader/test/data/result.txt', mode='w', encoding='UTF-8') as f:
            f.write('')

        with open('app/PDFReader/test/data/result.txt', mode='a', encoding='UTF-8') as f:
            for text in list:
                f.write(text + '\n\n')


    # def __get_text_chunks(self) -> dict:
    #     key = self.__initial_key
    #     text_chunks = {}

    #     for page in self.doc:
    #         blocks = page.get_text('blocks')            
    #         for block in blocks:
    #             row = block[4].strip()
    #             doc = self.__cl_model(row).cats # Verify if is a title

    #             if doc['Clausula'] >= 0.95:
    #                 new_key = row.lower()
    #                 new_key = unidecode(new_key) # Removes accent from string
    #                 new_key = new_key.replace(' - ', '')
    #                 new_key = new_key.replace(' ', '_')

    #                 if len(all_text) != 0:
    #                     if paragraph != '':
    #                         all_text.append(paragraph)
    #                     text_chunks[key] = all_text

    #                 key = new_key
    #                 all_text = []
    #                 paragraph = ''

    #             elif len(row) < min_row_len:
    #                 paragraph += row
    #                 if paragraph != '' and len(paragraph) > 5:
    #                     all_text.append(paragraph.replace('- ', '  '))
    #                 paragraph = ''

    #             else:
    #                 paragraph += row

    #     if len(all_text) != 0:
    #         text_chunks[key] = all_text

    #     return text_chunks        
    

    # def __get_text_chunks_from_list(self, list: list) -> dict:
    #     key = self.__initial_key
    #     text_chunks = {}
    #     all_text = []
    #     paragraph = ''
    #     min_row_len = 90

    #     for block in list:
    #         row = block.strip()
    #         doc = self.__cl_model(row).cats # Verify if is a title

    #         if doc['Clausula'] >= 0.95:
    #             new_key = row.lower()
    #             new_key = unidecode(new_key) # Removes accent from string
    #             new_key = new_key.replace(' - ', ' ')
    #             new_key = new_key.replace(' ', '_')

    #             if len(all_text) != 0:
    #                 if paragraph != '':
    #                     all_text.append(paragraph)
    #                 text_chunks[key] = all_text

    #             key = new_key
    #             all_text = []
    #             paragraph = ''

    #         elif len(row) < min_row_len:
    #             paragraph += row
    #             if paragraph != '' and len(paragraph) > 5:
    #                 all_text.append(paragraph.replace('- ', '  '))
    #             paragraph = ''

    #         else:
    #             all_text += row

    #     if len(all_text) != 0:
    #         text_chunks[key] = all_text
            
    #     return text_chunks
