from decimal import Decimal

try:
    from .algorithms import insertion_sort, linear_search
    from .classification import add_book, lookup_subject
    from .data import books as original_books
except ImportError:
    from algorithms import insertion_sort, linear_search
    from classification import add_book, lookup_subject
    from data import books as original_books


def _copy_books():
    return [book.copy() for book in original_books]


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}\nExpected: {expected}\nActual: {actual}")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def test_mixed_order():
    books = _copy_books()

    matches = linear_search(books, "530")
    assert_equal(len(matches), 2, "Search for 530 should return 2 books.")
    assert_equal([book["id"] for book in matches], ["B001", "B012"], "530 search should return B001 and B012 in original order.")

    result = add_book(books, "B013", "Environmental Studies", "Natural resources")
    assert_true(result["success"], "B013 should be added successfully.")
    assert_equal(len(books), 13, "After adding B013, there should be 13 books.")
    assert_equal(books[-1]["class_no"], "333.7", "B013 should receive class number 333.7.")

    insertion_sort(books)

    assert_true(
        all(Decimal(books[i]["class_no"]) <= Decimal(books[i + 1]["class_no"]) for i in range(len(books) - 1)),
        "Books should be in ascending class-number order after sorting."
    )

    b011_index = next(i for i, book in enumerate(books) if book["id"] == "B011")
    b013_index = next(i for i, book in enumerate(books) if book["id"] == "B013")
    assert_true(b011_index < b013_index, "B011 should remain before B013 because both have class 333.7.")

    assert_equal(
        [book["id"] for book in linear_search(books, "530")],
        ["B001", "B012"],
        "530 search should still return B001 and B012 after sorting."
    )


def test_already_sorted():
    books = [
        {"id": "B002", "title": "Python Programming", "subject": "Programming", "class_no": "005"},
        {"id": "B006", "title": "Introduction to AI", "subject": "Artificial intelligence", "class_no": "006"},
        {"id": "B004", "title": "Psychology Basics", "subject": "Psychology", "class_no": "150"},
        {"id": "B007", "title": "Economics Essentials", "subject": "Economics", "class_no": "330"},
        {"id": "B011", "title": "A Brighter Tomorrow", "subject": "Natural resources", "class_no": "333.7"},
        {"id": "B009", "title": "English Grammar", "subject": "English grammar", "class_no": "425"},
        {"id": "B008", "title": "Mathematics Basics", "subject": "Mathematics", "class_no": "510"},
        {"id": "B001", "title": "Physics Fundamentals", "subject": "Physics", "class_no": "530"},
        {"id": "B012", "title": "Physics Experiments", "subject": "Physics", "class_no": "530"},
        {"id": "B010", "title": "Chemistry Basics", "subject": "Chemistry", "class_no": "540"},
        {"id": "B005", "title": "Engineering Design", "subject": "Engineering", "class_no": "620"},
        {"id": "B003", "title": "Thai History", "subject": "Southeast Asian history", "class_no": "959"}
    ]

    original_order = [book["id"] for book in books]
    insertion_sort(books)
    assert_equal([book["id"] for book in books], original_order, "Already-sorted books should remain in the same order.")

    duplicate_books = [
        {"id": "D1", "title": "Physics A", "subject": "Physics", "class_no": "530"},
        {"id": "D2", "title": "Physics B", "subject": "Physics", "class_no": "530"},
        {"id": "D3", "title": "Chemistry", "subject": "Chemistry", "class_no": "540"}
    ]
    insertion_sort(duplicate_books)
    assert_equal([book["id"] for book in duplicate_books], ["D1", "D2", "D3"], "Duplicate class numbers should keep original order.")


def test_reverse_order():
    books = [
        {"id": "B003", "title": "Thai History", "subject": "Southeast Asian history", "class_no": "959"},
        {"id": "B005", "title": "Engineering Design", "subject": "Engineering", "class_no": "620"},
        {"id": "B010", "title": "Chemistry Basics", "subject": "Chemistry", "class_no": "540"},
        {"id": "B012", "title": "Physics Experiments", "subject": "Physics", "class_no": "530"},
        {"id": "B001", "title": "Physics Fundamentals", "subject": "Physics", "class_no": "530"},
        {"id": "B008", "title": "Mathematics Basics", "subject": "Mathematics", "class_no": "510"},
        {"id": "B009", "title": "English Grammar", "subject": "English grammar", "class_no": "425"},
        {"id": "B011", "title": "A Brighter Tomorrow", "subject": "Natural resources", "class_no": "333.7"},
        {"id": "B007", "title": "Economics Essentials", "subject": "Economics", "class_no": "330"},
        {"id": "B004", "title": "Psychology Basics", "subject": "Psychology", "class_no": "150"},
        {"id": "B006", "title": "Introduction to AI", "subject": "Artificial intelligence", "class_no": "006"},
        {"id": "B002", "title": "Python Programming", "subject": "Programming", "class_no": "005"}
    ]

    insertion_sort(books)

    assert_true(
        all(Decimal(books[i]["class_no"]) <= Decimal(books[i + 1]["class_no"]) for i in range(len(books) - 1)),
        "Reverse-order list should be sorted into ascending class-number order."
    )


def test_edge_cases():
    books = [
        {"id": "E1", "title": "Sample 1", "subject": "Programming", "class_no": "005"},
        {"id": "E2", "title": "Sample 2", "subject": "Physics", "class_no": "530"},
        {"id": "E3", "title": "Sample 3", "subject": "Physics", "class_no": "530"},
        {"id": "E4", "title": "Sample 4", "subject": "Natural resources", "class_no": "333.7"},
        {"id": "E5", "title": "Sample 5", "subject": "Mathematics", "class_no": "333.75"}
    ]

    insertion_sort(books)
    assert_equal([book["class_no"] for book in books], ["005", "333.7", "333.75", "530", "530"], "Leading zero and decimal values should be ordered correctly.")
    assert_equal(linear_search(books, "999"), [], "Search for a missing class returns an empty list.")
    assert_equal([book["id"] for book in linear_search(books, "530")], ["E2", "E3"], "Duplicate 530 values must remain in original order.")
    assert_equal(lookup_subject("Programming"), "005", "lookup_subject should return the correct code for a valid subject.")
    assert_equal(lookup_subject("Unknown subject"), None, "lookup_subject should return None for an invalid subject.")


def run_all_tests():
    test_mixed_order()
    test_already_sorted()
    test_reverse_order()
    test_edge_cases()
    print("All tests passed.")


if __name__ == "__main__":
    run_all_tests()
