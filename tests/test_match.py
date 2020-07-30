"""
Tests de andi.webservice.match
"""

import andi.webservice.match as target


def test_selected_nafs_from_romes():
    result, _ = target.selected_nafs_from_romes(["A1101"])
    assert result == {'0161Z': '5', '7731Z': '4', '0210Z': '3', '0114Z': '3', '0220Z': '3', '0141Z': '3', '0111Z': '2',
                      '1091Z': '1', '7830Z': '1', '4941B': '1', '4941A': '1', '4312A': '1', '0121Z': '1', '0146Z': '1',
                      '2365Z': '1'}
