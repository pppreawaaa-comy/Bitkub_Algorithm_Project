# Bitkub Algorithm Project

## Library book catalog

The project includes a browser-based catalog for adding and finding books. It
uses only the Python standard library and does not require third-party
packages or a desktop display.

Run `run_app.py` from the project folder. It opens the desktop app when a
desktop display is available and otherwise starts the browser app. When using
the browser app, open the displayed URL. Running the launcher again safely
stops and replaces a previous Li-BIT-ry web server. In a remote VS Code
workspace, allow port 8000 to be forwarded if prompted.

```bash
python run_app.py
```

Search the catalog by book ID, title, subject, or classification number. To add
a book, enter its name and choose a subject. The book ID and classification
number are assigned automatically. The catalog is preloaded with the original
books and sample records. New books are kept in memory and are reset when the
application closes.

Use the **Run tests** button at the bottom of the right-hand panel to run the
project checks and follow their output in the test log.

The original console menu and Tkinter desktop interface are also available:

```bash
python -m library_book_classification.main --cli
python -m library_book_classification.main
```

Run the algorithm tests with:

```bash
python -c "from library_book_classification.tests import run_all_tests; run_all_tests()"
```
