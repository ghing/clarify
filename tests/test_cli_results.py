import os.path
import unittest

from clarify.cli.results import result_as_dict
from clarify.parser import Parser


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestResultsCLI(unittest.TestCase):
    def test_result_as_dict(self):
        parser = Parser()
        parser.parse(os.path.join(TEST_DATA_DIR, 'county.xml'))
        result = parser.results[0]

        result_dict = result_as_dict(result)

        self.assertEqual(result_dict['race'], result.contest.text)
        self.assertEqual(result_dict['candidate'], result.choice.text)
        self.assertEqual(result_dict['party'], result.choice.party)
        self.assertEqual(result_dict['votes'], result.choice.total_votes)
