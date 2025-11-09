import speech_recognition as sr
import os
from audio_processor import convert_to_wav

def transcribe_audio(audio_path):
    """Transcribe audio to English"""
    try:
        recognizer = sr.Recognizer()
        
        # Convert to WAV if needed
        if not audio_path.endswith('.wav'):
            audio_path = convert_to_wav(audio_path)
        
        print("🔊 Transcribing audio to English...")
        
        with sr.AudioFile(audio_path) as source:
            # Adjust for ambient noise and record
            print("🎙️ Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("🎤 Recording audio...")
            audio_data = recognizer.record(source)
            
            # Perform speech recognition
            print("🔄 Converting speech to text...")
            text = recognizer.recognize_google(audio_data, language='en-US')
            
            print(f"✅ Transcription successful. Text length: {len(text)}")
            return text
            
    except sr.UnknownValueError:
        raise Exception("Speech recognition could not understand the audio. Please try with clearer audio.")
    except sr.RequestError as e:
        raise Exception(f"Speech recognition service error. Please check your internet connection: {e}")
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")