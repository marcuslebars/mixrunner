"""
Mixing Agent - Uses LLM to make intelligent mixing decisions
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from loguru import logger

from .llm_client import LLMClient, LLMProvider
from ..analyzers import GainAnalyzer, PhaseAnalyzer, FrequencyAnalyzer
from ..ai_engine import TrackClassifier


class MixingAgent:
    """
    AI agent that uses LLM to make mixing decisions
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.CLAUDE,
        api_key: Optional[str] = None
    ):
        """
        Initialize mixing agent

        Args:
            provider: LLM provider to use
            api_key: API key for the provider
        """
        self.llm = LLMClient(provider=provider, api_key=api_key)
        self.gain_analyzer = GainAnalyzer()
        self.phase_analyzer = PhaseAnalyzer()
        self.freq_analyzer = FrequencyAnalyzer()
        self.track_classifier = TrackClassifier()

        logger.info(f"Mixing agent initialized with {provider.value}")

    def analyze_track_with_ai(
        self,
        audio_path: Path,
        track_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive AI-powered track analysis

        Args:
            audio_path: Path to audio file
            track_name: Name of the track

        Returns:
            Complete analysis with AI recommendations
        """
        logger.info(f"AI analyzing track: {track_name}")

        # Technical analysis
        gain_analysis = self.gain_analyzer.analyze_file(audio_path)
        phase_analysis = self.phase_analyzer.analyze_stereo_file(audio_path)
        freq_analysis = self.freq_analyzer.analyze_file(audio_path)

        # Classify track type
        track_type, confidence = self.track_classifier.classify_track(
            track_name=track_name
        )

        # Get LLM recommendations
        eq_rec = self.llm.get_eq_recommendation(
            track_name=track_name,
            track_type=track_type,
            frequency_analysis=freq_analysis
        )

        comp_rec = self.llm.get_compression_recommendation(
            track_name=track_name,
            track_type=track_type,
            dynamic_analysis={
                'dynamic_range': gain_analysis.get('dynamic_range'),
                'crest_factor': gain_analysis.get('crest_factor')
            }
        )

        return {
            'track_name': track_name,
            'track_type': track_type,
            'classification_confidence': confidence,
            'gain_analysis': gain_analysis,
            'phase_analysis': phase_analysis,
            'frequency_analysis': freq_analysis,
            'ai_recommendations': {
                'eq': eq_rec,
                'compression': comp_rec
            }
        }

    def get_panning_recommendation(
        self,
        track_classifications: Dict[int, str]
    ) -> Dict[int, float]:
        """
        Get AI-powered panning recommendations for all tracks

        Args:
            track_classifications: Dict mapping track index to type

        Returns:
            Dict mapping track index to pan position (-1.0 to 1.0)
        """
        # Build context for LLM
        tracks_str = "\n".join([
            f"Track {idx}: {track_type}"
            for idx, track_type in track_classifications.items()
        ])

        prompt = f"""Recommend stereo panning for these tracks (values from -1.0 (hard left) to 1.0 (hard right), 0.0 is center):

{tracks_str}

Return ONLY a JSON object mapping track numbers to pan values, nothing else.
Example: {{"1": 0.0, "2": -0.3, "3": 0.3}}"""

        messages = [{"role": "user", "content": prompt}]
        response = self.llm.chat(messages, temperature=0.1)

        # Parse response
        import json
        try:
            pan_dict = json.loads(response)
            return {int(k): float(v) for k, v in pan_dict.items()}
        except:
            logger.error("Failed to parse panning recommendations")
            return {}

    def get_mixing_workflow(
        self,
        session_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get complete AI-generated mixing workflow

        Args:
            session_data: Complete session information

        Returns:
            Ordered list of mixing steps to perform
        """
        prompt = f"""Create a step-by-step mixing workflow for this session:

**Tracks:**
{self._format_tracks_for_prompt(session_data.get('tracks', []))}

**Current Issues:**
{self._format_issues_for_prompt(session_data.get('issues', []))}

Generate a numbered workflow with specific actions for each step.
Include track names, parameter values, and reasoning."""

        messages = [{"role": "user", "content": prompt}]
        system = """You are an expert mixing engineer creating a detailed mixing workflow.
        Be specific with all settings and explain WHY each step is needed."""

        response = self.llm.chat(messages, system=system, temperature=0.4)

        return self._parse_workflow_response(response)

    def _format_tracks_for_prompt(self, tracks: List[Dict]) -> str:
        """Format track list for LLM prompt"""
        lines = []
        for track in tracks:
            line = f"- {track.get('name', 'Unknown')}"
            if 'type' in track:
                line += f" ({track['type']})"
            if 'peak_db' in track:
                line += f" - Peak: {track['peak_db']:.1f}dB"
            lines.append(line)
        return "\n".join(lines)

    def _format_issues_for_prompt(self, issues: List[Dict]) -> str:
        """Format issues list for LLM prompt"""
        if not issues:
            return "None detected"

        lines = []
        for issue in issues:
            severity = issue.get('severity', 'info')
            desc = issue.get('description', 'Unknown issue')
            lines.append(f"[{severity.upper()}] {desc}")
        return "\n".join(lines)

    def _parse_workflow_response(self, response: str) -> List[Dict]:
        """Parse LLM workflow response into structured steps"""
        # Simple parsing - extract numbered steps
        steps = []
        lines = response.split('\n')

        current_step = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's a numbered step
            if line[0].isdigit() and ('.' in line or ')' in line):
                if current_step:
                    steps.append(current_step)

                # Extract step number and description
                parts = line.split('.', 1) if '.' in line else line.split(')', 1)
                step_num = int(parts[0].strip())
                description = parts[1].strip() if len(parts) > 1 else ""

                current_step = {
                    'step': step_num,
                    'description': description,
                    'details': []
                }
            elif current_step and line.startswith('-'):
                # Add detail to current step
                current_step['details'].append(line[1:].strip())

        if current_step:
            steps.append(current_step)

        return steps
