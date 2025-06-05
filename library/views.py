from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .firebase_service import FirebaseService
from .forms import BookForm, SearchForm
import json
import logging

# Get logger for this module
logger = logging.getLogger('library')

def home(request):
    """
    Home page view that displays all books and handles search functionality.
    This serves as the main dashboard for the Library Management System.
    """
    try:
        firebase_service = FirebaseService()
        search_form = SearchForm()
        books = []
        search_performed = False
        
        # Handle search functionality
        if request.method == 'GET' and request.GET.get('search_query'):
            search_form = SearchForm(request.GET)
            if search_form.is_valid():
                search_type = search_form.cleaned_data.get('search_type')
                search_query = search_form.cleaned_data.get('search_query')
                
                # Perform search based on type
                all_books = firebase_service.get_all_books()
                books = []
                search_performed = True
                
                for book in all_books:
                    if search_type == 'title' and search_query.lower() in book.get('book_title', '').lower():
                        books.append(book)
                    elif search_type == 'author' and search_query.lower() in book.get('author_name', '').lower():
                        books.append(book)
                    elif search_type == 'genre' and search_query.lower() in book.get('genre', '').lower():
                        books.append(book)
                    elif search_type == 'id' and str(search_query) == str(book.get('id', '')):
                        books.append(book)
        else:
            # Display all books if no search is performed
            books = firebase_service.get_all_books()
        
        # Sort books by ID for consistent display
        books.sort(key=lambda x: x.get('id', 0))
        
        context = {
            'books': books,
            'search_form': search_form,
            'search_performed': search_performed,
            'total_books': len(books)
        }
        return render(request, 'library/home.html', context)
    
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        messages.error(request, 'An error occurred while loading the library. Please try again.')
        return render(request, 'library/home.html', {
            'books': [],
            'search_form': SearchForm(),
            'search_performed': False,
            'total_books': 0
        })


def add_book(request):
    """
    View to handle adding new books to the Firebase database.
    Implements Create operation of CRUD.
    """
    firebase_service = FirebaseService()
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # Check if book ID already exists
            existing_books = firebase_service.get_all_books()
            book_id = form.cleaned_data['id']
            
            # Verify ID uniqueness
            id_exists = any(book.get('id') == book_id for book in existing_books)
            if id_exists:
                messages.error(request, f'Book ID {book_id} already exists. Please use a different ID.')
                return render(request, 'library/add_book.html', {'form': form})
            
            # Create book data dictionary
            book_data = {
                'id': form.cleaned_data['id'],
                'book_title': form.cleaned_data['book_title'],
                'author_name': form.cleaned_data['author_name'],
                'genre': form.cleaned_data['genre'],
            }
            
            # Save to Firebase
            doc_id = firebase_service.create_book(book_data)
            if doc_id:
                messages.success(request, f'Book "{book_data["book_title"]}" has been successfully added to the library!')
                return redirect('home')
            else:
                messages.error(request, 'An error occurred while adding the book. Please try again.')
    else:
        form = BookForm()
    
    return render(request, 'library/add_book.html', {'form': form})


def edit_book(request, doc_id):
    """
    View to handle editing existing books in the Firebase database.
    Implements Update operation of CRUD.
    """
    firebase_service = FirebaseService()
    
    # Get the existing book data
    book = firebase_service.get_book_by_id(doc_id)
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            # Check if the new ID conflicts with other books (excluding current book)
            existing_books = firebase_service.get_all_books()
            new_book_id = form.cleaned_data['id']
            
            # Check for ID conflicts with other books
            id_conflict = any(
                existing_book.get('id') == new_book_id and existing_book.get('doc_id') != doc_id 
                for existing_book in existing_books
            )
            
            if id_conflict:
                messages.error(request, f'Book ID {new_book_id} is already used by another book. Please use a different ID.')
                return render(request, 'library/edit_book.html', {'form': form, 'book': book})
            
            # Prepare updated book data
            updated_data = {
                'id': form.cleaned_data['id'],
                'book_title': form.cleaned_data['book_title'],
                'author_name': form.cleaned_data['author_name'],
                'genre': form.cleaned_data['genre'],
            }
            
            # Update in Firebase
            if firebase_service.update_book(doc_id, updated_data):
                messages.success(request, f'Book "{updated_data["book_title"]}" has been successfully updated!')
                return redirect('home')
            else:
                messages.error(request, 'An error occurred while updating the book. Please try again.')
    else:
        # Pre-populate form with existing data
        initial_data = {
            'id': book.get('id'),
            'book_title': book.get('book_title'),
            'author_name': book.get('author_name'),
            'genre': book.get('genre'),
        }
        form = BookForm(initial=initial_data)
    
    return render(request, 'library/edit_book.html', {'form': form, 'book': book})


def delete_book(request, doc_id):
    """
    View to handle deleting books from the Firebase database.
    Implements Delete operation of CRUD.
    """
    firebase_service = FirebaseService()
    
    # Get the book to be deleted
    book = firebase_service.get_book_by_id(doc_id)
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('home')
    
    if request.method == 'POST':
        # Confirm deletion
        if firebase_service.delete_book(doc_id):
            messages.success(request, f'Book "{book.get("book_title")}" has been successfully deleted from the library.')
        else:
            messages.error(request, 'An error occurred while deleting the book. Please try again.')
        return redirect('home')
    
    return render(request, 'library/delete_book.html', {'book': book})


def view_book(request, doc_id):
    """
    View to display detailed information about a specific book.
    Implements Read operation of CRUD.
    """
    firebase_service = FirebaseService()
    
    # Get the book details
    book = firebase_service.get_book_by_id(doc_id)
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('home')
    
    return render(request, 'library/view_book.html', {'book': book})


def books_by_genre(request, genre):
    """
    View to display books filtered by a specific genre.
    """
    firebase_service = FirebaseService()
    books = firebase_service.get_books_by_genre(genre)
    
    # Sort books by ID
    books.sort(key=lambda x: x.get('id', 0))
    
    context = {
        'books': books,
        'genre': genre,
        'total_books': len(books)
    }
    return render(request, 'library/books_by_genre.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def api_books(request):
    """
    API endpoint to get all books in JSON format for testing.
    This endpoint can be used for API testing and integration.
    """
    firebase_service = FirebaseService()
    books = firebase_service.get_all_books()
    
    # Sort books by ID
    books.sort(key=lambda x: x.get('id', 0))
    
    return JsonResponse({
        'status': 'success',
        'total_books': len(books),
        'books': books
    })


def statistics(request):
    """
    View to display library statistics and analytics.
    """
    firebase_service = FirebaseService()
    all_books = firebase_service.get_all_books()
    
    # Calculate statistics
    total_books = len(all_books)
    
    # Count books by genre
    genre_counts = {}
    for book in all_books:
        genre = book.get('genre', 'Unknown')
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Get most popular genre
    most_popular_genre = max(genre_counts.items(), key=lambda x: x[1]) if genre_counts else ('None', 0)
    
    # Get authors count
    authors = set(book.get('author_name', '').strip() for book in all_books if book.get('author_name'))
    total_authors = len(authors)
    
    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'genre_counts': genre_counts,
        'most_popular_genre': most_popular_genre,
        'all_books': all_books[:5]  # Show latest 5 books for preview
    }
    
    return render(request, 'library/statistics.html', context)
