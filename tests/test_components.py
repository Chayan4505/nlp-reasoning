
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.claim_extraction import extract_claims
from src.aggregation import aggregate_decisions

class TestComponents(unittest.TestCase):
    def test_aggregation_logic_consistent(self):
        decisions = [
            {"label": "SUPPORT", "confidence": 0.9, "analysis": "Supports"},
            {"label": "NONE", "confidence": 0.0, "analysis": ""},
        ]
        result = aggregate_decisions(decisions, "test_1")
        self.assertEqual(result["prediction"], 1)
        self.assertIn("Consistent", result["rationale"])

    def test_aggregation_logic_contradiction(self):
        decisions = [
            {"label": "CONTRADICT", "confidence": 0.95, "analysis": "Contradicts core belief"},
            {"label": "SUPPORT", "confidence": 0.4, "analysis": "Supports"},
        ]
        result = aggregate_decisions(decisions, "test_2")
        self.assertEqual(result["prediction"], 0)
        self.assertIn("Contradiction", result["rationale"])

    @patch("src.claim_extraction.client")
    def test_extract_claims(self, mock_client):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"claims": [{"text": "Claim 1", "type": "event", "importance": "core"}]}'
        mock_client.chat.completions.create.return_value = mock_response
        
        claims = extract_claims("Some backstory", "story_1")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["text"], "Claim 1")
        self.assertEqual(claims[0]["id"], "story_1_c0")

if __name__ == '__main__':
    unittest.main()
