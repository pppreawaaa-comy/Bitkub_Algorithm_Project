if __package__:
    from .data import SUBJECT_CODES
else:
    from data import SUBJECT_CODES


def lookup_subject(subject):
    """Return the classification code for a subject, or None if unknown."""
    return SUBJECT_CODES.get(subject)


def add_book(books, title, subject):
    """Add a book with the next available ID when its details are valid."""
    title, subject = title.strip(), subject.strip()
    if not title or not subject:
        return False, "Please enter a book name and choose a subject."

    class_no = lookup_subject(subject)
    if class_no is None:
        return False, "Subject is not in the predefined dictionary."

    used_ids = {book["id"] for book in books}
    next_number = max(
        (
            int(book_id[1:])
            for book_id in used_ids
            if book_id.startswith("B") and book_id[1:].isdigit()
        ),
        default=0,
    ) + 1
    book_id = f"B{next_number:03d}"
    while book_id in used_ids:
        next_number += 1
        book_id = f"B{next_number:03d}"

    books.append(
        {
            "id": book_id,
            "title": title,
            "subject": subject,
            "class_no": class_no,
        }
    )
    return True, "Book added successfully."
