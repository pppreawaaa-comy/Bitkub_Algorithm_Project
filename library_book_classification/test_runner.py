import queue
import subprocess
import sys
import threading
import time
from pathlib import Path


def run_test_process(on_output, timeout=60):
    """Run the project test suite in a child process and stream its output."""
    project_root = Path(__file__).resolve().parent.parent
    process = subprocess.Popen(
        [sys.executable, "-u", "-m", "library_book_classification.tests"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    output_queue = queue.Queue()

    def read_output():
        try:
            for line in process.stdout:
                output_queue.put(line.rstrip("\n"))
        finally:
            output_queue.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout
    output_finished = False

    while not output_finished:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            process.kill()
            process.wait()
            reader.join(timeout=1)
            on_output(f"Tests timed out after {timeout} seconds.")
            return False
        try:
            line = output_queue.get(timeout=min(0.1, remaining))
        except queue.Empty:
            if process.poll() is not None and not reader.is_alive():
                break
            continue
        if line is None:
            output_finished = True
        else:
            on_output(line)

    return_code = process.wait()
    return return_code == 0
