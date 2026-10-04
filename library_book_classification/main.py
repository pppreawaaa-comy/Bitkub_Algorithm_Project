try:
    from .algorithms import insertion_sort, linear_search
    from .classification import add_book
    from .data import books
except ImportError:
    from algorithms import insertion_sort, linear_search
    from classification import add_book
    from data import books


def display_books(books):
    print("Book ID | Title | Subject | Class No.")
    for book in books:
        print(f"{book['id']} | {book['title']} | {book['subject']} | {book['class_no']}")


def display_search_results(results):
    if not results:
        print("No books found")
        return

    print("Book ID | Title | Subject | Class No.")
    for book in results:
        print(f"{book['id']} | {book['title']} | {book['subject']} | {book['class_no']}")


def show_menu():
    print("===== Library Book Classification System =====")
    print("1. Display all books")
    print("2. Add a book")
    print("3. Sort books by class number")
    print("4. Search books by class number")
    print("5. Run tests")
    print("6. Exit")


def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_books(books)
        elif choice == "2":
            book_id = input("Book ID: ").strip()
            title = input("Title: ").strip()
            subject = input("Subject: ").strip()
            result = add_book(books, book_id, title, subject)
            if result["success"]:
                print("Book added successfully.")
            else:
                print(result["message"])
        elif choice == "3":
            insertion_sort(books)
            display_books(books)
        elif choice == "4":
            class_no = input("Enter class number: ").strip()
            results = linear_search(books, class_no)
            display_search_results(results)
        elif choice == "5":
            from tests import run_all_tests
            run_all_tests()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

        print()


if __name__ == "__main__":
    main()
