"""
Logic Pro Interface Layer
Handles communication with Logic Pro via AppleScript/JXA and MIDI scripting
"""

from .logic_controller import LogicController
from .session_reader import SessionReader
from .track_manager import TrackManager

__all__ = ['LogicController', 'SessionReader', 'TrackManager']
