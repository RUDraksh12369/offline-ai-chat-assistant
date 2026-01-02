

```markdown
# Offline AI Chat Assistant (ChatGPT-like Desktop App)

A fully **offline**, **local LLM-powered** chat assistant with a modern desktop UI, persistent memory, multi-chat support, and smart autocomplete — built using **Python**, **Ollama**, and **PySide6**.

This project is designed to explore **LLM integration**, **agent-based architecture**, and **desktop AI UX**, without relying on cloud APIs.

---

## ✨ Features

### 🧠 AI & Memory
- Runs **fully offline** using open-source LLMs via **Ollama**
- Global long-term memory (remembers name, preferences across chats)
- Conversation-based short-term memory
- Configurable response creativity (temperature)
- Safe token limits for stability

### 💬 Chat Experience
- Multiple chat sessions (Chat 1–Chat 5)
- Automatic deletion of oldest chats after limit
- Continue conversations anytime
- Delete all chats (keep memory)
- Hard reset (wipe everything)

### 🖥️ Desktop UI
- Modern PySide6 GUI
- Sidebar for chat history (ChatGPT-style)
- Smooth typing / streaming effect
- No UI freezing (background threads)

### ⌨️ Smart Autocomplete
- Mobile-style **word suggestion chips**
- Suggests complete words (not letters)
- Debounced & async (no lag)
- Click-to-complete input
- Fully offline autocomplete logic

### 🛠️ Agent + Tools
- Intelligent routing between:
  - Chat (LLM)
  - System tools (open apps, read files)
- Tools trigger **only on explicit commands**
  - `open notepad`
  - `read test.txt`

---

## 🏗️ Project Structure

```

.
├── main.py              # Application entry point
├── gui.py               # PySide6 GUI (chat, sidebar, autocomplete)
├── chat.py              # Chat logic + memory + database
├── agent.py             # Tool vs chat routing
├── tools.py             # System tools (open app, read file)
├── autocomplete.py      # Word suggestion logic
├── llm.py               # Ollama LLM interface
├── config.py            # Temperature & token settings
├── chat_memory.db       # SQLite database (auto-created)
└── README.md

```

---

## ⚙️ Requirements

- Python **3.10+** (tested on 3.13)
- Ollama installed and running
- A local model (e.g. `llama3`, `mistral`, `qwen`)
- OS: Windows / Linux / macOS

### Python Dependencies

```

pip install PySide6 requests

````

---

## 🚀 Getting Started

### 1️⃣ Install Ollama
👉 https://ollama.com/

Pull a model:
```bash
ollama pull llama3
````

Run Ollama:

```bash
ollama serve
```

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/offline-ai-chat-assistant.git
cd offline-ai-chat-assistant
```

---

### 3️⃣ Run the App

```bash
python main.py
```

---

## 🧪 Example Commands

### Normal Chat

```
Write a simple C++ calculator program
What is my name?
Explain pointers in C++
```

### Tool Commands

```
open notepad
read test.txt
```

### Memory

```
My name is Rudra
I prefer learning with examples
```

The assistant will remember this **across chats**.

---

## 🧠 Design Philosophy

* **Offline-first** → privacy & control
* **Explicit tools** → no accidental actions
* **Separation of concerns**

  * UI ≠ AI ≠ Tools ≠ Memory
* **Performance-aware**

  * Debounced autocomplete
  * Background threads
  * Safe token limits

---

## 🔒 Privacy

* No cloud APIs
* No telemetry
* All data stored locally in SQLite
* You control deletion and reset

---

## 📌 Limitations

* Depends on local model quality
* Not intended for large-scale deployment
* No true token streaming (simulated typing effect)

---

## 🔮 Future Improvements

* Markdown & code block rendering
* Auto-continue long responses
* Memory inspector UI
* Dark mode theming
* Voice input / TTS
* Packaging as `.exe`

---

## 🤝 Contributing

This project is primarily for learning and experimentation, but suggestions and improvements are welcome.

---

## 📜 License

MIT License

---

## ⭐ Acknowledgements

* Ollama (local LLM runtime)
* Open-source LLM community
* Qt / PySide6

---

