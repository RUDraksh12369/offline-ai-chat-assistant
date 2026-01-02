# agent.py

from chat import chat
from tools import open_app, read_file


def handle(user_input: str) -> str:
    """
    Decide whether to call a tool or use the LLM.
    Tools are triggered ONLY by explicit commands.
    """

    text = user_input.strip().lower()

    # ---------- TOOL: OPEN ----------
    if text.startswith("open "):
        app_name = text.replace("open ", "", 1)
        return open_app(app_name)

    # ---------- TOOL: READ FILE ----------
    if text.startswith("read "):
        file_name = text.replace("read ", "", 1)
        return read_file(file_name)

    # ---------- FALLBACK: CHAT ----------
    return chat(user_input)
