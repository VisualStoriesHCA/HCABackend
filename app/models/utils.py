import re

from diff_match_patch import diff_match_patch


def generate_user_id(user_name: str) -> str:
    return "id_" + user_name


def tokenize(text):
    return re.findall(r'\s+|\w+|[^\w\s]', text, re.UNICODE)


def highlight_additions(old_text, new_text):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diffs)

    result = []
    for op, data in diffs:
        if op == dmp.DIFF_EQUAL:
            result.append(data)
        elif op == dmp.DIFF_INSERT:
            for char in data:
                if char.isspace():
                    result.append(char)
                else:
                    result.append(f"<mark>{char}</mark>")
    return ''.join(result)


def get_raw_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("<mark>", "").replace("</mark>", "")
