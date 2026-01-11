"""
Frequency Analyzer - Analyzes frequency content and suggests EQ
"""

import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple
from loguru import logger


class FrequencyAnalyzer:
    """
    Analyzes frequency content of audio files
    Detects issues like low-end buildup, harshness, etc.
    """

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

        # Frequency bands for analysis
        self.bands = {
            'sub_bass': (20, 60),
            'bass': (60, 250),
            'low_mids': (250, 500),
            'mids': (500, 2000),
            'high_mids': (2000, 6000),
            'presence': (6000, 12000),
            'brilliance': (12000, 20000),
        }

    def analyze_file(self, audio_path: Path) -> Dict[str, any]:
        """
        Analyze frequency content of audio file

        Returns detailed frequency analysis
        """
        try:
            # Load audio
            audio, sr = sf.read(audio_path)

            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Calculate spectrum
            spectrum = self._calculate_spectrum(audio, sr)

            # Analyze frequency bands
            band_energy = self._analyze_bands(audio, sr)

            # Detect issues
            issues = self._detect_frequency_issues(band_energy, spectrum)

            # Calculate spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]

            result = {
                'band_energy': band_energy,
                'spectral_centroid_hz': float(np.mean(spectral_centroid)),
                'spectral_rolloff_hz': float(np.mean(spectral_rolloff)),
                'brightness': self._calculate_brightness(band_energy),
                'low_end_balance': self._calculate_low_end_balance(band_energy),
                'issues': issues,
                'eq_suggestions': self._generate_eq_suggestions(band_energy, issues),
            }

            logger.info(
                f"{audio_path.name}: Centroid={result['spectral_centroid_hz']:.0f}Hz, "
                f"Brightness={result['brightness']:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Frequency analysis failed for {audio_path}: {e}")
            return {'error': str(e)}

    def _calculate_spectrum(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Calculate frequency spectrum using FFT"""
        # Use STFT for better frequency resolution
        D = librosa.stft(audio, n_fft=4096)
        magnitude = np.abs(D)
        return np.mean(magnitude, axis=1)

    def _analyze_bands(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Calculate energy in each frequency band"""
        from scipy import signal

        band_energies = {}

        for band_name, (low_freq, high_freq) in self.bands.items():
            # Design bandpass filter
            sos = signal.butter(
                4,
                [low_freq, min(high_freq, sr/2 - 100)],
                'bandpass',
                fs=sr,
                output='sos'
            )

            # Filter audio
            filtered = signal.sosfilt(sos, audio)

            # Calculate RMS energy
            energy = np.sqrt(np.mean(filtered ** 2))

            # Convert to dB
            if energy > 0:
                energy_db = 20 * np.log10(energy)
            else:
                energy_db = -np.inf

            band_energies[band_name] = float(energy_db)

        return band_energies

    def _calculate_brightness(self, band_energy: Dict[str, float]) -> float:
        """
        Calculate brightness metric (0-1)
        Higher values = brighter sound
        """
        # Weight high frequency bands more
        weights = {
            'sub_bass': 0.05,
            'bass': 0.1,
            'low_mids': 0.15,
            'mids': 0.2,
            'high_mids': 0.25,
            'presence': 0.15,
            'brilliance': 0.1,
        }

        # Normalize energies
        energies = []
        for band, weight in weights.items():
            energy = band_energy.get(band, -np.inf)
            if not np.isinf(energy):
                energies.append(energy * weight)

        if not energies:
            return 0.5

        # Normalize to 0-1 range
        brightness = np.clip(np.mean(energies) / 20.0 + 0.5, 0, 1)
        return float(brightness)

    def _calculate_low_end_balance(self, band_energy: Dict[str, float]) -> float:
        """
        Calculate low-end balance
        Returns ratio of bass to sub-bass
        """
        bass = band_energy.get('bass', -np.inf)
        sub_bass = band_energy.get('sub_bass', -np.inf)

        if np.isinf(bass) or np.isinf(sub_bass):
            return 1.0

        # Calculate ratio
        balance = bass - sub_bass  # dB difference
        return float(balance)

    def _detect_frequency_issues(
        self,
        band_energy: Dict[str, float],
        spectrum: np.ndarray
    ) -> List[Dict]:
        """Detect frequency-related issues"""
        issues = []

        # Too much sub-bass
        sub_bass = band_energy.get('sub_bass', -np.inf)
        bass = band_energy.get('bass', -np.inf)

        if not np.isinf(sub_bass) and not np.isinf(bass):
            if sub_bass > bass + 3:
                issues.append({
                    'severity': 'warning',
                    'type': 'excessive_sub_bass',
                    'description': 'Excessive sub-bass content',
                    'recommendation': 'Apply high-pass filter around 30-40Hz'
                })

        # Muddy low-mids
        low_mids = band_energy.get('low_mids', -np.inf)
        mids = band_energy.get('mids', -np.inf)

        if not np.isinf(low_mids) and not np.isinf(mids):
            if low_mids > mids + 5:
                issues.append({
                    'severity': 'warning',
                    'type': 'muddy_low_mids',
                    'description': 'Buildup in low-mids (200-500Hz)',
                    'recommendation': 'Reduce 250-500Hz by 2-4dB'
                })

        # Harsh high-mids
        high_mids = band_energy.get('high_mids', -np.inf)
        presence = band_energy.get('presence', -np.inf)

        if not np.isinf(high_mids) and high_mids > -10:
            if not np.isinf(presence) and high_mids > presence + 6:
                issues.append({
                    'severity': 'info',
                    'type': 'harsh_high_mids',
                    'description': 'Potential harshness in 2-6kHz range',
                    'recommendation': 'Check for resonances around 3-4kHz'
                })

        # Lack of presence
        if not np.isinf(presence) and presence < -20:
            issues.append({
                'severity': 'info',
                'type': 'lack_of_presence',
                'description': 'Low presence frequencies',
                'recommendation': 'Consider boosting 6-10kHz for clarity'
            })

        # Too dark
        brilliance = band_energy.get('brilliance', -np.inf)
        if not np.isinf(brilliance) and brilliance < -25:
            issues.append({
                'severity': 'info',
                'type': 'dark_sound',
                'description': 'Lacking high-frequency content',
                'recommendation': 'Add air with shelf boost above 12kHz'
            })

        return issues

    def _generate_eq_suggestions(
        self,
        band_energy: Dict[str, float],
        issues: List[Dict]
    ) -> List[Dict]:
        """Generate EQ suggestions based on analysis"""
        suggestions = []

        for issue in issues:
            issue_type = issue.get('type')

            if issue_type == 'excessive_sub_bass':
                suggestions.append({
                    'type': 'high_pass',
                    'frequency': 35,
                    'slope': '12dB/oct',
                    'description': 'Remove rumble'
                })

            elif issue_type == 'muddy_low_mids':
                suggestions.append({
                    'type': 'cut',
                    'frequency': 350,
                    'q': 1.0,
                    'gain': -3,
                    'description': 'Reduce muddiness'
                })

            elif issue_type == 'harsh_high_mids':
                suggestions.append({
                    'type': 'cut',
                    'frequency': 3500,
                    'q': 2.0,
                    'gain': -2,
                    'description': 'Tame harshness'
                })

            elif issue_type == 'lack_of_presence':
                suggestions.append({
                    'type': 'boost',
                    'frequency': 8000,
                    'q': 1.5,
                    'gain': 2,
                    'description': 'Add presence'
                })

            elif issue_type == 'dark_sound':
                suggestions.append({
                    'type': 'high_shelf',
                    'frequency': 12000,
                    'gain': 2,
                    'description': 'Add air and sparkle'
                })

        return suggestions

    def analyze_batch(self, audio_files: List[Path]) -> Dict[Path, Dict]:
        """Analyze frequency content for multiple files"""
        results = {}

        for audio_path in audio_files:
            logger.info(f"Analyzing frequency content: {audio_path.name}")
            results[audio_path] = self.analyze_file(audio_path)

        return results

    def compare_spectral_balance(
        self,
        analyses: Dict[Path, Dict]
    ) -> Dict[str, any]:
        """
        Compare spectral balance across multiple tracks
        Useful for identifying outliers
        """
        # Collect all brightness values
        brightness_values = [
            a.get('brightness', 0.5)
            for a in analyses.values()
            if 'brightness' in a
        ]

        if not brightness_values:
            return {}

        avg_brightness = np.mean(brightness_values)
        std_brightness = np.std(brightness_values)

        # Find outliers
        outliers = []
        for path, analysis in analyses.items():
            brightness = analysis.get('brightness', avg_brightness)
            deviation = abs(brightness - avg_brightness)

            if deviation > 2 * std_brightness:
                outliers.append({
                    'file': path.name,
                    'brightness': brightness,
                    'deviation': deviation,
                    'status': 'too_bright' if brightness > avg_brightness else 'too_dark'
                })

        return {
            'average_brightness': float(avg_brightness),
            'std_brightness': float(std_brightness),
            'outliers': outliers,
        }
