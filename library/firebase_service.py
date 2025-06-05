import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import json
import logging

# Get logger for this module
logger = logging.getLogger('library')

class FirebaseService:
    """
    Firebase service class to handle all database operations for the Library Management System.
    This service provides CRUD operations for managing books in Firebase Firestore.
    """
    
    def __init__(self):
        # Initialize Firebase connection only once
        if not firebase_admin._apps:
            try:
                # Load Firebase credentials from the JSON file
                cred = credentials.Certificate(settings.FIREBASE_CONFIG)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {str(e)}")
                raise
        
        # Get Firestore database instance
        self.db = firestore.client()
        self.collection_name = 'books'  # Our main collection for storing books
    
    def create_book(self, book_data):
        """
        Create a new book record in Firebase Firestore.
        
        Args:
            book_data (dict): Dictionary containing book information
            
        Returns:
            str: Document ID of the created book, or None if creation failed
        """
        try:
            # Add the book data to Firestore collection
            doc_ref = self.db.collection(self.collection_name).add(book_data)
            logger.info(f"Book created successfully: {book_data.get('book_title', 'Unknown')}")
            return doc_ref[1].id  # Return the document ID
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            return None
    
    def get_all_books(self):
        """
        Retrieve all books from the Firebase Firestore collection.
        
        Returns:
            list: List of dictionaries containing book data with document IDs
        """
        try:
            books = []
            # Get all documents from the books collection
            docs = self.db.collection(self.collection_name).stream()
            
            for doc in docs:
                book_data = doc.to_dict()
                book_data['doc_id'] = doc.id  # Add document ID to the data
                books.append(book_data)
            
            logger.info(f"Retrieved {len(books)} books from database")
            return books
        except Exception as e:
            logger.error(f"Error retrieving books: {str(e)}")
            return []
    
    def get_book_by_id(self, doc_id):
        """
        Retrieve a specific book by its document ID.
        
        Args:
            doc_id (str): Firebase document ID
            
        Returns:
            dict: Book data dictionary or None if not found
        """
        try:
            doc = self.db.collection(self.collection_name).document(doc_id).get()
            if doc.exists:
                book_data = doc.to_dict()
                book_data['doc_id'] = doc.id
                logger.info(f"Book retrieved: {book_data.get('book_title', 'Unknown')}")
                return book_data
            logger.warning(f"Book not found with ID: {doc_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving book: {str(e)}")
            return None
    
    def update_book(self, doc_id, book_data):
        """
        Update an existing book record in Firebase Firestore.
        
        Args:
            doc_id (str): Firebase document ID of the book to update
            book_data (dict): Updated book information
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Update the document with new data
            self.db.collection(self.collection_name).document(doc_id).update(book_data)
            logger.info(f"Book updated successfully: {book_data.get('book_title', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error updating book: {str(e)}")
            return False
    
    def delete_book(self, doc_id):
        """
        Delete a book record from Firebase Firestore.
        
        Args:
            doc_id (str): Firebase document ID of the book to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Delete the document from Firestore
            self.db.collection(self.collection_name).document(doc_id).delete()
            logger.info(f"Book deleted successfully: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            return False
    
    def get_books_by_genre(self, genre):
        """
        Retrieve books filtered by genre.
        
        Args:
            genre (str): Genre to filter by
            
        Returns:
            list: List of books matching the specified genre
        """
        try:
            books = []
            # Query books by genre
            docs = self.db.collection(self.collection_name).where('genre', '==', genre).stream()
            
            for doc in docs:
                book_data = doc.to_dict()
                book_data['doc_id'] = doc.id
                books.append(book_data)
            
            logger.info(f"Retrieved {len(books)} books for genre: {genre}")
            return books
        except Exception as e:
            logger.error(f"Error retrieving books by genre: {str(e)}")
            return [] 