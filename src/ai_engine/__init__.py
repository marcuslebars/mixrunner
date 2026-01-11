"""
AI Engine for Track Classification and Analysis
Uses machine learning to identify and categorize tracks
"""

from .track_classifier import TrackClassifier
from .audio_feature_extractor import AudioFeatureExtractor

__all__ = ['TrackClassifier', 'AudioFeatureExtractor']
