import logging
from flask import Blueprint, request, jsonify
from urllib.parse import unquote

from psycopg2 import pool
from .book import BookRepo
logger = logging.getLogger(__name__)


def createBlueprint(config):
    cpool = pool.ThreadedConnectionPool(**config['connection_pool'])
    if not cpool:
        raise ValueError('Unable to create a connection pool.')

    book_repo = BookRepo(cpool)
    book_routes = BookRoutes(book_repo)

    blueprint = Blueprint('books_api', __name__)
    blueprint.add_url_rule('/books', view_func=book_routes.get_books, methods=['GET'])
    blueprint.add_url_rule('/books', view_func=book_routes.create_book, methods=['POST'])
    blueprint.add_url_rule('/books/<int:id>', view_func=book_routes.get_book, methods=['GET'])
    blueprint.add_url_rule('/books/<int:id>', view_func=book_routes.update_book, methods=['PATCH'])
    blueprint.add_url_rule('/books/<int:id>/update', view_func=book_routes.update_book, methods=['POST'])
    blueprint.add_url_rule('/books/<int:id>', view_func=book_routes.delete_book, methods=['DELETE'])
    blueprint.add_url_rule('/books/<int:id>/delete', view_func=book_routes.delete_book, methods=['POST'])
    return blueprint


class BookRoutes:

    def __init__(self, book_repo):
        self._book_repo = book_repo

    def create_book(self):
        """
        Creates a new book
        """
        book_info = request.get_json()
        if not book_info:
            raise ValueError('No json found in the request')

        book = self._book_repo.get_empty_book()
        book.set_values(**book_info)
        book.save()
        logger.info('Created a new book with id: %d', book.id)
        return {
            'status_code': 201,
            'status': 'success',
            'data': [{'book': book.values()}]
        }

    def get_book(self, id):
        book = self._book_repo.get_book(id)
        logger.info('Found a book with id: %s', id)
        return {
            'status_code': 200,
            'status': 'success',
            'data': book.values()
        }

    def get_books(self):
        filters = request.get_json()
        if not filters:
            filters = {}
        logger.debug('Get all books matching with filters: %s', filters)
        books = self._book_repo.get_books(**filters)
        logger.info('Found %d books for given filters: %s', len(books), filters)
        return {
            'status_code': 200,
            'status': 'success',
            'data': [book.values() for book in books]
        }

    def update_book(self, id):
        book_info = request.get_json()
        if not book_info:
            raise ValueError('No json found in the request')
        book = self._book_repo.get_book(id)
        book.set_values(**book_info)
        book.save()
        logger.info('Updated a book with id: %s', id)
        return {
            'status_code': 200,
            'status': 'success',
            'message': 'The book {} was updated successfully'.format(book.name),
            'data': book.values()
        }

    def delete_book(self, id):
        book = self._book_repo.get_book(id)
        book.delete()
        logger.info('Found a book with id: %s', id)
        return {
            'status_code': 204,
            'status': 'success',
            'message': 'The book {} was updated successfully'.format(book.name),
            'data': []
        }
