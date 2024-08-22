# application.py
# Created by: Ali
# Created on: 04/08/2024
# For : Digimax | Dental.
# Description:
# This is a LLM Based Application for Digimax. That suggest grammer errors
# from the website. It start with crawling a website. Then LLM injestion and 
# suggest grammer errors. 


# ==============================================================================
# Importing Library
import datetime
from langchain_community.document_loaders import FireCrawlLoader
from langchain_community.document_loaders import Docx2txtLoader
import threading
from langchain_core.pydantic_v1 import BaseModel, Field, validator, root_validator
from langchain_community.document_loaders import FireCrawlLoader
from langchain_groq import ChatGroq
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
import os
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from typing import List
import re
from langchain_text_splitters import CharacterTextSplitter

from dotenv import load_dotenv
# from src.models import ResponseModel, SentenceParser
from langchain.chains import LLMChain
import concurrent.futures
from difflib import ndiff
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import urlparse
from src.db_driver import *
from src.file_handler import handle_files
from utils.utils import *
#===============================================================================
# Load environment variables
load_dotenv()

# ==============================================================================
# making an LLM object
llm=ChatOpenAI(temperature=0.0, model_name="gpt-4o") 



# ==============================================================================
from typing import List, Optional
from pydantic import BaseModel, Field, root_validator, ValidationError

class SentenceParser(BaseModel):
    originalContent: str = Field(..., description="Original Sentence with no correction")
    correctedSentence: str = Field(..., description="Corrected Sentence in English UK. Enclosed corrections in <b></b>.")

    @root_validator(pre=True)
    def fill_missing_fields(cls, values):
        values['correctedSentence'] = values.get('correctedSentence', '')
        return values

# Define ResponseModel to include sentences
class ResponseModel(BaseModel):
    sentences: List[SentenceParser]
    

def get_html(url,mode='scrape',ignore_pages=[],max_pages=0):
    """
    Retrieves HTML content from a given URL.
    Args:
        url (str): The URL from which to retrieve the HTML content.
        mode (str, optional): The mode in which to retrieve the HTML content. 
            Defaults to 'scrape'. Options are 'scrape' or 'crawl'.
        ignore_pages (List[str], optional): A list of pages to ignore when 
            retrieving the HTML content. Defaults to an empty list.
        max_pages (int, optional): The maximum number of pages to retrieve 
            when in 'crawl' mode. Defaults to 4.
    Returns:
        List[Document]: A list of Document objects representing the HTML content 
            retrieved from the URL.

    Raises:
        None

    """
    if mode == 'scrape':
        loader = FireCrawlLoader(
        api_key=os.environ.get('FIRECRAWL_API_KEY'), url=url, mode=mode
            )
    else:
        crawl_params = {
                'crawlerOptions': {
                    'excludes': [
                        'blog/*', 'login/*', 'account/*', 'user/*', 'profile/*',
                        'admin/*', 'dashboard/*', 'search/*', 'filter/*',
                        'checkout/*', 'payment/*', 'cart/*', 'css/*', 'js/*',
                        'images/*', 'assets/*', 'temp/*', 'under-construction/*',
                        'api/*', '404', '500', 'downloads/*', 'files/*', 'pdfs/*',
                        'archive/*', 'old/*', 'version/*', 'forum/*', 'comments/*',
                        'reviews/*', 'external/*', 'outbound/*', 'product/*', 'shop/*',
                        'category/*', 'promo/*', 'deals/*', 'offers/*', 'help/*',
                        'support/*', 'news/*', 'press/*', 'events/*',
                        'calendar/*', 'subscribe/*', 'signup/*', 'test/*', 'staging/*',
                        'wp-admin/*', 'backend/*', 'admin-panel/*', 'management/*'
                    ],
                    'includes': [], # leave empty for all pages
                }
            }

        loader = FireCrawlLoader(
        api_key=os.environ.get('FIRECRAWL_API_KEY'), url=url, mode=mode,
        params=crawl_params
            ) 
        
    # crawl or scrape the website
    docs = loader.load()
    
    return docs

def remove_all_repetitions(text):

    """
    Removes all repetitions of words in a given text.

    Args:
        text (str): The input text from which repetitions will be removed.

    Returns:
        str: The text with all repetitions removed, where each word appears only once.
    """

    words = text.split()
    seen = set()
    result = []

    for word in words:
        if word not in seen:
            seen.add(word)
            result.append(word)

    return ' '.join(result)

def extract_plain_text_from_markdown(markdown_content):
    """
    Extracts plain text from Markdown content by removing image tags, links, HTML tags, and symbols.

    Args:
        markdown_content (str): The Markdown content to extract plain text from.

    Returns:
        str: The plain text extracted from the Markdown content.

    Removes image tags (Markdown and HTML) by replacing the image tag with an empty string.
    Removes links (Markdown and plain URLs) by replacing the link with an empty string.
    Removes any remaining inline links by replacing the inline link with an empty string.
    Removes HTML tags (including SVG) by replacing the HTML tag with an empty string.
    Removes all symbols except ., "", '', ?, and , by replacing them with an empty string.
    Removes any extra whitespace and newlines by replacing multiple whitespace characters with a single space and stripping leading and trailing whitespace.
    """
    # Remove image tags (Markdown and HTML)
    print(markdown_content)
    markdown_content = re.sub(r'!\[.*?\]\(.*?\)', '', markdown_content)
    markdown_content = re.sub(r'<img.*?>', '', markdown_content)
    
    # Remove links (Markdown and plain URLs)
    markdown_content = re.sub(r'\[.*?\]\(.*?\)', '', markdown_content)
    markdown_content = re.sub(r'\(https?://.*?\)', '', markdown_content)
    markdown_content = re.sub(r'https?://\S+|www\.\S+', '', markdown_content)
    
    # Remove any remaining inline links
    markdown_content = re.sub(r'\[.*?\]', '', markdown_content)
    
    # Remove HTML tags (including SVG)
    markdown_content = re.sub(r'<.*?>', '', markdown_content)
    
    # Remove all symbols except ., "", '', ?, and ,
    markdown_content = re.sub(r"[^a-zA-Z0-9\s.,\"'?']", '', markdown_content)
    
    # Remove any extra whitespace and newlines
    markdown_content = re.sub(r'\s+', ' ', markdown_content).strip()
    
    return markdown_content


def get_splited_text(text):
    """
    Splits the given text into multiple documents using the RecursiveCharacterTextSplitter.

    Args:
        text (str): The input text to be split.

    Returns:
        List[Document]: A list of Document objects representing the split text.

    This function takes a text as input and splits it into multiple documents using the
    RecursiveCharacterTextSplitter. The chunk size is set to 8000, with a chunk overlap of
    100. The length function used is the built-in len function. The is_separator_regex
    parameter is set to False. The input text is passed as a list to the create_documents
    method of the text_splitter object. The resulting documents are returned as a list.

    Example usage:
        text = "This is a sample text to be split."
        documents = get_splited_text(text)
        print(documents)

    Output:
        [Document(page_content='This is a sample text to be split.', metadata={}), ...]
    """
    text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=10000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
    )
    texts = text_splitter.create_documents([text])
    return texts


def get_corrected_content(page_content):

    """
    Retrieves corrected content from a given page content.

    Args:
        page_content (str): The content of the page to be corrected.

    Returns:
        Union[str, dict]: The corrected content as a JSON object with a single key "sentences"
        which contains a list of objects. Each object should have keys "originalContent" and
        "correctedSentence". If the result is not a dictionary, it is returned as is.

    Raises:
        None

    """

    # llm = ChatGroq(
    #         model="llama-3.1-70b-versatile",
    #         temperature=0,
    #         max_tokens=None,
    #         timeout=None,
    #         max_retries=3,
    #         # other params...
    #     )

    llm = ChatOpenAI(temperature=0.0, model_name="gpt-4o")
    

    parser = PydanticOutputParser(pydantic_object=ResponseModel)

    prompt = PromptTemplate(
        template="""
        You are a smart assistant.
        You will be given a page-long document.
        You will return sentences or group of words. Each line contain a sentence or group of words.
        If there is any HTML content or non-textual content, you will remove it.
        First, you will clean the text by removing the images and links, and extract plain text.
        You will not expand any point or enhance anything. 
        If sentence contain the social media or web development related things like cookies etc you will remove it.
        Just return what is in the original text.
        Provide the English UK version of sentences, performing both spelling and grammar checks.
        Return the result as a JSON object with a single key "sentences" which contains a list of objects.
        Each object should have keys "originalContent" and "correctedSentence".

        \n\n{query}\n
        """,
        input_variables=["query"]
    )

    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)

    result = chain({"query": page_content})

    if isinstance(result,dict):
        result = result['text']
        return result
    return result

def reterive_split_text(url,mode,ignore_pages=[],max_pages=4,enable_db=False,id=''):
    """
    Retrieves HTML content from a given URL and splits it into multiple documents.

    Args:
        url (str): The URL from which to retrieve the HTML content.
        mode (str): The mode of retrieval, either 'crawl' or 'scrape'.
        ignore_pages (List[int]): A list of page numbers to ignore.
        max_pages (int): The maximum number of pages to retrieve.

    Returns:
        List[Document]: A list of Document objects representing the split text.

    """
    documents_list = []
    html_content = get_html(url,mode=mode,ignore_pages=ignore_pages,max_pages=max_pages)
    base_page_url = get_base_url(url)
    if enable_db:
        pass
    for document in html_content:
        document_dict = {}
        chunk_list = []
        plain_text = preproces_content_new(document.page_content)
        # plain_text = extract_plain_text_from_markdown(document.page_content)
        # plain_text = remove_all_repetitions(plain_text)
        metadata = document.dict().get('metadata',{})
        print('='*20)
        print(metadata)
        print('='*20)

        url = metadata.get('url','')
        if url == '':
            url = metadata.get('ogUrl','')

        if url == '':
            url = metadata.get('sourceURL','')

        if url == '':
            url = 'No URL Found Particularly'

        title = metadata.get('title','')

        if title == '': 
            title = metadata.get('ogTitle','')

        if title == '':
            title = metadata.get('title','')

        if title == '':
            title = metadata.get('sourceTitle','')

        if title == '':
            title = 'No Title Found Particularly'


        document_dict = {'url':url,'title':title,'page_content':plain_text}
        chunks = get_splited_text(plain_text)
        for chunk in chunks:
            chunk_list.append(chunk.page_content)
        document_dict['chunks'] = chunk_list
        document_dict['status'] = 'init'
        document_dict['timestamp'] = datetime.now()
        document_dict['parent_url'] = base_page_url
        document_dict['parrent_id'] = id
        documents_list.append(document_dict)

    # print(documents_list)
    
    if enable_db:

        status_1 = add_processed_pages(documents_list)
        # print(status_1)

        status_2 = update_parent_doc_status_by_id(id, 'processing')
        
    return documents_list

def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url




def process_document(doc):
    """
    Corrects the grammar of text chunks in a single document using ThreadPoolExecutor.

    Args:
        doc (dict): A dictionary representing the document with 'url', 'title',
                    'page_content', and 'chunks'.

    Returns:
        dict: The updated document with corrected text chunks.
    """
    with concurrent.futures.ThreadPoolExecutor() as chunk_executor:
        chunks = doc['chunks']
        chunk_futures = {chunk_executor.submit(get_corrected_content, chunk): chunk for chunk in chunks}
        corrected_chunks = [future.result() for future in concurrent.futures.as_completed(chunk_futures)]
        doc['chunks_corrected'] = corrected_chunks
    return doc

def grammar_check_main_concurrent(doc_list=[]):
    """
    Corrects the grammar of text chunks in each document using ThreadPoolExecutor and yields each processed document.

    Args:
        doc_list (list): List of documents where each document is a dictionary
                         with 'url', 'title', 'page_content', and 'chunks'.

    Yields:
        dict: The updated document with corrected text chunks.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        doc_futures = {executor.submit(process_document, doc): doc for doc in doc_list}
        for future in concurrent.futures.as_completed(doc_futures):
            corrected_doc = future.result()
            yield corrected_doc
            # Process the document further as needed here (e.g., store in database, display)
            print(f"Processed document: {corrected_doc['title']}")


def highlight_changes(original, corrected):
    """
    Generates a highlighted version of the changes between the original and corrected strings.

    Args:
        original (str): The original string.
        corrected (str): The corrected string.

    Returns:
        str: The highlighted version of the changes.

    Example:
        >>> original = "Hello world!"
        >>> corrected = "Hello World!"
        >>> highlight_changes(original, corrected)
        '<b>H</b>ello <b>W</b>orld!'
    """
    diff = list(ndiff(original.split(), corrected.split()))
    result = []
    in_change = False

    for d in diff:
        if d.startswith('- '):
            continue
        elif d.startswith('+ '):
            if not in_change:
                result.append('<b>')
                in_change = True
            result.append(d[2:])
        elif d.startswith('  '):
            if in_change:
                result.append('</b>')
                in_change = False
            result.append(d[2:])
    
    if in_change:
        result.append('</b>')

    return ' '.join(result)


# Function to add <b></b> around caution words
def highlight_caution_words(sentence, caution_word_list):
    pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in caution_word_list) + r')\b', re.IGNORECASE)
    highlighted_sentence = pattern.sub(r'<b>\1</b>', sentence)
    if highlighted_sentence != sentence:
        return highlighted_sentence
    return None

def normalize_and_filter(df, column_name):
    # Create a temporary column in lowercase for normalization and matching
    df['temp_lower'] = df[column_name].str.lower()
    
    # Pattern to match social media names, specific extensions, and keywords like 'cookies'
    pattern = r'\b(company|facebook|twitter|instagram|linkedin|youtube|\.com|\.ad|\.gov|\.uk|\.php|\.asp|cookies|cookies|statistical|tracking|ads|script|event|policy|Cloudflare|cookie|cfduid|llc|party)\b'
    
    # Filter rows where the temporary lowercase column does not contain any of the specified patterns
    filtered_df = df[~df['temp_lower'].str.contains(pattern, flags=re.IGNORECASE, regex=True)]
    
    # Drop the temporary column
    filtered_df.drop('temp_lower', axis=1, inplace=True)
    
    return filtered_df

def get_corrected_highlights(temp_doc,caution_word_list=["Best", "Specialist", "Specialised", "Finest",
                                                          "Most experienced",
                                "Superior", "Principle", "Expert", "Amazing", "Speciality",
                                "leader", "leaders", "service", "implantologist"
            ]):
    temp_sent_list = []
    for doc in temp_doc:
        for sentence in doc.dict().get('sentences',[]):
            temp_ab = highlight_changes(sentence.get('originalContent',[]),sentence.get('correctedSentence',[]))
            orignal_content = sentence.get('originalContent','')
            cc_content = sentence.get('correctedSentence','')
            highlighted = temp_ab
            highlight_sentence = {}
            highlight_sentence['originalContent'] = orignal_content
            highlight_sentence['correctedSentence'] = cc_content
            highlight_sentence['highlighted'] = highlighted
            temp_sent_list.append(highlight_sentence)


    df = pd.DataFrame(temp_sent_list)
    print(df)
    filtered_df = df[df['highlighted'].str.contains('<b>')]
    filtered_df = normalize_and_filter(filtered_df,'highlighted')
    org_sentences = df['originalContent'].tolist()
    highlighted_sentences = [highlight_caution_words(sentence,caution_word_list=caution_word_list) for sentence in org_sentences if highlight_caution_words(sentence,caution_word_list)]
    flatten_doc_list = filtered_df.to_dict('records')

    ret_docs = {}
    ret_docs['table_data'] = flatten_doc_list
    ret_docs['caution_sentences'] = highlighted_sentences
    return ret_docs


def ai_runner(doc_list,caution_word_list=[],enable_db=False):
    doc_list_ccc = []
    for corrected_doc in grammar_check_main_concurrent(doc_list):
        print('Working on ' + corrected_doc.get('title',''))
        temp_doc = {}
        temp_doc = get_corrected_highlights(corrected_doc.get('chunks_corrected'))

        corrected_doc['main_data'] = temp_doc
        corrected_doc['status'] = 'done'
        del corrected_doc['chunks_corrected']
        doc_list_ccc.append(corrected_doc)


    if enable_db:
        status = update_processed_documents(doc_list_ccc)
        print('Database updated!',status)
    return doc_list_ccc


def main(url, mode='crawl', max_pages=4, input_type="URL", caution_words=None,id=''):

    
    if caution_words is None:
        caution_words = []

    final_results = []
    print('Id is ',id)
    # try:
    try:
        # 1. Retrieve and split text documents
        document_list = reterive_split_text(url=url, mode=mode, max_pages=max_pages, enable_db=True, id=id)
        
        # 2. Enter a loop to process remaining documents
        while True:
            # 3. Get the base URL for further processing
            base_url = get_base_url(url)
            
            # 4. Retrieve the initial documents with their parent information
            retrieved_documents = get_first_two_init_pages_with_parent(id)
            print(f'Length of Remaining docs: {len(retrieved_documents)}')
            
            # 5. Check if there are documents to process
            if len(retrieved_documents) == 0:
                print('All Documents Completed')
                
                # 6. Update the document status in the database
                status = update_parent_doc_status_by_id(id, 'done')
                print(f'Status Update: {status}')
                break
            
            # 7. Process the retrieved documents using AI if they exist
            if retrieved_documents:
                res = ai_runner(retrieved_documents, caution_word_list=caution_words, enable_db=True)
                final_results.extend(res)
            
        # 8. Return the final results after processing all documents
        return final_results
    
    
    except Exception as e:
        # 9. Handle any exceptions that occur
        print(f"An error occurred: {str(e)}")
        return None


def file_main(file_content,url,id,enable_db=True):
    documents_list = []
    plain_text = extract_plain_text_from_markdown(file_content)
    plain_text = remove_all_repetitions(plain_text)
    document_dict = {'url':url,'title':url,'page_content':plain_text}
    chunks = get_splited_text(plain_text)
    chunk_list = []
    for chunk in chunks:
        chunk_list.append(chunk.page_content)
    document_dict['chunks'] = chunk_list
    document_dict['status'] = 'init'
    document_dict['timestamp'] = datetime.now()
    document_dict['parent_url'] = url
    document_dict['parrent_id'] = id
    documents_list.append(document_dict)

    if enable_db:

        status_1 = add_processed_pages(documents_list)
        # print(status_1)

        status_2 = update_parent_doc_status_by_id(id, 'processing')
        
    return documents_list 
    


def process_file(file_path, option='crawl', max_pages=4, input_type="URL", caution_words=None,id=''):
    url = os.path.basename(file_path)
    file_content = handle_files(file_path, option=option, max_pages=max_pages, input_type=input_type, caution_words=caution_words)
    document_list = file_main(file_content,url,id)
    final_results = []
    while True:
        # 3. Get the base URL for further processing
        
        # 4. Retrieve the initial documents with their parent information
        retrieved_documents = get_first_two_init_pages_with_parent(id)
        print(f'Length of Remaining docs: {len(retrieved_documents)}')
        
        # 5. Check if there are documents to process
        if len(retrieved_documents) == 0:
            print('All Documents Completed')
            
            # 6. Update the document status in the database
            status = update_parent_doc_status_by_id(id, 'done')
            print(f'Status Update: {status}')
            break
            
        # 7. Process the retrieved documents using AI if they exist
        if retrieved_documents:
            res = ai_runner(retrieved_documents, caution_word_list=caution_words, enable_db=True)
            final_results.extend(res)
        
    # 8. Return the final results after processing all documents
    return final_results 


if __name__ == "__main__":
    # url = "https://www.smilecliniq.com"

     
    # main(url,mode='crawl',max_pages=4,input_type="URL",caution_words=["Best", "Specialist", "Specialised", "Finest"],id=id)
    file_name = 'US_English_Sentences.docx'
    id=add_parrent_doc(file_name, number_of_pages=4, tags=["Best", "Specialist", "Specialised", "Finest"], options='crawl',status='init')
    print(id)
    process_file(file_name, caution_words=["Best", "Specialist", "Specialised", "Finest"],id=id)