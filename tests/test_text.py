import unittest

from tts_ai.config import infer_language_for_voice
from tts_ai.text import chunk_text, normalize_text


class TextHelpersTest(unittest.TestCase):
    def test_normalize_text_trims_spacing(self) -> None:
        text = " Hello   world \n\n\n This is   a test. "
        self.assertEqual(normalize_text(text), "Hello world\n\nThis is a test.")

    def test_chunk_text_keeps_short_input_whole(self) -> None:
        chunks = chunk_text("Hello world. This stays together.", max_chars=200)
        self.assertEqual(chunks, ["Hello world. This stays together."])

    def test_chunk_text_splits_long_input(self) -> None:
        text = (
            "This is a long sentence that should be split into smaller chunks, "
            "because it keeps going far beyond the configured limit, and it should "
            "still preserve readable boundaries where possible."
        )
        chunks = chunk_text(text, max_chars=90)
        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all(len(chunk) <= 90 for chunk in chunks))

    def test_infer_language_for_voice(self) -> None:
        self.assertEqual(infer_language_for_voice("af_heart"), "en-us")
        self.assertEqual(infer_language_for_voice("jf_alpha"), "ja")


if __name__ == "__main__":
    unittest.main()
