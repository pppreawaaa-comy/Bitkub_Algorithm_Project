try:
    from .data import SUBJECT_CODES
except ImportError:
    from data import SUBJECT_CODES


def lookup_subject(subject):
    """Return the classification code for a known subject."""
    if subject in SUBJECT_CODES:
        return SUBJECT_CODES[subject]
    return None


def add_book(books, book_id, title, subject):
    """Add a new book after validating the book ID and subject."""
    for book in books:
        if book["id"] == book_id:
            return {
                "success": False,
                "message": f"Book ID '{book_id}' already exists."
            }

    class_no = lookup_subject(subject)
    if class_no is None:
        return {
            "success": False,
            "message": f"Subject '{subject}' is not in the predefined dictionary."
        }

    new_book = {
        "id": book_id,
        "title": title,
        "subject": subject,
        "class_no": class_no
    }
    books.append(new_book)
    return {
        "success": True,
        "book": new_book,
        "message": f"Book '{title}' added successfully."
    }
