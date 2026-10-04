from decimal import Decimal

if __package__:
    from .algorithms import insertion_sort, linear_search
    from .classification import add_book
    from .data import books as original_books
else:
    from algorithms import insertion_sort, linear_search
    from classification import add_book
    from data import books as original_books


def _copy_books(records):
    return [book.copy() for book in records]


def _is_ascending(records):
    for index in range(1, len(records)):
        if Decimal(records[index - 1]["class_no"]) > Decimal(records[index]["class_no"]):
            return False
    return True


def test_mixed_order():
    test_books = _copy_books(original_books)

    matches = linear_search(test_books, "530")
    assert [book["id"] for book in matches] == ["B001", "B012"]

    success, message = add_book(
        test_books, "B013", "Environmental Studies", "Natural resources"
    )
    assert success, message
    insertion_sort(test_books)

    assert len(test_books) == 13
    assert _is_ascending(test_books)
    assert [book["id"] for book in test_books if book["class_no"] == "333.7"] == [
        "B011",
        "B013",
    ]
    return True


def test_already_sorted():
    test_books = _copy_books(original_books)
    insertion_sort(test_books)
    sorted_books = _copy_books(test_books)

    insertion_sort(test_books)

    assert test_books == sorted_books
    physics_ids = [
        book["id"] for book in test_books if book["class_no"] == "530"
    ]
    assert physics_ids == ["B001", "B012"]
    return True


def test_reverse_order():
    test_books = _copy_books(original_books)
    insertion_sort(test_books)
    test_books.reverse()
    reversed_physics_ids = [
        book["id"] for book in test_books if book["class_no"] == "530"
    ]

    insertion_sort(test_books)

    assert _is_ascending(test_books)
    assert [book["id"] for book in test_books if book["class_no"] == "530"] == reversed_physics_ids
    return True


def test_edge_cases():
    test_books = [
        {"id": "E001", "title": "Programming", "subject": "Programming", "class_no": "005"},
        {"id": "E002", "title": "Physics One", "subject": "Physics", "class_no": "530"},
        {"id": "E003", "title": "Physics Two", "subject": "Physics", "class_no": "530"},
        {
            "id": "E004",
            "title": "Natural Resources",
            "subject": "Natural resources",
            "class_no": "333.7",
        },
        {
            "id": "E005",
            "title": "More Resources",
            "subject": "Natural resources",
            "class_no": "333.75",
        },
    ]

    insertion_sort(test_books)

    assert [book["class_no"] for book in test_books] == [
        "005",
        "333.7",
        "333.75",
        "530",
        "530",
    ]
    assert test_books[0]["class_no"] == "005"
    assert [book["id"] for book in test_books if book["class_no"] == "530"] == [
        "E002",
        "E003",
    ]
    assert linear_search(test_books, "999") == []
    return True


def run_all_tests():
    tests = [
        ("Mixed Order", test_mixed_order),
        ("Already Sorted", test_already_sorted),
        ("Reverse Order", test_reverse_order),
        ("Edge Cases", test_edge_cases),
    ]
    for test_name, test_function in tests:
        test_function()
        print(f"{test_name}: PASS")
    print("All tests passed.")
    return True
