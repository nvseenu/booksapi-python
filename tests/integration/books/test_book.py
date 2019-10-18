import pytest
import config_qa
from psycopg2 import pool
from books import BookRepo
from datetime import datetime


class TestBook:
    """
    BookRepo and Book classes are storing / retrieving book records into/from db.
    As these classes generate dynamic queries, only db can verify the queries.
    Hence it is better to test against db, instead of writing unit tests with mock
    and verifying the queries. 
    """

    @pytest.fixture(scope='module')
    def book_repo(self):
        cpool = pool.ThreadedConnectionPool(**config_qa.books_api['connection_pool'])
        if not cpool:
            raise ValueError('Unable to create a connection pool.')

        return BookRepo(cpool)

    def test_create_book(self, book_repo):
        # Create a new book
        book_info = self.new_book_info()
        new_book = book_repo.get_empty_book()
        new_book.set_values(**book_info)
        new_book.save()
        assert new_book.id > 0
        book_info['id'] = new_book.id

        # Fetch the same book and check if the deails are same
        same_book = book_repo.get_book(new_book.id)
        assert same_book.values() == book_info

    def test_update_book(self, book_repo):
        # Create a new book
        book_info = self.new_book_info()
        new_book = book_repo.get_empty_book()
        new_book.set_values(**book_info)
        new_book.save()

        # Update the book
        update_book_info = {
            'name': 'Water World',
            'isbn': '123-11111',
            'authors': ['George William'],
            'country': 'United Kingdom',
            'number_of_pages': 123,
            'publisher': 'Manning',
            'release_date': '2017-01-07'
        }

        new_book.set_values(**update_book_info)
        new_book.save()
        update_book_info['id'] = new_book.id

        # Fetch the same book and check if the details are same
        same_book = book_repo.get_book(new_book.id)
        assert same_book.values() == update_book_info

    def test_delete_book(self, book_repo):
        # Create a new book
        book_info = self.new_book_info()

        new_book = book_repo.get_empty_book()
        new_book.set_values(**book_info)
        new_book.save()

        # Delete the book
        new_book.delete()

        # Fetch the same book and it should be none
        same_book = book_repo.get_book(new_book.id)
        assert same_book is None

    def test_get_books(self, book_repo):
        # Create new books
        new_book_infoset = [self.new_book_info() for i in range(2)]

        new_books = []
        for book_info in new_book_infoset:
            new_book = book_repo.get_empty_book()
            new_book.set_values(**book_info)
            new_book.save()
            new_books.append(new_book)

        # Filter books by name
        books = book_repo.get_books(name=new_book_infoset[0]['name'])
        assert len(books) == 1
        assert books[0].values() == new_books[0].values()

        # Filter books by country
        books = book_repo.get_books(country=new_book_infoset[0]['country'])
        assert len(books) >= 2

        # Filter books by publisher
        books = book_repo.get_books(publisher=new_book_infoset[0]['publisher'])
        assert len(books) >= 2

        # Filter books by release_date
        books = book_repo.get_books(release_date=2019)
        assert len(books) >= 2

        # Filter books by country and publisher
        books = book_repo.get_books(publisher=new_book_infoset[0]['publisher'], country=new_book_infoset[0]['country'])
        assert len(books) >= 2

    def new_book_info(self):
        ctime = self.current_time_str()
        book_info = {
            'name': 'A Game of thrones ' + ctime,
            'isbn': ctime,
            'authors': ['John Doe'],
            'country': 'United States',
            'number_of_pages': 450,
            'publisher': 'ORielly',
            'release_date': '2019-01-01'
        }
        return book_info.copy()

    def current_time_str(self):
        return datetime.strftime(datetime.today(), '%Y-%m-%d-%H-%M-%S-%f')
