from api_call_management import *
import json
import logging

workfiles = []
version = "v1.2"
home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='documents_processor.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': client_id}
logger = logging.getLogger('tcpserver')

def documents_processor(urls, job_id, client_id):
    """
    Call each url in the list, process the results of the calls and then form a json file to send back the results
    :param urls: list of urls that have to be called
    :param job_id: the id of the job that is being worked on currently
    :param client_id: id of the client calling this function
    :return result: the json to be returned to the server after each call is processed
    """
    global workfiles
    workfiles = []
    logger.warning('Call Successful: %s', 'documents_processor: Processing documents', extra=d)
    for url in urls:
        try:
            logger.warning('Call Successful: %s', 'documents_processor: Processing URL: ' + url, extra=d)
            result = api_call_manager(add_api_key(url))
            process_results(result)
            logger.warning('Call Successful: %s', 'documents_processor: Done processing URL: ' + url, extra=d)
        except:
            logger.warning('Exception: %s', 'documents_processor: Error processing URL: ' + url, extra=d)
    logger.warning('Assign Variable: %s', 'documents_processor: Load the json', extra=d)
    result = json.loads(json.dumps({"job_id" : job_id, "type": "docs", "data" : workfiles, "client_id" : str(client_id), "version" : version}))
    logger.warning('Variable Success: %s', 'documents_processor: successfully loaded json', extra=d)
    logger.warning('Returning: %s', 'documents_processor: returning the json', extra=d)
    return result


def process_results(result):
    """
    Loads the json from the results of the api call
    Gets the list of documents from the json
    Creates a new json that contains the documents returned from each api call
    :param result: Result of the api call
    :return: returns True if the processing completed successfully
    """
    logger.warning('Call Successful: %s', 'documents_processor: Processing Documents Results', extra=d)
    docs_json = json.loads(result.text)
    try:
        doc_list = docs_json["documents"]
    except TypeError:
        logger.warning('Exception: %s', 'BadJsonException for return docs', extra=d)
        raise BadJsonException
    work = make_docs(doc_list)

    return True


def make_docs(doc_list):
    """
    Given a list of document jsons that contain the id and the attachment count
    Add the ids to lists that will contain calls that in total have no more than 1000 predicted API calls
    :param doc_list: list of document ids and attachment counts as a dictionary
    :return: the global workfiles variable that contains all of the work in list
    """
    global workfiles
    size = 0
    work_list = []
    for doc in doc_list:
        doc_id = doc["documentId"]
        calls = doc["attachmentCount"] + 1
        if size + calls > 1000:
            workfiles.append(work_list)
            work_list = []
            size = 0
        size += calls
        document = {"id" : doc_id, "count" : calls}
        work_list.append(document)
    if size != 0:
        workfiles.append(work_list)
    return workfiles


# Raised if the json is not correctly formatted or is empty
class BadJsonException(Exception):
    print("NOTICE: The Json appears to be formatted incorrectly.")
