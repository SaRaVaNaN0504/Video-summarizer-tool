import os
import tempfile
from moviepy.editor import VideoFileClip
sys.modules["audioop"] = pyaudioop
from pydub import AudioSegment

def extract_audio_from_video(video_path):
    """Extract audio from video file and convert to WAV"""
    try:
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, "audio.wav")
        
        # Extract audio using moviepy
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        
        # Write audio file
        audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)
        
        # Close clips to free memory
        audio_clip.close()
        video_clip.close()
        
        return temp_audio_path, temp_dir
        
    except Exception as e:
        raise Exception(f"Audio extraction failed: {str(e)}")

def convert_to_wav(audio_path):
    """Convert any audio format to WAV using pydub"""
    try:
        # Get file extension
        ext = os.path.splitext(audio_path)[1].lower()
        
        if ext == '.wav':
            return audio_path
            
        # Load and convert
        if ext == '.mp3':
            audio = AudioSegment.from_mp3(audio_path)
        elif ext == '.m4a':
            audio = AudioSegment.from_file(audio_path, "m4a")
        else:
            # Try generic loading
            audio = AudioSegment.from_file(audio_path)
        
        # Export as WAV
        wav_path = audio_path.replace(ext, '.wav')
        audio.export(wav_path, format='wav')
        
        return wav_path
        
    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")

def get_video_duration(video_path):
    """Get video duration in seconds"""
    try:
        video_clip = VideoFileClip(video_path)
        duration = video_clip.duration
        video_clip.close()
        return duration
    except Exception as e:
        print(f"Warning: Could not get video duration: {e}")
        return 0