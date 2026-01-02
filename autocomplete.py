# autocomplete.py

from llm import generate
from config import AUTOCOMPLETE_TEMPERATURE, AUTOCOMPLETE_MAX_TOKENS


def suggest(text):
    """
    Suggests the next few words for a given partial text.
    """

    prompt = (
        "Continue the following text naturally.\n"
        "Only return the next few words. Do not repeat the text.\n\n"
        f"Text:\n{text}"
    )

    suggestion = generate(
        prompt,
        temperature=AUTOCOMPLETE_TEMPERATURE,
        max_tokens=AUTOCOMPLETE_MAX_TOKENS
    )

    return suggestion
