from fastapi import FastAPI, BackgroundTasks, Query,HTTPException,Body
from fastapi import File, UploadFile, Form
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.application import main,process_file
from src.make_pdf import single_page_pdf_runner, multi_page_pdf_runner
import time
from pydantic import BaseModel, HttpUrl
from typing import List,Dict,Optional,Union
from bson import ObjectId
from datetime import datetime
from utils.utils import *
from src.db_driver import (
    add_parrent_doc, 
    update_parent_doc_status_by_id, 
    get_parent_doc_status_by_id, 
    get_all_not_done_parent_docs,
    get_non_halted_non_completed_docs,
    halt_task,
    unhalt_task,
    get_all_parent_docs,
    delete_parent_doc_and_associated_pages,
    get_child_docs_by_id,
    get_parent_url_from_id,
    update_document,
    get_parent_by_id,
    get_keys_from_db,
    add_keys_to_db,
    get_child_doc_by_id
)
import os
import time
import threading
import certifi

ca = certifi.where()

app = FastAPI()

# Set up CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins, adjust this to your needs
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
#     allow_headers=["*"],  # Allow all headers
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your client URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # Expose Content-Disposition header
)

class UrlItem(BaseModel):
    url: str

class PassKeyItem(BaseModel):
    passkey: str
    

class KeyItem(BaseModel):
    open_ai_key: str
    firecrawl_key: str
    password: str

class SearchItem(BaseModel):
    url: str
    number_of_pages: int = 0
    option: str
    tags: List[str]

class UrlRequest(BaseModel):
    url: str


class IdRequest(BaseModel):
    ids: str

# class TableData(BaseModel):
#     originalContent: str
#     correctedSentence: str
#     highlighted: str


# class MainData(BaseModel):
#     table_data: Optional[List[TableData]] = None
#     caution_sentences: Optional[List[str]] = None


# class Document(BaseModel):
#     id: str
#     url: str
#     title: str
#     page_content: str
#     chunks: List[str]
#     status: str
#     timestamp: Union[datetime, str]
#     parent_url: Optional[HttpUrl] = None
#     parent_id: Optional[str] = None
#     main_data: Optional[MainData] = None



@app.get("/get-parent-docs/", response_model=List[Dict])
async def get_parent_docs():
    docs = get_all_parent_docs()  # Make sure to await the async function
    docs = [format_card(doc) for doc in docs]
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")
    return docs

def long_task(url: str, number_of_pages: int, option: str, tags: List[str],id: str):

    file_format = ['pdf','docx','doc','txt']
    is_file = False
    for i in file_format:
        if i in url:
            is_file = True
            break

    if is_file:
        res  = process_file(url, option=option, max_pages=number_of_pages, input_type="URL", caution_words=tags,id=id)
    else:
        res = main(url,mode=option,max_pages=number_of_pages,input_type="URL",caution_words=tags,id=id)
    # print(res)
    # print(f"Processing {url}...")
    # print(f"Number of Pages: {number_of_pages}")
    # print(f"Option: {option}")
    # print(f"Tags: {', '.join(tags)}")
    # # Simulate a long task
    # time.sleep(0.01)
    print(f"Completed processing {url}")





def process_pending_tasks():
    while True:
        pending_tasks = get_all_not_done_parent_docs()
        for task in pending_tasks:
            long_task(task['url'], task['number_of_pages'], task['option'], task['tags'],str(task['_id']))
        time.sleep(60)  # Check for pending tasks every 60 seconds

# Background thread to process pending tasks continuously
threading.Thread(target=process_pending_tasks, daemon=True).start()


UPLOAD_DIR = "uploads"

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
@app.post("/correct/")
def correct_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), tags: str = Form(...)):
    try:
        # Decode the tags from JSON string to Python list
        tags = json.loads(tags)
        
        # Save the uploaded file to the specified directory
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        
        url = os.path.basename(file_location)

        # Call the function synchronously
        new_id = add_parrent_doc(str(url), 4, tags, 'file', status='init')

        background_tasks.add_task(
            long_task,
            url,
            4,
            'file',
            tags,
            new_id
        )
        # Add the task to the queue
        
        # Return the file path and success message
        return {"message": f"Correction task completed successfully. File saved at: {file_location}", "new_id": new_id}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@app.post("/search/")
def submit_url(item: SearchItem, background_tasks: BackgroundTasks):
    new_id = add_parrent_doc(str(item.url), item.number_of_pages, item.tags, item.option,status='init')
    pending_tasks = get_non_halted_non_completed_docs()
    if pending_tasks:
        for task in pending_tasks:
            background_tasks.add_task(
                long_task,
                task['url'],
                task['number_of_pages'],
                task['option'],
                task['tags'],
                task['_id']
            )
    else:
        background_tasks.add_task(
            long_task,
            item.url,
            item.number_of_pages,
            item.option,
            item.tags,
            new_id
        )
    return {"url": item.url, "message": "Task has been started in the background"}

@app.get("/status/")
def get_status(request: IdRequest ):
    status = get_parent_doc_status_by_id(str(request.ids))
    if status:
        return {"Ids": request.ids, "status": status}
    else:
        return {"Ids": request.ids, "status": "not found"}
    

@app.post("/ana/")
def search(item: SearchItem):
    print(f'Searching with URL: {item.url}')
    print(f'Number of Pages: {item.number_of_pages}')
    print(f'Option: {item.option}')
    print(f'Tags: {", ".join(item.tags)}')
    
    return {
        "url": item.url,
        "number_of_pages": item.number_of_pages,
        "option": item.option,
        "tags": item.tags,
        "message": "Search task initiated"
    }


@app.post("/halt/")
async def halt(request: IdRequest):
    # Print the received URL
    msg = halt_task(str(request.ids))
    return {"message": msg}

@app.post("/unhalt/")
async def unhalt(request: IdRequest):
    # Print the received URL
    msg = unhalt_task(str(request.ids))
    return {"message": msg}

@app.post('/delete_doc/')
async def delte_doc(request: IdRequest ):
    # Print the received URL
    msg = delete_parent_doc_and_associated_pages(str(request.ids))
    return {"message": msg}

@app.post('/get_child_pages/')
async def get_child_pages(request: IdRequest):
    # Print the received URL
    print('child id ',request.ids)
    docs = get_child_docs_by_id(request.ids)
    docs = [format_child_card(doc) for doc in docs] 
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")
    return docs


@app.post('/get_child_page_by_id/')
async def get_child_page_by_id(request: IdRequest):
    # Print the received URL
    print('child id ',request.ids)
    docs = get_child_doc_by_id(request.ids)
    
    docs = format_child_card(docs)
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")
    return docs
# Define the data models
class TableData(BaseModel):
    originalContent: str
    correctedSentence: str
    highlighted: str

class MainData(BaseModel):
    table_data: List[TableData]
    caution_sentences: List[str]

class RequestData(BaseModel):
    id: str
    parent_url: str
    url: str
    title: str
    status: str
    timestamp: str
    main_data: MainData


@app.post("/update_table_data/")
async def process_data(data: RequestData):
    try:
        resp = update_document(data.model_dump())
        return {"message": resp}
    except Exception as e:
        return {"message": str(e)}

    
@app.post("/get_pdf_page/")
async def get_pdf_single(request: IdRequest):
    resp = single_page_pdf_runner(str(request.ids))

    if resp['status']:
        file_path = resp['file_name']
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=os.path.basename(file_path))
        else:
            raise HTTPException(status_code=404, detail="File not found.")
    else:
        raise HTTPException(status_code=400, detail=resp.get('message', 'Error generating PDF'))
    
@app.post("/get_parent_by_id/")
async def get_parent_by_id_api(request: IdRequest):
    docs = get_parent_by_id(str(request.ids))
    return {"title":docs['url'],
            "status":docs['status']}

# @app.post("/get_multipage_pdf/")
# async def get_multipage_pdf(request: IdRequest):
#     print('Page Id',request.ids)
#     resp = multi_page_pdf_runner(str(request.ids))

#     if resp['status']:
#         file_path = resp['file_name']
#         if os.path.exists(file_path):
#             print('file_name is',file_path)
#             return FileResponse(file_path, filename=os.path.basename(file_path))
#         else:
#             raise HTTPException(status_code=404, detail="File not found.")
#     else:
#         raise HTTPException(status_code=400, detail=resp.get('message', 'Error generating PDF'))
job_status = {}
@app.post("/get_multipage_pdf/")
async def get_multipage_pdf(request: IdRequest):
    print('Page Id', request.ids)
    resp = multi_page_pdf_runner(str(request.ids))
    if resp['status']:
        file_path = resp['file_name']
        if os.path.exists(file_path):
            print('file_name is', file_path)
            headers = {
                "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"
            }
            return FileResponse(file_path, headers=headers)
        else:
            raise HTTPException(status_code=404, detail="File not found.")
    else:
        raise HTTPException(status_code=400, detail=resp.get('message', 'Error generating PDF'))

@app.get("/get_keys/")
async def get_keys1():
    docs = get_keys_from_db()
    docs = [format_keys(doc) for doc in docs]
    try:
        resp = {'resp':docs,'status':'true'}
        return resp
    except Exception as e:

        resp = {'resp':str(e),'status':'false'}
        return resp
    
@app.post("/update_keys/")
async def set_keys_1(request: KeyItem):
    resp = add_keys_to_db(**request.dict())
    return {"message": resp}

@app.post("/auth_xyz/")
async def auth(request: PassKeyItem):
    docs = get_keys_from_db()
    docs = [format_keys(doc) for doc in docs]
    base_pass_key = docs[0]['PASSWORD']
    print(request)
    if request.passkey == base_pass_key:
        return {"key":"d1g1max"}
    else:
        return {"key":"xyz"}

# @app.post("/update_keys/")
# async def update_keys(request: PassKeyItem):
#     # Log the request
#     print(f"Received passkey: {request.passkey}")
#     # process the passkey or update the keys
#     # return {"status": "success"}
        

 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

