def base64_decode(s):
    """Add missing padding to string and return the decoded base64 string."""
    if not s:
        return None

    s = s[s.index(','):]
    if not s:
        return None
    try:
        return s.decode('base64')
    except:
        s += '=' * (-len(s) % 4)  # restore stripped '='
        return s.decode('base64')

