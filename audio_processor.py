import os
import sys
import tempfile
from moviepy.editor import VideoFileClip

# -------------------------------------------------------------------
# Compatibility patch for Python 3.13 (audioop removed from stdlib)
# -------------------------------------------------------------------


from pydub import AudioSegment


def extract_audio_from_video(video_path):
    """
    Extracts the audio track from a video file and saves it as a WAV file.
    
    Args:
        video_path (str): Path to the video file.
    
    Returns:
        tuple: (path_to_extracted_audio, temp_directory_path)
    """
    try:
        # Create a temporary directory for extracted audio
        temp_dir = tempfile.mkdtemp()
        temp_audio_path = os.path.join(temp_dir, "audio.wav")

        # Extract audio using moviepy
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio

        if audio_clip is None:
            raise Exception("No audio stream found in the video.")

        # Write the audio to a WAV file (quietly)
        audio_clip.write_audiofile(temp_audio_path, verbose=False, logger=None)

        # Release resources
        audio_clip.close()
        video_clip.close()

        return temp_audio_path, temp_dir

    except Exception as e:
        raise Exception(f"Audio extraction failed: {str(e)}")


def convert_to_wav(audio_path):
    """
    Converts an audio file to WAV format using pydub.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        str: Path to the converted WAV file.
    """
    try:
        ext = os.path.splitext(audio_path)[1].lower()

        # If it's already a WAV file, just return it
        if ext == '.wav':
            return audio_path

        # Load based on file extension
        if ext == '.mp3':
            audio = AudioSegment.from_mp3(audio_path)
        elif ext == '.m4a':
            audio = AudioSegment.from_file(audio_path, format="m4a")
        else:
            audio = AudioSegment.from_file(audio_path)

        # Export to WAV
        wav_path = audio_path.replace(ext, '.wav')
        audio.export(wav_path, format='wav')

        return wav_path

    except Exception as e:
        raise Exception(f"Audio conversion failed: {str(e)}")


def get_video_duration(video_path):
    """
    Gets the duration of a video in seconds.

    Args:
        video_path (str): Path to the video file.

    Returns:
        float: Duration of the video in seconds (0 if not available).
    """
    try:
        video_clip = VideoFileClip(video_path)
        duration = video_clip.duration or 0
        video_clip.close()
        return duration
    except Exception as e:
        print(f"Warning: Could not get video duration: {e}")
        return 0
