import re
import os
import uuid
def format_card(doc):
    return {
        "id": str(doc["_id"]),  # Convert ObjectId to string
        "url": doc["url"],
        "number_of_pages": doc["number_of_pages"],
        "option": doc["option"],
        "status": doc["status"],
        "tags": doc["tags"],
        "timestamp": doc["timestamp"],
        "halt_status": doc["halt_status"]
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