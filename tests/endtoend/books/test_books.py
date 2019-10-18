import requests
import json
import pytest
from datetime import datetime


class TestBooksApi:
    """
    We run end to end tests by considering apis are blackbox.
    It means that i dont want to setup / cleanup db before executing tests
    """

    @pytest.fixture
    def client(self):
        client = BookApiClient('http://127.0.0.1:5000/api/v1')
        return client

    def test_create_and_get_book(self, client):
        book_info_req = self.new_book_info()
        book_resp = client.create_book(book_info_req)
        assert book_resp['status_code'] == 201
        assert book_resp['status'] == 'success'
        data = book_resp['data']
        assert data is not None, 'Could not find "data" array in json'
        assert isinstance(data, list)
        assert len(data) > 0
        books = data[0]
        book_info = books['book']
        assert book_info is not None
        self.assert_dict(book_info, book_info_req)

        get_book_resp = client.get_book(book_info['id'])
        assert get_book_resp['status_code'] == 200
        assert get_book_resp['status'] == 'success'
        get_book_info = get_book_resp['data']
        assert get_book_info is not None, 'Could not find "data" array in json'
        self.assert_dict(get_book_info, book_info, assert_id=True)

    test_update_book_with_alternative_url = [
        (False,),
        (True,)
    ]
    @pytest.mark.parametrize('use_alternative_url', test_update_book_with_alternative_url)
    def test_update(self, client, use_alternative_url):
        """
        Test if both update book end point and its alternative are working 
        """
        book_info_req = self.new_book_info()
        book_resp = client.create_book(book_info_req)
        # Checking create book is not a focus of this test. Hence we assumed
        # it is correct.
        created_book_info = book_resp['data'][0]['book']

        ctime1 = self.current_time_str()
        update_book_info_req = {
            'name': 'A Game of thrones' + ctime1,
            'isbn': ctime1,
            'authors': ['John Doe', 'Albert'],
            'country': 'United Kingdom',
            'number_of_pages': 470,
            'publisher': 'O Rielly Publishing',
            'release_date': '2019-10-10'
        }

        update_book_resp = client.update_book(created_book_info['id'], update_book_info_req, use_alternative_url)
        assert update_book_resp['status_code'] == 200
        assert update_book_resp['status'] == 'success'
        assert update_book_resp['message'] == 'The book {} was updated successfully'.format(
            update_book_info_req['name'])
        update_book_info = update_book_resp['data']
        assert update_book_info is not None, 'Could not find "data" attribute in json'
        # Add id before comparing. so that both structure will have id attribute
        update_book_info_req['id'] = created_book_info['id']
        self.assert_dict(update_book_info, update_book_info_req, assert_id=True)


    test_delete_book_with_alternative_url = [
        (False,),
        (True,)
    ]
    @pytest.mark.parametrize('use_alternative_url', test_delete_book_with_alternative_url)
    def test_delete_book(self, client, use_alternative_url):
        """
        Test if both delete book end point and its alternative are working 
        """
        book_info_req = self.new_book_info()
        book_resp = client.create_book(book_info_req)
        # Checking create book is not a focus of this test. Hence we assumed
        # it is correct.
        created_book_info = book_resp['data'][0]['book']

        expected_resp = {
            'status_code': 204,
            'status': 'success',
            'message': 'The book {} was updated successfully'.format(book_info_req['name']),
            'data': []
        }
        delete_book_resp = client.delete_book(created_book_info['id'], use_alternative_url)
        self.assert_dict(delete_book_resp, expected_resp)

    def test_get_books(self, client):
        """
        Test if get books end point is working as expected
        """
        book_info_req = self.new_book_info()
        book_resp = client.create_book(book_info_req)
        created_book_info = book_resp['data'][0]['book']

        get_books_resp = client.get_books()
        assert get_books_resp is not None
        assert get_books_resp['status_code'] == 200
        assert get_books_resp['status'] == 'success'
        data = get_books_resp['data']
        assert data is not None
        assert len(data) > 0
        matching_books = [book for book in data if book == created_book_info]
        assert len(matching_books) == 1, 'Expected book: {}, but it is not found in the response'.format(created_book_info)

    def assert_dict(self, dict1, dict2, assert_id=False):
        for key, value in dict2.items():
            if not assert_id and key == 'id':
                continue
            value1 = dict1.get(key, None)
            assert value1 == value, 'For key: {}, Expected {}, but got {}'.format(key, value, value1)

    def current_time_str(self):
        return datetime.strftime(datetime.today(), '%Y%m%d%H%M%S%f')

    def new_book_info(self):
        ctime = self.current_time_str()
        book_info = {
            'name': 'A Game of thrones' + ctime,
            'isbn': ctime,
            'authors': ['John Doe'],
            'country': 'United States',
            'number_of_pages': 350,
            'publisher': 'Acme Books Publishing',
            'release_date': '2019-01-01'
        }
        return book_info.copy()
            


class BookApiClient:
    """
    This is a REST client to books api.
    """

    def __init__(self, base_url):
        self._base_url = base_url

    def create_book(self, book_info):
        headers = {
            'Content-Type': 'application/json'
        }
        resp = requests.post('{}/books'.format(self._base_url),
                             headers=headers,
                             data=json.dumps(book_info))
        return resp.json()

    def update_book(self, id, book_info, use_alternative_url=False):
        headers = {
            'Content-Type': 'application/json'
        }
        url = '{}/books/{}'.format(self._base_url, id)

        resp = None
        if use_alternative_url:
            resp = requests.post(url+'/update',
                            headers=headers,
                            data=json.dumps(book_info))

        else:
            resp = requests.patch(url,
                            headers=headers,
                            data=json.dumps(book_info))
                
        return resp.json()

    def get_book(self, id):
        resp = requests.get('{}/books/{}'.format(self._base_url, id))
        return resp.json()

    def get_books(self, **filters):
        resp = requests.get('{}/books'.format(self._base_url),
                            params=filters)
        return resp.json()

    def delete_book(self, id, use_alternative_url=False):
        url = '{}/books/{}'.format(self._base_url, id)

        resp = None
        if use_alternative_url:
            resp = requests.post(url+'/delete')
        else:
            resp = requests.delete(url)   
        return resp.json()
