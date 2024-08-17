import docx
import pypdf
import os

def handle_files(file_path, option='crawl', max_pages=4, input_type="URL", caution_words=None):
    content = ''
    # if word file
    if file_path.endswith('.docx') or file_path.endswith('.doc'):
        document = docx.Document(file_path)
        content = "\n".join(paragraph.text for paragraph in document.paragraphs)
        # Process the content as needed
        print("Processed .docx or .doc file:", content)
        

    # if pdf file
    elif file_path.endswith('.pdf'):
        content = []
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in range(min(max_pages, len(reader.pages))):
                content.append(reader.pages[page].extract_text())
        content = "\n".join(content)
        # Process the content as needed
        print("Processed .pdf file:", content)


    # if text file
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            content = file.read()
        # Process the content as needed
        print("Processed .txt file:", content)
    
    # Handle other file types or errors
    else:
        print(f"Unsupported file type: {os.path.splitext(file_path)[1]}")
    return content


if __name__ == '__main__':
    file_path = 'US_English_Sentences.docx'
    handle_files(file_path)
