from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import re

def hybrid_summarize_advanced(text, sentence_count=3):
    """Create meaningful summary with proper text processing"""
    try:
        if not text or len(str(text).strip()) == 0:
            return "No text available for summarization."
            
        text = str(text).strip()
        
        # Clean and preprocess text
        cleaned_text = preprocess_text(text)
        word_count = len(cleaned_text.split())
        
        print(f"📝 Generating summary from {word_count} words...")
        
        # For very short texts, return as is
        if word_count < 50:
            return extract_key_sentences(cleaned_text, min(2, len(cleaned_text.split('.'))))
            
        # Try advanced summarization
        try:
            summary = advanced_summarize(cleaned_text, sentence_count)
            if summary and is_valid_summary(summary, cleaned_text):
                return summary
        except Exception as e:
            print(f"Advanced summarization failed: {e}")
        
        # Fallback methods
        return create_intelligent_summary(cleaned_text, sentence_count)
        
    except Exception as e:
        print(f"Summarization failed: {e}")
        return get_fallback_summary(text)

def preprocess_text(text):
    """Clean and prepare text for summarization"""
    # Fix common speech recognition errors
    text = re.sub(r'\bi\b', 'I', text)  # Fix 'i' to 'I'
    text = re.sub(r" i'm ", " I'm ", text)
    text = re.sub(r" i've ", " I've ", text)
    text = re.sub(r" i'll ", " I'll ", text)
    text = re.sub(r" i'd ", " I'd ", text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Ensure proper sentence structure
    sentences = text.split('. ')
    cleaned_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            # Capitalize first letter
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
            # Ensure sentence ends with period
            if not sentence.endswith('.'):
                sentence += '.'
            cleaned_sentences.append(sentence)
    
    return ' '.join(cleaned_sentences)

def advanced_summarize(text, sentence_count=3):
    """Use LSA for extractive summarization"""
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        stemmer = Stemmer("english")
        
        # Use LSA summarizer
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        
        # Get summary sentences
        summary_sentences = []
        for sentence in summarizer(parser.document, sentence_count + 2):
            sentence_text = str(sentence).strip()
            if sentence_text and len(sentence_text.split()) > 3:
                summary_sentences.append(sentence_text)
        
        if summary_sentences:
            # Ensure summary is significantly shorter than original
            original_word_count = len(text.split())
            summary_word_count = len(' '.join(summary_sentences).split())
            
            if summary_word_count < original_word_count * 0.8:  # At least 20% reduction
                summary = '. '.join(summary_sentences[:sentence_count])
                if not summary.endswith('.'):
                    summary += '.'
                return summary
        
        return None
        
    except Exception as e:
        print(f"LSA summarization error: {e}")
        return None

def extract_key_sentences(text, sentence_count=2):
    """Extract important sentences for short texts"""
    sentences = text.split('. ')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= sentence_count:
        return text
    
    # Select first and last sentences (usually most important)
    selected = []
    if sentences:
        selected.append(sentences[0])  # Introduction
    if len(sentences) > 1 and sentences[-1] not in selected:
        selected.append(sentences[-1])  # Conclusion
    
    # Add middle sentence if needed
    if len(selected) < sentence_count and len(sentences) > 2:
        middle_idx = len(sentences) // 2
        if sentences[middle_idx] not in selected:
            selected.append(sentences[middle_idx])
    
    summary = '. '.join(selected[:sentence_count])
    if not summary.endswith('.'):
        summary += '.'
    
    return summary

def create_intelligent_summary(text, sentence_count=3):
    """Create summary by selecting diverse sentences"""
    try:
        sentences = text.split('. ')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= sentence_count:
            return text
        
        # Score sentences by position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0
            # First and last sentences get higher scores
            if i == 0 or i == len(sentences) - 1:
                score += 2
            # Medium length sentences are often most informative
            word_count = len(sentence.split())
            if 8 <= word_count <= 25:
                score += 1
            scored_sentences.append((score, sentence))
        
        # Sort by score and take top sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:sentence_count]]
        
        # Sort back to original order for coherence
        top_sentences_sorted = []
        for sentence in sentences:
            if sentence in top_sentences:
                top_sentences_sorted.append(sentence)
        
        summary = '. '.join(top_sentences_sorted)
        if not summary.endswith('.'):
            summary += '.'
            
        return summary
        
    except Exception as e:
        print(f"Intelligent summary failed: {e}")
        return extract_key_sentences(text, sentence_count)

def is_valid_summary(summary, original_text):
    """Check if summary is actually different from original"""
    summary_words = set(summary.lower().split())
    original_words = set(original_text.lower().split())
    
    # Summary should be at least 30% different from original
    common_words = summary_words.intersection(original_words)
    similarity = len(common_words) / len(summary_words) if summary_words else 0
    
    return similarity < 0.7 and len(summary.split()) < len(original_text.split()) * 0.8

def get_fallback_summary(text):
    """Final fallback summary"""
    try:
        # Return first 100 words or 30% of text, whichever is smaller
        words = text.split()
        if len(words) <= 100:
            return text
        else:
            summary_length = min(100, int(len(words) * 0.3))
            return ' '.join(words[:summary_length]) + '...'
    except:
        return "Summary unavailable."

# Test function
if __name__ == "__main__":
    test_text = "This is a test document. It contains multiple sentences. Each sentence should be processed separately. The summary should capture the main points. This is the final sentence. Another point to consider is that summaries need to be concise. They should avoid repetition and focus on key information."
    print("Testing summarization:")
    print(f"Original: {test_text}")
    print(f"Summary: {hybrid_summarize_advanced(test_text)}")