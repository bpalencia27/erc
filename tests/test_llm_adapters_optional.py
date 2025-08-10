import os
import unittest
from app.api.llm_adapters import get_llm_adapter

@unittest.skipUnless(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"), "Se requieren API keys para esta prueba opcional")
class TestLLMAdaptersReal(unittest.TestCase):
    def test_generate_content_short(self):
        adapter = get_llm_adapter()
        resp = adapter.generate_content("Prueba corta clínica")
        self.assertTrue(len(resp.text) > 0)

if __name__ == '__main__':
    unittest.main()
