import unittest

from yt_blinds.context.app_context import app_context
from yt_blinds.downloader import Downloader


class TestYTBlinds(unittest.TestCase):

    downloader = Downloader(app_context)

    def test_downloader_empty_query(self):
        results, source = self.downloader.search_videos("")
        self.assertEqual(results, [])

    def test_fallback_search(self):
        results, source = self.downloader._fallback_search("test", 5)
        self.assertTrue(len(results) > 0)

    def test_accessibility_announce(self):
        # Should execute without errors on Linux / test environment
        app_context.accessibility_manager.announce("Prueba de accesibilidad")

    def test_accessibility_stop_announces(self):
        app_context.accessibility_manager.announce("Anuncio 1")
        app_context.accessibility_manager.announce("Anuncio 2")
        app_context.accessibility_manager.stop_announces()
        self.assertTrue(app_context.accessibility_manager.speech_queue.empty())

if __name__ == '__main__':
    unittest.main()
