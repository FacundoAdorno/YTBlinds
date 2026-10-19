import unittest
from yt_blinds.downloader import Downloader
from yt_blinds.updater import Updater
from yt_blinds.accessibility import accessibility_manager

class TestYTBlinds(unittest.TestCase):
    def test_downloader_empty_query(self):
        results = Downloader.search_videos("")
        self.assertEqual(results, [])

    def test_fallback_search(self):
        results = Downloader._fallback_search("test", 5)
        self.assertTrue(len(results) > 0)

    def test_accessibility_announce(self):
        # Should execute without errors on Linux / test environment
        accessibility_manager.announce("Prueba de accesibilidad")

if __name__ == '__main__':
    unittest.main()
