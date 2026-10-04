# Bitkub Algorithm Project

## Library book catalog

The project includes a browser-based catalog for adding and finding books. It
uses only the Python standard library and does not require third-party
packages or a desktop display.

Run `run_app.py` from the project folder. The app starts a local web server;
open the displayed URL in your browser. Running the launcher again safely
stops and replaces a previous Li-BIT-ry instance. In a remote VS Code
workspace, allow port 8000 to be forwarded if prompted.

```bash
python run_app.py
```

Search the catalog by book ID, title, subject, or classification number. To add
a book, enter its ID and title and choose a subject; the classification number
is assigned automatically. The catalog is preloaded with the original books
and sample records. New books are kept in memory and are reset when the
application closes.

The original console menu and Tkinter desktop interface are also available:

```bash
python -m library_book_classification.main --cli
python -m library_book_classification.main
```

Run the algorithm tests with:

```bash
python -c "from library_book_classification.tests import run_all_tests; run_all_tests()"
```
