"""Exercise the built site at a project subpath in Chromium."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=temporary)
        )
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.getenv("CHROME_BIN"))
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")
                page.locator("#work").wait_for()
                assert "2025-04-01" == page.locator("#week").input_value()
                assert page.locator("#summary tr").count() > 0
                page.locator("#type").select_option("ROW Litter")
                assert page.locator("#issues tr").count() > 0
                page.locator("#area").select_option(index=1)
                assert page.locator("#summary tr").count() == 1
                with page.expect_download() as pending:
                    page.locator("#csv").click()
                assert "request_id" in Path(pending.value.path()).read_text()
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate(
                    "document.documentElement.scrollWidth <= window.innerWidth"
                )
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                assert not errors, errors
                browser.close()
            print(
                "Browser checks passed: project subpath, filters, data export and mobile layout"
            )
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
