#!/usr/bin/env python3
"""
Voice-to-Text Prototype
Uses OpenAI Whisper for local transcription
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def extract_audio(video_path, output_audio):
    """Extract audio from video using ffmpeg"""
    print(f"Extracting audio from {video_path}...")
    cmd = [
        'ffmpeg', '-y', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
        output_audio
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extracting audio: {result.stderr}")
        return False
    print(f"Audio extracted: {output_audio}")
    return True

def transcribe_audio(audio_path, model_size='base'):
    """Transcribe audio using Whisper"""
    print(f"Loading Whisper {model_size} model...")
    
    try:
        import whisper
        
        # Load model
        model = whisper.load_model(model_size)
        print(f"Model loaded. Transcribing...")
        
        # Transcribe
        start_time = time.time()
        result = model.transcribe(audio_path, word_timestamps=True)
        elapsed = time.time() - start_time
        
        print(f"Transcription complete in {elapsed:.1f} seconds")
        return result, elapsed
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None, 0

def main():
    # Video file path
    video_path = "/Volumes/2TB/Sync/Flat/Flerfs/C C/Videos/Think about it friday on our Flat-earth 2025-01-17.mp4"
    output_dir = "/Users/mctoon/.openclaw/workspace/research/voice-fingerprinting/prototype-test"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"Processing: {video_path}")
    print(f"Output directory: {output_dir}")
    
    # Extract audio
    audio_path = os.path.join(output_dir, "extracted_audio.wav")
    if not extract_audio(video_path, audio_path):
        print("Failed to extract audio")
        sys.exit(1)
    
    # Get audio duration
    probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', audio_path]
    duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    audio_duration = float(duration_result.stdout.strip())
    print(f"Audio duration: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
    
    # Transcribe
    result, elapsed = transcribe_audio(audio_path, model_size='base')
    
    if result:
        # Add metadata
        output = {
            'metadata': {
                'source_video': video_path,
                'audio_duration_seconds': audio_duration,
                'model': 'whisper-base',
                'processing_time_seconds': elapsed,
                'real_time_factor': elapsed / audio_duration if audio_duration > 0 else 0,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            },
            'transcription': result
        }
        
        # Save results
        output_path = os.path.join(output_dir, "transcription_result.json")
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
        print(f"Real-time factor: {output['metadata']['real_time_factor']:.2f}x")
        print(f"Text preview: {result['text'][:200]}...")
        
        # Cleanup audio file
        os.remove(audio_path)
        print(f"Cleaned up temporary audio file")
        
    else:
        print("Transcription failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
