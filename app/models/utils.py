import difflib
def generate_user_id(user_name: str) -> str:
    return "id_" + user_name


def highlight_additions(old_text, new_text: str) -> str:
    old_words = old_text.split()
    new_words = new_text.split()

    matcher = difflib.SequenceMatcher(None, old_words, new_words)
    result = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == 'equal':
            result.extend(new_words[j1:j2])
        elif opcode in ('insert', 'replace'):
            for word in new_words[j1:j2]:
                result.append(f"<mark>{word}</mark>")
        # 'delete' ignored

    return ' '.join(result)


def get_raw_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("<mark>", "").replace("</mark>", "")
