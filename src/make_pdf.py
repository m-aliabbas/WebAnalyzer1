from src.db_driver import *
from utils.utils import *
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, ListFlowable, ListItem, Image
from reportlab.graphics.shapes import Drawing, Rect
from svglib.svglib import svg2rlg
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import datetime
import uuid
import os
from PIL import Image as PILImage
from pypdf import PdfWriter



# Register custom fonts (use TTF versions if possible)
pdfmetrics.registerFont(TTFont('Aptos', './src/fonts/Fonts/Aptos.ttf'))
pdfmetrics.registerFont(TTFont('AptosDisplay', './src/fonts/Fonts/Aptos-Display.ttf'))
pdfmetrics.registerFont(TTFont('AptosDisplay-Bold', './src/fonts/Fonts/Aptos-Display-Bold.ttf'))


def create_square():
    drawing = Drawing(20, 20)
    square = Rect(0, 0, 20, 20, strokeColor=colors.black, fillColor=colors.white)
    drawing.add(square)
    return drawing

def centered_square():
    square = create_square()
    centered_square_table = Table([[Spacer(1, 0.25*inch)], [square], [Spacer(1, 0.25*inch)]])
    centered_square_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return centered_square_table

# Function to process the text and apply color to bold text
def process_text_with_bold(text):
    parts = text.split('<b>')
    processed_parts = [parts[0]]
    for part in parts[1:]:
        subparts = part.split('</b>')
        processed_parts.append(f'<font color="#f5c949"><b>{subparts[0]}</b></font>{subparts[1]}')
    return ''.join(processed_parts)

def prepare_page_data(id):
    '''
    returns:
    data: list of dictionaries
    caution_words: list
    title: string
    url: string
    '''
    try:
        doc = get_child_by_id(id)
        doc = format_child_card(doc)
        title = doc['title']
        url = doc['url']
        
        table_data = doc['main_data']['table_data']
        caution_words = doc['main_data']['caution_sentences']
        if len(caution_words) <= 1:
            caution_words = []
        df = pd.DataFrame(table_data)
        df['changes'] = df['highlighted'].apply(cleanify)
        df['changes'] = df['changes'].apply(cleanify)
        filtered_df = df[df['originalContent'].str.split().str.len() > 2]
        filtered_df = filtered_df[~filtered_df['originalContent'].str.contains(r'(\.\.+|,,+)$')]
        filtered_df = filtered_df[~filtered_df['originalContent'].str.contains(r'^\s+$')]
        data = filtered_df.to_dict('records')
        print('=='*20)
        print(data[0].keys())
        print('=='*20)
        print(caution_words)
        return data , caution_words, title, url
    except Exception as e:
        print(e)
        return [], [], '', ''


def create_pdf(file_name,data,caution_sentences,title,url):
    try:
        doc = SimpleDocTemplate(file_name, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        styleN = ParagraphStyle(name='Normal', fontName='Aptos', fontSize=12)
        styleLN = ParagraphStyle(name='AptosDisplay', fontName='Aptos', fontSize=26)
        styleAptosDisplay = ParagraphStyle(name='AptosDisplay', fontName='AptosDisplay', fontSize=14)
        styleAptosDisplayBold = ParagraphStyle(name='AptosDisplay-Bold', fontName='AptosDisplay-Bold', fontSize=14)
        styleTitle = ParagraphStyle(name='Title', fontName='AptosDisplay-Bold', fontSize=24, spaceAfter=20)
        styleFooter = ParagraphStyle(name='Footer', fontName='Aptos', fontSize=12)

        elements = []

        # Add the logo image at the top left
        logo_path = "./src/imgs/image.png"  # Replace with the actual path to your logo image
        # logo = Image(logo_path)
        
        # logo.drawWidth = 1 * inch
        # logo.drawHeight = logo.drawWidth * 0.6  # Adjust height proportionally to maintain aspect ratio
        # logo.hAlign = 'LEFT'
        # elements.append(logo)
        # Load the image using PIL to get its original dimensions
        # image = PILImage.open(logo_path)
        # original_width, original_height = image.size

        # # Set the desired width
        # desired_width = 1.5 * inch

        # # Calculate the proportional height based on the original aspect ratio
        # aspect_ratio = original_height / float(original_width)
        # desired_height = desired_width * aspect_ratio

        # # Create the image in the report
        # logo = Image(logo_path)
        # logo.drawWidth = desired_width
        # logo.drawHeight = desired_height
        # logo.hAlign = 'LEFT'

        # # Add to elements list
        # elements.append(logo)
        image = PILImage.open(logo_path)
        original_width, original_height = image.size

        # Set a maximum width and height based on the layout
        max_width = 3 * inch  # Maximum width you want to allow
        max_height = 1.5 * inch  # Maximum height you want to allow

        # Calculate the scaling factor to maintain aspect ratio
        width_ratio = max_width / float(original_width)
        height_ratio = max_height / float(original_height)
        scaling_factor = min(width_ratio, height_ratio)

        # Calculate the final dimensions based on the scaling factor
        final_width = original_width * scaling_factor
        final_height = original_height * scaling_factor

        # Create the image in the report
        logo = Image(logo_path)
        logo.drawWidth = final_width
        logo.drawHeight = final_height

        # Align image as needed, center or left
        logo.hAlign = 'LEFT'  # You can change this to 'LEFT' or 'RIGHT'

        # Add the logo to the elements list
        elements.append(logo)

        # Add the line with website link on the left and current date time on the right
        current_datetime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M GMT")
        footer_data = [
            [Paragraph(url, styleFooter), Spacer(1, 0.1*inch), Paragraph(current_datetime, styleFooter)]
        ]
        footer_table = Table(footer_data, colWidths=[2.5*inch, 3*inch, 2.5*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        elements.append(footer_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Add the page title below the logo
        elements.append(Spacer(1, 0.2 * inch))  # Adjusted upward
        title = Paragraph("Language Audit", styleLN)
        elements.append(title)
        elements.append(Spacer(1, 0.5 * inch))  # Added gap
        svg_path = "./src/imgs/discover-icon.svg"  # Replace with the actual path to your SVG image
        svg_drawing = svg2rlg(svg_path)
        svg_drawing.scale(1.0, 1.0)  # Adjust scaling as needed
        if len(caution_sentences) > 0:
            # Load the SVG image
            

            # Caution Sentences Header Data
            caution_header_data = [
                [svg_drawing, Paragraph("Caution Sentences", styleAptosDisplayBold)]
            ]

            # Caution Sentences Body Data
            list_items = [ListItem(Paragraph(process_text_with_bold(sentence), styleN)) for sentence in caution_sentences]
            caution_body_data = [
                ['', ListFlowable(list_items, bulletType='bullet', start='circle', leftIndent=0.25*inch)]
            ]

            # Combine Caution Sentences Header and Body Data
            caution_data = caution_header_data + caution_body_data

            # Create caution table
            caution_table = Table(caution_data, colWidths=[1*inch, 6*inch])
            caution_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (1, 1), (-1, 1), 14),
                ('BOTTOMPADDING', (1, 1), (-1, 1), 12),
                ('BACKGROUND', (1, 2), (-1, -1), colors.white),  # Set the background to white
                ('GRID', (0, 0), (-1, -1), 0, colors.white),     # Remove the grid
            ]))

            elements.append(caution_table)
            elements.append(Spacer(1, 0.5*inch))

        if len(data) > 0:
            # Header Data
            header_data = [
                [svg_drawing, Paragraph("Language Suggestion", styleAptosDisplayBold), ""]
            ]

            # Table Data
            table_data = [['', Paragraph('Original Content', styleAptosDisplayBold), Paragraph('Changes', styleAptosDisplayBold)]]

            for item in data:
                row = [
                    centered_square(),
                    Paragraph(item['originalContent'], styleN),
                    Paragraph(process_text_with_bold(item['changes']), styleN)
                ]
                table_data.append(row)

            # Combine Header and Table Data
            combined_data = header_data + table_data

            # Create table
            table = Table(combined_data, colWidths=[1*inch, 3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (1, 1), (-1, 1), 14),
                ('BOTTOMPADDING', (1, 1), (-1, 1), 12),
                ('BACKGROUND', (1, 2), (-1, -1), colors.white),  # Set the background to white
                ('GRID', (0, 0), (-1, -1), 0, colors.white),     # Remove the grid
            ]))

            elements.append(table)
        doc.build(elements)

        # print("PDF created successfully!")
        return {"status":True,"msg": "PDF created successfully!", "file_name": file_name}

    except Exception as e:
        # print(f"An error occurred: {e}")
        return {"status": False,"msg": f"An error occurred: {e}","file_name": None}


def single_page_pdf_runner(id):
    print('='*20)
    print('Processing PDF for id:', id)
    
    file_name = generate_random_file_name_uuid(id)
    data , caution_words, title, url = prepare_page_data(id)
    resp = create_pdf(file_name,data, caution_words, title, url) 
    # print('Response',resp)
    # print('='*20)
    return resp
    

    


def multi_page_pdf_runner(id):
    try:

        download_link = get_parent_download_link(id)
        if download_link:
            return {"status": True, "file_name": download_link,"message": "PDF reterived successfully!"}
        
        merger = PdfWriter()
        

        url = get_parent_url_by_id(id)

        file_name_gen = generate_random_file_name_uuid(id)

        if url:
            file_name_gen = get_major_part(url)
            file_name_gen = make_file_name(file_name_gen)
        
        
        docs = get_child_docs_by_id(id)
        
        docs = [format_child_card(doc) for doc in docs]
        pdf_name_list = []
        for doc in docs:
            if doc['status'] != 'done':
                continue
            
            resp = single_page_pdf_runner(doc['id'])
            print('resp',resp)
            if resp['status']:
                print('appending ',resp['file_name'])
                pdf_name_list.append(resp['file_name'])
        
        # Merge the individual PDFs into a single PDF
        
        print('pdf_name_list',pdf_name_list)
        for pdf_name in pdf_name_list:
            merger.append(pdf_name)
        
        final_pdf_name = file_name_gen
        merger.write(final_pdf_name)
        merger.close()
        res = set_download_link(id,file_path=final_pdf_name)
        return {"status": True, "file_name": final_pdf_name,"message": "PDF created successfully!"}
    except Exception as e:
        return {"status": False, "file_name": None, "message": str(e)}
if __name__ == '__main__':

    # resp = single_page_pdf_runner('66bad725df6dfacfb2cf4294')
    # print(resp)

    resp = multi_page_pdf_runner('66bad711be364485a47b7301')
    print(resp)
