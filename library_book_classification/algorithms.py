from decimal import Decimal


def insertion_sort(books):
    """Sort books by class number using stable insertion sort."""
    for i in range(1, len(books)):
        current_book = books[i]
        current_value = Decimal(current_book["class_no"])
        j = i - 1

        while j >= 0 and Decimal(books[j]["class_no"]) > current_value:
            books[j + 1] = books[j]
            j -= 1

        books[j + 1] = current_book

    return books


def linear_search(books, class_no):
    """Return all books whose class number matches the given class number."""
    matches = []
    target = str(class_no).strip()

    for book in books:
        if str(book["class_no"]) == target:
            matches.append(book)

    return matches
