from flask import Flask, render_template, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
import shutil

# Import our modular services
from audio_processor import extract_audio_from_video, get_video_duration
from transcription_service import transcribe_audio
from translation_service import translate_text, LANGUAGES
from summarization_service import hybrid_summarize_advanced

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB
app.config['ALLOWED_EXTENSIONS'] = {'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_files(file_paths):
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up {file_path}: {e}")

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/test-translation')
def test_translation():
    """Route to test translation service"""
    print("🧪 Running translation service test...")
    test_translation_service()
    return jsonify({'message': 'Check console for test results'})

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    temp_files = []
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'})
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No video file selected'})
        
        if not allowed_file(video_file.filename):
            return jsonify({'success': False, 'error': 'Only MP4 files are allowed'})
        
        target_language = request.form.get('language', 'hi')
        if target_language not in LANGUAGES:
            return jsonify({'success': False, 'error': 'Invalid language selected'})
        
        # Save uploaded file
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        video_file.save(video_path)
        temp_files.append(video_path)
        
        # Check video duration (max 5 minutes)
        duration = get_video_duration(video_path)
        if duration > 300:
            cleanup_files(temp_files)
            return jsonify({'success': False, 'error': 'Video must be 5 minutes or shorter'})
        
        # Extract audio
        audio_path, temp_dir = extract_audio_from_video(video_path)
        temp_files.append(audio_path)
        temp_files.append(temp_dir)
        
        # Transcribe audio to English
        english_text = transcribe_audio(audio_path)
        
        if not english_text or len(english_text.strip()) == 0:
            cleanup_files(temp_files)
            return jsonify({'success': False, 'error': 'No speech detected in the video'})
        
        print(f"📊 Original transcription: {len(english_text)} characters")
        
        # Translate to target language
        if target_language != 'en':
            translated_text = translate_text(english_text, target_language)
        else:
            translated_text = english_text
        
        # Clean up files
        cleanup_files(temp_files)
        
        return jsonify({
            'success': True,
            'transcription_english': english_text,
            'transcription_target': translated_text,
            'language': LANGUAGES[target_language],
            'original_length': len(english_text),
            'translated_length': len(translated_text) if translated_text else 0
        })
        
    except Exception as e:
        cleanup_files(temp_files)
        print(f"❌ Transcription route error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/summarize', methods=['POST'])
def summarize_video():
    temp_files = []
    try:
        # Validate request
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'})
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No video file selected'})
        
        if not allowed_file(video_file.filename):
            return jsonify({'success': False, 'error': 'Only MP4 files are allowed'})
        
        target_language = request.form.get('language', 'hi')
        if target_language not in LANGUAGES:
            return jsonify({'success': False, 'error': 'Invalid language selected'})
        
        # Save uploaded file
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        video_file.save(video_path)
        temp_files.append(video_path)
        
        # Check video duration
        duration = get_video_duration(video_path)
        if duration > 300:
            cleanup_files(temp_files)
            return jsonify({'success': False, 'error': 'Video must be 5 minutes or shorter'})
        
        # Extract audio
        audio_path, temp_dir = extract_audio_from_video(video_path)
        temp_files.append(audio_path)
        temp_files.append(temp_dir)
        
        # Transcribe audio to English
        english_text = transcribe_audio(audio_path)
        
        if not english_text or len(english_text.strip()) == 0:
            cleanup_files(temp_files)
            return jsonify({'success': False, 'error': 'No speech detected in the video'})
        
        # Create summary in English
        english_summary = hybrid_summarize_advanced(english_text)
        
        # Translate summary to target language
        if target_language != 'en':
            translated_summary = translate_text(english_summary, target_language)
        else:
            translated_summary = english_summary
        
        # Clean up files
        cleanup_files(temp_files)
        
        return jsonify({
            'success': True,
            'summary_english': english_summary,
            'summary_target': translated_summary,
            'language': LANGUAGES[target_language],
            'original_text_length': len(english_text),
            'summary_length': len(english_summary)
        })
        
    except Exception as e:
        cleanup_files(temp_files)
        print(f"❌ Summarize route error: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)