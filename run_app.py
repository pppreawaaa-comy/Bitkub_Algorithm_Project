"""Start the browser-based Li-BIT-ry book catalog."""

from library_book_classification.web_app import restart_existing_app, serve


if __name__ == "__main__":
    restart_existing_app()
    serve()
