from multiprocessing import Manager
import re


def create_shared_data():
    manager = Manager()
    shared_data = manager.dict({
        'counter': 0,
        'processes': manager.dict(),
        'queries': manager.list(),
    })
    return shared_data

def create_query(query: str, **kwargs):
    return query.format(**kwargs)

def clean_deep_research_text(text):
    """
    Remove both <think> tags and source citations from text.
    
    Args:
        text (str): Input text containing tags to be removed
        
    Returns:
        str: Cleaned text with all specified tags removed
    """
    # Remove <think> tags and surrounding whitespace
    text = re.sub(r'\s*<think>.*?</think>\s*', '', text, flags=re.DOTALL)
    
    # Remove source citations [1], [2], etc. (including optional whitespace inside brackets)
    text = re.sub(r'\[\s*\d+\s*\]', '', text)
    
    return text.strip()