"""
Audio Feature Extractor - Extracts features from audio for ML classification
"""

import numpy as np
import librosa
from pathlib import Path
from typing import Dict, Optional, Tuple
from loguru import logger
import soundfile as sf


class AudioFeatureExtractor:
    """
    Extracts audio features for track classification
    """

    def __init__(self, sample_rate: int = 22050, duration: float = 30.0):
        """
        Args:
            sample_rate: Target sample rate for analysis
            duration: Duration of audio to analyze (seconds)
        """
        self.sample_rate = sample_rate
        self.duration = duration

    def extract_features(self, audio_path: Path) -> Dict[str, np.ndarray]:
        """
        Extract comprehensive audio features

        Returns dict with:
            - spectral_features: MFCC, spectral centroid, rolloff, etc.
            - temporal_features: Zero crossing rate, RMS energy
            - rhythm_features: Tempo, beat strength
            - harmonic_features: Chroma, tonnetz
        """
        try:
            # Load audio
            y, sr = self._load_audio(audio_path)

            if y is None or len(y) == 0:
                logger.warning(f"Could not load audio from {audio_path}")
                return self._get_empty_features()

            # Extract features
            features = {}

            # Spectral features
            features['mfcc'] = self._extract_mfcc(y, sr)
            features['spectral_centroid'] = self._extract_spectral_centroid(y, sr)
            features['spectral_rolloff'] = self._extract_spectral_rolloff(y, sr)
            features['spectral_bandwidth'] = self._extract_spectral_bandwidth(y, sr)

            # Temporal features
            features['zero_crossing_rate'] = self._extract_zero_crossing_rate(y)
            features['rms_energy'] = self._extract_rms_energy(y)

            # Rhythm features
            features['tempo'], features['beat_strength'] = self._extract_tempo(y, sr)

            # Harmonic features
            features['chroma'] = self._extract_chroma(y, sr)

            # Statistical aggregations
            features['stats'] = self._compute_statistics(features)

            return features

        except Exception as e:
            logger.error(f"Feature extraction failed for {audio_path}: {e}")
            return self._get_empty_features()

    def _load_audio(self, audio_path: Path) -> Tuple[Optional[np.ndarray], int]:
        """Load and preprocess audio file"""
        try:
            # Load audio
            y, sr = librosa.load(
                audio_path,
                sr=self.sample_rate,
                duration=self.duration,
                mono=True
            )

            # Normalize
            if len(y) > 0:
                y = librosa.util.normalize(y)

            return y, sr

        except Exception as e:
            logger.error(f"Failed to load audio {audio_path}: {e}")
            return None, self.sample_rate

    def _extract_mfcc(self, y: np.ndarray, sr: int, n_mfcc: int = 13) -> np.ndarray:
        """Extract Mel-frequency cepstral coefficients"""
        try:
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
            return np.mean(mfcc, axis=1)
        except:
            return np.zeros(n_mfcc)

    def _extract_spectral_centroid(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract spectral centroid (brightness)"""
        try:
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            return np.mean(centroid)
        except:
            return np.array([0.0])

    def _extract_spectral_rolloff(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract spectral rolloff"""
        try:
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            return np.mean(rolloff)
        except:
            return np.array([0.0])

    def _extract_spectral_bandwidth(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract spectral bandwidth"""
        try:
            bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
            return np.mean(bandwidth)
        except:
            return np.array([0.0])

    def _extract_zero_crossing_rate(self, y: np.ndarray) -> np.ndarray:
        """Extract zero crossing rate (percussiveness indicator)"""
        try:
            zcr = librosa.feature.zero_crossing_rate(y)
            return np.mean(zcr)
        except:
            return np.array([0.0])

    def _extract_rms_energy(self, y: np.ndarray) -> np.ndarray:
        """Extract RMS energy"""
        try:
            rms = librosa.feature.rms(y=y)
            return np.mean(rms)
        except:
            return np.array([0.0])

    def _extract_tempo(self, y: np.ndarray, sr: int) -> Tuple[float, float]:
        """Extract tempo and beat strength"""
        try:
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_strength = np.mean(librosa.onset.onset_strength(y=y, sr=sr))
            return float(tempo), float(beat_strength)
        except:
            return 0.0, 0.0

    def _extract_chroma(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract chroma features (pitch class)"""
        try:
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            return np.mean(chroma, axis=1)
        except:
            return np.zeros(12)

    def _compute_statistics(self, features: Dict) -> Dict[str, float]:
        """Compute statistical aggregations of features"""
        stats = {}

        # Aggregate key features
        try:
            stats['mean_mfcc'] = float(np.mean(features.get('mfcc', [0])))
            stats['std_mfcc'] = float(np.std(features.get('mfcc', [0])))
            stats['mean_centroid'] = float(features.get('spectral_centroid', 0))
            stats['mean_rolloff'] = float(features.get('spectral_rolloff', 0))
            stats['mean_zcr'] = float(features.get('zero_crossing_rate', 0))
            stats['mean_rms'] = float(features.get('rms_energy', 0))
            stats['tempo'] = float(features.get('tempo', 0))
            stats['beat_strength'] = float(features.get('beat_strength', 0))
        except Exception as e:
            logger.error(f"Error computing statistics: {e}")

        return stats

    def _get_empty_features(self) -> Dict:
        """Return empty feature dict for failed extractions"""
        return {
            'mfcc': np.zeros(13),
            'spectral_centroid': np.array([0.0]),
            'spectral_rolloff': np.array([0.0]),
            'spectral_bandwidth': np.array([0.0]),
            'zero_crossing_rate': np.array([0.0]),
            'rms_energy': np.array([0.0]),
            'tempo': 0.0,
            'beat_strength': 0.0,
            'chroma': np.zeros(12),
            'stats': {}
        }

    def extract_batch_features(self, audio_paths: list) -> Dict[Path, Dict]:
        """Extract features from multiple audio files"""
        results = {}

        for audio_path in audio_paths:
            logger.info(f"Extracting features from {audio_path.name}")
            results[audio_path] = self.extract_features(audio_path)

        return results
