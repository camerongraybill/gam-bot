from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import Client, SimpleTestCase, override_settings


class StaticFilesTests(SimpleTestCase):
    def test_web_app_serves_files_from_static_root(self) -> None:
        with TemporaryDirectory() as static_root:
            (Path(static_root) / "probe.txt").write_text("served")
            with override_settings(STATIC_ROOT=static_root):
                response = Client().get("/static/probe.txt")
                self.assertEqual(response.status_code, 200)
                body = b"".join(response.streaming_content)  # type: ignore[attr-defined]
                response.close()
        self.assertEqual(body, b"served")

    def test_loads_without_a_static_root(self) -> None:
        with override_settings(STATIC_ROOT=None):
            self.assertEqual(Client().get("/static/probe.txt").status_code, 404)
