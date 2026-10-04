"""Launch the desktop catalog when available, otherwise use the browser app."""

from library_book_classification.web_app import restart_existing_app, serve


def main():
    restart_existing_app()
    try:
        from library_book_classification.gui import desktop_available, launch_gui
    except ModuleNotFoundError as error:
        if error.name not in {"tkinter", "_tkinter"}:
            raise
        desktop_ready = False
    else:
        desktop_ready = desktop_available()

    if desktop_ready:
        print("Opening Li-BIT-ry desktop app.")
        launch_gui()
    else:
        print("No desktop display detected; opening Li-BIT-ry in your browser.")
        serve()


if __name__ == "__main__":
    main()
