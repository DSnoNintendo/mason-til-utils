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

def extract_json_substring(text: str) -> str:
    """Extract a JSON substring starting from the first '{' or '[' character."""
    start_idx = -1
    for i, char in enumerate(text):
        if char in '{[':
            start_idx = i
            break
    
    if start_idx == -1:
        return ""
        
    # Track nested brackets to find the matching end bracket
    stack = []
    for i in range(start_idx, len(text)):
        char = text[i]
        if char in '{[':
            stack.append(char)
        elif char in '}]':
            if not stack:
                continue
            if (char == '}' and stack[-1] == '{') or (char == ']' and stack[-1] == '['):
                stack.pop()
                if not stack:  # Found matching end bracket
                    return text[start_idx:i+1]
    return ""