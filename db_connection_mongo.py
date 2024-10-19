from pymongo import MongoClient
import datetime


def connectDataBase():
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

def updateDocument(documents, docId, docText, docTitle, docDate, docCat):
    deleteDocument(documents, docId)
    createDocument(documents, docId, docText, docTitle, docDate, docCat)

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
    return master_index

def create_terms_array(text):
    text = prepare_text_for_index(text)
    word_count_map = create_word_count_map(text)
    terms_array = convert_map_to_array(word_count_map)
    return terms_array

def convert_map_to_array(text_count_map):
    terms_array = []
    for key, value in text_count_map.items():
        terms_array.append({"term": key, "count": value})
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

