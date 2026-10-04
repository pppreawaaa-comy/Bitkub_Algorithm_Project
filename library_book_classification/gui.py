from threading import Thread
import tkinter as tk
from tkinter import ttk

if __package__:
    from .algorithms import insertion_sort
    from .classification import add_book
    from .data import MOCK_BOOKS, SUBJECT_CODES, books as starter_books
    from .test_runner import run_test_process
else:
    from algorithms import insertion_sort
    from classification import add_book
    from data import MOCK_BOOKS, SUBJECT_CODES, books as starter_books
    from test_runner import run_test_process


def filter_books(records, query):
    """Return books containing the query in any visible catalog field."""
    query = query.strip().casefold()
    if not query:
        return list(records)

    return [
        book
        for book in records
        if any(
            query in str(book[field]).casefold()
            for field in ("id", "title", "subject", "class_no")
        )
    ]


class LibraryApp:
    BACKGROUND = "#f3f6fb"
    INK = "#172b4d"
    MUTED = "#62718a"
    ACCENT = "#3157d5"

    def __init__(self, root):
        self.root = root
        self.root.title("Li-BIT-ry | Library")
        self.root.geometry("1120x740")
        self.root.minsize(900, 620)
        self.root.configure(bg=self.BACKGROUND)
        self.catalog = [book.copy() for book in starter_books + MOCK_BOOKS]

        self._configure_style()
        self._build_layout()
        self._refresh_catalog()

    def _configure_style(self):
        style = ttk.Style(self.root)
        style.configure("TFrame", background=self.BACKGROUND)
        style.configure("Card.TFrame", background="#ffffff")
        style.configure(
            "Title.TLabel",
            background=self.BACKGROUND,
            foreground=self.INK,
            font=("TkDefaultFont", 23, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.BACKGROUND,
            foreground=self.MUTED,
            font=("TkDefaultFont", 10),
        )
        style.configure(
            "CardTitle.TLabel",
            background="#ffffff",
            foreground=self.INK,
            font=("TkDefaultFont", 12, "bold"),
        )
        style.configure(
            "Metric.TLabel",
            background="#ffffff",
            foreground=self.INK,
            font=("TkDefaultFont", 18, "bold"),
        )
        style.configure(
            "MetricCaption.TLabel",
            background="#ffffff",
            foreground=self.MUTED,
            font=("TkDefaultFont", 9),
        )
        style.configure(
            "Treeview",
            rowheight=34,
            font=("TkDefaultFont", 10),
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=self.INK,
        )
        style.configure(
            "Treeview.Heading",
            font=("TkDefaultFont", 9, "bold"),
            foreground=self.MUTED,
            padding=(8, 8),
        )
        style.map(
            "Treeview",
            background=[("selected", "#dce6ff")],
            foreground=[("selected", self.INK)],
        )
        style.configure("Accent.TButton", font=("TkDefaultFont", 10, "bold"))

    def _build_layout(self):
        page = ttk.Frame(self.root, padding=(28, 22))
        page.pack(fill="both", expand=True)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(3, weight=1)

        header = ttk.Frame(page)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ttk.Label(header, text="Li-BIT-ry", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="A calmer way to organize and discover your next read.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        metrics = ttk.Frame(page)
        metrics.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        for column in range(3):
            metrics.columnconfigure(column, weight=1, uniform="metric")
        self.total_metric = self._metric_card(metrics, 0, "BOOKS", "0")
        self.subject_metric = self._metric_card(metrics, 1, "SUBJECTS", "0")
        self.visible_metric = self._metric_card(metrics, 2, "SHOWING", "0")

        toolbar = ttk.Frame(page)
        toolbar.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        toolbar.columnconfigure(0, weight=1)
        search_box = ttk.Frame(toolbar, style="Card.TFrame", padding=(12, 8))
        search_box.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_box.columnconfigure(1, weight=1)
        ttk.Label(search_box, text="⌕", foreground=self.ACCENT).grid(
            row=0, column=0, padx=(0, 8)
        )
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("TkDefaultFont", 11),
        )
        search_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(
            toolbar,
            text="Sort by class no.",
            command=self._sort_catalog,
        ).grid(row=0, column=1, sticky="ns")

        content = ttk.Frame(page)
        content.grid(row=3, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, minsize=300)
        content.rowconfigure(0, weight=1)

        catalog_card = ttk.Frame(content, style="Card.TFrame", padding=16)
        catalog_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        catalog_card.columnconfigure(0, weight=1)
        catalog_card.rowconfigure(1, weight=1)
        catalog_heading = ttk.Frame(catalog_card, style="Card.TFrame")
        catalog_heading.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(
            catalog_heading, text="Book catalog", style="CardTitle.TLabel"
        ).pack(side="left")
        ttk.Label(
            catalog_heading,
            text="Search by book ID, title, subject or class number",
            foreground=self.MUTED,
            background="#ffffff",
            font=("TkDefaultFont", 9),
        ).pack(side="right")

        table_frame = ttk.Frame(catalog_card, style="Card.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        columns = ("id", "title", "subject", "class_no")
        self.table = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        for column, label, width in (
            ("id", "BOOK ID", 78),
            ("title", "TITLE", 230),
            ("subject", "SUBJECT", 165),
            ("class_no", "CLASS NO.", 90),
        ):
            self.table.heading(column, text=label)
            self.table.column(column, width=width, minwidth=60, anchor="w")
        self.table.column("class_no", anchor="center")
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.table.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.tag_configure("alternate", background="#f7f9fd")
        self.search_var.trace_add("write", lambda *_: self._refresh_catalog())
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            catalog_card,
            textvariable=self.status_var,
            foreground=self.MUTED,
            background="#ffffff",
            font=("TkDefaultFont", 9),
        ).grid(row=2, column=0, sticky="w", pady=(10, 0))

        form = ttk.Frame(content, style="Card.TFrame", padding=18)
        form.grid(row=0, column=1, sticky="nsew")
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Add a book", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            form,
            text="Add it to your catalog and get its class number automatically.",
            wraplength=255,
            justify="left",
            foreground=self.MUTED,
            background="#ffffff",
            font=("TkDefaultFont", 9),
        ).grid(row=1, column=0, sticky="w", pady=(6, 16))

        self.title_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.form_status_var = tk.StringVar(value=" ")
        fields = (
            ("Book name", self.title_var),
        )
        row = 2
        for label, variable in fields:
            ttk.Label(
                form,
                text=label,
                foreground=self.INK,
                background="#ffffff",
                font=("TkDefaultFont", 9, "bold"),
            ).grid(row=row, column=0, sticky="w", pady=(0, 5))
            row += 1
            field = ttk.Entry(form, textvariable=variable)
            field.grid(row=row, column=0, sticky="ew", ipady=5, pady=(0, 13))
            row += 1

        ttk.Label(
            form,
            text="Subject",
            foreground=self.INK,
            background="#ffffff",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=row, column=0, sticky="w", pady=(0, 5))
        row += 1
        subjects = sorted(SUBJECT_CODES, key=str.casefold)
        self.subject_combo = ttk.Combobox(
            form, textvariable=self.subject_var, values=subjects, state="readonly"
        )
        self.subject_combo.grid(
            row=row, column=0, sticky="ew", ipady=4, pady=(0, 4)
        )
        row += 1
        self.class_hint = ttk.Label(
            form,
            text="Choose a subject to see its class number.",
            foreground=self.MUTED,
            background="#ffffff",
            font=("TkDefaultFont", 9),
        )
        self.class_hint.grid(row=row, column=0, sticky="w", pady=(3, 13))
        self.subject_var.trace_add("write", lambda *_: self._update_class_hint())
        row += 1

        ttk.Button(
            form,
            text="Add to catalog",
            style="Accent.TButton",
            command=self._add_book,
        ).grid(row=row, column=0, sticky="ew", ipady=5)
        row += 1
        self.form_status_label = ttk.Label(
            form,
            textvariable=self.form_status_var,
            wraplength=255,
            justify="left",
            background="#ffffff",
            foreground=self.MUTED,
            font=("TkDefaultFont", 9),
        )
        self.form_status_label.grid(row=row, column=0, sticky="w", pady=(10, 0))
        row += 1

        ttk.Separator(form).grid(row=row, column=0, sticky="ew", pady=(16, 12))
        row += 1
        test_header = ttk.Frame(form, style="Card.TFrame")
        test_header.grid(row=row, column=0, sticky="ew")
        test_header.columnconfigure(0, weight=1)
        ttk.Label(test_header, text="Test log", style="CardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.run_tests_button = ttk.Button(
            test_header,
            text="Run tests",
            command=self._run_tests,
        )
        self.run_tests_button.grid(row=0, column=1, sticky="e")
        row += 1

        log_frame = ttk.Frame(form, style="Card.TFrame")
        log_frame.grid(row=row, column=0, sticky="nsew", pady=(9, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.test_log = tk.Text(
            log_frame,
            height=6,
            wrap="word",
            state="disabled",
            background="#f7f9fd",
            foreground=self.INK,
            relief="flat",
            padx=9,
            pady=7,
            font=("TkFixedFont", 9),
        )
        self.test_log.grid(row=0, column=0, sticky="nsew")
        log_scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.test_log.yview
        )
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.test_log.configure(yscrollcommand=log_scrollbar.set)
        self._append_test_log("Ready to run the project tests.")

        ttk.Label(
            page,
            text="Includes sample books to help you explore the catalog.",
            style="Subtitle.TLabel",
        ).grid(row=4, column=0, sticky="w", pady=(12, 0))

    def _metric_card(self, parent, column, caption, value):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(16, 11))
        card.grid(row=0, column=column, sticky="ew", padx=(0, 10) if column < 2 else 0)
        metric = ttk.Label(card, text=value, style="Metric.TLabel")
        metric.pack(anchor="w")
        ttk.Label(card, text=caption, style="MetricCaption.TLabel").pack(
            anchor="w", pady=(2, 0)
        )
        return metric

    def _update_class_hint(self):
        code = SUBJECT_CODES.get(self.subject_var.get())
        text = (
            f"Class number: {code}"
            if code
            else "Choose a subject to see its class number."
        )
        self.class_hint.configure(text=text)

    def _refresh_catalog(self):
        if not hasattr(self, "table") or self.table is None:
            return

        matches = filter_books(self.catalog, self.search_var.get())
        self.table.delete(*self.table.get_children())
        for index, book in enumerate(matches):
            tags = ("alternate",) if index % 2 else ()
            self.table.insert(
                "",
                "end",
                values=(
                    book["id"],
                    book["title"],
                    book["subject"],
                    book["class_no"],
                ),
                tags=tags,
            )

        self.total_metric.configure(text=str(len(self.catalog)))
        self.subject_metric.configure(
            text=str(len({book["subject"] for book in self.catalog}))
        )
        self.visible_metric.configure(text=str(len(matches)))
        if matches:
            self.status_var.set(
                f"{len(matches)} book{'s' if len(matches) != 1 else ''} found"
            )
        else:
            self.status_var.set(
                "No books match your search. Try another title or subject."
            )

    def _sort_catalog(self):
        insertion_sort(self.catalog)
        self._refresh_catalog()
        self.status_var.set("Books sorted by classification number.")

    def _add_book(self):
        title = self.title_var.get().strip()
        subject = self.subject_var.get().strip()
        if not title or not subject:
            self.form_status_var.set(
                "Please enter a book name and choose a subject."
            )
            self.form_status_label.configure(foreground="#b42318")
            return

        success, message = add_book(self.catalog, title, subject)
        self.form_status_var.set(message)
        self.form_status_label.configure(
            foreground="#18804b" if success else "#b42318"
        )
        if success:
            self.title_var.set("")
            self._refresh_catalog()

    def _append_test_log(self, line):
        self.test_log.configure(state="normal")
        self.test_log.insert("end", f"{line}\n")
        self.test_log.see("end")
        self.test_log.configure(state="disabled")

    def _run_tests(self):
        self.run_tests_button.configure(state="disabled", text="Running…")
        self.test_log.configure(state="normal")
        self.test_log.delete("1.0", "end")
        self.test_log.insert("end", "Running project tests…\n")
        self.test_log.configure(state="disabled")

        def report_line(line):
            self.root.after(0, self._append_test_log, line)

        def run():
            try:
                passed = run_test_process(report_line)
            except OSError as error:
                report_line(f"Could not start the test runner: {error}")
                passed = False
            self.root.after(0, self._finish_tests, passed)

        Thread(target=run, daemon=True).start()

    def _finish_tests(self, passed):
        self._append_test_log(
            "All tests passed." if passed else "Tests failed. See the log above."
        )
        self.run_tests_button.configure(state="normal", text="Run tests")

    def run(self):
        self.root.mainloop()


def launch_gui():
    root = tk.Tk()
    LibraryApp(root).run()


def desktop_available():
    """Check whether Tk can open a window in the current environment."""
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.update_idletasks()
    except tk.TclError:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass
        return False

    root.destroy()
    return True
