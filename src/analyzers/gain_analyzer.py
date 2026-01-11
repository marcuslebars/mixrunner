"""
Gain Analyzer - Analyzes levels and suggests gain staging
"""

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pathlib import Path
from typing import Dict, Optional, Tuple
from loguru import logger


class GainAnalyzer:
    """
    Analyzes audio levels and provides gain staging recommendations
    """

    def __init__(
        self,
        target_lufs: float = -18.0,
        target_peak: float = -6.0,
        headroom_db: float = 6.0
    ):
        """
        Args:
            target_lufs: Target integrated loudness (LUFS)
            target_peak: Target peak level (dBFS)
            headroom_db: Desired headroom in dB
        """
        self.target_lufs = target_lufs
        self.target_peak = target_peak
        self.headroom_db = headroom_db
        self.meter = pyln.Meter(48000)  # Will update based on actual SR

    def analyze_file(self, audio_path: Path) -> Dict[str, any]:
        """
        Analyze gain levels of an audio file

        Returns comprehensive level analysis
        """
        try:
            # Load audio
            audio, sr = sf.read(audio_path, always_2d=True)

            # Update meter sample rate
            self.meter = pyln.Meter(sr)

            # Convert to mono for loudness measurement if stereo
            if audio.shape[1] > 1:
                audio_mono = np.mean(audio, axis=1)
            else:
                audio_mono = audio[:, 0]

            # Measurements
            peak_db = self._calculate_peak(audio)
            rms_db = self._calculate_rms(audio_mono)
            lufs = self._calculate_lufs(audio_mono, sr)
            crest_factor = self._calculate_crest_factor(audio_mono)
            dynamic_range = self._calculate_dynamic_range(audio_mono)

            # Determine gain adjustment needed
            gain_adjustment = self._calculate_gain_adjustment(peak_db, lufs)

            # Check for issues
            issues = self._detect_issues(peak_db, lufs, crest_factor)

            result = {
                'peak_db': float(peak_db),
                'rms_db': float(rms_db),
                'lufs': float(lufs),
                'crest_factor': float(crest_factor),
                'dynamic_range': float(dynamic_range),
                'headroom': float(0.0 - peak_db),  # Headroom to 0dBFS
                'gain_adjustment_db': float(gain_adjustment),
                'is_clipping': peak_db >= -0.1,
                'is_too_quiet': lufs < -30.0,
                'is_too_loud': lufs > -6.0,
                'issues': issues,
                'status': self._get_level_status(peak_db, lufs),
            }

            logger.info(
                f"{audio_path.name}: Peak={peak_db:.1f}dB, "
                f"LUFS={lufs:.1f}, Status={result['status']}"
            )

            return result

        except Exception as e:
            logger.error(f"Gain analysis failed for {audio_path}: {e}")
            return {'error': str(e)}

    def _calculate_peak(self, audio: np.ndarray) -> float:
        """Calculate true peak level in dBFS"""
        peak = np.max(np.abs(audio))
        if peak == 0:
            return -np.inf
        return float(20 * np.log10(peak))

    def _calculate_rms(self, audio: np.ndarray) -> float:
        """Calculate RMS level in dBFS"""
        rms = np.sqrt(np.mean(audio ** 2))
        if rms == 0:
            return -np.inf
        return float(20 * np.log10(rms))

    def _calculate_lufs(self, audio: np.ndarray, sr: int) -> float:
        """Calculate integrated loudness (LUFS)"""
        try:
            loudness = self.meter.integrated_loudness(audio)
            return float(loudness)
        except:
            return -np.inf

    def _calculate_crest_factor(self, audio: np.ndarray) -> float:
        """Calculate crest factor (peak to RMS ratio) in dB"""
        peak = np.max(np.abs(audio))
        rms = np.sqrt(np.mean(audio ** 2))

        if rms == 0:
            return 0.0

        crest_factor_db = 20 * np.log10(peak / rms)
        return float(crest_factor_db)

    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Estimate dynamic range using percentile method"""
        # Use 95th percentile as "loud" and 5th as "quiet"
        loud = np.percentile(np.abs(audio), 95)
        quiet = np.percentile(np.abs(audio), 5)

        if quiet == 0:
            return np.inf

        dynamic_range = 20 * np.log10(loud / quiet)
        return float(dynamic_range)

    def _calculate_gain_adjustment(self, peak_db: float, lufs: float) -> float:
        """Calculate recommended gain adjustment"""
        # Target is to hit target LUFS while maintaining headroom

        # Calculate gain needed to reach target LUFS
        lufs_adjustment = self.target_lufs - lufs

        # Calculate what peak would be after adjustment
        projected_peak = peak_db + lufs_adjustment

        # If projected peak would exceed target, limit by peak instead
        if projected_peak > self.target_peak:
            return self.target_peak - peak_db
        else:
            return lufs_adjustment

    def _detect_issues(
        self,
        peak_db: float,
        lufs: float,
        crest_factor: float
    ) -> list:
        """Detect gain-related issues"""
        issues = []

        # Clipping
        if peak_db >= -0.1:
            issues.append({
                'severity': 'critical',
                'type': 'clipping',
                'description': 'Audio is clipping',
                'recommendation': f'Reduce gain by at least {abs(peak_db) + self.headroom_db:.1f}dB'
            })

        # Insufficient headroom
        elif peak_db > -3.0:
            issues.append({
                'severity': 'warning',
                'type': 'low_headroom',
                'description': 'Insufficient headroom',
                'recommendation': f'Reduce gain by {abs(peak_db + self.headroom_db):.1f}dB'
            })

        # Too quiet
        if lufs < -40.0:
            issues.append({
                'severity': 'warning',
                'type': 'too_quiet',
                'description': 'Audio level too low',
                'recommendation': f'Increase gain by approximately {self.target_lufs - lufs:.1f}dB'
            })

        # Over-compressed (low crest factor)
        if crest_factor < 3.0:
            issues.append({
                'severity': 'info',
                'type': 'over_compressed',
                'description': 'Low dynamic range detected',
                'recommendation': 'Audio may be over-compressed'
            })

        # Very high crest factor (might be problematic)
        if crest_factor > 20.0:
            issues.append({
                'severity': 'info',
                'type': 'high_crest',
                'description': 'Very high crest factor',
                'recommendation': 'Consider gentle compression for more consistent levels'
            })

        return issues

    def _get_level_status(self, peak_db: float, lufs: float) -> str:
        """Get human-readable status"""
        if peak_db >= -0.1:
            return 'clipping'
        elif peak_db > -3.0:
            return 'too_hot'
        elif lufs < -40.0:
            return 'too_quiet'
        elif -self.headroom_db <= peak_db <= -3.0 and -25.0 <= lufs <= -12.0:
            return 'optimal'
        else:
            return 'acceptable'

    def normalize_recommendations(self, analysis: Dict) -> Dict[str, float]:
        """
        Generate specific normalization recommendations

        Returns dict with 'gain_db' and 'method'
        """
        return {
            'gain_db': analysis.get('gain_adjustment_db', 0.0),
            'method': 'peak' if analysis.get('is_clipping') else 'loudness',
            'target_peak': self.target_peak,
            'target_lufs': self.target_lufs,
        }

    def analyze_batch(self, audio_files: list) -> Dict[Path, Dict]:
        """Analyze gain for multiple files"""
        results = {}

        for audio_path in audio_files:
            logger.info(f"Analyzing gain: {audio_path.name}")
            results[audio_path] = self.analyze_file(audio_path)

        return results

    def calculate_batch_normalization(
        self,
        analyses: Dict[Path, Dict]
    ) -> Dict[Path, float]:
        """
        Calculate normalization for a batch to match levels

        Returns gain adjustments for each file
        """
        # Find median LUFS
        lufs_values = [
            a.get('lufs', -18.0)
            for a in analyses.values()
            if not np.isinf(a.get('lufs', -np.inf))
        ]

        if not lufs_values:
            return {}

        target = np.median(lufs_values)

        # Calculate adjustments
        adjustments = {}
        for path, analysis in analyses.items():
            current_lufs = analysis.get('lufs', target)
            if np.isinf(current_lufs):
                adjustments[path] = 0.0
            else:
                adjustments[path] = target - current_lufs

        logger.info(f"Batch normalization target: {target:.1f} LUFS")
        return adjustments
