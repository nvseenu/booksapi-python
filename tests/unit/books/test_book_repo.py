from books import BookRepo, BookError

import pytest


class TestBookRepo:

    test_data = [
        (
         {},
         'SELECT id, name, isbn, authors, country, number_of_pages, publisher, release_date FROM books'
         ),
        (
            {
            'name': 'A Game of thrones',
            'country': 'unites states',
            'release_date': 2019
            },

            "SELECT id, name, isbn, authors, country, number_of_pages, publisher, release_date FROM books WHERE country=%s and name=%s and date_part('year', release_date)=%s"
        ),
    ]

    @pytest.mark.parametrize('filters, expected', test_data)
    def test_get_all_books_query(self, filters, expected):
        book_repo = BookRepo(None)
        query = book_repo._get_all_books_query(filters)
        assert query == expected

    
    unsupported_filters_data = [
       { 'number_of_pages': 450},
       { 'authors': 'George'},
       { 'isbn': '123-12345'}
    ]
    @pytest.mark.parametrize('filters', unsupported_filters_data)
    def test_get_books_for_unsupported_filter(self, filters):
        with pytest.raises(BookError) as err:
            book_repo = BookRepo(None)
            book_repo.get_books(**filters)