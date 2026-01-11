"""
Mix Readiness Engine - Main orchestrator for session preparation
"""

from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger
import sys

from .logic_interface import LogicController, SessionReader, TrackManager
from .ai_engine import TrackClassifier, AudioFeatureExtractor
from .analyzers import PhaseAnalyzer, GainAnalyzer, FrequencyAnalyzer
from .processors import SessionCleaner, AudioNormalizer


class MixReadinessEngine:
    """
    Main engine that orchestrates the complete mix preparation workflow
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Mix Readiness Engine

        Args:
            config: Optional configuration dict
        """
        self.config = config or self._default_config()

        # Initialize components
        self.logic_controller = LogicController()
        self.session_reader: Optional[SessionReader] = None
        self.track_manager: Optional[TrackManager] = None
        self.track_classifier = TrackClassifier()

        # Analyzers
        self.phase_analyzer = PhaseAnalyzer()
        self.gain_analyzer = GainAnalyzer(
            target_lufs=self.config['target_lufs'],
            target_peak=self.config['target_peak']
        )
        self.frequency_analyzer = FrequencyAnalyzer()

        # Processors
        self.session_cleaner: Optional[SessionCleaner] = None
        self.audio_normalizer = AudioNormalizer(
            target_lufs=self.config['target_lufs'],
            target_peak=self.config['target_peak']
        )

        # Session state
        self.project_path: Optional[Path] = None
        self.analysis_results: Dict = {}
        self.track_classifications: Dict = {}

        logger.info("Mix Readiness Engine initialized")

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'target_lufs': -18.0,
            'target_peak': -6.0,
            'auto_color_tracks': True,
            'auto_organize': True,
            'create_buses': True,
            'remove_empty_tracks': True,
            'normalize_audio': True,
            'check_phase': True,
        }

    def connect_to_logic(self) -> bool:
        """Connect to Logic Pro"""
        logger.info("Connecting to Logic Pro...")
        success = self.logic_controller.connect()

        if success:
            logger.info("Connected to Logic Pro")
        else:
            logger.error("Failed to connect to Logic Pro")

        return success

    def analyze_session(self, project_path: Optional[Path] = None) -> Dict:
        """
        Analyze current Logic Pro session

        Args:
            project_path: Optional path to project file

        Returns:
            Comprehensive analysis results
        """
        logger.info("=" * 60)
        logger.info("ANALYZING SESSION")
        logger.info("=" * 60)

        # Get project path
        if project_path:
            self.project_path = Path(project_path)
        else:
            self.project_path = self.logic_controller.get_current_project_path()

        if not self.project_path:
            logger.error("No project loaded in Logic Pro")
            return {}

        logger.info(f"Project: {self.project_path.name}")

        # Initialize session reader
        self.session_reader = SessionReader(self.project_path)
        self.session_reader.read_session()

        # Initialize track manager
        self.track_manager = TrackManager(self.logic_controller)

        # Initialize session cleaner
        self.session_cleaner = SessionCleaner(
            self.logic_controller,
            self.session_reader
        )

        # Get session info
        session_info = self.session_reader.get_project_info()
        logger.info(f"Tracks: {session_info['track_count']}")
        logger.info(f"Audio files: {session_info['audio_file_count']}")
        logger.info(f"Sample rate: {session_info['sample_rate']} Hz")

        # Analyze tracks
        logger.info("\nClassifying tracks...")
        self._classify_tracks()

        # Analyze audio files
        logger.info("\nAnalyzing audio files...")
        audio_files = self.session_reader.get_audio_files()

        if audio_files:
            self._analyze_audio_files(audio_files[:10])  # Limit to first 10 for demo

        # Get session statistics
        stats = self.session_reader.get_session_statistics()

        self.analysis_results = {
            'session_info': session_info,
            'session_stats': stats,
            'track_classifications': self.track_classifications,
            'audio_analysis': getattr(self, '_audio_analysis', {}),
        }

        logger.info("\nAnalysis complete!")
        return self.analysis_results

    def _classify_tracks(self):
        """Classify all tracks in session"""
        track_count = self.logic_controller.get_track_count()

        tracks_to_classify = []

        for i in range(1, track_count + 1):
            track_info = self.logic_controller.get_track_info(i)
            tracks_to_classify.append({
                'index': i,
                'name': track_info.get('name', ''),
            })

        # Classify using AI
        classifications = self.track_classifier.classify_batch(tracks_to_classify)

        # Store results
        self.track_classifications = {}
        for track_idx, (category, confidence) in classifications.items():
            self.track_classifications[track_idx] = {
                'category': category,
                'confidence': confidence,
            }

    def _analyze_audio_files(self, audio_files: List[Path]):
        """Analyze audio files for technical issues"""
        self._audio_analysis = {
            'phase': {},
            'gain': {},
            'frequency': {},
        }

        for audio_file in audio_files[:5]:  # Limit for demo
            # Phase analysis
            if audio_file.suffix in ['.wav', '.aif', '.aiff']:
                try:
                    phase_result = self.phase_analyzer.analyze_stereo_file(audio_file)
                    self._audio_analysis['phase'][audio_file] = phase_result
                except Exception as e:
                    logger.warning(f"Phase analysis failed for {audio_file.name}: {e}")

            # Gain analysis
            try:
                gain_result = self.gain_analyzer.analyze_file(audio_file)
                self._audio_analysis['gain'][audio_file] = gain_result
            except Exception as e:
                logger.warning(f"Gain analysis failed for {audio_file.name}: {e}")

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        if not self.analysis_results:
            return "No analysis results available. Run analyze_session() first."

        lines = []
        lines.append("=" * 70)
        lines.append("MIX READINESS ANALYSIS REPORT")
        lines.append("=" * 70)

        # Session info
        session_info = self.analysis_results.get('session_info', {})
        lines.append(f"\nProject: {session_info.get('name', 'Unknown')}")
        lines.append(f"Sample Rate: {session_info.get('sample_rate', 0)} Hz")
        lines.append(f"Total Tracks: {session_info.get('track_count', 0)}")
        lines.append(f"Audio Files: {session_info.get('audio_file_count', 0)}")

        # Track breakdown
        lines.append("\n" + "-" * 70)
        lines.append("TRACK CLASSIFICATION")
        lines.append("-" * 70)

        category_counts = {}
        for track_data in self.track_classifications.values():
            category = track_data['category']
            category_counts[category] = category_counts.get(category, 0) + 1

        for category, count in sorted(category_counts.items()):
            lines.append(f"  {category.replace('_', ' ').title()}: {count}")

        # Issues found
        lines.append("\n" + "-" * 70)
        lines.append("ISSUES DETECTED")
        lines.append("-" * 70)

        stats = self.analysis_results.get('session_stats', {})
        if stats.get('empty_tracks', 0) > 0:
            lines.append(f"  ⚠ Empty tracks: {stats['empty_tracks']}")
        if stats.get('muted_tracks', 0) > 0:
            lines.append(f"  ⚠ Muted tracks: {stats['muted_tracks']}")

        # Audio issues
        audio_analysis = self.analysis_results.get('audio_analysis', {})
        gain_issues = sum(
            1 for g in audio_analysis.get('gain', {}).values()
            if g.get('issues', [])
        )
        if gain_issues > 0:
            lines.append(f"  ⚠ Files with gain issues: {gain_issues}")

        phase_issues = sum(
            1 for p in audio_analysis.get('phase', {}).values()
            if p.get('needs_correction', False)
        )
        if phase_issues > 0:
            lines.append(f"  ⚠ Files with phase issues: {phase_issues}")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)

    def apply_cleanup(self) -> bool:
        """Apply session cleanup"""
        if not self.session_cleaner:
            logger.error("No session loaded")
            return False

        logger.info("Applying session cleanup...")

        self.session_cleaner.clean_session(
            remove_empty=self.config['remove_empty_tracks'],
            remove_muted=False,  # Keep muted for safety
            find_unused=True
        )

        return True

    def organize_tracks(self) -> bool:
        """Organize tracks by type"""
        if not self.track_manager or not self.track_classifications:
            logger.error("No session analyzed")
            return False

        logger.info("Organizing tracks...")

        # Convert classifications to simple dict
        classifications = {
            idx: data['category']
            for idx, data in self.track_classifications.items()
        }

        # Organize by type
        if self.config['auto_organize']:
            self.track_manager.organize_tracks_by_type(classifications)

        # Apply color scheme
        if self.config['auto_color_tracks']:
            self.track_manager.apply_color_scheme(classifications)

        # Rename tracks
        self.track_manager.rename_tracks_by_convention(classifications)

        logger.info("Track organization complete")
        return True

    def normalize_technical(self) -> bool:
        """Apply technical normalization"""
        if not self.session_reader:
            logger.error("No session loaded")
            return False

        logger.info("Applying technical normalization...")

        audio_files = self.session_reader.get_audio_files()

        if not audio_files:
            logger.warning("No audio files to normalize")
            return True

        # Normalize audio levels
        if self.config['normalize_audio']:
            logger.info(f"Normalizing {len(audio_files)} audio files...")
            self.audio_normalizer.normalize_batch(
                audio_files[:10],  # Limit for demo
                match_levels=True
            )

        logger.info("Technical normalization complete")
        return True

    def export_session(self, output_path: Optional[Path] = None) -> bool:
        """Save optimized session"""
        logger.info("Saving optimized session...")

        success = self.logic_controller.save_project()

        if success:
            logger.info("Session saved successfully")
        else:
            logger.error("Failed to save session")

        return success

    def run_full_workflow(self) -> bool:
        """
        Run complete mix readiness workflow:
        1. Connect to Logic
        2. Analyze session
        3. Clean up
        4. Organize tracks
        5. Normalize
        6. Save
        """
        logger.info("=" * 70)
        logger.info("STARTING FULL MIX READINESS WORKFLOW")
        logger.info("=" * 70)

        # Step 1: Connect
        if not self.connect_to_logic():
            return False

        # Step 2: Analyze
        self.analyze_session()
        print("\n" + self.generate_report())

        # Step 3: Cleanup
        self.apply_cleanup()

        # Step 4: Organize
        self.organize_tracks()

        # Step 5: Normalize
        self.normalize_technical()

        # Step 6: Save
        self.export_session()

        logger.info("=" * 70)
        logger.info("MIX READINESS WORKFLOW COMPLETE!")
        logger.info("=" * 70)

        return True


def main():
    """CLI entry point"""
    logger.add(sys.stderr, level="INFO")

    engine = MixReadinessEngine()
    engine.run_full_workflow()


if __name__ == '__main__':
    main()
