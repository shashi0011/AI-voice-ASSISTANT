import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import threading
import pyttsx3

# === Import your assistant script functions ===
# Replace the following imports with your actual assistant logic or make sure they are accessible here
from assistant import greet_user, listen, find_best_match, commands, ask_openrouter, stop_listening

class AssistantThread(QThread):
    signal_update_text = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.listening = True

    def run(self):
        greet_user()
        while self.listening:
            user_input = listen()
            self.signal_update_text.emit(f"You said: {user_input}")

            if "exit" in user_input or "goodbye" in user_input:
                self.signal_update_text.emit("Goodbye! Exiting.")
                break
            elif "show menu" in user_input:
                self.signal_update_text.emit("Showing available commands...")
            else:
                match = find_best_match(user_input)
                if match:
                    self.signal_update_text.emit(f"Running: {match}")
                    commands[match]()
                else:
                    self.signal_update_text.emit("Thinking...")
                    response = ask_openrouter(user_input)
                    self.signal_update_text.emit(f"Assistant: {response}")


class AssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cutie Assistant")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        self.title = QLabel("\ud83e\udde0 Cutie is Listening...")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        self.listen_button = QPushButton("Start Listening")
        self.listen_button.clicked.connect(self.start_listening)
        layout.addWidget(self.listen_button)

        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.clicked.connect(self.stop_listening)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)
        self.assistant_thread = AssistantThread()
        self.assistant_thread.signal_update_text.connect(self.update_text)

    def start_listening(self):
        self.title.setText("\ud83d\udfe2 Listening...")
        if not self.assistant_thread.isRunning():
            self.assistant_thread.start()

    def stop_listening(self):
        self.title.setText("\u26d4 Paused")
        self.assistant_thread.listening = False
        stop_listening()

    def update_text(self, text):
        self.text_area.append(text)

        # In AssistantGUI
    
    def update_text(self, text):
    
        self.text_area.append(text)
    
        if text.startswith("Assistant:"):
    
            self.speak(text.replace("Assistant:", "").strip())
    
    
    def speak(self, message):
    
        try:
    
            engine = pyttsx3.init()
    
            engine.say(message)
    
            engine.runAndWait()
    
        except Exception as e:
    
            print("TTS error:", e)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantGUI()
    window.show()
    sys.exit(app.exec_())
