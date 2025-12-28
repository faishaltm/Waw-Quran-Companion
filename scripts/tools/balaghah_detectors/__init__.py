"""
Balaghah detectors package for Quranic rhetoric analysis.

This package contains specialized detectors for various balaghah (rhetorical) devices:
- taqdim_detector: Word order advancement/delay detection
- tibaq_detector: Antithesis detection using root oppositions
- tashbih_detector: Simile/comparison particle detection
"""

from .taqdim_detector import detect_taqdim_takhir
from .tibaq_detector import detect_tibaq
from .tashbih_detector import detect_tashbih_candidates

__all__ = [
    'detect_taqdim_takhir',
    'detect_tibaq',
    'detect_tashbih_candidates'
]
