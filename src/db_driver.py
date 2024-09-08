from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from pymongo import ReturnDocument
import certifi

ca = certifi.where()

# MongoDB connection URI
uri = "mongodb+srv://deamersoftlab2013:misrial22@digimax.bh5xd.mongodb.net/?retryWrites=true&w=majority&appName=digimax"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Define the database and collections
db = client['your_database_name']  # Replace with your database name
parent_docs_collection = db['parent_docs']
processed_pages_collection = db['processed_pages']

def add_parrent_doc(address, number_of_pages,tags, options, status='init', halt_status=False, timestamp=datetime.now()):
    
    web_page_document = {
        'url': str(address).rstrip('/'),
        'number_of_pages': number_of_pages,
        'option': str(options).lower(),
        'tags': tags,
        'status': status,
        'halt_status': halt_status,
        'timestamp': timestamp
    }



    result = parent_docs_collection.insert_one(web_page_document)
    return str(result.inserted_id)


def add_processed_pages(documents):
    status = processed_pages_collection.insert_many(documents)
    return status


def read_parent_docs(query):
    documents = parent_docs_collection.find(query)
    return [doc for doc in documents]
def read_processed_pages(query):
    documents = processed_pages_collection.find(query)
    return [doc for doc in documents]

def get_first_two_init_pages_with_parent(parent_doc_id):
    # Find the parent document
    parent_doc = parent_docs_collection.find_one({'_id': ObjectId(parent_doc_id)})

    if not parent_doc:
        return None, f"No parent document found with id: {parent_doc_id}"
     
    # Find the first two documents with status 'init' and matching parent_url
    query = {'status': 'init', 'parrent_id': parent_doc_id}
    documents = processed_pages_collection.find(query).limit(4)
    
    return [doc for doc in documents]

def update_processed_documents(documents,del_flag=False):
    for doc in documents:
        # Extract the ID from the document
        document_id = doc['_id']
        
        # Create the filter criteria using the document ID
        filter_criteria = {'_id': document_id}
        
        if not del_flag:
            # Create the update operation (remove _id from the update values)
            update_values = {key: value for key, value in doc.items() if key != '_id'}
            update_operation = {'$set': update_values}
            
            
            # Perform the update_one operation
            result = processed_pages_collection.update_one(filter_criteria, update_operation)
            
            if result.matched_count == 0:
                print(f"No document found with _id: {document_id} to update.")
            else:
                print(f"Document with _id: {document_id} updated successfully.")
        
        else:
            print('Deleting specific page')
            # Perform the delete_one operation
            result = processed_pages_collection.delete_one(filter_criteria)
            
    return "Documents updated successfully."

def empty_database(db):
    collections = db.list_collection_names()
    for collection_name in collections:
        collection = db[collection_name]
        result = collection.delete_many({})
        print(f"Deleted {result.deleted_count} documents from collection '{collection_name}'")

def update_parent_doc_status_by_id(id, new_status):
    # Update the status of the parent document
    # print(url)
    
    query = {'_id':  ObjectId(id)}
    update = {'$set': {'status': new_status}}
    # print(update)
    result = parent_docs_collection.update_one(query, update)
    
    if result.matched_count == 0:
        return f"No document found with Id: {id}"
    elif result.modified_count == 0:
        return f"Document with Id: {id} was already in the desired status: {new_status}"
    else:
        return f"Document with Id: {id} updated successfully to status: {new_status}"
    
def get_parent_doc_status_by_id(id):
    query = {'_id':  ObjectId(id)}
    result = parent_docs_collection.find_one(query)
    if result:
        return result['status']
    else:
        return None

def get_child_docs_by_url(url):
    query = {'parent_url': url}
    result = processed_pages_collection.find(query)
    return [doc for doc in result]

def get_child_doc_by_id(doc_id):    
    query = {'_id': ObjectId(doc_id)}
    result = processed_pages_collection.find(query)
    docs_ret = [doc for doc in result]

    return docs_ret[0]
    
def get_all_not_done_parent_docs():
    query = {'halt_status': False, 'status': {'$nin': ['done', 'processing']}}
    result = parent_docs_collection.find(query)
    return [doc for doc in result]


# Function to get halt_status from parent_docs_collection
def get_halt_status(doc_id):
    # query = {'url': url}
    query = {'_id': ObjectId(doc_id)}
    document = parent_docs_collection.find_one(query, {'_id': 0, 'halt_status': 1})
    
    if document:
        return document.get('halt_status', None)
    else:
        return f"No document found with URL: {doc_id}"

# Function to update halt_status in parent_docs_collection
def update_halt_status(doc_id, new_halt_status):
    query = {'_id': ObjectId(doc_id)}
    update = {'$set': {'halt_status': new_halt_status}}
    
    result = parent_docs_collection.update_one(query, update)
    
    if result.matched_count == 0:
        return f"No document found with URL: {doc_id}"
    elif result.modified_count == 0:
        return f"Document with URL: {doc_id} was already in the desired halt_status: {new_halt_status}"
    else:
        return f"Document with URL: {doc_id} updated successfully to halt_status: {new_halt_status}"
    
def get_all_parent_docs():
    documents = parent_docs_collection.find()
    return [doc for doc in documents]
    
def get_non_halted_non_completed_docs():
    query = {'halt_status': False, 'status': {'$nin': ['done', 'processing']}}
    documents = parent_docs_collection.find(query)
    return [doc for doc in documents]

def halt_task(doc_id):
    query = {'_id': ObjectId(doc_id)}
    update = {'$set': {'halt_status': True}}
    
    result = parent_docs_collection.update_one(query, update)
    
    if result.matched_count == 0:
        return f"No document found with URL: {doc_id}"
    elif result.modified_count == 0:
        print("Document with URL: {doc_id} was already halted.")
        return f"Document with URL: {doc_id} was already halted."
    else:
        print("Document with URL: {doc_id} halted successfully.")
        return f"Document with URL: {doc_id} halted successfully."

def unhalt_task(doc_id):
    query = {'_id': ObjectId(doc_id)}
    update = {'$set': {'halt_status': False}}
    
    result = parent_docs_collection.update_one(query, update)
    
    if result.matched_count == 0:
        print(f"No document found with URL: {doc_id}")
        return 
    elif result.modified_count == 0:
        print(f"Document with URL: {doc_id} was not halted.")
        return f"Document with URL: {doc_id} was not halted."
    else:
        print(f"Document with URL: {doc_id} unhalted successfully.")
        return f"Document with URL: {doc_id} unhalted successfully."
    

def delete_parent_doc_and_associated_pages(id):
    # Find the parent document by URL
    parent_doc = parent_docs_collection.find_one({'_id': ObjectId(id)})
    
    if not parent_doc:
        return f"No parent document found with id: {id}"
    
    # Delete the associated processed pages
    # 
    print('Id reached',id)
    delete_result = processed_pages_collection.delete_many({'parrent_id': id})
    print(f"Deleted {delete_result.deleted_count} associated pages for id: {id}")
    
    # Delete the parent document
    parent_delete_result = parent_docs_collection.delete_one({'_id': ObjectId(id)})
    
    if parent_delete_result.deleted_count == 0:
        return f"Failed to delete the parent document with id: {id}"
    else:
        return f"Parent document with id: {id} and its associated pages deleted successfully."
    

def get_child_docs_by_id(doc_id):
    # Check if the doc_id is a valid ObjectId
    if ObjectId.is_valid(doc_id):
        query = {'parrent_id': ObjectId(doc_id)}
    else:
        query = {'parrent_id': doc_id}
    
    result = processed_pages_collection.find(query)
    return [doc for doc in result]



def get_parent_url_from_id(doc_id):
    query = {'_id': ObjectId(doc_id)}
    result = parent_docs_collection.find_one(query)
    return result['url']

def get_parent_by_id(doc_id):
    query = {'_id': ObjectId(doc_id)}
    result = parent_docs_collection.find_one(query)
    return result

def get_child_docs_by_id(doc_id):
    try:
        # Try querying with ObjectId
        if ObjectId.is_valid(doc_id):
            query = {'parrent_id': ObjectId(doc_id)}
            result = list(processed_pages_collection.find(query))
            if result:
                return result
            else:
                print(f"No documents found with ObjectId: {doc_id}")
        
        # Query with string
        query = {'parrent_id': doc_id}
        result = list(processed_pages_collection.find(query))
        if result:
            return result
        else:
            print(f"No documents found with string: {doc_id}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return []

def update_document(data):
    '''
    Update a document in the processed_pages_collection
    only update the fields that are changed with respect to orignal data.
    '''
    
    query = {'_id': ObjectId(data['id'])}
    update = {'$set': data}
    
    result = processed_pages_collection.update_one(query, update)
    
    if result.matched_count == 0:
        print(f"No document found with Id: {data['id']}")
        return f"No document found with Id: {data['id']}"
    elif result.modified_count == 0:
        print(f"Document with Id: {data['id']} was already in the desired status: {data['status']}")
        return f"Document with Id: {data['id']} was already in the desired status: {data['status']}"
    else:
        print(f"Document with Id: {data['id']} updated successfully to status: {data['status']}")
        return f"Document with Id: {data['id']} updated successfully to status: {data['status']}"
    

def get_child_by_id(doc_id):
    query = {'_id': ObjectId(doc_id)}
    result = processed_pages_collection.find_one(query)
    return result
def get_id(doc_id):
    id = ObjectId(doc_id)
    return id



def update_child_doc_status_by_id(id, new_status):
    """
    Update the status of a child document by its ID in the processed_pages_collection.

    :param id: str, The ID of the document to update.
    :param new_status: str, The new status to set.
    :return: str, A message indicating the result of the operation.
    """
    # Convert the string ID to ObjectId
    query = {'_id': ObjectId(id)}
    
    # Define the update operation
    update = {'$set': {'status': new_status}}
    print(update)  # Optional: print the update operation for debugging

    # Perform the update operation
    result = processed_pages_collection.update_one(query, update)
    
    # Check the result and return an appropriate message
    if result.matched_count == 0:
        return f"No document found with ID: {id}"
    elif result.modified_count == 0:
        return f"Document with ID: {id} was already in the desired status: {new_status}"
    else:
        return f"Document with ID: {id} updated successfully to status: {new_status}"
    
def delete_stopped_processed_documents(parent_id):
    try:
        # 'parrent_id': parent_doc_id
        query = {'parrent_id': parent_id, 'status': 'stopped'}
        result = processed_pages_collection.delete_many(query)
        print(f"Deleted {result.deleted_count} documents with status 'stopped'")
    except Exception as e:
        print(f"An error occurred: {e}")
