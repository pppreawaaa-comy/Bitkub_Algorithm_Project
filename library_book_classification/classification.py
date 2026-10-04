if __package__:
    from .data import SUBJECT_CODES
else:
    from data import SUBJECT_CODES


def lookup_subject(subject):
    """Return the classification code for a subject, or None if unknown."""
    return SUBJECT_CODES.get(subject)


def add_book(books, book_id, title, subject):
    """Add a book when its ID and subject are valid."""
    for book in books:
        if book["id"] == book_id:
            return False, "Book ID already exists."

    class_no = lookup_subject(subject)
    if class_no is None:
        return False, "Subject is not in the predefined dictionary."

    books.append(
        {
            "id": book_id,
            "title": title,
            "subject": subject,
            "class_no": class_no,
        }
    )
    return True, "Book added successfully."
