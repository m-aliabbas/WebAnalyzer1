import re
import os
import uuid
from bs4 import BeautifulSoup
import markdown
def format_card(doc):
    return {
        "id": str(doc["_id"]),  # Convert ObjectId to string
        "url": doc["url"],
        "number_of_pages": doc["number_of_pages"],
        "option": doc["option"],
        "status": doc["status"],
        "tags": doc["tags"],
        "timestamp": doc["timestamp"],
        "halt_status": doc["halt_status"],
        'download_link': doc.get('download_link','')
    }


def format_keys(doc):
    return {
        'id' : str(doc["_id"]),
        'OPENAI_API_KEY': doc.get("OPENAI_API_KEY",""),
        'FIRECRAWL_API_KEY': doc.get("FIRECRAWL_API_KEY",""),
        'PASSWORD': doc.get("PASSWORD","")
    }
def format_child_card(doc):
    '''
    '''
    return {
        "id": str(doc["_id"]),  # Convert ObjectId to string
        "parent_url": doc.get("parent_url", ''),
        "url": doc.get("url", ''),
        "title": doc.get("title", ''),
        "status": doc.get("status", ''),
        "timestamp": doc.get("timestamp", ''),
        "main_data": doc.get("main_data", {}),
        'download_link': doc.get('download_link','')
    }



def cleanify(input_string):
    """
    Remove newline characters, plus signs, minus signs, brackets,
    consecutive dots, and consecutive spaces from the input string.
    
    Args:
    input_string (str): The string to be cleaned.
     
    Returns:
    str: The cleaned string.
    """
    # Define the pattern to remove specific characters
    pattern = r'[\n+\-\[\]\(\)^]'
    cleaned_string = re.sub(pattern, '', input_string)
    
    # Remove consecutive dots
    cleaned_string = re.sub(r'\.{2,}', '.', cleaned_string)
    
    # Remove consecutive spaces
    cleaned_string = re.sub(r'\s{2,}', ' ', cleaned_string)
    
    return cleaned_string.strip()


def get_major_part(uri):
    # Remove 'http://', 'https://', or 'www.'
    uri = re.sub(r'(https?://|www\.)', '', uri)
    
    # For URLs, match the domain name part before the first dot (e.g., example.com -> example)
    url_match = re.match(r'([^\.]+)', uri)
    if url_match:
        return url_match.group(1)
    
    # For file names, extract everything before the first dot
    file_match = re.match(r'([^\.]+)', uri)
    if file_match:
        return file_match.group(1)
    
    return uri  #
def generate_random_file_name_uuid(file_name=None,folder_path='./temp_docs/'):

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


    if file_name is None:
        file_name = f"{uuid.uuid4()}.pdf"
    else:
        ran_str = str(uuid.uuid4())[:2]
        file_name = file_name+'_'+f"{ran_str}"
        if not file_name.endswith('.pdf'):
            file_name += '.pdf'
    file_name = os.path.join(folder_path, file_name)
    return file_name


def make_file_name(file_name=None,folder_path='./temp_docs/'):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_name = file_name + '.pdf'
    file_name = os.path.join(folder_path, file_name)
    return file_name
    
    

def get_text_str(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    out_text = ""
    elements = soup.find_all(['p', 'div', 'span','h1','h2','h3'])  # You can add more tags to this list
    for elem in elements:
        
        out_text += ('-'*50)
        out_text += '\n'
        out_text += elem.get_text()
        out_text += '\n'
    return out_text

import re

def process_text(text):
    # Split the text into lines
    lines = text.splitlines()
    
    # Initialize variables
    processed_lines = []
    ignore_content = False
    merge_line = ""
    
    cookies_meta_found = False
    cookies_meta_line_position = 0

    for i, line in enumerate(lines):
        # Remove leading and trailing whitespace from the line
        line = line.strip()

        # Skip empty lines
        if not line:
            continue
        
        # Rule 1: Ignore lines starting with '#'
        if line.startswith('#'):
            continue
        
        # Rule 2: Ignore lines with '|'
        if '|' in line:
            continue
        
        # Rule 3: Ignore lines with 'copyright', 'Copy Right', or a copyright symbol
        if re.search(r'copyright|Copy Right|©', line, re.IGNORECASE):
            continue
        
        # Rule 4: Handle cookies/meta-data-related content
        if re.search(r'cookies?|meta[-_ ]data', line, re.IGNORECASE):
            if i < 25:
                # If found within the first 25 lines, ignore the line
                continue
            else:
                # If found after the 25th line, set the flag to ignore subsequent lines
                cookies_meta_found = True
                cookies_meta_line_position = i
                continue

        # If ignore_content flag is set and we are in the next line after the found keyword
        if cookies_meta_found and i > cookies_meta_line_position:
            continue
        
        # Rule 5: Treat content between '--------' lines as a single line
        if line.startswith('--------'):
            if merge_line:
                processed_lines.append(merge_line.strip())
                merge_line = ""
            continue
        else:
            merge_line += " " + line if merge_line else line
        
        # Additional Rule: Ignore lines containing "Open Menu", "Close Menu", "Privacy", or "Follow Us"
        if re.search(r'Open Menu|Close Menu|Privacy|Follow Us', line, re.IGNORECASE):
            continue
    
    # Add the last accumulated line if any
    if merge_line:
        processed_lines.append(merge_line.strip())

    # Apply further post-processing rules
    final_lines = []
    for line in processed_lines:
        # Rule 6: Remove lines that contain only numbers
        if line.isdigit():
            continue
        
        # Rule 7: Remove lines that have only two words or fewer
        if len(line.split()) <= 2:
            continue
        
        # Rule 8: Remove lines with all capital letters and less than 4 words
        if line.isupper() and len(line.split()) < 4:
            continue
        
        final_lines.append(line)

    # Join the final lines into a single string
    processed_text = '\n'.join(final_lines)
    processed_text = processed_text.replace("\\", "")
    return processed_text



def clean_text(input_string):
    # Define the keywords to remove lines containing them
    keywords = ['Open Menu', 'Close Menu', 'Privacy', 'Term and Condition', 'T&C', 
                'Facebook', 'http', 'https', 'Insta', 'Twitter', 'LinkedIn', 'Snapchat', 'TikTok','field']

    # Split the input string into lines
    lines = input_string.splitlines()

    # Initialize a set to track unique lines
    unique_lines = set()

    # Define a regex pattern to detect lines with only numeric characters or less than 4 alphabetic characters
    alpha_numeric_pattern = re.compile(r'^[\d\s]*[a-zA-Z]{0,3}[\d\s]*$')

    # Define a regex pattern to identify numbers followed by words with no space, excluding ordinal numbers
    number_word_pattern = re.compile(r'(\d)(?!st|nd|rd|th)([a-zA-Z])')

    # Process each line
    cleaned_lines = []
    for line in lines:
        # Insert newline if a number is followed by a word without space, except for ordinal numbers
        line = number_word_pattern.sub(r'\1\n\2', line)

        # Check if line contains any of the keywords or matches the numeric pattern
        if (any(keyword.lower() in line.lower() for keyword in keywords) or
                alpha_numeric_pattern.match(line)):
            continue
        
        # Check for duplicates
        if line not in unique_lines:
            unique_lines.add(line)
            cleaned_lines.append(line)
    
    # Join the cleaned lines back into a string
    return '\n'.join(cleaned_lines)


def get_markdown(markdown_text):
    html = markdown.markdown(markdown_text)
    return html
def preproces_content_new(html_page_content):
    html = get_markdown(html_page_content)
    text_o = get_text_str(html)
    preprocessed_text = process_text(text_o)
    cleaned_text = clean_text(preprocessed_text)
    return cleaned_text

