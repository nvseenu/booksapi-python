from books import BookRepo, DbBook, BookError
from collections import OrderedDict
from datetime import datetime, date
import pytest


class TestDbBook:

    def test_from_db_row(self):
        """
        Tests if a row from 'books' table can be converted properly
        """
        row = (1, 'A Game of thrones', '123-45678', '["John Doe"]', 'United States', 450, 'ORielly', date(2019, 1, 1))
        expected = dict(
            id=1,
            name='A Game of thrones',
            isbn='123-45678',
            authors=['John Doe'],
            country='United States',
            number_of_pages=450,
            publisher='ORielly',
            release_date='2019-01-01'
        )
        book = DbBook._from_db_row(None, row)
        assert book.values() == expected, 'Expected: {}, but got {}'.format(expected, book.values())

    def test_set_values(self):
        """
        Tests if set_values() sets given values into appropriate fields.
        """
        values = {
            'name': 'A Game of thrones',
            'isbn': '123-45678',
            'authors': ['John Doe'],
            'country': 'United States',
            'number_of_pages': 450,
            'publisher': 'ORielly',
            'release_date': '2019-01-01'
        }

        expected = {
            'name': 'A Game of thrones',
            'isbn': '123-45678',
            'authors': ['John Doe'],
            'country': 'United States',
            'number_of_pages': 450,
            'publisher': 'ORielly',
            'release_date': '2019-01-01',
            'id': None
        }
        book = DbBook(None)
        book.set_values(**values)
        assert book.values() == expected, 'Expected: {}, but got {}'.format(expected, book.values())

    test_set_values_data = [
        (
            'When date is invalid',
            {
                'name': 'A Game of thrones',
                'isbn': '123-45678',
                'authors': ['John Doe'],
                'country': 'United States',
                'number_of_pages': 450,
                'publisher': 'ORielly',
                'release_date': 'Some date in 2019'
            },
            ''
        ),
        (
            'When name and isbn are empty',
            {
                'name': '',
                'isbn': '',
                'authors': ['John Doe'],
                'country': 'United States',
                'number_of_pages': 450,
                'publisher': 'ORielly',
                'release_date': 'Some date in 2019'
            },
            ''
        )
    ]
    @pytest.mark.parametrize('title, values, expected', test_set_values_data)
    def test_set_values_for_invalid_data(self, title, values, expected):
        with pytest.raises(BookError) as err:
            book = DbBook(None)
            book.set_values(**values)
