from googletrans import Translator
import time
import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supported languages
LANGUAGES = {
    'ta': 'Tamil',
    'hi': 'Hindi', 
    'bn': 'Bengali',
    'te': 'Telugu',
    'mr': 'Marathi',
    'en': 'English'
}

# Language codes for different services
LANGUAGE_CODES = {
    'ta': 'ta', 'hi': 'hi', 'bn': 'bn', 'te': 'te', 'mr': 'mr', 'en': 'en'
}

def translate_text(text, target_lang):
    """Robust translation with multiple fallback methods"""
    try:
        if not text or len(str(text).strip()) == 0:
            return text

        cleaned_text = clean_text(text)
        logging.info(f"🌐 Translating {len(cleaned_text)} characters to {LANGUAGES.get(target_lang, target_lang)}")

        # Method 1: Try googletrans with error handling
        result = safe_googletrans_translate(cleaned_text, target_lang)
        if result:
            return result

        # Method 2: Fallback to simple split translation
        logging.info("🔄 Trying split translation method...")
        result = split_and_translate(cleaned_text, target_lang)
        if result:
            return result

        # Method 3: Final fallback
        logging.warning("⚠️ All translation methods failed, returning original text")
        return f"[Translation unavailable] {cleaned_text}"

    except Exception as e:
        logging.error(f"💥 Translation error: {str(e)}")
        return f"[Translation error] {text}"

def safe_googletrans_translate(text, target_lang):
    """Safe wrapper around googletrans with error handling"""
    try:
        translator = Translator()
        time.sleep(1)  # Rate limiting
        
        # For long texts, split into smaller chunks
        if len(text) > 500:
            return split_and_translate(text, target_lang)
        
        result = translator.translate(text, dest=target_lang)
        
        if result and hasattr(result, 'text') and result.text:
            return str(result.text).strip()
        return None
        
    except TypeError as e:
        if "sequence item" in str(e) and "NoneType" in str(e):
            logging.warning("🔧 Googletrans internal error detected, using fallback")
            return split_and_translate(text, target_lang)
        else:
            logging.error(f"Googletrans TypeError: {e}")
            return None
    except Exception as e:
        logging.error(f"Googletrans error: {e}")
        return None

def split_and_translate(text, target_lang, max_chunk_size=400):
    """Split text into chunks and translate separately"""
    try:
        translator = Translator()
        
        # Split text into sentences
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # Add any remaining text
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Filter out empty sentences
        sentences = [s for s in sentences if s and len(s.strip()) > 0]
        
        if not sentences:
            return text
        
        logging.info(f"📝 Split into {len(sentences)} sentences for translation")
        
        # Translate each sentence individually
        translated_sentences = []
        for i, sentence in enumerate(sentences):
            try:
                time.sleep(0.5)  # Rate limiting between sentences
                result = translator.translate(sentence, dest=target_lang)
                if result and hasattr(result, 'text') and result.text:
                    translated_sentences.append(str(result.text).strip())
                    logging.info(f"✅ Translated sentence {i+1}/{len(sentences)}")
                else:
                    translated_sentences.append(sentence)  # Keep original if translation fails
                    logging.warning(f"⚠️ Failed to translate sentence {i+1}, keeping original")
            except Exception as e:
                translated_sentences.append(sentence)  # Keep original on error
                logging.warning(f"⚠️ Error translating sentence {i+1}: {e}")
        
        # Combine all translated sentences
        final_translation = ' '.join(translated_sentences)
        logging.info(f"🎉 Successfully translated {len(sentences)} sentences")
        return final_translation
        
    except Exception as e:
        logging.error(f"Split translation error: {e}")
        return None

def clean_text(text):
    """Clean text for better translation"""
    try:
        text = str(text).strip()
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Fix common speech recognition issues
        replacements = {
            ' i ': ' I ',
            " i'm ": " I'm ",
            " i've ": " I've ",
            " i'll ": " I'll ",
            " i'd ": " I'd ",
        }
        
        for wrong, correct in replacements.items():
            text = text.replace(wrong, correct)
        
        # Ensure proper sentence structure
        if text and not text[-1] in '.!?':
            text += '.'
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return text
        
    except Exception as e:
        logging.error(f"Text cleaning error: {e}")
        return str(text)

def detect_language(text):
    """Detect the language of the given text"""
    try:
        translator = Translator()
        detected = translator.detect(text)
        return detected.lang, detected.confidence
    except Exception as e:
        logging.error(f"Language detection failed: {e}")
        return 'en', 0.0

# Test function
if __name__ == "__main__":
    test_text = "Hello world, this is a test of the translation service."
    result = translate_text(test_text, "ta")
    print(f"Test result: {result}")