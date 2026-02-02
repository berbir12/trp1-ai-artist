#!/usr/bin/env python3
"""
Example 09: Combine Video and Audio into Music Video

Combines a video file with an audio file to create a music video using MoviePy.
This script was used to create the Ethiopian Mountains Music Video.

Usage:
    python examples/09_combine_music_video.py

    # Or with custom paths:
    python examples/09_combine_music_video.py --video exports/video.mp4 --audio exports/audio.wav --output exports/result.mp4
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip


def combine_audio_video(video_path: str, audio_path: str, output_path: str):
    """
    Combine video and audio files into a single music video.
    
    Args:
        video_path: Path to the video file (MP4)
        audio_path: Path to the audio file (WAV/MP3)
        output_path: Path for the output music video (MP4)
    """
    print(f"[VIDEO] Loading video: {video_path}")
    video = VideoFileClip(video_path)
    
    print(f"[AUDIO] Loading audio: {audio_path}")
    audio = AudioFileClip(audio_path)
    
    # Use the shorter duration to avoid extending beyond content
    duration = min(video.duration, audio.duration)
    print(f"[INFO] Duration: {duration:.2f} seconds")
    print(f"[INFO] Video resolution: {video.w}x{video.h} @ {video.fps} fps")
    
    # Trim both to the same length
    video = video.subclipped(0, duration)
    audio = audio.subclipped(0, duration)
    
    # Combine - replace video's audio with new audio
    print("[INFO] Combining video and audio...")
    final_video = video.with_audio(audio)
    
    # Export with optimal settings
    print(f"[EXPORT] Exporting to: {output_path}")
    final_video.write_videofile(
        output_path,
        codec='libx264',          # H.264 video codec
        audio_codec='aac',        # AAC audio codec
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        fps=video.fps,            # Preserve original fps
        preset='medium',          # Encoding speed vs quality
        threads=4                 # Use multiple threads
    )
    
    # Clean up memory
    video.close()
    audio.close()
    final_video.close()
    
    print(f"[SUCCESS] Music video created successfully!")
    print(f"[OUTPUT] {output_path}")


def main():
    """Main function with command-line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Combine video and audio into a music video"
    )
    parser.add_argument(
        "--video", "-v",
        default="exports/simien_mountain_cinematic_view.mp4",
        help="Path to video file"
    )
    parser.add_argument(
        "--audio", "-a",
        default="exports/ethio_jazz_instrumental.wav",
        help="Path to audio file"
    )
    parser.add_argument(
        "--output", "-o",
        default="exports/music_video_ethiopian_mountains.mp4",
        help="Path to output file"
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects and verify existence
    video_file = Path(args.video)
    audio_file = Path(args.audio)
    output_file = Path(args.output)
    
    # Verify files exist
    if not video_file.exists():
        print(f"[ERROR] Video file not found: {video_file}")
        sys.exit(1)
    
    if not audio_file.exists():
        print(f"[ERROR] Audio file not found: {audio_file}")
        sys.exit(1)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Combine
    combine_audio_video(str(video_file), str(audio_file), str(output_file))


if __name__ == "__main__":
    main()
