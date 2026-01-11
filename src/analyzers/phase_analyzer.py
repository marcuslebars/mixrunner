"""
Phase Analyzer - Detects and analyzes phase issues in stereo tracks
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Tuple, Optional
from loguru import logger


class PhaseAnalyzer:
    """
    Analyzes phase relationships in stereo audio files
    Detects phase cancellation and correlation issues
    """

    def __init__(self):
        self.threshold_warning = 0.3  # Phase correlation warning threshold
        self.threshold_critical = 0.0  # Critical phase issues

    def analyze_stereo_file(self, audio_path: Path) -> Dict[str, any]:
        """
        Analyze phase correlation of a stereo audio file

        Returns:
            Dict with phase analysis results
        """
        try:
            # Load stereo audio
            audio, sr = sf.read(audio_path, always_2d=True)

            if audio.shape[1] < 2:
                logger.warning(f"{audio_path.name} is not stereo")
                return {'is_stereo': False}

            left = audio[:, 0]
            right = audio[:, 1]

            # Calculate phase correlation
            correlation = self._calculate_correlation(left, right)

            # Analyze frequency-dependent phase
            freq_phase = self._analyze_frequency_phase(left, right, sr)

            # Detect phase issues
            issues = self._detect_issues(correlation, freq_phase)

            result = {
                'is_stereo': True,
                'correlation': float(correlation),
                'correlation_status': self._get_correlation_status(correlation),
                'frequency_phase': freq_phase,
                'issues': issues,
                'needs_correction': correlation < self.threshold_warning,
            }

            logger.info(
                f"{audio_path.name}: Phase correlation = {correlation:.3f} "
                f"({result['correlation_status']})"
            )

            return result

        except Exception as e:
            logger.error(f"Phase analysis failed for {audio_path}: {e}")
            return {'error': str(e)}

    def _calculate_correlation(self, left: np.ndarray, right: np.ndarray) -> float:
        """
        Calculate phase correlation between left and right channels
        Returns value between -1 (out of phase) and 1 (in phase)
        """
        # Normalize signals
        left_norm = left / (np.max(np.abs(left)) + 1e-10)
        right_norm = right / (np.max(np.abs(right)) + 1e-10)

        # Calculate correlation
        correlation = np.correlate(left_norm, right_norm, mode='valid')[0] / len(left_norm)

        return float(np.clip(correlation, -1, 1))

    def _analyze_frequency_phase(
        self,
        left: np.ndarray,
        right: np.ndarray,
        sr: int
    ) -> Dict[str, float]:
        """Analyze phase correlation across frequency bands"""
        from scipy import signal

        # Define frequency bands
        bands = {
            'sub': (20, 60),
            'bass': (60, 250),
            'low_mid': (250, 500),
            'mid': (500, 2000),
            'high_mid': (2000, 6000),
            'high': (6000, 20000),
        }

        results = {}

        for band_name, (low_freq, high_freq) in bands.items():
            # Design bandpass filter
            sos = signal.butter(
                4,
                [low_freq, high_freq],
                'bandpass',
                fs=sr,
                output='sos'
            )

            # Filter both channels
            left_filtered = signal.sosfilt(sos, left)
            right_filtered = signal.sosfilt(sos, right)

            # Calculate correlation for this band
            correlation = self._calculate_correlation(left_filtered, right_filtered)
            results[band_name] = float(correlation)

        return results

    def _detect_issues(
        self,
        overall_correlation: float,
        freq_correlations: Dict[str, float]
    ) -> list:
        """Detect specific phase issues"""
        issues = []

        # Overall phase issues
        if overall_correlation < self.threshold_critical:
            issues.append({
                'severity': 'critical',
                'type': 'out_of_phase',
                'description': 'Severe phase cancellation detected',
                'recommendation': 'Flip phase on one channel'
            })
        elif overall_correlation < self.threshold_warning:
            issues.append({
                'severity': 'warning',
                'type': 'phase_issues',
                'description': 'Phase correlation issues detected',
                'recommendation': 'Check stereo imaging and phase'
            })

        # Frequency-specific issues
        for band, correlation in freq_correlations.items():
            if correlation < self.threshold_warning:
                issues.append({
                    'severity': 'warning',
                    'type': 'frequency_phase',
                    'band': band,
                    'correlation': correlation,
                    'description': f'Phase issues in {band} range',
                    'recommendation': f'Check phase in {band} frequencies'
                })

        return issues

    def _get_correlation_status(self, correlation: float) -> str:
        """Get human-readable correlation status"""
        if correlation > 0.9:
            return 'excellent'
        elif correlation > 0.7:
            return 'good'
        elif correlation > 0.3:
            return 'acceptable'
        elif correlation > 0.0:
            return 'poor'
        else:
            return 'out_of_phase'

    def analyze_batch(self, audio_files: list) -> Dict[Path, Dict]:
        """Analyze phase for multiple files"""
        results = {}

        for audio_path in audio_files:
            logger.info(f"Analyzing phase: {audio_path.name}")
            results[audio_path] = self.analyze_stereo_file(audio_path)

        return results

    def suggest_correction(self, analysis_result: Dict) -> Optional[str]:
        """Suggest phase correction strategy"""
        if not analysis_result.get('needs_correction'):
            return None

        correlation = analysis_result.get('correlation', 1.0)

        if correlation < 0:
            return 'invert_phase'  # Flip phase on one channel
        elif correlation < 0.3:
            return 'check_mono_compatibility'  # Issues with mono sum
        else:
            return 'adjust_stereo_width'  # Reduce width
