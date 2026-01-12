"""
Ableton Live Controller - Main interface for communicating with Ableton Live 12
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading


class AbletonController:
    """
    Controls Ableton Live 12 via MIDI Remote Script and OSC
    Provides high-level interface for session manipulation
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 11000, receive_port: int = 11001, try_port_discovery: bool = True):
        """
        Initialize Ableton Live controller

        Args:
            host: Host address for OSC communication
            port: Port for sending OSC messages to Ableton (default 11000)
            receive_port: Port for receiving OSC responses (default 11001)
            try_port_discovery: Automatically try common port configurations if default fails
        """
        self.try_port_discovery = try_port_discovery
        self.app_name = "Ableton Live 12"
        self.host = host
        self.port = port
        self.receive_port = receive_port
        self.is_connected = False
        self.current_project_path: Optional[Path] = None

        # OSC client for sending messages to Ableton
        self.osc_client = None

        # OSC server for receiving responses from Ableton
        self.osc_server = None
        self.server_thread = None
        self.dispatcher = Dispatcher()

        # Storage for responses
        self.last_response = None
        self.response_received = threading.Event()

    def connect(self) -> bool:
        """Establish connection to Ableton Live"""
        try:
            # Initialize OSC client for sending messages
            self.osc_client = udp_client.SimpleUDPClient(self.host, self.port)

            # Set up dispatcher for receiving responses
            self.dispatcher.map("/live/*", self._handle_response)
            self.dispatcher.set_default_handler(self._handle_response)

            # Start OSC server for receiving responses
            self.osc_server = ThreadingOSCUDPServer(
                (self.host, self.receive_port),
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.osc_server.serve_forever, daemon=True)
            self.server_thread.start()

            # Send test message to check if Ableton is responsive
            self.osc_client.send_message("/live/test", [])
            time.sleep(0.1)  # Brief wait for response

            self.is_connected = True
            logger.info(f"Connected to Ableton Live on port {self.port}")
            logger.info(f"Listening for responses on port {self.receive_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Ableton Live: {e}")
            logger.info("Make sure Ableton Live is running and AbletonOSC is installed")
            return False

    def _handle_response(self, address, *args):
        """Handle incoming OSC messages from Ableton"""
        self.last_response = {'address': address, 'args': args}
        self.response_received.set()

    def disconnect(self):
        """Close connection to Ableton Live"""
        if self.osc_server:
            self.osc_server.shutdown()
            self.osc_server = None
        self.osc_client = None
        self.is_connected = False

    def get_current_project_path(self) -> Optional[Path]:
        """Get path to currently open Ableton Live project"""
        try:
            response = self._send_command('/live/song/get/file_path')
            if response and response.get('args'):
                path_str = response['args'][0] if response['args'] else ''
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
            if response and response.get('args'):
                count = response['args'][0] if response['args'] else 0
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

            def get_value(response, default):
                if response and response.get('args'):
                    return response['args'][0]
                return default

            # Get values with proper type conversion
            name_val = get_value(name_response, f'Track {track_index + 1}')

            return {
                'index': track_index,
                'name': str(name_val) if name_val is not None else f'Track {track_index + 1}',
                'muted': bool(get_value(mute_response, False)),
                'solo': bool(get_value(solo_response, False)),
                'color': int(get_value(color_response, 0)),
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
            if response and response.get('args'):
                return float(response['args'][0])
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
            if response and response.get('args'):
                return float(response['args'][0])
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
            if response and response.get('args'):
                return float(response['args'][0])
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

    def _send_command(self, address: str, params: Optional[Dict] = None, timeout: float = 1.0) -> Optional[Dict]:
        """
        Send OSC command to Ableton Live

        Args:
            address: OSC address (e.g., '/live/song/get/tempo')
            params: Optional parameters dictionary
            timeout: Time to wait for response in seconds

        Returns:
            Response dictionary or None
        """
        try:
            if not self.osc_client:
                return None

            # Clear previous response
            self.response_received.clear()
            self.last_response = None

            # Build arguments list from params
            args = []
            if params:
                if isinstance(params, dict):
                    # Convert dict to list of values
                    for key, value in params.items():
                        args.append(value)
                elif isinstance(params, list):
                    args = params
                else:
                    args = [params]

            # Send OSC message
            self.osc_client.send_message(address, args)

            # Wait for response
            if self.response_received.wait(timeout):
                return self.last_response
            else:
                # No response within timeout
                logger.debug(f"No response for {address}")
                return None

        except Exception as e:
            logger.debug(f"Command {address} failed: {e}")
            return None

    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
