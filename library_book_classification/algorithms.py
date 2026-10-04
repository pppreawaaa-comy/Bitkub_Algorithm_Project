from decimal import Decimal


def insertion_sort(books):
    """Sort books in place by class number using stable Insertion Sort."""
    for index in range(1, len(books)):
        current_book = books[index]
        current_class_no = Decimal(current_book["class_no"])
        position = index - 1

        # Compare and shift larger class numbers one position to the right.
        while position >= 0 and Decimal(books[position]["class_no"]) > current_class_no:
            books[position + 1] = books[position]
            position -= 1

        # Insert the complete book record into its sorted position.
        books[position + 1] = current_book

    return books


def linear_search(books, class_no):
    """Return every book whose class number exactly matches class_no."""
    matches = []
    for book in books:
        if book["class_no"] == class_no:
            matches.append(book)
    return matches
