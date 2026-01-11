"""
LLM Client - Unified interface for Claude, GPT, and Gemini
"""

import os
from typing import Dict, List, Optional, Any
from enum import Enum
from loguru import logger


class LLMProvider(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"


class LLMClient:
    """
    Unified client for interacting with LLMs for mixing decisions
    """

    def __init__(
        self,
        provider: LLMProvider = LLMProvider.CLAUDE,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM client

        Args:
            provider: Which LLM to use (Claude, GPT, Gemini)
            api_key: API key (or set via environment variable)
            model: Specific model to use
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.client = None

        self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment"""
        key_map = {
            LLMProvider.CLAUDE: "ANTHROPIC_API_KEY",
            LLMProvider.GPT: "OPENAI_API_KEY",
            LLMProvider.GEMINI: "GOOGLE_API_KEY"
        }
        env_var = key_map.get(self.provider)
        return os.getenv(env_var)

    def _get_default_model(self) -> str:
        """Get default model for provider"""
        models = {
            LLMProvider.CLAUDE: "claude-3-5-sonnet-20241022",
            LLMProvider.GPT: "gpt-4-turbo-preview",
            LLMProvider.GEMINI: "gemini-1.5-pro"
        }
        return models.get(self.provider, "")

    def _initialize_client(self):
        """Initialize the specific LLM client"""
        try:
            if self.provider == LLMProvider.CLAUDE:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Initialized Claude client")

            elif self.provider == LLMProvider.GPT:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info("Initialized OpenAI GPT client")

            elif self.provider == LLMProvider.GEMINI:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info("Initialized Gemini client")

        except ImportError as e:
            logger.error(f"Failed to import {self.provider.value} library: {e}")
            logger.info(f"Install with: pip install {self._get_package_name()}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider.value} client: {e}")

    def _get_package_name(self) -> str:
        """Get pip package name for provider"""
        packages = {
            LLMProvider.CLAUDE: "anthropic",
            LLMProvider.GPT: "openai",
            LLMProvider.GEMINI: "google-generativeai"
        }
        return packages.get(self.provider, "")

    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Send chat completion request to LLM

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum response tokens

        Returns:
            LLM response text
        """
        if not self.client:
            return "Error: LLM client not initialized"

        try:
            if self.provider == LLMProvider.CLAUDE:
                return self._chat_claude(messages, system, temperature, max_tokens)
            elif self.provider == LLMProvider.GPT:
                return self._chat_gpt(messages, system, temperature, max_tokens)
            elif self.provider == LLMProvider.GEMINI:
                return self._chat_gemini(messages, system, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            return f"Error: {str(e)}"

    def _chat_claude(
        self,
        messages: List[Dict],
        system: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Claude-specific chat"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "You are an expert audio mixing engineer.",
            messages=messages
        )
        return response.content[0].text

    def _chat_gpt(
        self,
        messages: List[Dict],
        system: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """GPT-specific chat"""
        if system:
            messages = [{"role": "system", "content": system}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content

    def _chat_gemini(
        self,
        messages: List[Dict],
        system: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Gemini-specific chat"""
        model = self.client.GenerativeModel(
            model_name=self.model,
            system_instruction=system or "You are an expert audio mixing engineer."
        )

        # Convert messages to Gemini format
        chat = model.start_chat(history=[])

        # Send last user message
        user_message = messages[-1]["content"] if messages else ""
        response = chat.send_message(
            user_message,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )

        return response.text

    def analyze_mix(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask LLM to analyze mix and provide recommendations

        Args:
            track_data: Dictionary with track information

        Returns:
            Dictionary with analysis and recommendations
        """
        prompt = self._create_mix_analysis_prompt(track_data)

        messages = [
            {"role": "user", "content": prompt}
        ]

        system = """You are an expert audio mixing engineer with 20+ years of experience.
        Analyze the provided session data and give specific, actionable mixing advice.
        Focus on: levels, panning, EQ, compression, effects, and overall balance."""

        response = self.chat(messages, system=system, temperature=0.3)

        return {
            "analysis": response,
            "track_data": track_data
        }

    def _create_mix_analysis_prompt(self, track_data: Dict) -> str:
        """Create detailed prompt for mix analysis"""
        prompt = f"""Analyze this mixing session and provide specific recommendations:

**Session Info:**
- Total Tracks: {track_data.get('track_count', 0)}
- Sample Rate: {track_data.get('sample_rate', 48000)} Hz

**Tracks:**
"""
        for track in track_data.get('tracks', []):
            prompt += f"\n- {track.get('name', 'Unknown')}: {track.get('type', 'unknown')} "
            if 'peak_db' in track:
                prompt += f"(Peak: {track['peak_db']:.1f} dB)"

        prompt += """

Provide recommendations for:
1. Overall level balance
2. Panning suggestions
3. EQ corrections needed
4. Compression settings
5. Effects to add
6. Mix bus processing

Be specific with frequencies, dB values, and settings."""

        return prompt

    def get_eq_recommendation(
        self,
        track_name: str,
        track_type: str,
        frequency_analysis: Dict
    ) -> str:
        """Get LLM recommendation for EQ settings"""
        prompt = f"""Recommend EQ settings for this track:

Track: {track_name}
Type: {track_type}
Frequency Analysis:
{frequency_analysis}

Provide specific EQ moves (frequency, Q, gain) in a clear format."""

        messages = [{"role": "user", "content": prompt}]
        system = "You are an expert audio engineer. Give precise EQ recommendations."

        return self.chat(messages, system=system, temperature=0.2)

    def get_compression_recommendation(
        self,
        track_name: str,
        track_type: str,
        dynamic_analysis: Dict
    ) -> str:
        """Get LLM recommendation for compression settings"""
        prompt = f"""Recommend compression settings for this track:

Track: {track_name}
Type: {track_type}
Dynamic Range: {dynamic_analysis.get('dynamic_range', 'N/A')} dB
Crest Factor: {dynamic_analysis.get('crest_factor', 'N/A')} dB

Provide specific compression parameters:
- Threshold, Ratio, Attack, Release, Makeup Gain"""

        messages = [{"role": "user", "content": prompt}]
        system = "You are an expert in dynamics processing. Give precise compressor settings."

        return self.chat(messages, system=system, temperature=0.2)
