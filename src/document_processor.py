import tempfile
from documents_processor import *

base_url = 'https://api.data.gov/regulations/v3/document?documentId='
home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='document_processor.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': client_id}
logger = logging.getLogger('tcpserver')


def document_processor(doc_ids):
    """
    This process takes all of the document ids given to it and saves all of the data for the documents in a temporary directory.
    :param doc_ids: list of document ids that have to be collected.
    :return: temporary directory that data was written to.
    """
    logger.warning('Call Successful: %s', 'document_processor: processing document ID list', extra=d)
    dirpath = tempfile.TemporaryDirectory()
    for doc_id in doc_ids:
        logger.warning('Call Successful: %s', 'document_processor: processing document: ' + doc_id, extra=d)
        result = api_call_manager(add_api_key(make_doc_url(doc_id)))
        total = get_extra_documents(result, dirpath.name, doc_id)
    return dirpath

def make_doc_url(documentId):
    """
    Given a documentId as a string append it to the end of the api call
    :param documentId: the string of a documentId
    :return: the url that will be called with a documentId through regulations.gov API
    """
    return base_url + documentId


def save_document(dirpath, doc_json, documentId):
    """
    Saves the json of the document call
    :param dirpath: path to the directory where the json will be saved
    :param doc_json: the json received from the api call
    :param documentId: the string of a documentId
    :return:
    """
    logger.warning('Call Successful: %s', 'document_processor: saving document with docID: ' + documentId, extra=d)
    location = dirpath + "/doc." + documentId + ".json"
    with open(location , "w+") as f:
        json.dump(doc_json, f)


def download_document(dirpath, documentId, result, type):
    """
    Saves the other file formats of the document call
    :param dirpath: path to the directory where the download will be saved
    :param documentId: the string of a documentId
    :param result: the result received from the api call
    :param type: the type of file that will be saved
    :return:
    """

    logger.warning('Call Successful: %s', 'document_processor: downloading document with docID: ' + documentId, extra=d)

    # These are special cases where the api representation is different from the user's interpretation
    if(type == "excel12book"):
        type = "xlsx"
    if(type == "msw12"):
        type = "doc"
    with open(dirpath + "/doc." + documentId + "." + type, 'wb') as f:
        for chunk in result.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_extra_documents(result, dirpath, documentId):
    """
    Download the json of the result from the original api call
    Determine if the document has additional file formats that need to be downloaded
    Determines if the document has attachments that need to be downloaded
    :param result: the result of the api call
    :param dirpath: path to the directory where the download will be saved
    :param documentId: the string of a documentId
    :return: the total number of requests required to download all of them
    """

    logger.warning('Call Successful: %s', 'document_processor: getting extra documents for docID: ' + documentId, extra=d)

    doc_json = json.loads(result.text)
    save_document(dirpath, doc_json, documentId)
    total_requests = 0
    total_requests += download_doc_formats(dirpath, doc_json, documentId)
    total_requests += download_attachments(dirpath, doc_json, documentId)
    return total_requests


def download_doc_formats(dirpath, doc_json, documentId):
    """
    Download the other formats for the document
    :param dirpath: path to the directory where the download will be saved
    :param doc_json: the json from a single document api call
    :param documentId: the string of a documentId
    :return: the total number of requests used to download the extra formats
    """

    logger.warning('Call Successful: %s', 'document_processor: downloading doc formats for docID: ' + documentId, extra=d)

    total_requests = 0
    try:
        extra_formats = doc_json["fileFormats"]
        total_requests += len(extra_formats)
        for extra_doc in extra_formats:
            result = api_call_manager(add_api_key(str(extra_doc)))
            here = extra_doc.index("contentType") + 12
            type = extra_doc[here:]
            download_document(dirpath, documentId, result, type)
    except KeyError:
        pass
    return total_requests


def download_attachments(dirpath, doc_json, documentId):
    """
    Download the other attachments for the document
    :param dirpath: path to the directory where the download will be saved
    :param doc_json: the json from a single document api call
    :param documentId: the string of a documentId
    :return: the total number of requests used to download the extra attachments
    """

    logger.warning('Call Successful: %s', 'document_processor: downloading attachments for docID: ' + documentId, extra=d)

    total_requests = 0
    try:
        extra_attachments = doc_json["attachments"]
        total_requests += len(extra_attachments)
        for attachment in extra_attachments:
            attachment_formats = attachment["fileFormats"]
            for a_format in attachment_formats:
                here = str(a_format).index("contentType") + 12
                type = str(a_format)[here:]
                result = api_call_manager(add_api_key(str(a_format)))
                download_document(dirpath, documentId, result, type)
    except KeyError:
        pass
    return total_requests
