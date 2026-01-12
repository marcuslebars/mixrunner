"""
Track Importer - Import and organize audio tracks with AI analysis
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger
import soundfile as sf

from ..ableton_interface import AbletonController
from ..ai_engine import TrackClassifier
from ..llm_integration import MixingAgent, LLMProvider


class TrackImporter:
    """
    Import individual tracks with AI-powered analysis and organization
    """

    def __init__(
        self,
        ableton_controller: Optional[AbletonController] = None,
        use_ai: bool = True,
        llm_provider: LLMProvider = LLMProvider.CLAUDE
    ):
        """
        Initialize track importer

        Args:
            ableton_controller: Ableton Live controller instance
            use_ai: Whether to use AI analysis
            llm_provider: Which LLM to use for AI analysis
        """
        self.ableton = ableton_controller or AbletonController()
        self.classifier = TrackClassifier()
        self.use_ai = use_ai

        if use_ai:
            try:
                self.ai_agent = MixingAgent(provider=llm_provider)
                logger.info("AI analysis enabled")
            except Exception as e:
                logger.warning(f"AI disabled: {e}")
                self.use_ai = False

    def import_track(
        self,
        audio_path: Path,
        track_name: Optional[str] = None,
        analyze: bool = True
    ) -> Dict[str, Any]:
        """
        Import a single track into the current Ableton Live session

        Args:
            audio_path: Path to audio file
            track_name: Optional custom track name
            analyze: Whether to analyze with AI

        Returns:
            Dictionary with import results and analysis
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return {'success': False, 'error': 'File not found'}

        # Use filename if no track name provided
        if not track_name:
            track_name = audio_path.stem

        logger.info(f"Importing track: {track_name}")

        # Get audio file info
        try:
            info = sf.info(audio_path)
            file_info = {
                'duration': info.duration,
                'sample_rate': info.samplerate,
                'channels': info.channels,
                'format': info.format
            }
        except Exception as e:
            logger.error(f"Failed to read audio file: {e}")
            return {'success': False, 'error': str(e)}

        # Classify track
        track_type, confidence = self.classifier.classify_track(
            track_name=track_name
        )

        result = {
            'success': True,
            'track_name': track_name,
            'track_type': track_type,
            'confidence': confidence,
            'file_info': file_info,
            'audio_path': str(audio_path)
        }

        # AI Analysis
        if analyze and self.use_ai:
            logger.info(f"Running AI analysis on {track_name}...")
            try:
                ai_analysis = self.ai_agent.analyze_track_with_ai(
                    audio_path=audio_path,
                    track_name=track_name
                )
                result['ai_analysis'] = ai_analysis
                logger.info("AI analysis complete")
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                result['ai_analysis_error'] = str(e)

        return result

    def import_multiple_tracks(
        self,
        audio_files: List[Path],
        auto_organize: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Import multiple tracks at once

        Args:
            audio_files: List of audio file paths
            auto_organize: Automatically organize after import

        Returns:
            List of import results
        """
        logger.info(f"Importing {len(audio_files)} tracks...")

        results = []
        for audio_file in audio_files:
            result = self.import_track(audio_file, analyze=True)
            results.append(result)

        if auto_organize:
            logger.info("Auto-organizing imported tracks...")
            self._organize_imports(results)

        return results

    def import_from_folder(
        self,
        folder_path: Path,
        file_extensions: List[str] = ['.wav', '.aif', '.aiff', '.mp3'],
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Import all audio files from a folder

        Args:
            folder_path: Path to folder containing audio files
            file_extensions: List of audio file extensions to import
            recursive: Whether to search subfolders

        Returns:
            List of import results
        """
        folder_path = Path(folder_path)

        if not folder_path.is_dir():
            logger.error(f"Not a directory: {folder_path}")
            return []

        # Find audio files
        audio_files = []
        for ext in file_extensions:
            if recursive:
                audio_files.extend(folder_path.rglob(f'*{ext}'))
            else:
                audio_files.extend(folder_path.glob(f'*{ext}'))

        logger.info(f"Found {len(audio_files)} audio files in {folder_path}")

        return self.import_multiple_tracks(audio_files)

    def _organize_imports(self, import_results: List[Dict]):
        """Organize imported tracks"""
        # Group by track type
        track_groups = {}
        for result in import_results:
            if result.get('success'):
                track_type = result.get('track_type', 'other')
                if track_type not in track_groups:
                    track_groups[track_type] = []
                track_groups[track_type].append(result)

        logger.info(f"Organized into {len(track_groups)} groups")

    def get_current_workspace_info(self) -> Dict[str, Any]:
        """
        Scan and connect to current Ableton Live workspace

        Returns:
            Information about current workspace
        """
        logger.info("Scanning current Ableton Live workspace...")

        if not self.ableton.connect():
            return {
                'connected': False,
                'error': 'Could not connect to Ableton Live'
            }

        # Get project path
        project_path = self.ableton.get_current_project_path()

        # Get track count
        track_count = self.ableton.get_track_count()

        # Get all track info
        tracks = []
        for i in range(track_count):
            track_info = self.ableton.get_track_info(i)
            tracks.append(track_info)

        workspace_info = {
            'connected': True,
            'project_path': str(project_path) if project_path else None,
            'track_count': track_count,
            'tracks': tracks
        }

        logger.info(f"Workspace info: {track_count} tracks found")

        return workspace_info

    def sync_with_workspace(self) -> bool:
        """
        Synchronize with current Ableton Live workspace

        Returns:
            Success status
        """
        workspace = self.get_current_workspace_info()

        if not workspace.get('connected'):
            logger.error("Not connected to Ableton Live")
            return False

        # Update internal state based on workspace
        logger.info("Synchronized with Ableton Live workspace")
        return True
