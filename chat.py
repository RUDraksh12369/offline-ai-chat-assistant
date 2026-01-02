# chat.py

import sqlite3
from llm import generate
from config import CHAT_TEMPERATURE, CHAT_MAX_TOKENS

DB_PATH = "chat_memory.db"
MAX_CONVERSATIONS = 5

# ---------------- DATABASE ----------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Conversations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Messages per conversation
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    role TEXT,
    message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Global long-term memory (name, preferences, etc.)
cursor.execute("""
CREATE TABLE IF NOT EXISTS global_memory (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()

current_conversation_id = None


# ---------------- GLOBAL MEMORY ----------------
def save_global_memory(key: str, value: str):
    cursor.execute(
        "INSERT OR REPLACE INTO global_memory (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()


def load_global_memory() -> dict:
    cursor.execute("SELECT key, value FROM global_memory")
    return dict(cursor.fetchall())


def extract_important_fact(text: str):
    """
    Uses the LLM to extract important long-term facts.
    Returns (key, value) or None.
    """
    prompt = f"""
Extract important personal information from the message.
If none, respond with NONE.

Respond strictly in this format:
key=value

Message:
{text}
"""
    result = generate(
        prompt,
        temperature=0.2,
        max_tokens=32
    ).strip()

    if result.upper() == "NONE" or "=" not in result:
        return None

    key, value = result.split("=", 1)
    return key.strip(), value.strip()


# ---------------- CONVERSATION MANAGEMENT ----------------
def enforce_conversation_limit():
    cursor.execute(
        "SELECT id FROM conversations ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()

    if len(rows) > MAX_CONVERSATIONS:
        for (cid,) in rows[MAX_CONVERSATIONS:]:
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (cid,)
            )
            cursor.execute(
                "DELETE FROM conversations WHERE id = ?",
                (cid,)
            )
        conn.commit()


def create_conversation(title="New Chat") -> int:
    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )
    conn.commit()
    enforce_conversation_limit()
    return cursor.lastrowid


def get_conversations():
    cursor.execute(
        "SELECT id, title FROM conversations ORDER BY created_at DESC"
    )
    return cursor.fetchall()


def set_current_conversation(cid: int):
    global current_conversation_id
    current_conversation_id = cid


def load_messages(conversation_id: int, limit=30):
    cursor.execute("""
        SELECT role, message
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        LIMIT ?
    """, (conversation_id, limit))
    return cursor.fetchall()


def save_message(conversation_id: int, role: str, message: str):
    cursor.execute("""
        INSERT INTO messages (conversation_id, role, message)
        VALUES (?, ?, ?)
    """, (conversation_id, role, message))
    conn.commit()


# ---------------- RESET FUNCTIONS ----------------
def delete_all_chats():
    """
    Deletes all chats but keeps global memory.
    """
    global current_conversation_id
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM conversations")
    conn.commit()
    current_conversation_id = None


def hard_reset():
    """
    Deletes everything including global memory.
    """
    global current_conversation_id
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM conversations")
    cursor.execute("DELETE FROM global_memory")
    conn.commit()
    current_conversation_id = None


# ---------------- CHAT FUNCTION ----------------
def chat(user_input: str) -> str:
    global current_conversation_id

    # Create a conversation if none exists
    if current_conversation_id is None:
        current_conversation_id = create_conversation(
            title=user_input[:30]
        )

    # Extract & save long-term memory
    fact = extract_important_fact(user_input)
    if fact:
        key, value = fact
        save_global_memory(key, value)

    # Save user message
    save_message(current_conversation_id, "user", user_input)

    # Load memories
    global_memory = load_global_memory()
    history = load_messages(current_conversation_id)

    # Build prompt
    prompt = "You are a helpful offline AI assistant.\n\n"

    if global_memory:
        prompt += "Important information about the user:\n"
        for k, v in global_memory.items():
            prompt += f"- {k}: {v}\n"
        prompt += "\n"

    for role, msg in history:
        prefix = "User:" if role == "user" else "AI:"
        prompt += f"{prefix} {msg}\n"

    prompt += "AI:"

    # Generate response
    response = generate(
        prompt,
        temperature=CHAT_TEMPERATURE,   # 0.7
        max_tokens=CHAT_MAX_TOKENS       # 2048
    )

    # Save AI response
    save_message(current_conversation_id, "ai", response)

    return response
