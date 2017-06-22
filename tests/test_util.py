import unittest

from clarify.util import jurisdiction_levels_from_url

class TestUtil(unittest.TestCase):
    def test_jurisdictions_levels_from_url(self):
        url = "http://results.enr.clarityelections.com/AR/Benton/63917/183978/Web01/en/summary.html"
        levels = jurisdiction_levels_from_url(url)

        self.assertEqual(len(levels), 2)
        self.assertEqual(levels[0]['level'], 'state')
        self.assertEqual(levels[0]['name'], 'AR')
        self.assertEqual(levels[1]['level'], 'county')
        self.assertEqual(levels[1]['name'], 'Benton')

        url = 'http://results.enr.clarityelections.com/AR/63912/184685/Web01/en/summary.html'
        levels = jurisdiction_levels_from_url(url)

        self.assertEqual(len(levels), 1)
        self.assertEqual(levels[0]['level'], 'state')
        self.assertEqual(levels[0]['name'], 'AR')
