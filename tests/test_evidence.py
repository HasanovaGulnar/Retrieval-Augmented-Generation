import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from evidence import candidates, requested_section


class FakeSections:
    def section(self, chunk, text):
        return chunk['section']


class EvidenceTests(unittest.TestCase):
    def chunk(self, text, section='4.7'):
        return dict(text=text, section=section, chunk_id='c1',
                    document_id='d1', page=1)

    def test_section_request(self):
        self.assertEqual(requested_section('4.7-ci bölmədə müddət nədir?'), '4.7')
        self.assertEqual(requested_section('adlı 5-ci bölmədə qayda'), '5')

    def test_other_section_excluded(self):
        rows = [self.chunk('Bu bölmədə yalnız fərqli bir qayda verilib.', '5')]
        self.assertEqual(candidates(rows, FakeSections(), '4.7-ci bölmədə nə var?'), [])

    def test_abbreviation_and_negation_preserved(self):
        text = 'Telefon, çanta və s. texniki vasitələri gətirmək qadağandır.'
        result = candidates([self.chunk(text)], FakeSections(), 'Hansı əşyalar?')
        self.assertEqual(result[0]['text'], text)

    def test_only_input_chunks_used(self):
        self.assertEqual(candidates([], FakeSections(), 'Sual'), [])


if __name__ == '__main__':
    unittest.main()
