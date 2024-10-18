import copy
from pymongo import MongoClient
import datetime
import pprint

def connectDataBase():

    # Creating a database connection object using pymongo

    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:

        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]

        return db

    except:
        print("Database not connected successfully")

def createUser(col, id, name, email):

    # Value to be inserted
    user = {"_id": id,
            "name": name,
            "email": email,
            }

    # Insert the document
    col.insert_one(user)

def updateUser(col, id, name, email):

    # User fields to be updated
    user = {"$set": {"name": name, "email": email} }

    # Updating the user
    col.update_one({"_id": id}, user)

def deleteUser(col, id):

    # Delete the document from the database
    col.delete_one({"_id": id})

def getUser(col, id):

    user = col.find_one({"_id":id})

    if user:
        return str(user['_id']) + " | " + user['name'] + " | " + user['email']
    else:
        return []

def createComment(col, id_user, dateTime, comment):

    # Comments to be included
    comments = {"$push": {"comments": {
                                       "datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S"),
                                       "comment": comment
                                       } }}

    # Updating the user document
    col.update_one({"_id": id_user}, comments)

def updateComment(col, id_user, dateTime, new_comment):

    # User fields to be updated
    comment = {"$set": {"comments.$.comment": new_comment} }

    # Updating the user
    col.update_one({"_id": id_user, "comments.datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S")}, comment)

def deleteComment(col, id_user, dateTime):

    # Comments to be delete
    comments = {"$pull": {"comments": {"datetime": datetime.datetime.strptime(dateTime, "%m/%d/%Y %H:%M:%S")} }}

    # Updating the user document
    col.update_one({"_id": id_user}, comments)

def getChat(col):

    # creating a document for each message
    pipeline = [
                 {"$unwind": { "path": "$comments" }},
                 {"$sort": {"comments.datetime": 1}}
               ]

    comments = col.aggregate(pipeline)

    chat = ""

    for com in comments:
        chat += com['name'] + " | " + com['comments']['comment'] + " | " + str(com['comments']['datetime']) + "\n"

    return chat

def createDocument(documents, docId, docText, docTitle, docDate, docCat):
    date = datetime.datetime.strptime(docDate, "%Y-%m-%d")
    terms_array = create_terms_array(docText)
    result = documents.insert_one({
        "_id": docId,
        "title": docTitle,
        "date": date,
        "category": docCat,
        "text" : docText,
        "terms" : terms_array
    })
    print(result)

def updateDocument(documents, docId, docText, docTitle, docDate, docCat):
    deleteDocument(documents, docId)
    date = datetime.datetime.strptime(docDate, "%Y-%m-%d")
    result = documents.insert_one({
        "_id": docId,
        "title": docTitle,
        "date": date,
        "category": docCat,
        "text" : docText,
    })
    print(result)


def deleteDocument(documents, docId):
    documents.delete_one({"_id": docId})

def getIndex(document_collection):
    pipeline = [{"$unwind": "$terms"}]
    unwound_documents = list(document_collection.aggregate(pipeline))

    master_index = dict()
    for individual_doc in unwound_documents:
        term = individual_doc["terms"]["term"]
        if term not in master_index:
            entry = dict()
            doc_title = individual_doc["title"]
            entry[doc_title] = individual_doc["terms"]["count"]
            master_index[individual_doc["terms"]["term"]] = entry
        else:
            doc_title = individual_doc["title"]
            master_index[term][doc_title] = individual_doc["terms"]["count"]
    pprint.pprint(master_index)
    return None

def some_kind_of_index(documents):
    all_documents = list(documents.find({}))
    for document in all_documents:
        cleaned_text = document["text"]
        cleaned_text = prepare_text_for_index(cleaned_text)
        index = create_word_count_map(cleaned_text)
        print(index)

def create_terms_array(text):
    text = prepare_text_for_index(text)
    word_count_map = create_word_count_map(text)
    terms_array = convert_map_to_array(word_count_map)
    return terms_array

def convert_map_to_array(text_count_map):
    terms_array = []
    for key, value in text_count_map.items():
        terms_array.append({"term": key, "count": value})
    print(terms_array)
    return terms_array

def create_word_count_map(document_text):
    index = dict()
    for word in document_text:
        if word not in index:
            index[word] = 1
        else:
            index[word] += 1
    return index

def prepare_text_for_index(text):
    prepared_text = remove_punctuation(text)
    prepared_text = prepared_text.lower()
    prepared_text = prepared_text.split(" ")
    return prepared_text

def remove_punctuation(text):
    punctuation_to_remove = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    for character in punctuation_to_remove:
        if character in text:
            text = text.replace(character, "")
    return text

