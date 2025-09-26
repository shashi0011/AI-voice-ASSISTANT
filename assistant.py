import os
import pvporcupine
import pyaudio
import numpy as np
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pyautogui
import difflib
import requests
import json
import smtplib 

from email.message import EmailMessage
from plyer import notification
from dotenv import load_dotenv
import shutil
import time
import psutil  

load_dotenv()  # Load .env variables if you're using one

# === Setup TTS engine ===
engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# === Greeting ===
def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        speak("Good morning! How can I help you?")
    elif 12 <= hour < 18:
        speak("Good afternoon! What can I do for you?")
    else:
        speak("Good evening! Ready when you are.")

# === Speech to text ===
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        return ""

# === OpenRouter + DeepSeek integration ===
def ask_openrouter(question):
    OPENROUTER_API_KEY = "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"

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "X-Title": "Cutie Assistant"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": question}]
            })
        )

        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return answer

    except Exception as e:
        print("OpenRouter error:", e)
        return "Sorry, I couldn't reach DeepSeek right now."

# === Show Command Menu ===
def show_command_menu():
    speak("Here are some things I can do:")
    print("👉 Available commands:")
    for cmd in commands:
        print(f"👉 {cmd}")
        speak(cmd)

# === Command Dictionary ===
commands = {
    "open chrome": lambda: os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
    "open youtube": lambda: webbrowser.open("https://youtube.com"),
    "take screenshot": lambda: pyautogui.screenshot().save("screenshot.png"),
    "what time is it": lambda: speak(datetime.datetime.now().strftime("%I:%M %p")),
    "shutdown": lambda: os.system("shutdown /s /t 1"),
    "open whatsapp": lambda: os.startfile("C:\\Users\\ravig\\AppData\\Local\\WhatsApp\\WhatsApp.exe"),
    "open vs code": lambda: os.startfile("C:\\Users\\ravig\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"),
    "open file": lambda: open_file("path_to_file"),
    "organize files": lambda: organize_files(),
    "clean temp files": lambda: clean_temp_files(),
    "set alarm": lambda: set_alarm(),
    "play youtube": lambda: play_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    "play music": lambda: play_music("C:/path/to/music.mp3"),
    "read emails": lambda: read_unread_emails(),
    "open website": lambda: open_website("https://www.example.com"),
    "close whatsapp": lambda: close_app("WhatsApp"),
    "close vs code": lambda: close_app("Code"),
     "stop listening": lambda: stop_listening(),
    "resume listening": lambda: resume_listening()
}

# === File Operations ===
def open_file(file_path):
    try:
        os.startfile(file_path)
        speak(f"Opening file: {file_path}")
    except Exception as e:
        speak(f"Error opening file: {e}")

# === Organize Files ===
def organize_files():
    try:
        downloads_folder = "C:/Users/ravig/Downloads"
        documents_folder = "C:/Users/ravig/Documents/Organized"
        if not os.path.exists(documents_folder):
            os.makedirs(documents_folder)

        for file_name in os.listdir(downloads_folder):
            file_path = os.path.join(downloads_folder, file_name)
            if os.path.isfile(file_path):
                shutil.move(file_path, os.path.join(documents_folder, file_name))

        speak("Files have been organized.")
    except Exception as e:
        speak(f"Error organizing files: {e}")

# === Clean Temp Files ===
def clean_temp_files():
    try:
        temp_folder = "C:/Users/ravig/AppData/Local/Temp"
        for file_name in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Could not delete {file_name}: {e}")
        speak("Temporary files have been cleaned.")
    except Exception as e:
        speak(f"Error cleaning temp files: {e}")

# === Set Alarm ===
def set_alarm(time_str="14:30"):
    try:
        alarm_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        current_time = datetime.datetime.now().time()

        time_diff = datetime.datetime.combine(datetime.date.today(), alarm_time) - datetime.datetime.combine(datetime.date.today(), current_time)
        if time_diff.total_seconds() < 0:
            time_diff += datetime.timedelta(days=1)

        speak(f"Alarm set for {time_str}.")
        time.sleep(time_diff.total_seconds())
        speak("Time to wake up!")
    except Exception as e:
        speak(f"Error setting alarm: {e}")

# === Play YouTube Video ===
def play_youtube_video(video_url):
    webbrowser.open(video_url)
    speak("Playing the YouTube video.")

# === Play Music ===
def play_music(music_file):
    try:
        #playsound(music_file)
        speak(f"Playing music from {music_file}.")
    except Exception as e:
        speak(f"Error playing music: {e}")

# === Read Unread Emails (Gmail) ===
def read_unread_emails():
    try:
        import imaplib
        import email

        email_user = "your_email@gmail.com"  # Replace with your email
        email_pass = "your_password"  # Replace with your email password
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        
        if len(email_ids) > 0:
            speak("You have unread emails. I'll read the most recent one.")
            latest_email_id = email_ids[-1]
            status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    from_ = msg["from"]
                    speak(f"You have a new email from {from_} with the subject: {subject}")
        else:
            speak("No unread emails.")

        mail.logout()
    except Exception as e:
        speak(f"Error reading emails: {e}")

# === Open Website ===
def open_website(url):
    try:
        webbrowser.open(url)
        speak(f"Opening website: {url}")
    except Exception as e:
        speak(f"Error opening website: {e}")

# === Close Apps ===
def close_app(app_name):
    try:
        # Iterate through running processes and terminate the app
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if app_name.lower() in proc.info['name'].lower():
                proc.terminate()
                speak(f"{app_name} has been closed.")
                return
        speak(f"{app_name} is not running.")
    except Exception as e:
        speak(f"Error closing {app_name}: {e}")

        # Global flag to control listening state
is_listening = True

# Function to stop listening
def stop_listening():
    global is_listening
    is_listening = False
    speak("I am now paused. Say 'resume listening' to continue.")

# Function to resume listening
def resume_listening():
    global is_listening
    is_listening = True
    speak("I am now listening again.")


# === Find Best Match ===
def find_best_match(user_input):
    matches = difflib.get_close_matches(user_input, commands.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

# === Main Assistant Loop ===
def run_assistant_loop():
    global is_listening

    while True:
        if is_listening:
            user_input = listen()

            if "exit" in user_input or "goodbye" in user_input:
                speak("Goodbye! Have a great day.")
                break
            elif "show menu" in user_input:
                show_command_menu()
            else:
                match = find_best_match(user_input)
                if match:
                    speak(f"Running command: {match}")
                    commands[match]()
                else:
                    speak("Let me think about that...")
                    response = ask_openrouter(user_input)
                    speak(response)


# === Wake Word Detection ===
def listen_for_wake_word():
    ACCESS_KEY = "ffztkzGHdmjyFSvvFMS66jfM6UKAdkPgCnkqrPah1CG6l1nINyyrIw=="
    KEYWORD_PATH = "C:\\Users\\ravig\\OneDrive\\Documents\\facebook\\AI\\hello-cutie.ppn"

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[KEYWORD_PATH]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("👂 Waiting for wake word: 'Cutie'...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = np.frombuffer(pcm, dtype=np.int16)

            result = porcupine.process(pcm)
            if result >= 0:
                print("🟢 Wake word detected!")
                break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

# === Main ===
if __name__ == "__main__":
    listen_for_wake_word()
    greet_user()
    run_assistant_loop()
