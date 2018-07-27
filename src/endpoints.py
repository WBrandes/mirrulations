from flask import Flask, request, Response
import redis
import json
from docs_filter import process_docs
from doc_filter import process_doc
from redis_manager import RedisManager
import logging
import config


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='endpoints_log.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'FLASK'}
logger = logging.getLogger('tcpserver')

app = Flask(__name__)


r = RedisManager(redis.Redis())

version = 'v1.2'

@app.route('/')
def default():
    """
    Default endpoint
    :return: returns empty json
    """
    logger.warning('Successful API Call: %s', 'default: default endpoint', extra=d)
    return json.dumps({})


@app.route('/get_work')
def get_work():
    """
    endpoint the user will use to get work from the queue
    client_id will be one of the parameters given for logging purposes
    :return: returns the json containing the job_id, the type of work to be done, the work that nees to be done, and
    the version number
    """
    logging.warning("Successful API Call: %s", 'get_work: get_work', extra=d)
    if len(request.args) != 1:
        logger.warning('Exception: %s', 'get_work: Get Exception for incorrect number of parameters', extra=d)
        raise GetException
    logger.warning('Assign Variable: %s', 'get_work: attempting to get client_id', extra=d)
    client_id = request.args.get('client_id')
    logger.warning('Variable Success: %s', 'get_work: successfully retrieved the client id', extra=d)
    if client_id is None:
        logging.warning("Exception: %s", 'get_work: BadParameterException, client id was none', extra=d)
        raise BadParameterException
    logger.warning('Assign Variable: %s', 'get_work: attempting to get json_info from get_work - Calling get_work', extra=d)
    json_info = r.get_work()
    logger.warning('Variable Success: %s', 'get_work: successfully retrieved the json_info', extra=d)
    logger.warning('Returning: %s', 'get_work: returning json_info to client from get_work', extra=d)
    return json.dumps(json_info)


@app.route('/return_docs', methods=['POST'])
def return_docs():
    """
    the endpoint the client calls to return the document ids received from the regulations docs calls
    :return: returns a string saying successful so the client knows the call was successful
    """
    logger.warning('Successful API Call: %s', 'return_docs: return docs', extra=d)
    try:
        logger.warning('Assign Variable: %s', 'return_docs: attempting to get json_info from the request', extra=d)
        json_info = request.get_json()
        logger.warning('Variable Success: %s', 'return_docs: successfully retreived json_info', extra=d)
    except:
        logger.warning('Exception: %s', 'return_docs: BadParameterException for return docs', extra=d)
        raise BadParameterException
    if json_info is None:
        logger.warning('Exception: %s', 'return_docs: PostException for return docs', extra=d)
        raise PostException
    logger.warning('Calling Function: %s', 'return_docs: return_docs calling process_docs', extra=d)
    process_docs(json_info)
    logger.warning('Function Successful: %s', 'return_docs: process_docs successfully called from return_docs', extra=d)
    logger.warning('Returning: %s', 'return_docs: returning success from return_docs', extra=d)
    return 'Successful!'


@app.route('/return_doc', methods=['POST'])
def return_doc():
    """
    the endpoint the client calls to return documents they received from the individual regulations doc calls
    :return: returns a string saying successful so the client knows the call was successful
    """
    logger.warning('Successful API Call: %s', 'return_doc: return_doc call successful', extra=d)
    try:
        logger.warning('Assign Variable: %s', 'return_doc: getting the files from the file request field', extra=d)
        files = request.files['file']
        logger.warning('Variable Success: %s', 'return_doc: files successfully retrieved from the return doc post', extra=d)
        logger.warning('Assign Variable: %s', 'return_doc: get the json_info from the post request', extra=d)
        json_info= request.form['json_info']
        logger.warning('Variable Success: %s', 'return_doc: json retrieved from the doc post call', extra=d)
    except:
        logger.warning('Exception: %s', 'return_doc: BadParameterException for return_doc', extra=d)
        raise BadParameterException
    logger.warning('Exception: %s', 'return_doc: BadParameterException for return_doc', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: call process_docs with the json and files posted to return_doc endpoint', extra=d)
    process_doc(json.dumps(json_info), files)
    logger.warning('Function Successful: %s', 'return_doc: success from return_doc', extra=d)
    logger.warning('Returning: %s', 'return_doc: returning success from return_doc', extra=d)
    return 'Successful!'


def generate_json(work_list):
    """
    given a list of values, the list will be converted into json format
    :param work_list: the list of values that will be converted into json
    :return: returns the json formatted list
    """
    logger.warning('Call Successful: %s', 'generate_json: generate_json called successfully', extra=d)
    logger.warning('Assign Variable: %s', 'generate_json: assign job_id from the work_list', extra=d)
    job_id = work_list[0]
    logger.warning('Variable Success: %s', 'generate_json: jod_id assigned', extra=d)
    logger.warning('Assign Variable: %s', 'generate_json: assign type from the work_list', extra=d)
    type = work_list[1]
    logger.warning('Variable Success: %s', 'generate_json: type assigned', extra=d)
    logger.warning('Assign Variable: %s', 'generate_json: assign data from the work_list', extra=d)
    data = work_list[2]
    logger.warning('Variable Success: %s', 'generate_json: data assigned', extra=d)
    logger.warning('Assign Variable: %s', 'generate_json: assign converted_json from the combination of job_id, type, and data', extra=d)
    converted_json = {
        "job_id": job_id,
        "type": type,
        "data": data,
        "version": version
    }
    logger.warning('Variable Success: %s', 'generate_json: converted_json created', extra=d)
    logger.warning("Returning: %s", 'generate_json: returning converted_json', extra=d)
    return json.dumps(converted_json)


# Throw exception if there is an error making the get call
class GetException(Exception):
    print("Bad Request")

# Throw exception if one of the parameters is incorrect
class BadParameterException(Exception):
    print("Bad Request")

# Throw exception if there was an error making the post request
class PostException(Exception):
    print("Bad Request")


if __name__ == '__main__':
    app.run(config.read_value("ip"), port=int(config.read_value("port")))



