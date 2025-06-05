from django import forms

class BookForm(forms.Form):
    """
    Form for creating and editing book records in the Library Management System.
    This form handles all the required fields as specified in the assignment.
    """
    
    # Available genres for the dropdown selection
    GENRE_CHOICES = [
        ('', 'Select a Genre'),
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('Science Fiction', 'Science Fiction'),
        ('Fantasy', 'Fantasy'),
        ('Thriller', 'Thriller'),
        ('Horror', 'Horror'),
        ('Biography', 'Biography'),
        ('History', 'History'),
        ('Self-Help', 'Self-Help'),
        ('Business', 'Business'),
        ('Technology', 'Technology'),
        ('Travel', 'Travel'),
        ('Health', 'Health'),
        ('Cooking', 'Cooking'),
        ('Art', 'Art'),
        ('Poetry', 'Poetry'),
        ('Children', 'Children'),
        ('Young Adult', 'Young Adult'),
    ]
    
    # ID field - accepts numbers only as per requirements
    id = forms.IntegerField(
        label='Book ID',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Book ID (numbers only)',
            'min': '1',
            'step': '1'
        }),
        help_text='Enter a unique numeric identifier for the book'
    )
    
    # Book title field - user input
    book_title = forms.CharField(
        label='Book Title',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter book title',
            'autocomplete': 'off'
        }),
        help_text='Enter the complete title of the book'
    )
    
    # Author name field - user input
    author_name = forms.CharField(
        label='Author Name',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter author name',
            'autocomplete': 'off'
        }),
        help_text='Enter the full name of the book author'
    )
    
    # Genre field - dropdown as per UI requirements
    genre = forms.ChoiceField(
        label='Genre',
        choices=GENRE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        help_text='Select the book genre from the dropdown'
    )
    
    def clean_id(self):
        """
        Custom validation for the ID field to ensure it's a positive integer.
        """
        book_id = self.cleaned_data.get('id')
        if book_id and book_id <= 0:
            raise forms.ValidationError('Book ID must be a positive number.')
        return book_id
    
    def clean_book_title(self):
        """
        Custom validation for the book title to ensure it's not empty and properly formatted.
        """
        title = self.cleaned_data.get('book_title')
        if title:
            title = title.strip()
            if len(title) < 2:
                raise forms.ValidationError('Book title must be at least 2 characters long.')
            if len(title) > 200:
                raise forms.ValidationError('Book title cannot exceed 200 characters.')
            # Check for potentially harmful characters
            if any(char in title for char in ['<', '>', '{', '}', '[', ']']):
                raise forms.ValidationError('Book title contains invalid characters.')
        return title
    
    def clean_author_name(self):
        """
        Custom validation for the author name to ensure proper formatting.
        """
        author = self.cleaned_data.get('author_name')
        if author:
            author = author.strip()
            if len(author) < 2:
                raise forms.ValidationError('Author name must be at least 2 characters long.')
            if len(author) > 100:
                raise forms.ValidationError('Author name cannot exceed 100 characters.')
            # Check if the name contains at least one letter
            if not any(char.isalpha() for char in author):
                raise forms.ValidationError('Author name must contain at least one letter.')
            # Check for potentially harmful characters
            if any(char in author for char in ['<', '>', '{', '}', '[', ']']):
                raise forms.ValidationError('Author name contains invalid characters.')
        return author
    
    def clean_genre(self):
        """
        Custom validation for genre selection.
        """
        genre = self.cleaned_data.get('genre')
        if not genre:
            raise forms.ValidationError('Please select a genre.')
        
        # Validate against allowed choices
        valid_genres = [choice[0] for choice in self.GENRE_CHOICES if choice[0]]
        if genre not in valid_genres:
            raise forms.ValidationError('Please select a valid genre.')
        
        return genre


class SearchForm(forms.Form):
    """
    Form for searching books by different criteria.
    """
    
    SEARCH_TYPE_CHOICES = [
        ('', 'Select Search Type'),
        ('title', 'Search by Title'),
        ('author', 'Search by Author'),
        ('genre', 'Search by Genre'),
        ('id', 'Search by ID'),
    ]
    
    search_type = forms.ChoiceField(
        label='Search Type',
        choices=SEARCH_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=False
    )
    
    search_query = forms.CharField(
        label='Search Query',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter search term...',
            'autocomplete': 'off'
        }),
        required=False
    ) 