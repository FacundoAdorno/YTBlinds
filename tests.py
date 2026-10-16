import unittest
from yt_blinds.downloader import Downloader
from yt_blinds.updater import Updater

class TestYTBlinds(unittest.TestCase):
    def test_downloader_empty_query(self):
        results = Downloader.search_videos("")
        self.assertEqual(results, [])

    def test_fallback_search(self):
        results = Downloader._fallback_search("test", 5)
        self.assertTrue(len(results) > 0)

if __name__ == '__main__':
    unittest.main()
