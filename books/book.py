from abc import ABC, abstractmethod
import psycopg2
import json
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


class BookRepo:

    def __init__(self, cpool):
        self._cpool = cpool

    supported_filters = ['name', 'country', 'publisher', 'release_date']

    def get_books(self, **filters):
        """
        Get books matching with given filters
        """

        ufilters = self.unsupported_filters(filters)
        if len(ufilters) > 0:
            raise BookError('FILTER_ERROR', 'Given filters: {} are not supported'.format(ufilters))

        try:
            with ConnectionPoolContext(self._cpool) as conn:
                query = self._get_all_books_query(filters)
                logger.debug('Executing query: %s', query)
                cur = conn.cursor()
                params = tuple(filters[key] for key in sorted(filters.keys()))
                cur.execute(query, params)
                books = [DbBook._from_db_row(self._cpool, row) for row in cur.fetchall()]
                cur.close()
                return books
        except psycopg2.Error as err:
            raise BookError(
                'GET_BOOKS_ERROR',
                'Unable to fetch books with filters: {} due to error: {}'.format(filters, err.pgerror),
                err)

    def _get_all_books_query(self, filters):
        query = 'SELECT id, name, isbn, authors, country, number_of_pages, publisher, release_date FROM books'
        if not filters:
            return query

        query += ' WHERE '
        values = ['{}=%s'.format(key) for key in sorted(filters.keys()) if key is not 'release_date']

        if 'release_date' in filters:
            values.append("date_part('year', release_date)=%s")

        return query + ' and '.join(values)

    def unsupported_filters(self, filters):
        if not filters:
            return []

        return [key for key in filters.keys() if key not in self.supported_filters]

    def get_book(self, id):
        """
        Get a book having given id
        """
        try:
            with ConnectionPoolContext(self._cpool) as conn:
                cur = conn.cursor()
                query = 'SELECT id, name, isbn, authors, country, number_of_pages, publisher, release_date FROM books WHERE id = %s'
                logger.debug('Executing query: %s', query)
                cur.execute(query, (id,))
                row = cur.fetchone()
                if not row:
                    return None

                book = DbBook._from_db_row(self._cpool, row)
                return book
        except psycopg2.Error as err:
            raise BookError(
                'GET_BOOK_ERROR',
                'Unable to fetch a book due to error: {} {}'.format(err.pgerror, err.pgcode),
                err)

    def get_empty_book(self):
        return DbBook(self._cpool)


class DbBook:
    """
    A book represents a row of 'books' table
    """

    def __init__(self, cpool, id=None):
        self._id = id
        self._cpool = cpool
        self._name = ''
        self._isbn = ''
        self._authors = []
        self._country = ''
        self._number_of_pages = 0
        self._publisher = ''
        self._release_date = None

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is None or len(name.strip()) == 0:
            raise BookError('INVALID_PROPERTY', 'name is blank')
        self._name = name

    @property
    def isbn(self):
        return self._isbn

    @isbn.setter
    def isbn(self, isbn):
        if isbn is None or len(isbn.strip()) == 0:
            raise BookError('INVALID_PROPERTY', 'isbn is blank')
        self._isbn = isbn

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, authors):
        self._authors = authors

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, country):
        self._country = country

    @property
    def number_of_pages(self):
        return self._number_of_pages

    @number_of_pages.setter
    def number_of_pages(self, number_of_pages):
        self._number_of_pages = number_of_pages

    @property
    def publisher(self):
        return self._publisher

    @publisher.setter
    def publisher(self, publisher):
        self._publisher = publisher

    @property
    def release_date(self):
        return self._release_date

    @release_date.setter
    def release_date(self, release_date):
        try:
            datetime.strptime(release_date, '%Y-%m-%d')
        except ValueError as err:
            raise BookError('INVALID_PROPERTY', 'release_date is not a date', err)

        self._release_date = release_date

    def set_values(self, **values):
        for key, value in values.items():
            if key == 'id':
                continue

            if hasattr(self, key):
                setattr(self, key, value)

    def save(self):
        try:
            with ConnectionPoolContext(self._cpool) as conn:
                cur = conn.cursor()
                if self._id:
                    self._update(cur)
                else:
                    self._create(cur)
                conn.commit()
        except psycopg2.Error as err:
            raise BookError(
                'SAVE_BOOK_ERROR',
                'Unable to save a book due to error: {} {}'.format(err.pgerror, err.pgcode),
                err)

    def delete(self):
        """
        Delete itself
        """
        try:
            with ConnectionPoolContext(self._cpool) as conn:
                cur = conn.cursor()
                cur.execute('DELETE FROM books WHERE id = %s', (self._id,))
                conn.commit()
                cur.close()
        except psycopg2.Error as err:
            raise BookError(
                'DELETE_BOOK_ERROR',
                'Unable to delete a book due to error: {} {}'.format(err.pgerror, err.pgcode),
                err)

    def _create(self, cur):
        authors = json.dumps(self._authors) if self._authors else None
        cur.execute(
            'INSERT INTO books (name, isbn, authors, country,number_of_pages, publisher, release_date) VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING id',
            (self._name,
             self._isbn,
             authors,
             self._country,
             self._number_of_pages,
             self._publisher,
             self._release_date))
        self._id = cur.fetchone()[0]
        logger.debug('New book record has been created with id: %d', self._id)

    def _update(self, cur):
        cur.execute("""UPDATE books
                       SET name = %s, isbn = %s, authors = %s, country = %s,
                       number_of_pages=%s, publisher=%s, release_date=%s
                       WHERE id = %s""",
                    (self._name, self._isbn, json.dumps(self._authors),
                     self._country, self._number_of_pages, self._publisher, self._release_date,
                     self._id))
        logger.debug('book record has been updated with id:%d', self._id)

    @staticmethod
    def _from_db_row(cpool, row):
        book = DbBook(cpool, row[0])
        book.name = row[1]
        book.isbn = row[2]
        book.authors = json.loads(row[3])
        book.country = row[4]
        book.number_of_pages = row[5]
        book.publisher = row[6]
        book.release_date = datetime.strftime(row[7], '%Y-%m-%d')
        return book

    def values(self):
        return {
            'id': self._id,
            'name': self._name,
            'isbn': self._isbn,
            'authors': self._authors,
            'country': self._country,
            'number_of_pages': self._number_of_pages,
            'publisher': self._publisher,
            'release_date': self._release_date
        }

    def __repr__(self):
        return str(self.values())


class ConnectionPoolContext:

    def __init__(self, cpool):
        self._cpool = cpool
        self._conn = None

    def __enter__(self):
        self._conn = self._cpool.getconn()
        return self._conn

    def __exit__(self, *args):
        self._cpool.putconn(self._conn)


class BookError(Exception):

    def __init__(self, name, message='', error=None):
        super().__init__()
        self._name = name
        self._message = message
        self._error = error

    def error(self):
        return self._error

    def name(self):
        return name

    def message(self):
        return self._message
