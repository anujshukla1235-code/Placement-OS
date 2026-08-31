import hashlib


def generate_hash_chain(
    content,
    previous_hash="0" * 64,
    student_name="",
    company_name="",
    role="",
    ctc="",
    joining_date="",
):
    content_string = f"{student_name}|{company_name}|{role}|{ctc}|{joining_date}|{content}|{previous_hash}"
    return hashlib.sha256(content_string.encode("utf-8")).hexdigest()
