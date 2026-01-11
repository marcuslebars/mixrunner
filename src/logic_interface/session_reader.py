"""
Session Reader - Reads and parses Logic Pro session data
"""

import plistlib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class AudioRegion:
    """Represents an audio region in Logic Pro"""
    name: str
    start_position: float
    length: float
    file_path: Optional[Path] = None
    is_muted: bool = False
    gain: float = 0.0


@dataclass
class TrackData:
    """Complete track data structure"""
    index: int
    name: str
    track_type: str  # 'audio', 'midi', 'aux', 'master'
    color: Optional[int] = None
    muted: bool = False
    solo: bool = False
    volume: float = 0.0
    pan: float = 0.0
    regions: List[AudioRegion] = None
    plugin_chain: List[str] = None
    sends: List[Dict] = None

    def __post_init__(self):
        if self.regions is None:
            self.regions = []
        if self.plugin_chain is None:
            self.plugin_chain = []
        if self.sends is None:
            self.sends = []


class SessionReader:
    """
    Reads Logic Pro session files and extracts data
    Logic Pro sessions are stored as packages (.logicx)
    """

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.session_data: Dict[str, Any] = {}
        self.tracks: List[TrackData] = []

    def read_session(self) -> bool:
        """Read and parse Logic Pro session"""
        try:
            if not self.project_path.exists():
                logger.error(f"Project not found: {self.project_path}")
                return False

            # Logic Pro X uses a package format
            if self.project_path.suffix == '.logicx':
                return self._read_logicx_session()
            else:
                logger.error("Unsupported project format")
                return False

        except Exception as e:
            logger.error(f"Failed to read session: {e}")
            return False

    def _read_logicx_session(self) -> bool:
        """Read Logic Pro X package format"""
        try:
            # Main project file locations
            alternatives_path = self.project_path / "Alternatives"
            resources_path = self.project_path / "Resources"
            media_path = self.project_path / "Media"

            # Try to find project data
            # Logic uses various internal formats, this is a simplified reader
            logger.info(f"Reading Logic Pro X project: {self.project_path.name}")

            # Read audio files
            audio_files = self._get_audio_files(media_path)
            logger.info(f"Found {len(audio_files)} audio files")

            self.session_data = {
                'project_name': self.project_path.stem,
                'audio_files': audio_files,
                'sample_rate': self._detect_sample_rate(audio_files),
            }

            return True

        except Exception as e:
            logger.error(f"Failed to read .logicx format: {e}")
            return False

    def _get_audio_files(self, media_path: Path) -> List[Path]:
        """Get all audio files in project"""
        audio_files = []
        if not media_path.exists():
            return audio_files

        audio_extensions = {'.wav', '.aif', '.aiff', '.mp3', '.m4a', '.caf'}

        for ext in audio_extensions:
            audio_files.extend(media_path.rglob(f'*{ext}'))

        return audio_files

    def _detect_sample_rate(self, audio_files: List[Path]) -> int:
        """Detect project sample rate from audio files"""
        try:
            if not audio_files:
                return 48000  # Default

            # Use soundfile to check first audio file
            import soundfile as sf
            info = sf.info(audio_files[0])
            return info.samplerate
        except Exception as e:
            logger.warning(f"Could not detect sample rate: {e}")
            return 48000

    def get_track_list(self) -> List[TrackData]:
        """Get list of all tracks with their data"""
        return self.tracks

    def get_audio_files(self) -> List[Path]:
        """Get all audio files in project"""
        return self.session_data.get('audio_files', [])

    def get_project_info(self) -> Dict[str, Any]:
        """Get general project information"""
        return {
            'name': self.session_data.get('project_name', ''),
            'sample_rate': self.session_data.get('sample_rate', 48000),
            'audio_file_count': len(self.session_data.get('audio_files', [])),
            'track_count': len(self.tracks),
        }

    def analyze_unused_files(self) -> List[Path]:
        """Find audio files not used in the project"""
        # This would require deeper analysis of region references
        # Simplified implementation
        used_files = set()
        for track in self.tracks:
            for region in track.regions:
                if region.file_path:
                    used_files.add(region.file_path)

        all_files = set(self.get_audio_files())
        return list(all_files - used_files)

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        stats = {
            'total_tracks': len(self.tracks),
            'audio_tracks': sum(1 for t in self.tracks if t.track_type == 'audio'),
            'midi_tracks': sum(1 for t in self.tracks if t.track_type == 'midi'),
            'aux_tracks': sum(1 for t in self.tracks if t.track_type == 'aux'),
            'muted_tracks': sum(1 for t in self.tracks if t.muted),
            'empty_tracks': sum(1 for t in self.tracks if not t.regions),
            'total_regions': sum(len(t.regions) for t in self.tracks),
            'audio_files': len(self.get_audio_files()),
            'sample_rate': self.session_data.get('sample_rate', 0),
        }
        return stats
