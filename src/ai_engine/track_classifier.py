"""
Track Classifier - AI-powered track type identification
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from .audio_feature_extractor import AudioFeatureExtractor


class TrackClassifier:
    """
    Classifies tracks into categories using ML and rule-based approaches

    Categories:
    - drums (kick, snare, hi-hat, overhead, etc.)
    - bass
    - guitar (electric, acoustic)
    - keys (piano, synth, organ)
    - vocals (lead, background)
    - strings
    - brass
    - fx (effects, ambience)
    - other
    """

    TRACK_CATEGORIES = [
        'kick', 'snare', 'hihat', 'drums', 'percussion',
        'bass', 'synth_bass',
        'guitar', 'electric_guitar', 'acoustic_guitar',
        'keys', 'piano', 'synth', 'organ', 'pad',
        'lead_vocal', 'vocal', 'bgv', 'choir',
        'strings', 'violin', 'cello',
        'brass', 'trumpet', 'sax',
        'fx', 'ambient', 'soundscape',
        'other'
    ]

    def __init__(self, model_path: Optional[Path] = None):
        self.feature_extractor = AudioFeatureExtractor()
        self.classifier: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None

        if model_path and model_path.exists():
            self.load_model(model_path)
        else:
            # Initialize with rule-based classification
            logger.info("No ML model loaded, using rule-based classification")

    def classify_track(
        self,
        audio_path: Optional[Path] = None,
        track_name: str = "",
        features: Optional[Dict] = None
    ) -> Tuple[str, float]:
        """
        Classify a track into a category

        Args:
            audio_path: Path to audio file
            track_name: Track name (used for name-based classification)
            features: Pre-extracted features (optional)

        Returns:
            (category, confidence) tuple
        """
        # Try name-based classification first (fast and often accurate)
        name_category, name_confidence = self._classify_by_name(track_name)

        if name_confidence > 0.8:
            logger.info(f"High confidence name-based classification: {name_category}")
            return name_category, name_confidence

        # If we have audio, use feature-based classification
        if audio_path or features:
            if features is None and audio_path:
                features = self.feature_extractor.extract_features(audio_path)

            if self.classifier is not None:
                # ML-based classification
                ml_category, ml_confidence = self._classify_by_ml(features)

                # Combine name-based and ML predictions
                if name_confidence > 0.5 and ml_confidence > 0.5:
                    # Both agree or close
                    if name_category == ml_category:
                        return ml_category, max(name_confidence, ml_confidence)
                    else:
                        # Take higher confidence
                        if ml_confidence > name_confidence:
                            return ml_category, ml_confidence
                        else:
                            return name_category, name_confidence
                elif ml_confidence > name_confidence:
                    return ml_category, ml_confidence
            else:
                # Rule-based classification
                rule_category, rule_confidence = self._classify_by_rules(features)

                if name_confidence > rule_confidence:
                    return name_category, name_confidence
                else:
                    return rule_category, rule_confidence

        # Fallback to name-based only
        return name_category if name_confidence > 0.3 else 'other', name_confidence

    def _classify_by_name(self, track_name: str) -> Tuple[str, float]:
        """Classify based on track name using keyword matching"""
        if not track_name:
            return 'other', 0.0

        name_lower = track_name.lower()

        # Keyword mapping with confidence weights
        keywords = {
            # Drums
            'kick': ('kick', 0.95),
            'kik': ('kick', 0.90),
            'bd': ('kick', 0.85),
            'snare': ('snare', 0.95),
            'snr': ('snare', 0.90),
            'sd': ('snare', 0.85),
            'hihat': ('hihat', 0.95),
            'hh': ('hihat', 0.90),
            'hat': ('hihat', 0.85),
            'overhead': ('drums', 0.90),
            'oh': ('drums', 0.85),
            'drum': ('drums', 0.90),
            'perc': ('percussion', 0.85),
            'tom': ('drums', 0.90),
            'cymbal': ('drums', 0.90),

            # Bass
            'bass': ('bass', 0.95),
            'sub': ('bass', 0.85),
            '808': ('bass', 0.90),

            # Guitar
            'guitar': ('guitar', 0.95),
            'gtr': ('guitar', 0.90),
            'elec': ('electric_guitar', 0.85),
            'acoustic': ('acoustic_guitar', 0.90),

            # Keys
            'piano': ('piano', 0.95),
            'keys': ('keys', 0.95),
            'synth': ('synth', 0.90),
            'pad': ('pad', 0.90),
            'organ': ('organ', 0.95),
            'rhodes': ('keys', 0.90),
            'wurli': ('keys', 0.90),

            # Vocals
            'vocal': ('vocal', 0.95),
            'vox': ('vocal', 0.90),
            'lead': ('lead_vocal', 0.85),
            'bgv': ('bgv', 0.95),
            'background': ('bgv', 0.90),
            'backing': ('bgv', 0.90),
            'choir': ('choir', 0.95),
            'harmony': ('bgv', 0.85),

            # Strings
            'string': ('strings', 0.95),
            'violin': ('violin', 0.95),
            'viola': ('strings', 0.95),
            'cello': ('cello', 0.95),

            # Brass
            'brass': ('brass', 0.95),
            'trumpet': ('trumpet', 0.95),
            'trombone': ('brass', 0.95),
            'sax': ('sax', 0.95),
            'horn': ('brass', 0.90),

            # FX
            'fx': ('fx', 0.95),
            'effect': ('fx', 0.90),
            'ambient': ('ambient', 0.90),
            'atmos': ('ambient', 0.85),
            'reverb': ('fx', 0.85),
            'delay': ('fx', 0.85),
        }

        # Check for keywords
        best_match = ('other', 0.0)

        for keyword, (category, confidence) in keywords.items():
            if keyword in name_lower:
                if confidence > best_match[1]:
                    best_match = (category, confidence)

        return best_match

    def _classify_by_rules(self, features: Dict) -> Tuple[str, float]:
        """Rule-based classification using audio features"""
        if not features or 'stats' not in features:
            return 'other', 0.0

        stats = features['stats']

        # Extract key features
        zcr = stats.get('mean_zcr', 0)
        centroid = stats.get('mean_centroid', 0)
        rms = stats.get('mean_rms', 0)
        tempo = stats.get('tempo', 0)
        beat_strength = stats.get('beat_strength', 0)

        # Rule-based classification
        # High ZCR + high beat strength = drums/percussion
        if zcr > 0.1 and beat_strength > 0.5:
            return 'drums', 0.7

        # Low centroid + low zcr = bass
        if centroid < 1000 and zcr < 0.05:
            return 'bass', 0.7

        # High centroid = bright instruments (cymbals, vocals)
        if centroid > 5000:
            if rms > 0.1:
                return 'vocal', 0.6
            else:
                return 'hihat', 0.6

        # Mid-range = guitars, keys
        if 1000 < centroid < 3000:
            return 'guitar', 0.5

        return 'other', 0.3

    def _classify_by_ml(self, features: Dict) -> Tuple[str, float]:
        """ML-based classification using trained model"""
        if self.classifier is None or self.scaler is None:
            return 'other', 0.0

        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)

            # Scale features
            scaled_features = self.scaler.transform([feature_vector])

            # Predict
            prediction = self.classifier.predict(scaled_features)[0]
            probabilities = self.classifier.predict_proba(scaled_features)[0]
            confidence = float(np.max(probabilities))

            return prediction, confidence

        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return 'other', 0.0

    def _prepare_feature_vector(self, features: Dict) -> np.ndarray:
        """Convert feature dict to vector for ML model"""
        stats = features.get('stats', {})

        feature_vector = [
            stats.get('mean_mfcc', 0),
            stats.get('std_mfcc', 0),
            stats.get('mean_centroid', 0),
            stats.get('mean_rolloff', 0),
            stats.get('mean_zcr', 0),
            stats.get('mean_rms', 0),
            stats.get('tempo', 0),
            stats.get('beat_strength', 0),
        ]

        return np.array(feature_vector)

    def classify_batch(
        self,
        tracks: List[Dict[str, any]]
    ) -> Dict[int, Tuple[str, float]]:
        """
        Classify multiple tracks

        Args:
            tracks: List of dicts with 'index', 'name', and optionally 'audio_path'

        Returns:
            Dict mapping track index to (category, confidence)
        """
        results = {}

        for track in tracks:
            index = track.get('index')
            name = track.get('name', '')
            audio_path = track.get('audio_path')

            category, confidence = self.classify_track(
                audio_path=audio_path,
                track_name=name
            )

            results[index] = (category, confidence)
            logger.info(f"Track {index} '{name}': {category} ({confidence:.2f})")

        return results

    def load_model(self, model_path: Path) -> bool:
        """Load trained ML model"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            self.classifier = model_data['classifier']
            self.scaler = model_data['scaler']

            logger.info(f"Loaded ML model from {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def save_model(self, model_path: Path) -> bool:
        """Save trained model"""
        try:
            model_data = {
                'classifier': self.classifier,
                'scaler': self.scaler,
            }

            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)

            logger.info(f"Saved model to {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
