# app/utils/hash_utils.py

import hashlib


def generate_hash(content: str) -> str:
    """
    Generate SHA256 hash from text.
    """

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()