import re

CYRILLIC_SYMBOLS = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюяёъыэ'
TRANSLATION = ("a", "b", "v", "h", "g", "d", "e", "ye", "j", "z", "y", "i", "yi", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "kh", "ts", "ch", "sh", "sch", "", "yu", "ya", "yo", "", "y", "ye")


TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.title()

def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name

