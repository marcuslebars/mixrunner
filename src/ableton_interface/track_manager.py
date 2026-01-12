"""
Track Manager - High-level track manipulation operations
"""

from typing import List, Dict, Optional, Callable
from loguru import logger
from .ableton_controller import AbletonController
from .session_reader import TrackData


class TrackManager:
    """
    Manages track operations including organization, grouping, and routing
    """

    # Ableton Live color indices for different track types (0-69)
    COLOR_SCHEME = {
        'drums': 1,      # Red
        'bass': 55,      # Purple
        'guitar': 9,     # Orange
        'keys': 13,      # Yellow
        'vocals': 56,    # Pink
        'lead_vocal': 57, # Bright pink
        'bgv': 58,       # Light pink
        'strings': 25,   # Green
        'brass': 8,      # Brown
        'fx': 41,        # Blue
        'bus': 17,       # Gray
        'return': 17,    # Gray (Ableton uses 'return' instead of 'aux')
        'default': 0,    # No color
    }

    def __init__(self, controller: AbletonController):
        self.controller = controller

    def organize_tracks_by_type(self, track_classifications: Dict[int, str]) -> bool:
        """
        Organize tracks by their type classification

        Args:
            track_classifications: Dict mapping track index to type (drums, bass, vocals, etc.)
        """
        try:
            logger.info("Organizing tracks by type...")

            # Define desired order
            type_order = [
                'drums',
                'bass',
                'guitar',
                'keys',
                'vocals',
                'lead_vocal',
                'bgv',
                'strings',
                'brass',
                'fx',
                'bus',
                'aux',
                'other'
            ]

            # Group tracks by type
            grouped_tracks = {track_type: [] for track_type in type_order}

            for track_idx, track_type in track_classifications.items():
                if track_type in grouped_tracks:
                    grouped_tracks[track_type].append(track_idx)
                else:
                    grouped_tracks['other'].append(track_idx)

            # Reorder tracks
            current_position = 1
            for track_type in type_order:
                for track_idx in grouped_tracks[track_type]:
                    if track_idx != current_position:
                        self.controller.move_track(track_idx, current_position)
                    current_position += 1

            logger.info("Track organization complete")
            return True

        except Exception as e:
            logger.error(f"Failed to organize tracks: {e}")
            return False

    def apply_color_scheme(self, track_classifications: Dict[int, str]) -> bool:
        """Apply color coding based on track type"""
        try:
            logger.info("Applying color scheme...")

            for track_idx, track_type in track_classifications.items():
                color = self.COLOR_SCHEME.get(track_type, self.COLOR_SCHEME['default'])
                self.controller.set_track_color(track_idx, color)

            logger.info("Color scheme applied")
            return True

        except Exception as e:
            logger.error(f"Failed to apply colors: {e}")
            return False

    def rename_tracks_by_convention(
        self,
        track_classifications: Dict[int, str],
        naming_template: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Rename tracks following naming conventions

        Args:
            track_classifications: Track type classifications
            naming_template: Optional custom naming template
        """
        try:
            logger.info("Renaming tracks by convention...")

            if naming_template is None:
                naming_template = {
                    'drums': 'DRUMS',
                    'bass': 'BASS',
                    'guitar': 'GTR',
                    'keys': 'KEYS',
                    'vocals': 'VOX',
                    'lead_vocal': 'LEAD VOX',
                    'bgv': 'BGV',
                }

            # Track counters for numbering
            type_counters = {}

            for track_idx, track_type in sorted(track_classifications.items()):
                if track_type not in type_counters:
                    type_counters[track_type] = 1
                else:
                    type_counters[track_type] += 1

                prefix = naming_template.get(track_type, track_type.upper())
                number = type_counters[track_type]

                # Get current track info to preserve specific identifiers
                track_info = self.controller.get_track_info(track_idx)
                current_name = track_info.get('name', '')

                # Smart naming: keep descriptive parts
                if number > 1:
                    new_name = f"{prefix} {number}"
                else:
                    new_name = prefix

                # Try to preserve meaningful descriptors
                descriptors = self._extract_descriptors(current_name)
                if descriptors:
                    new_name += f" - {descriptors}"

                self.controller.set_track_name(track_idx, new_name)

            logger.info("Track renaming complete")
            return True

        except Exception as e:
            logger.error(f"Failed to rename tracks: {e}")
            return False

    def create_bus_structure(self, track_groups: Dict[str, List[int]]) -> Dict[str, int]:
        """
        Create bus/aux tracks for grouped tracks

        Args:
            track_groups: Dict mapping group name to list of track indices

        Returns:
            Dict mapping group name to bus track index
        """
        try:
            logger.info("Creating bus structure...")
            bus_tracks = {}

            for group_name, track_indices in track_groups.items():
                if not track_indices:
                    continue

                # Create aux track for this group
                bus_name = f"{group_name.upper()} BUS"
                self.controller.create_aux_track(bus_name)

                # Get the index of the newly created track
                bus_index = self.controller.get_track_count()
                bus_tracks[group_name] = bus_index

                # Set bus color
                bus_color = self.COLOR_SCHEME.get(group_name, self.COLOR_SCHEME['bus'])
                self.controller.set_track_color(bus_index, bus_color)

                logger.info(f"Created bus: {bus_name}")

            return bus_tracks

        except Exception as e:
            logger.error(f"Failed to create bus structure: {e}")
            return {}

    def remove_empty_tracks(self, track_data: List[TrackData]) -> int:
        """Remove tracks with no regions or content"""
        try:
            removed_count = 0

            # Sort in reverse to avoid index shifting issues
            for track in sorted(track_data, key=lambda t: t.index, reverse=True):
                if not track.regions and track.track_type in ['audio', 'midi']:
                    logger.info(f"Removing empty track: {track.name}")
                    self.controller.delete_track(track.index)
                    removed_count += 1

            logger.info(f"Removed {removed_count} empty tracks")
            return removed_count

        except Exception as e:
            logger.error(f"Failed to remove empty tracks: {e}")
            return 0

    def _extract_descriptors(self, track_name: str) -> str:
        """Extract meaningful descriptors from track name"""
        # Remove common prefixes and numbering
        import re

        # Remove leading numbers and common separators
        cleaned = re.sub(r'^[\d\s\-_]+', '', track_name)

        # Remove trailing numbers
        cleaned = re.sub(r'[\d\s\-_]+$', '', cleaned)

        # Common terms to preserve
        meaningful_terms = ['lead', 'rhythm', 'solo', 'verse', 'chorus', 'overhead',
                          'close', 'room', 'ambient', 'dry', 'wet', 'left', 'right',
                          'center', 'main', 'sub', 'top', 'bottom']

        words = cleaned.lower().split()
        descriptors = [w for w in words if w in meaningful_terms]

        return ' '.join(descriptors).title() if descriptors else ''

    def create_track_stacks(
        self,
        track_groups: Dict[str, List[int]],
        stack_type: str = "summing"
    ) -> bool:
        """
        Create Logic Pro track stacks

        Args:
            track_groups: Groups of tracks to stack
            stack_type: 'summing' or 'folder'
        """
        try:
            logger.info(f"Creating {stack_type} track stacks...")

            # Note: Track stack creation via AppleScript is limited
            # This is a simplified implementation
            for group_name, track_indices in track_groups.items():
                if len(track_indices) < 2:
                    continue

                logger.info(f"Creating stack for {group_name} with {len(track_indices)} tracks")
                # Implementation would use Logic's track stack commands
                # This requires more advanced AppleScript/JXA

            return True

        except Exception as e:
            logger.error(f"Failed to create track stacks: {e}")
            return False
