"""
Audio Normalizer - Applies gain staging and normalization
"""

import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

from ..analyzers.gain_analyzer import GainAnalyzer


class AudioNormalizer:
    """
    Applies normalization and gain staging to audio files
    """

    def __init__(
        self,
        target_lufs: float = -18.0,
        target_peak: float = -6.0,
        backup: bool = True
    ):
        """
        Args:
            target_lufs: Target integrated loudness
            target_peak: Target peak level
            backup: Create backup files before processing
        """
        self.target_lufs = target_lufs
        self.target_peak = target_peak
        self.backup = backup
        self.gain_analyzer = GainAnalyzer(target_lufs, target_peak)

    def normalize_file(
        self,
        audio_path: Path,
        method: str = 'loudness',
        gain_db: Optional[float] = None
    ) -> bool:
        """
        Normalize an audio file

        Args:
            audio_path: Path to audio file
            method: 'peak' or 'loudness'
            gain_db: Manual gain adjustment (optional)

        Returns:
            Success status
        """
        try:
            logger.info(f"Normalizing {audio_path.name} using {method} method")

            # Backup original
            if self.backup:
                self._create_backup(audio_path)

            # Load audio
            audio, sr = sf.read(audio_path, always_2d=True)

            # Analyze if gain not specified
            if gain_db is None:
                analysis = self.gain_analyzer.analyze_file(audio_path)
                gain_db = analysis.get('gain_adjustment_db', 0.0)

            # Apply gain
            if abs(gain_db) > 0.1:  # Only if significant adjustment needed
                logger.info(f"Applying {gain_db:+.1f}dB gain")
                normalized = self._apply_gain(audio, gain_db)

                # Write normalized file
                sf.write(audio_path, normalized, sr)
                logger.info(f"Normalized {audio_path.name}")
                return True
            else:
                logger.info(f"No normalization needed for {audio_path.name}")
                return True

        except Exception as e:
            logger.error(f"Normalization failed for {audio_path}: {e}")
            return False

    def normalize_batch(
        self,
        audio_files: list,
        match_levels: bool = True
    ) -> Dict[Path, bool]:
        """
        Normalize multiple files

        Args:
            audio_files: List of audio file paths
            match_levels: Match all files to same average level

        Returns:
            Dict mapping file paths to success status
        """
        results = {}

        if match_levels:
            # Analyze all files first
            logger.info("Analyzing batch for level matching...")
            analyses = self.gain_analyzer.analyze_batch(audio_files)

            # Calculate batch normalization
            adjustments = self.gain_analyzer.calculate_batch_normalization(analyses)

            # Apply adjustments
            for audio_path in audio_files:
                gain_db = adjustments.get(audio_path, 0.0)
                success = self.normalize_file(
                    audio_path,
                    method='loudness',
                    gain_db=gain_db
                )
                results[audio_path] = success
        else:
            # Normalize each independently
            for audio_path in audio_files:
                success = self.normalize_file(audio_path, method='loudness')
                results[audio_path] = success

        return results

    def _apply_gain(self, audio: np.ndarray, gain_db: float) -> np.ndarray:
        """Apply gain in dB to audio"""
        gain_linear = 10 ** (gain_db / 20.0)
        normalized = audio * gain_linear

        # Prevent clipping
        peak = np.max(np.abs(normalized))
        if peak > 0.99:
            safety_gain = 0.99 / peak
            normalized *= safety_gain
            logger.warning(f"Applied safety limiting: {20*np.log10(safety_gain):.1f}dB")

        return normalized

    def peak_normalize(
        self,
        audio_path: Path,
        target_db: float = -6.0
    ) -> bool:
        """Normalize to target peak level"""
        try:
            audio, sr = sf.read(audio_path, always_2d=True)

            # Find current peak
            current_peak = np.max(np.abs(audio))

            if current_peak == 0:
                logger.warning(f"{audio_path.name} is silent")
                return False

            # Calculate required gain
            current_peak_db = 20 * np.log10(current_peak)
            gain_db = target_db - current_peak_db

            # Apply normalization
            return self.normalize_file(audio_path, method='peak', gain_db=gain_db)

        except Exception as e:
            logger.error(f"Peak normalization failed: {e}")
            return False

    def rms_normalize(
        self,
        audio_path: Path,
        target_db: float = -18.0
    ) -> bool:
        """Normalize to target RMS level"""
        try:
            audio, sr = sf.read(audio_path, always_2d=True)

            # Calculate current RMS
            rms = np.sqrt(np.mean(audio ** 2))

            if rms == 0:
                logger.warning(f"{audio_path.name} is silent")
                return False

            # Calculate required gain
            current_rms_db = 20 * np.log10(rms)
            gain_db = target_db - current_rms_db

            # Apply normalization
            return self.normalize_file(audio_path, method='loudness', gain_db=gain_db)

        except Exception as e:
            logger.error(f"RMS normalization failed: {e}")
            return False

    def _create_backup(self, audio_path: Path) -> bool:
        """Create backup of original file"""
        try:
            backup_path = audio_path.with_suffix(audio_path.suffix + '.backup')

            if not backup_path.exists():
                import shutil
                shutil.copy2(audio_path, backup_path)
                logger.debug(f"Created backup: {backup_path.name}")

            return True

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False

    def restore_from_backup(self, audio_path: Path) -> bool:
        """Restore file from backup"""
        try:
            backup_path = audio_path.with_suffix(audio_path.suffix + '.backup')

            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, audio_path)
                logger.info(f"Restored from backup: {audio_path.name}")
                return True
            else:
                logger.warning(f"No backup found for {audio_path.name}")
                return False

        except Exception as e:
            logger.error(f"Restore from backup failed: {e}")
            return False

    def cleanup_backups(self, directory: Path) -> int:
        """Remove all backup files in directory"""
        backup_files = list(directory.rglob('*.backup'))

        removed = 0
        for backup_file in backup_files:
            try:
                backup_file.unlink()
                removed += 1
            except Exception as e:
                logger.error(f"Failed to remove backup {backup_file}: {e}")

        logger.info(f"Removed {removed} backup files")
        return removed
