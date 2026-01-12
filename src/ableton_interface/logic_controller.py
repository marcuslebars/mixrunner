"""
Logic Pro Controller - Main interface for communicating with Logic Pro
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class LogicController:
    """
    Controls Logic Pro via AppleScript/JXA
    Provides high-level interface for session manipulation
    """

    def __init__(self):
        self.app_name = "Logic Pro"
        self.is_connected = False
        self.current_project_path: Optional[Path] = None

    def connect(self) -> bool:
        """Establish connection to Logic Pro"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    if it is running then
                        return true
                    else
                        return false
                    end if
                end tell
            '''
            result = self._run_applescript(script)
            self.is_connected = result.strip().lower() == 'true'
            logger.info(f"Logic Pro connection: {self.is_connected}")
            return self.is_connected
        except Exception as e:
            logger.error(f"Failed to connect to Logic Pro: {e}")
            return False

    def get_current_project_path(self) -> Optional[Path]:
        """Get path to currently open Logic Pro project"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    if (count of documents) > 0 then
                        set projectPath to path of front document
                        return POSIX path of projectPath
                    else
                        return ""
                    end if
                end tell
            '''
            result = self._run_applescript(script)
            if result.strip():
                self.current_project_path = Path(result.strip())
                return self.current_project_path
            return None
        except Exception as e:
            logger.error(f"Failed to get project path: {e}")
            return None

    def get_track_count(self) -> int:
        """Get total number of tracks in current project"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        return count of tracks
                    end tell
                end tell
            '''
            result = self._run_applescript(script)
            return int(result.strip())
        except Exception as e:
            logger.error(f"Failed to get track count: {e}")
            return 0

    def get_track_info(self, track_index: int) -> Dict[str, Any]:
        """Get information about a specific track"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        tell track {track_index}
                            set trackName to name
                            set trackMuted to mute
                            set trackSolo to solo
                            set trackColor to color
                            return trackName & "|" & trackMuted & "|" & trackSolo
                        end tell
                    end tell
                end tell
            '''
            result = self._run_applescript(script)
            parts = result.strip().split('|')

            return {
                'index': track_index,
                'name': parts[0] if len(parts) > 0 else '',
                'muted': parts[1].lower() == 'true' if len(parts) > 1 else False,
                'solo': parts[2].lower() == 'true' if len(parts) > 2 else False,
            }
        except Exception as e:
            logger.error(f"Failed to get track {track_index} info: {e}")
            return {}

    def set_track_name(self, track_index: int, name: str) -> bool:
        """Set track name"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        set name of track {track_index} to "{name}"
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Renamed track {track_index} to '{name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to rename track {track_index}: {e}")
            return False

    def set_track_color(self, track_index: int, color_index: int) -> bool:
        """Set track color (0-30 in Logic Pro)"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        set color of track {track_index} to {color_index}
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Set track {track_index} color to {color_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to set track color: {e}")
            return False

    def delete_track(self, track_index: int) -> bool:
        """Delete a track"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        delete track {track_index}
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Deleted track {track_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete track {track_index}: {e}")
            return False

    def create_audio_track(self, name: str = "Audio") -> bool:
        """Create a new audio track"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        make new audio track with properties {{name:"{name}"}}
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Created audio track: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create audio track: {e}")
            return False

    def create_aux_track(self, name: str = "Aux") -> bool:
        """Create a new aux/bus track"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        make new aux track with properties {{name:"{name}"}}
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Created aux track: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create aux track: {e}")
            return False

    def move_track(self, from_index: int, to_index: int) -> bool:
        """Move track from one position to another"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    tell front document
                        move track {from_index} to before track {to_index}
                    end tell
                end tell
            '''
            self._run_applescript(script)
            logger.info(f"Moved track from {from_index} to {to_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to move track: {e}")
            return False

    def save_project(self) -> bool:
        """Save current project"""
        try:
            script = f'''
                tell application "{self.app_name}"
                    save front document
                end tell
            '''
            self._run_applescript(script)
            logger.info("Project saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    def _run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.error(f"AppleScript error: {result.stderr}")
                raise RuntimeError(result.stderr)
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error("AppleScript execution timed out")
            raise
        except Exception as e:
            logger.error(f"Failed to execute AppleScript: {e}")
            raise
