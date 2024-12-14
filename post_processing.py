import re

def german_word_correction(text: str) -> str:
    """Correct commonly misread German medical terms."""
    corrections = {
        'Abklarung': 'Abklärung',
        'Aktivitat': 'Aktivität',
        'Aktivitatsparameter': 'Aktivitätsparameter',

    }

    # Create case-insensitive replacements
    for wrong, correct in list(corrections.items()):
        # Add title case version
        if wrong.title() != wrong:
            corrections[wrong.title()] = correct.title()
        # Add upper case version
        if wrong.upper() != wrong:
            corrections[wrong.upper()] = correct.upper()

    # Apply  word replacements
    for wrong, correct in corrections.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text)
    # Special character replacements
    special_chars = [
        (r'â', 'ä'), (r'ô', 'ö'), (r'û', 'ü'), (r'à', 'ä'),
        (r'Â', 'Ä'), (r'Ô', 'Ö'), (r'Û', 'Ü'), (r'À', 'Ä')
    ]
    
    # Unit corrections
    unit_corrections = [
        (r'/u1(?![a-zA-Z])', r'/µl'),
        (r'g7dl(?![a-zA-Z])', r'g/dl'),
        (r'g7a1(?![a-zA-Z])', r'g/dl'),        
        (r'(<\s*\d+|\d+)\s*Apl', r'\1 /µl')
    ]

    # Apply special character replacements
    for pattern, replacement in special_chars + unit_corrections:
        text = re.sub(pattern, replacement, text)
    
    return text
