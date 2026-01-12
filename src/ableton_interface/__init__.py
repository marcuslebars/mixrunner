"""
Ableton Live Interface Layer
Handles communication with Ableton Live 12 via OSC and MIDI Remote Scripts
"""

from .ableton_controller import AbletonController
from .session_reader import SessionReader
from .track_manager import TrackManager

__all__ = ['AbletonController', 'SessionReader', 'TrackManager']
