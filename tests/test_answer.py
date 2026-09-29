import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import ask


class AnswerGateTests(unittest.TestCase):
    def test_disabled_retrieval_calls_same_llm_with_empty_context(self):
        with patch.object(ask, 'generate', return_value='{"evidence_id":0}') as model:
            result = ask.answer_question('A question', retrieval_enabled=False)
        self.assertEqual(result['status'], 'not_found')
        self.assertEqual(result['retrieved'], [])
        messages = model.call_args.args[0]
        self.assertEqual(messages[0]['content'], ask.RAG_SYSTEM)
        self.assertIn('CONTEXT:\n[]', messages[1]['content'])

    def test_disabled_retrieval_cannot_invent_evidence(self):
        with patch.object(ask, 'generate', return_value='{"evidence_id":1}'):
            with self.assertRaises(ValueError):
                ask.answer_question('A question', retrieval_enabled=False)

    def test_baseline_has_no_context_or_citations(self):
        with patch.object(ask, 'generate', return_value='Model-only answer') as model:
            result = ask.answer_question('A question', mode='baseline')
        self.assertEqual(result['citations'], [])
        self.assertNotIn('CONTEXT', model.call_args.args[0][1]['content'])


if __name__ == '__main__':
    unittest.main()
