import ipaddress
import json
import os
import secrets
import socket
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread
from urllib.error import URLError
from urllib.request import Request, urlopen
from urllib.parse import parse_qs, urlparse

if __package__:
    from .algorithms import insertion_sort
    from .classification import add_book
    from .data import MOCK_BOOKS, SUBJECT_CODES, books as starter_books
else:
    from algorithms import insertion_sort
    from classification import add_book
    from data import MOCK_BOOKS, SUBJECT_CODES, books as starter_books


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#f3f6fb">
  <title>Li-BIT-ry | Library</title>
  <style>
    :root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: #172b4d; background: #f3f6fb; }
    * { box-sizing: border-box; }
    body { margin: 0; }
    main { max-width: 1200px; margin: 0 auto; padding: 36px 28px; }
    h1 { margin: 0; font-size: clamp(27px, 4vw, 36px); letter-spacing: -.04em; }
    .subtitle, .muted { color: #62718a; }
    .subtitle { margin: 7px 0 24px; }
    .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px; }
    .card, .metric { background: white; border: 1px solid #e7ebf2; border-radius: 14px; box-shadow: 0 3px 12px #172b4d08; }
    .metric { padding: 16px 18px; }
    .metric strong { display: block; font-size: 24px; }
    .metric span { color: #62718a; font-size: 11px; letter-spacing: .08em; }
    .layout { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 16px; align-items: start; }
    .card { padding: 20px; }
    .card h2 { margin: 0; font-size: 17px; }
    .bar { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 16px; }
    input, select, button { font: inherit; }
    input, select { width: 100%; min-height: 42px; padding: 9px 11px; border: 1px solid #d9e0eb; border-radius: 8px; background: white; color: #172b4d; }
    input:focus, select:focus { outline: 3px solid #3157d522; border-color: #3157d5; }
    button { min-height: 42px; border: 0; border-radius: 8px; padding: 9px 14px; color: white; background: #3157d5; font-weight: 650; cursor: pointer; white-space: nowrap; }
    button:hover { background: #2446ba; }
    .secondary { background: #edf1fa; color: #3157d5; }
    .secondary:hover { background: #e1e8f7; }
    .search { display: flex; flex: 1; gap: 9px; }
    .search input { max-width: 440px; }
    .table-wrap { overflow: auto; max-height: 58vh; border: 1px solid #edf0f5; border-radius: 9px; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    th, td { padding: 11px 12px; border-bottom: 1px solid #edf0f5; }
    th { position: sticky; top: 0; background: #f7f9fd; color: #62718a; font-size: 10px; letter-spacing: .07em; }
    td { font-size: 13px; }
    tbody tr:nth-child(even) { background: #fafbfe; }
    .form-card > p { margin: 7px 0 18px; font-size: 13px; line-height: 1.5; }
    label { display: block; margin: 13px 0 6px; font-size: 12px; font-weight: 650; }
    .class-hint { min-height: 30px; padding: 8px 0; color: #62718a; font-size: 12px; }
    .form-card button { width: 100%; }
    #message { min-height: 22px; margin: 10px 0 0; font-size: 12px; }
    #message[data-kind="error"] { color: #b42318; }
    #message[data-kind="success"] { color: #18804b; }
    #result-count { margin: 12px 0 0; font-size: 12px; }
    footer { margin-top: 16px; color: #62718a; font-size: 12px; }
    @media (max-width: 800px) {
      main { padding: 24px 16px; }
      .layout { grid-template-columns: 1fr; }
    }
    @media (max-width: 520px) {
      .metrics { gap: 8px; }
      .metric { padding: 12px; }
      .metric strong { font-size: 20px; }
      .bar { align-items: stretch; flex-direction: column; }
      .search input { max-width: none; }
      .table-wrap { max-height: 52vh; }
      th, td { padding: 10px 8px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Li-BIT-ry</h1>
      <p class="subtitle">A calmer way to organize and discover your next read.</p>
    </header>
    <section class="metrics" aria-label="Catalog summary">
      <div class="metric"><strong id="total">—</strong><span>BOOKS</span></div>
      <div class="metric"><strong id="subjects">—</strong><span>SUBJECTS</span></div>
      <div class="metric"><strong id="showing">—</strong><span>SHOWING</span></div>
    </section>
    <div class="layout">
      <section class="card">
        <div class="bar">
          <div class="search">
            <input id="query" type="search" placeholder="Find by book ID, title, subject or class number" aria-label="Search books">
          </div>
          <button id="sort" class="secondary" type="button">Sort by class no.</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>BOOK ID</th><th>TITLE</th><th>SUBJECT</th><th>CLASS NO.</th></tr></thead>
            <tbody id="books"></tbody>
          </table>
        </div>
        <p id="result-count" class="muted" aria-live="polite"></p>
      </section>
      <aside class="card form-card">
        <h2>Add a book</h2>
        <p class="muted">Enter a book's details and its class number will be assigned automatically.</p>
        <form id="add-form">
          <label for="book-id">Book ID</label>
          <input id="book-id" name="id" placeholder="e.g. B031" required>
          <label for="title">Title</label>
          <input id="title" name="title" placeholder="Enter the book title" required>
          <label for="subject">Subject</label>
          <select id="subject" name="subject" required>
            <option value="">Choose a subject</option>
            __SUBJECT_OPTIONS__
          </select>
          <div id="class-hint" class="class-hint">Choose a subject to see its class number.</div>
          <button type="submit">Add to catalog</button>
          <p id="message" role="status" aria-live="polite"></p>
        </form>
      </aside>
    </div>
    <footer>Sample books are included to help you explore the catalog. Books added here are kept until the app closes.</footer>
  </main>
  <script>
    const queryInput = document.querySelector("#query");
    const tbody = document.querySelector("#books");
    const message = document.querySelector("#message");
    const subjectSelect = document.querySelector("#subject");
    let searchTimer;

    async function loadBooks(sorted = false) {
      const params = new URLSearchParams();
      if (queryInput.value.trim()) params.set("q", queryInput.value.trim());
      if (sorted) params.set("sort", "class_no");
      const response = await fetch(`/api/books?${params}`);
      if (!response.ok) throw new Error("Could not load the book catalog.");
      const data = await response.json();
      tbody.replaceChildren();
      for (const book of data.books) {
        const row = document.createElement("tr");
        for (const value of [book.id, book.title, book.subject, book.class_no]) {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        }
        tbody.append(row);
      }
      document.querySelector("#total").textContent = data.total;
      document.querySelector("#subjects").textContent = data.subjects;
      document.querySelector("#showing").textContent = data.books.length;
      document.querySelector("#result-count").textContent = data.books.length
        ? `${data.books.length} book${data.books.length === 1 ? "" : "s"} found`
        : "No books match your search. Try another title or subject.";
    }

    queryInput.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => loadBooks().catch(showLoadError), 140);
    });
    document.querySelector("#sort").addEventListener("click", () => {
      loadBooks(true).catch(showLoadError);
    });
    subjectSelect.addEventListener("change", () => {
      const code = subjectSelect.selectedOptions[0].dataset.code;
      document.querySelector("#class-hint").textContent = code
        ? `Class number: ${code}`
        : "Choose a subject to see its class number.";
    });
    document.querySelector("#add-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      message.textContent = "";
      message.dataset.kind = "";
      const form = new FormData(event.currentTarget);
      try {
        const response = await fetch("/api/books", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(form)),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || "Could not add this book.");
        message.textContent = data.message;
        message.dataset.kind = "success";
        event.currentTarget.reset();
        document.querySelector("#class-hint").textContent = "Choose a subject to see its class number.";
        await loadBooks();
      } catch (error) {
        message.textContent = error.message;
        message.dataset.kind = "error";
      }
    });

    function showLoadError(error) {
      document.querySelector("#result-count").textContent = error.message;
    }

    loadBooks().catch(showLoadError);
  </script>
</body>
</html>
"""


def _state_path():
    return Path.home() / ".li-bit-ry" / "server.json"


def _write_server_state(server, token):
    state_path = _state_path()
    state_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        os.chmod(state_path.parent, 0o700)
    except OSError:
        pass
    descriptor, temporary_path = tempfile.mkstemp(dir=state_path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as state_file:
            json.dump(
                {
                    "pid": os.getpid(),
                    "port": server.server_port,
                    "token": token,
                },
                state_file,
            )
        os.replace(temporary_path, state_path)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise


def _remove_server_state(token):
    state_path = _state_path()
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    if state.get("token") == token:
        state_path.unlink(missing_ok=True)


def restart_existing_app():
    """Stop a prior managed Li-BIT-ry instance before starting a new one."""
    state_path = _state_path()
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"Could not read the Li-BIT-ry server state at {state_path}: {error}"
        ) from error

    port = state.get("port")
    token = state.get("token")
    if (
        not isinstance(port, int)
        or isinstance(port, bool)
        or not 0 < port < 65_536
        or not isinstance(token, str)
    ):
        raise RuntimeError(
            f"The Li-BIT-ry server state at {state_path} is invalid; "
            "remove that file only after confirming the app is not running."
        )

    request = Request(
        f"http://127.0.0.1:{port}/api/shutdown",
        headers={"X-Li-BIT-ry-Token": token},
        method="POST",
    )
    try:
        with urlopen(request, timeout=3) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"The existing Li-BIT-ry server refused to stop (HTTP "
                    f"{response.status})."
                )
    except URLError as error:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                raise RuntimeError(
                    "A server is still using Li-BIT-ry's port, but it could not "
                    "be stopped safely. Close that app and try again."
                ) from error
        except OSError:
            _remove_server_state(token)
            return

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                time.sleep(0.1)
        except OSError:
            _remove_server_state(token)
            return
    raise RuntimeError("The existing Li-BIT-ry server did not stop in time.")


def _create_handler(catalog, catalog_lock, token):
    class CatalogHandler(BaseHTTPRequestHandler):
        def _send(self, status, body, content_type):
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(encoded)

        def _send_json(self, status, data):
            self._send(
                status,
                json.dumps(data, ensure_ascii=False),
                "application/json; charset=utf-8",
            )

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                options = "".join(
                    f'<option value="{_escape_html(subject)}" '
                    f'data-code="{_escape_html(code)}">'
                    f'{_escape_html(subject)} ({_escape_html(code)})</option>'
                    for subject, code in sorted(
                        SUBJECT_CODES.items(), key=lambda item: item[0].casefold()
                    )
                )
                self._send(
                    200,
                    PAGE.replace("__SUBJECT_OPTIONS__", options),
                    "text/html; charset=utf-8",
                )
                return

            if parsed.path != "/api/books":
                self._send_json(404, {"message": "Not found."})
                return

            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0].strip().casefold()
            with catalog_lock:
                if params.get("sort") == ["class_no"]:
                    insertion_sort(catalog)
                matches = [
                    book.copy()
                    for book in catalog
                    if not query
                    or any(
                        query in str(book[field]).casefold()
                        for field in ("id", "title", "subject", "class_no")
                    )
                ]
                total = len(catalog)
                subjects = len({book["subject"] for book in catalog})
            self._send_json(
                200,
                {
                    "books": matches,
                    "total": total,
                    "subjects": subjects,
                },
            )

        def do_POST(self):
            path = urlparse(self.path).path
            if path == "/api/shutdown":
                try:
                    is_local = ipaddress.ip_address(self.client_address[0]).is_loopback
                except ValueError:
                    is_local = False
                provided_token = self.headers.get("X-Li-BIT-ry-Token", "")
                if not is_local or not secrets.compare_digest(provided_token, token):
                    self._send_json(403, {"message": "Forbidden."})
                    return
                self._send_json(200, {"message": "Li-BIT-ry is restarting."})
                Thread(target=self.server.shutdown, daemon=True).start()
                return
            if path != "/api/books":
                self._send_json(404, {"message": "Not found."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16_384:
                    self._send_json(400, {"message": "Please submit valid book details."})
                    return
                payload = json.loads(self.rfile.read(length))
            except (ValueError, UnicodeDecodeError):
                self._send_json(400, {"message": "Please submit valid book details."})
                return
            if not isinstance(payload, dict):
                self._send_json(400, {"message": "Please submit valid book details."})
                return

            book_id = payload.get("id")
            title = payload.get("title")
            subject = payload.get("subject")
            if not all(isinstance(value, str) for value in (book_id, title, subject)):
                self._send_json(400, {"message": "Please enter a book ID, title, and subject."})
                return
            book_id, title, subject = book_id.strip(), title.strip(), subject.strip()
            if not book_id or not title or not subject:
                self._send_json(400, {"message": "Please enter a book ID, title, and subject."})
                return

            with catalog_lock:
                success, result = add_book(catalog, book_id, title, subject)
            self._send_json(
                201 if success else 400,
                {"message": result},
            )

        def log_message(self, format, *args):
            print(f"[{self.log_date_time_string()}] {format % args}")

    return CatalogHandler


def _escape_html(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def create_server(host="127.0.0.1", port=8000):
    catalog = [book.copy() for book in starter_books + MOCK_BOOKS]
    token = secrets.token_urlsafe(32)
    server = ThreadingHTTPServer(
        (host, port), _create_handler(catalog, Lock(), token)
    )
    server.li_bit_ry_token = token
    return server


def serve(host="0.0.0.0", port=8000):
    server = create_server(host, port)
    token = server.li_bit_ry_token
    _write_server_state(server, token)
    print(f"Li-BIT-ry is running. Open http://localhost:{server.server_port} in your browser.")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLi-BIT-ry stopped.")
    finally:
        server.server_close()
        _remove_server_state(token)
