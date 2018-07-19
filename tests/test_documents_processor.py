from documents_processor import *
import tempfile
import pytest
import requests_mock

from api_call import *

home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()

base_url = 'https://api.data.gov:443/regulations/v3/documents.json?'
base_url2 = 'https://www.website.com/regulations/v3/documents.json?'


@pytest.fixture
def mock_req():
    with requests_mock.Mocker() as m:
        yield m


def test_documents_processor(mock_req):
    urls = [base_url, base_url2]
    mock_req.get(add_api_key(base_url), status_code=200, text='{"documents": '
                                                              '[{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    mock_req.get(add_api_key(base_url2), status_code=200, text='{"documents": '
                                                              '[{"documentId": "CMS-2005-0001-0003", "attachmentCount": 88},\
                                                                {"documentId": "CMS-2005-0001-0004", "attachmentCount": 666}]}')
    docs = documents_processor(urls, 'Job ID', client_id)
    assert docs == ({'job_id': 'Job ID', 'data': [{'id': 'CMS-2005-0001-0001', 'count': 5},
                                                    {'id': 'CMS-2005-0001-0002', 'count': 1000},
                                                    {'id': 'CMS-2005-0001-0003', 'count': 89},
                                                    {'id': 'CMS-2005-0001-0004', 'count': 667}],
                                                    'version': 'v1.0', 'client_id': str(client_id)})


def test_valid_results(mock_req):
    urls = [base_url]
    mock_req.get(add_api_key(base_url), status_code=200, text='{"documents": '
                                                              '[{"documentId": "CMS-2005-0001-0001", "attachmentCount": 4},\
                                                                {"documentId": "CMS-2005-0001-0002", "attachmentCount": 999}]}')
    result = process_results(api_call_manager(add_api_key(base_url)))
    assert result


def test_successful_call(mock_req):
    mock_req.get(base_url, status_code=200, text='{}')
    assert api_call_manager(base_url).text == '{}'


def test_call_fail_raises_exception(mock_req):
    mock_req.get(base_url, status_code=407, text='{}')
    with pytest.raises(CallFailException):
        api_call_manager(base_url)


def test_empty_json(mock_req):
    mock_req.get(base_url, status_code=200, text='')
    with pytest.raises(BadJsonException):
        process_results(api_call_manager(base_url))


def test_bad_json_format(mock_req):
    mock_req.get(base_url, status_code=200, text='{information: [{},{}]}')
    with pytest.raises(BadJsonException):
        process_results(api_call_manager(base_url))
