# gui.py

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QMessageBox
)
from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtGui import QTextCursor, QFont

from agent import handle
from chat import (
    get_conversations,
    load_messages,
    set_current_conversation,
    create_conversation,
    delete_all_chats,
    hard_reset
)

MAX_CHATS = 5


# ---------------- WORKER THREAD ----------------
class Worker(QThread):
    response_ready = Signal(str)

    def __init__(self, user_text):
        super().__init__()
        self.user_text = user_text

    def run(self):
        response = handle(self.user_text)
        self.response_ready.emit(response)


# ---------------- MAIN WINDOW ----------------
class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Offline AI Assistant")
        self.resize(980, 620)

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(8)

        # ---------- SIDEBAR ----------
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(6)

        self.new_chat_btn = QPushButton("➕ New Chat")
        self.new_chat_btn.clicked.connect(self.new_chat)

        self.delete_chats_btn = QPushButton("🧹 Delete All Chats")
        self.delete_chats_btn.clicked.connect(self.confirm_delete_chats)

        self.hard_reset_btn = QPushButton("🔥 Hard Reset")
        self.hard_reset_btn.clicked.connect(self.confirm_hard_reset)

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color:#d9534f;font-size:10px;")
        self.warning_label.setWordWrap(True)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(230)
        self.sidebar.itemClicked.connect(self.load_conversation)

        sidebar_layout.addWidget(self.new_chat_btn)
        sidebar_layout.addWidget(self.delete_chats_btn)
        sidebar_layout.addWidget(self.hard_reset_btn)
        sidebar_layout.addWidget(self.warning_label)
        sidebar_layout.addWidget(self.sidebar, 1)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)

        # ---------- CHAT AREA ----------
        chat_layout = QVBoxLayout()
        chat_layout.setSpacing(6)

        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)

        # 🔑 FIX SPACING PROPERLY
        self.chat_box.document().setDocumentMargin(4)
        self.chat_box.setStyleSheet("""
            QTextEdit { padding: 4px; }
            .user { margin-bottom: 4px; }
            .ai { margin-bottom: 8px; }
        """)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message…")
        self.input_box.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)

        # Fonts
        self.chat_box.setFont(QFont("Segoe UI", 11))
        self.input_box.setFont(QFont("Segoe UI", 12))
        self.send_btn.setFont(QFont("Segoe UI", 11))

        chat_layout.addWidget(self.chat_box, 1)
        chat_layout.addWidget(self.input_box)
        chat_layout.addWidget(self.send_btn)

        main_layout.addWidget(sidebar_widget)
        main_layout.addLayout(chat_layout, 1)

        # ---------- TYPING EFFECT ----------
        self.full_response = ""
        self.current_index = 0
        self.current_cursor = None

        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.type_next_char)

        self.worker = None
        self.load_sidebar()

    # ---------- SIDEBAR ----------
    def load_sidebar(self):
        self.sidebar.clear()
        conversations = get_conversations()

        for i, (cid, _) in enumerate(conversations, start=1):
            item = QListWidgetItem(f"Chat {i}")
            item.setData(1, cid)
            self.sidebar.addItem(item)

        self.warning_label.setText(
            "⚠ Oldest chat will be deleted when a new chat is created"
            if len(conversations) >= MAX_CHATS else ""
        )

    def load_conversation(self, item):
        cid = item.data(1)
        set_current_conversation(cid)
        self.chat_box.clear()

        for role, msg in load_messages(cid):
            name = "You" if role == "user" else "AI"
            cls = "user" if role == "user" else "ai"
            self.chat_box.append(
                f'<div class="{cls}"><b>{name}:</b> {msg}</div>'
            )

    # ---------- ACTIONS ----------
    def new_chat(self):
        cid = create_conversation()
        set_current_conversation(cid)
        self.chat_box.clear()
        self.load_sidebar()

    def confirm_delete_chats(self):
        if QMessageBox.question(
            self,
            "Delete All Chats",
            "Delete all chats but keep personal memory?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            delete_all_chats()
            self.chat_box.clear()
            self.load_sidebar()

    def confirm_hard_reset(self):
        if QMessageBox.warning(
            self,
            "Hard Reset",
            "⚠ This deletes EVERYTHING.\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            hard_reset()
            self.chat_box.clear()
            self.load_sidebar()

    # ---------- CHAT ----------
    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.input_box.clear()
        self.chat_box.append(
            f'<div class="user"><b>You:</b> {text}</div>'
        )

        self.input_box.setDisabled(True)
        self.send_btn.setDisabled(True)

        self.worker = Worker(text)
        self.worker.response_ready.connect(self.start_typing)
        self.worker.start()

    def start_typing(self, response):
        self.full_response = response
        self.current_index = 0

        self.chat_box.append('<div class="ai"><b>AI:</b> ')
        self.current_cursor = self.chat_box.textCursor()
        self.current_cursor.movePosition(QTextCursor.End)

        self.typing_timer.start(12)

    def type_next_char(self):
        if self.current_index < len(self.full_response):
            self.current_cursor.insertText(
                self.full_response[self.current_index]
            )
            self.current_index += 1
        else:
            self.typing_timer.stop()
            self.current_cursor.insertHtml("</div>")
            self.input_box.setDisabled(False)
            self.send_btn.setDisabled(False)
            self.input_box.setFocus()


# ---------- APP ENTRY ----------
def run_gui():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
