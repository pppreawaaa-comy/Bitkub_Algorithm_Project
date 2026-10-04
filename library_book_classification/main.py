import sys

if __package__:
    from .algorithms import insertion_sort, linear_search
    from .classification import add_book
    from .data import books
    from .tests import run_all_tests
else:
    from algorithms import insertion_sort, linear_search
    from classification import add_book
    from data import books
    from tests import run_all_tests


def display_books(books):
    print("Book ID | Title | Subject | Class No.")
    for book in books:
        print(
            f'{book["id"]} | {book["title"]} | {book["subject"]} | '
            f'{book["class_no"]}'
        )


def display_search_results(results):
    if not results:
        print("No books found")
        return
    display_books(results)


def show_menu():
    print("===== Library Book Classification System =====")
    print("1. Display all books")
    print("2. Add a book")
    print("3. Sort books by class number")
    print("4. Search books by class number")
    print("5. Run tests")
    print("6. Exit")


def console_main():
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_books(books)
        elif choice == "2":
            book_id = input("Enter Book ID: ").strip()
            title = input("Enter title: ").strip()
            subject = input("Enter subject: ").strip()
            _, message = add_book(books, book_id, title, subject)
            print(message)
        elif choice == "3":
            insertion_sort(books)
            display_books(books)
        elif choice == "4":
            class_no = input("Enter classification number: ").strip()
            display_search_results(linear_search(books, class_no))
        elif choice == "5":
            run_all_tests()
        elif choice == "6":
            print("Exiting the Library Book Classification System.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")


def main():
    if "--cli" in sys.argv[1:]:
        console_main()
        return

    if __package__:
        from .gui import launch_gui
    else:
        from gui import launch_gui
    launch_gui()


if __name__ == "__main__":
    main()
