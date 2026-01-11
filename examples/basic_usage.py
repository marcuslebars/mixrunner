"""
Mix Readiness AI - Basic Usage Examples
"""

from pathlib import Path
from src.mixrunner_engine import MixrunnerEngine


def example_1_full_workflow():
    """
    Example 1: Complete automatic workflow
    This is the simplest way to use the tool
    """
    print("=" * 70)
    print("EXAMPLE 1: Full Automatic Workflow")
    print("=" * 70)

    # Initialize engine
    engine = MixrunnerEngine()

    # Run complete workflow
    # This will: connect, analyze, clean, organize, normalize, and save
    engine.run_full_workflow()


def example_2_step_by_step():
    """
    Example 2: Step-by-step workflow with control
    Run each step individually for more control
    """
    print("=" * 70)
    print("EXAMPLE 2: Step-by-Step Workflow")
    print("=" * 70)

    engine = MixrunnerEngine()

    # Step 1: Connect to Logic Pro
    print("\n1. Connecting to Logic Pro...")
    if not engine.connect_to_logic():
        print("Failed to connect!")
        return

    # Step 2: Analyze the session
    print("\n2. Analyzing session...")
    engine.analyze_session()

    # Step 3: Review the analysis
    print("\n3. Analysis Report:")
    print(engine.generate_report())

    # Step 4: Ask user before proceeding
    response = input("\nProceed with optimization? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Step 5: Clean up session
    print("\n4. Cleaning up session...")
    engine.apply_cleanup()

    # Step 6: Organize tracks
    print("\n5. Organizing tracks...")
    engine.organize_tracks()

    # Step 7: Normalize audio
    print("\n6. Normalizing audio...")
    engine.normalize_technical()

    # Step 8: Save
    print("\n7. Saving session...")
    engine.export_session()

    print("\n✓ Complete!")


def example_3_analysis_only():
    """
    Example 3: Analysis only (no modifications)
    Useful for understanding the session before making changes
    """
    print("=" * 70)
    print("EXAMPLE 3: Analysis Only")
    print("=" * 70)

    engine = MixrunnerEngine()

    # Connect and analyze
    if engine.connect_to_logic():
        engine.analyze_session()

        # Show detailed report
        print("\n" + engine.generate_report())

        # Access specific results
        results = engine.analysis_results

        print("\nDetailed Statistics:")
        print(f"  Total Tracks: {results['session_stats']['total_tracks']}")
        print(f"  Audio Tracks: {results['session_stats']['audio_tracks']}")
        print(f"  Empty Tracks: {results['session_stats']['empty_tracks']}")

        # Show track classifications
        print("\nTrack Classifications:")
        for idx, data in engine.track_classifications.items():
            track_info = engine.logic_controller.get_track_info(idx)
            print(f"  Track {idx}: {track_info['name']}")
            print(f"    → {data['category']} (confidence: {data['confidence']:.2f})")


def example_4_custom_config():
    """
    Example 4: Using custom configuration
    Customize behavior for specific needs
    """
    print("=" * 70)
    print("EXAMPLE 4: Custom Configuration")
    print("=" * 70)

    # Custom configuration
    custom_config = {
        'target_lufs': -16.0,  # Louder target for electronic music
        'target_peak': -3.0,   # Less headroom
        'auto_color_tracks': True,
        'auto_organize': True,
        'create_buses': True,
        'remove_empty_tracks': True,
        'normalize_audio': False,  # Skip normalization
    }

    # Initialize with custom config
    engine = MixrunnerEngine(config=custom_config)

    # Run workflow
    if engine.connect_to_logic():
        engine.run_full_workflow()


def example_5_individual_analyzers():
    """
    Example 5: Using individual analyzers
    Access specific analysis tools directly
    """
    print("=" * 70)
    print("EXAMPLE 5: Individual Analyzers")
    print("=" * 70)

    from src.analyzers import PhaseAnalyzer, GainAnalyzer, FrequencyAnalyzer

    # Example audio file
    audio_file = Path("path/to/your/audio.wav")

    if not audio_file.exists():
        print(f"Audio file not found: {audio_file}")
        return

    # Phase Analysis
    print("\n1. Phase Analysis:")
    phase_analyzer = PhaseAnalyzer()
    phase_result = phase_analyzer.analyze_stereo_file(audio_file)
    print(f"   Phase Correlation: {phase_result.get('correlation', 0):.3f}")
    print(f"   Status: {phase_result.get('correlation_status', 'unknown')}")

    # Gain Analysis
    print("\n2. Gain Analysis:")
    gain_analyzer = GainAnalyzer()
    gain_result = gain_analyzer.analyze_file(audio_file)
    print(f"   Peak: {gain_result.get('peak_db', 0):.1f} dB")
    print(f"   LUFS: {gain_result.get('lufs', 0):.1f}")
    print(f"   Status: {gain_result.get('status', 'unknown')}")

    # Frequency Analysis
    print("\n3. Frequency Analysis:")
    freq_analyzer = FrequencyAnalyzer()
    freq_result = freq_analyzer.analyze_file(audio_file)
    print(f"   Brightness: {freq_result.get('brightness', 0):.2f}")
    print(f"   Spectral Centroid: {freq_result.get('spectral_centroid_hz', 0):.0f} Hz")


def example_6_track_classification():
    """
    Example 6: Manual track classification
    Classify tracks without Logic Pro connection
    """
    print("=" * 70)
    print("EXAMPLE 6: Track Classification")
    print("=" * 70)

    from src.ai_engine import TrackClassifier

    classifier = TrackClassifier()

    # Classify by name
    test_tracks = [
        "Kick Drum",
        "Snare Top",
        "Bass Guitar DI",
        "Electric Guitar Rhythm L",
        "Lead Vocal",
        "BGV Harmony 1",
        "Piano Main",
        "Synth Pad",
    ]

    print("\nClassifying tracks by name:")
    for track_name in test_tracks:
        category, confidence = classifier.classify_track(track_name=track_name)
        print(f"  '{track_name}'")
        print(f"    → {category} (confidence: {confidence:.2f})")


def example_7_audio_normalization():
    """
    Example 7: Standalone audio normalization
    Normalize audio files without Logic Pro
    """
    print("=" * 70)
    print("EXAMPLE 7: Audio Normalization")
    print("=" * 70)

    from src.processors import AudioNormalizer
    from pathlib import Path

    # Initialize normalizer
    normalizer = AudioNormalizer(
        target_lufs=-18.0,
        target_peak=-6.0,
        backup=True  # Create backups
    )

    # Get audio files
    audio_dir = Path("path/to/audio/files")
    audio_files = list(audio_dir.glob("*.wav"))

    if not audio_files:
        print(f"No audio files found in {audio_dir}")
        return

    print(f"\nNormalizing {len(audio_files)} files...")

    # Normalize with level matching
    results = normalizer.normalize_batch(
        audio_files,
        match_levels=True  # Match all files to same average level
    )

    # Show results
    success_count = sum(1 for success in results.values() if success)
    print(f"\n✓ Normalized {success_count}/{len(audio_files)} files")


# Main menu
def main():
    """Run example selector"""
    print("\n" + "=" * 70)
    print("Mix Readiness AI - Usage Examples")
    print("=" * 70)

    examples = {
        '1': ("Full Automatic Workflow", example_1_full_workflow),
        '2': ("Step-by-Step Workflow", example_2_step_by_step),
        '3': ("Analysis Only", example_3_analysis_only),
        '4': ("Custom Configuration", example_4_custom_config),
        '5': ("Individual Analyzers", example_5_individual_analyzers),
        '6': ("Track Classification", example_6_track_classification),
        '7': ("Audio Normalization", example_7_audio_normalization),
    }

    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")

    print("\n  q. Quit")

    choice = input("\nSelect example (1-7): ").strip()

    if choice.lower() == 'q':
        return

    if choice in examples:
        _, example_func = examples[choice]
        print("\n")
        example_func()
    else:
        print("Invalid choice!")


if __name__ == '__main__':
    main()
