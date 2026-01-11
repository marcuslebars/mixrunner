"""
Session Cleaner - Removes unused files, empty tracks, and optimizes session
"""

from pathlib import Path
from typing import List, Dict, Set
from loguru import logger

from ..logic_interface.session_reader import SessionReader, TrackData
from ..logic_interface.logic_controller import LogicController


class SessionCleaner:
    """
    Cleans and optimizes Logic Pro sessions
    """

    def __init__(
        self,
        controller: LogicController,
        session_reader: SessionReader
    ):
        self.controller = controller
        self.session_reader = session_reader
        self.cleanup_stats = {
            'empty_tracks_removed': 0,
            'unused_files_found': 0,
            'muted_tracks_removed': 0,
        }

    def clean_session(
        self,
        remove_empty: bool = True,
        remove_muted: bool = False,
        find_unused: bool = True
    ) -> Dict[str, any]:
        """
        Perform complete session cleanup

        Args:
            remove_empty: Remove tracks with no regions
            remove_muted: Remove permanently muted tracks
            find_unused: Identify unused audio files

        Returns:
            Cleanup statistics
        """
        logger.info("Starting session cleanup...")

        if remove_empty:
            self._remove_empty_tracks()

        if remove_muted:
            self._remove_muted_tracks()

        if find_unused:
            self._find_unused_files()

        logger.info(f"Cleanup complete: {self.cleanup_stats}")
        return self.cleanup_stats.copy()

    def _remove_empty_tracks(self) -> int:
        """Remove tracks with no audio regions or MIDI data"""
        logger.info("Removing empty tracks...")

        tracks = self.session_reader.get_track_list()
        removed = 0

        # Sort in reverse to avoid index shifting
        for track in sorted(tracks, key=lambda t: t.index, reverse=True):
            if self._is_track_empty(track):
                logger.info(f"Removing empty track {track.index}: {track.name}")
                if self.controller.delete_track(track.index):
                    removed += 1

        self.cleanup_stats['empty_tracks_removed'] = removed
        logger.info(f"Removed {removed} empty tracks")
        return removed

    def _is_track_empty(self, track: TrackData) -> bool:
        """Check if track is empty"""
        # Track is empty if it has no regions and is audio/MIDI type
        if track.track_type not in ['audio', 'midi']:
            return False

        return len(track.regions) == 0

    def _remove_muted_tracks(self) -> int:
        """Remove tracks that are permanently muted"""
        logger.info("Removing muted tracks...")

        tracks = self.session_reader.get_track_list()
        removed = 0

        for track in sorted(tracks, key=lambda t: t.index, reverse=True):
            if track.muted and track.track_type in ['audio', 'midi']:
                logger.info(f"Removing muted track {track.index}: {track.name}")
                if self.controller.delete_track(track.index):
                    removed += 1

        self.cleanup_stats['muted_tracks_removed'] = removed
        logger.info(f"Removed {removed} muted tracks")
        return removed

    def _find_unused_files(self) -> List[Path]:
        """Find audio files not used in the project"""
        logger.info("Finding unused audio files...")

        unused_files = self.session_reader.analyze_unused_files()

        self.cleanup_stats['unused_files_found'] = len(unused_files)

        if unused_files:
            logger.info(f"Found {len(unused_files)} unused audio files:")
            for file_path in unused_files[:10]:  # Show first 10
                logger.info(f"  - {file_path.name}")

            if len(unused_files) > 10:
                logger.info(f"  ... and {len(unused_files) - 10} more")

        return unused_files

    def consolidate_takes(self) -> int:
        """Consolidate take folders to active takes only"""
        # This would require deep Logic Pro API integration
        # Placeholder for now
        logger.info("Take consolidation requires manual Logic Pro operations")
        return 0

    def remove_unused_automation(self) -> int:
        """Remove automation on deleted or unused parameters"""
        # Placeholder - requires Logic Pro API
        logger.info("Automation cleanup requires Logic Pro scripting")
        return 0

    def optimize_audio_files(self, project_path: Path) -> Dict[str, any]:
        """
        Optimize audio files in project
        - Convert to project sample rate
        - Remove duplicates
        - Consolidate formats
        """
        logger.info("Analyzing audio files for optimization...")

        audio_files = self.session_reader.get_audio_files()

        stats = {
            'total_files': len(audio_files),
            'formats': {},
            'sample_rates': {},
            'duplicates_found': 0,
        }

        # Analyze file formats and sample rates
        for audio_file in audio_files:
            try:
                import soundfile as sf
                info = sf.info(audio_file)

                # Track formats
                fmt = audio_file.suffix
                stats['formats'][fmt] = stats['formats'].get(fmt, 0) + 1

                # Track sample rates
                sr = info.samplerate
                stats['sample_rates'][sr] = stats['sample_rates'].get(sr, 0) + 1

            except Exception as e:
                logger.warning(f"Could not analyze {audio_file.name}: {e}")

        # Find potential duplicates by name similarity
        duplicates = self._find_duplicate_files(audio_files)
        stats['duplicates_found'] = len(duplicates)

        logger.info(f"Audio file analysis: {stats}")
        return stats

    def _find_duplicate_files(self, files: List[Path]) -> List[tuple]:
        """Find potentially duplicate files based on names"""
        from difflib import SequenceMatcher

        duplicates = []
        checked = set()

        for i, file1 in enumerate(files):
            if file1 in checked:
                continue

            for file2 in files[i+1:]:
                if file2 in checked:
                    continue

                # Compare file names
                similarity = SequenceMatcher(
                    None,
                    file1.stem.lower(),
                    file2.stem.lower()
                ).ratio()

                if similarity > 0.9:  # 90% similar
                    duplicates.append((file1, file2, similarity))
                    checked.add(file2)

        return duplicates

    def generate_cleanup_report(self) -> str:
        """Generate human-readable cleanup report"""
        report = []
        report.append("=" * 50)
        report.append("SESSION CLEANUP REPORT")
        report.append("=" * 50)

        for key, value in self.cleanup_stats.items():
            label = key.replace('_', ' ').title()
            report.append(f"{label}: {value}")

        report.append("=" * 50)

        return "\n".join(report)
