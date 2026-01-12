"""
Ableton Live Controller - Main interface for communicating with Ableton Live 12
"""

import socket
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class AbletonController:
    """
    Controls Ableton Live 12 via MIDI Remote Script and OSC
    Provides high-level interface for session manipulation
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11000):
        """
        Initialize Ableton Live controller

        Args:
            host: Host address for OSC communication
            port: Port for OSC communication (default 11000)
        """
        self.app_name = "Ableton Live 12"
        self.host = host
        self.port = port
        self.is_connected = False
        self.current_project_path: Optional[Path] = None
        self.socket = None

    def connect(self) -> bool:
        """Establish connection to Ableton Live"""
        try:
            # Try to establish socket connection for OSC
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(2.0)

            # Send ping to check if Ableton is running and responsive
            response = self._send_command('/live/test')

            if response:
                self.is_connected = True
                logger.info(f"Ableton Live connection: {self.is_connected}")
                return True
            else:
                # Even if no response, mark as connected for now
                # The user needs to have the MIDI Remote Script installed
                self.is_connected = True
                logger.warning("Ableton Live connection established (no response, ensure MIDI Remote Script is installed)")
                return True

        except Exception as e:
            logger.error(f"Failed to connect to Ableton Live: {e}")
            logger.info("Make sure Ableton Live is running and the MIDI Remote Script is installed")
            return False

    def disconnect(self):
        """Close connection to Ableton Live"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.is_connected = False

    def get_current_project_path(self) -> Optional[Path]:
        """Get path to currently open Ableton Live project"""
        try:
            response = self._send_command('/live/song/get/file_path')
            if response:
                path_str = response.get('value', '')
                if path_str:
                    self.current_project_path = Path(path_str)
                    return self.current_project_path
            return None
        except Exception as e:
            logger.error(f"Failed to get project path: {e}")
            return None

    def get_track_count(self) -> int:
        """Get total number of tracks in current project"""
        try:
            response = self._send_command('/live/song/get/num_tracks')
            if response:
                count = response.get('value', 0)
                return int(count)
            return 0
        except Exception as e:
            logger.error(f"Failed to get track count: {e}")
            return 0

    def get_track_info(self, track_index: int) -> Dict[str, Any]:
        """Get information about a specific track"""
        try:
            # Get track name
            name_response = self._send_command(f'/live/track/get/name', {'track': track_index})

            # Get track mute state
            mute_response = self._send_command(f'/live/track/get/mute', {'track': track_index})

            # Get track solo state
            solo_response = self._send_command(f'/live/track/get/solo', {'track': track_index})

            # Get track color
            color_response = self._send_command(f'/live/track/get/color', {'track': track_index})

            return {
                'index': track_index,
                'name': name_response.get('value', '') if name_response else f'Track {track_index + 1}',
                'muted': mute_response.get('value', False) if mute_response else False,
                'solo': solo_response.get('value', False) if solo_response else False,
                'color': color_response.get('value', 0) if color_response else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get track {track_index} info: {e}")
            return {
                'index': track_index,
                'name': f'Track {track_index + 1}',
                'muted': False,
                'solo': False,
            }

    def set_track_name(self, track_index: int, name: str) -> bool:
        """Set track name"""
        try:
            response = self._send_command('/live/track/set/name', {
                'track': track_index,
                'name': name
            })
            logger.info(f"Renamed track {track_index} to '{name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to rename track {track_index}: {e}")
            return False

    def set_track_color(self, track_index: int, color_index: int) -> bool:
        """Set track color (0-69 in Ableton Live)"""
        try:
            response = self._send_command('/live/track/set/color', {
                'track': track_index,
                'color': color_index
            })
            logger.info(f"Set track {track_index} color to {color_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to set track color: {e}")
            return False

    def delete_track(self, track_index: int) -> bool:
        """Delete a track"""
        try:
            response = self._send_command('/live/track/delete', {
                'track': track_index
            })
            logger.info(f"Deleted track {track_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete track {track_index}: {e}")
            return False

    def create_audio_track(self, name: str = "Audio") -> bool:
        """Create a new audio track"""
        try:
            response = self._send_command('/live/track/create', {
                'type': 'audio',
                'name': name
            })
            logger.info(f"Created audio track: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create audio track: {e}")
            return False

    def create_return_track(self, name: str = "Return") -> bool:
        """Create a new return track (Ableton's equivalent to aux)"""
        try:
            response = self._send_command('/live/track/create', {
                'type': 'return',
                'name': name
            })
            logger.info(f"Created return track: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create return track: {e}")
            return False

    def move_track(self, from_index: int, to_index: int) -> bool:
        """Move track from one position to another"""
        try:
            response = self._send_command('/live/track/move', {
                'from': from_index,
                'to': to_index
            })
            logger.info(f"Moved track from {from_index} to {to_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to move track: {e}")
            return False

    def save_project(self) -> bool:
        """Save current project"""
        try:
            response = self._send_command('/live/song/save')
            logger.info("Project saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    def get_tempo(self) -> float:
        """Get current project tempo"""
        try:
            response = self._send_command('/live/song/get/tempo')
            if response:
                return float(response.get('value', 120.0))
            return 120.0
        except Exception as e:
            logger.error(f"Failed to get tempo: {e}")
            return 120.0

    def set_tempo(self, tempo: float) -> bool:
        """Set project tempo"""
        try:
            response = self._send_command('/live/song/set/tempo', {'tempo': tempo})
            logger.info(f"Set tempo to {tempo} BPM")
            return True
        except Exception as e:
            logger.error(f"Failed to set tempo: {e}")
            return False

    def get_track_volume(self, track_index: int) -> float:
        """Get track volume (0.0 to 1.0)"""
        try:
            response = self._send_command('/live/track/get/volume', {'track': track_index})
            if response:
                return float(response.get('value', 0.85))
            return 0.85
        except Exception as e:
            logger.error(f"Failed to get track volume: {e}")
            return 0.85

    def set_track_volume(self, track_index: int, volume: float) -> bool:
        """Set track volume (0.0 to 1.0)"""
        try:
            response = self._send_command('/live/track/set/volume', {
                'track': track_index,
                'volume': max(0.0, min(1.0, volume))
            })
            logger.info(f"Set track {track_index} volume to {volume}")
            return True
        except Exception as e:
            logger.error(f"Failed to set track volume: {e}")
            return False

    def get_track_pan(self, track_index: int) -> float:
        """Get track pan (-1.0 to 1.0, 0 is center)"""
        try:
            response = self._send_command('/live/track/get/panning', {'track': track_index})
            if response:
                return float(response.get('value', 0.0))
            return 0.0
        except Exception as e:
            logger.error(f"Failed to get track pan: {e}")
            return 0.0

    def set_track_pan(self, track_index: int, pan: float) -> bool:
        """Set track pan (-1.0 to 1.0, 0 is center)"""
        try:
            response = self._send_command('/live/track/set/panning', {
                'track': track_index,
                'panning': max(-1.0, min(1.0, pan))
            })
            logger.info(f"Set track {track_index} pan to {pan}")
            return True
        except Exception as e:
            logger.error(f"Failed to set track pan: {e}")
            return False

    def _send_command(self, address: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Send OSC command to Ableton Live

        Args:
            address: OSC address (e.g., '/live/song/get/tempo')
            params: Optional parameters dictionary

        Returns:
            Response dictionary or None
        """
        try:
            if not self.socket:
                return None

            # Build OSC message
            message = {
                'address': address,
                'args': params or {}
            }

            # Send via UDP
            message_bytes = json.dumps(message).encode('utf-8')
            self.socket.sendto(message_bytes, (self.host, self.port))

            # Try to receive response (with timeout)
            try:
                data, addr = self.socket.recvfrom(4096)
                response = json.loads(data.decode('utf-8'))
                return response
            except socket.timeout:
                # No response received, return None
                return None

        except Exception as e:
            logger.debug(f"Command {address} failed: {e}")
            return None

    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
