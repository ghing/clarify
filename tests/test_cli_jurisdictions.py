import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from clarify.cli.jurisdictions import get_all_jurisdictions
from clarify.jurisdiction import Jurisdiction


class TestJurisdictionsCLI(unittest.TestCase):
    def test_get_all_jurisdictions(self):
        j = Jurisdiction(
            'http://results.enr.clarityelections.com/AR/63912/184685/Web01/en/summary.html',
            level='state',
            name='Arkansas')

        county = Jurisdiction(
            'http://results.enr.clarityelections.com/AR/63912/184685/Web01/en/summary.html',
            level='county',
            name='Arkansas')

        with patch.object(county,'get_subjurisdictions') as mock_county, patch.object(j,'get_subjurisdictions') as mock_j:
            mock_county.get_subjurisdictions.return_value = []
            mock_j.get_subjurisdictions.return_value = [mock_county]

            j_all_jurisdictions = get_all_jurisdictions(mock_j)

            self.assertEquals(len(j_all_jurisdictions), 2)
            self.assertIn(mock_j, j_all_jurisdictions)
            self.assertIn(mock_county, j_all_jurisdictions)
