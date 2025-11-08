import pytesseract
import cv2
import pyttsx3
import os
import speech_recognition as sr
import subprocess
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox

# Set Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# Set Indian English voice if available
voices = engine.getProperty("voices")
for voice in voices:
    if "IN" in voice.id or "Heera" in voice.name or "Ravi" in voice.name:
        engine.setProperty("voice", voice.id)
        break

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def image_processing_mode():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Cannot open webcam.")
        return

    speak("Press 'a' to capture the frame...")

    while True:
        status, frame = cap.read()
        if not status:
            speak("Failed to grab frame.")
            break

        cv2.imshow('Live Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('a'):
            save_path = r"C:\Temp\Captain.png"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, frame)
            print(f"Image saved to {save_path}")
            break

    cap.release()
    cv2.destroyAllWindows()

    img = cv2.imread(save_path)
    if img is None:
        speak("Image not found.")
        return

    mytext = pytesseract.image_to_string(img)
    print("Detected Text:\n", mytext)

    boxes = pytesseract.image_to_boxes(img)
    hIMG, wIMG, _ = img.shape

    for b in boxes.splitlines():
        b = b.split(' ')
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x, hIMG - y), (w, hIMG - h), (250, 0, 0), 1)
        cv2.putText(img, b[0], (x - 20, hIMG - y - 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)

    cv2.imshow("Detected Text", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    speak(mytext)

def voice_assistant_mode():
    recognizer = sr.Recognizer()
    running = True

    def listen():
        with sr.Microphone() as source:
            print("🎤 Listening...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio).strip().lower()
                print("You said:", command)
                return command
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
            except sr.RequestError:
                speak("Network error.")
            return ""

    def execute_command(command):
        nonlocal running
        if any(phrase in command for phrase in ["exit", "quit", "close", "stop", "terminate", "goodbye"]):
            speak("Goodbye!")
            running = False
        elif "open notepad" in command:
            speak("Opening Notepad")
            subprocess.Popen(["notepad.exe"])

        elif "kaise ho" in command:
            speak("I am fine.")
            
        elif "open chrome" in command:
            speak("Opening Chrome")
            subprocess.Popen(["C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"])

        elif "what time is it" in command:
            now = datetime.now().strftime("%H:%M:%S")
            speak(f"The current time is {now}")

        elif "open office" in command:
            speak("Opening office")
            subprocess.Popen(["C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"])
        elif "open team" in command:
            speak("Opening Telegram")
            subprocess.Popen(["C:\\Users\\risha\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe"])
    


        else:
            speak("Command not recognized.")

    while running:
        user_command = listen()
        if user_command:
            execute_command(user_command)

# GUI Setup
def start_image_mode():
    threading.Thread(target=image_processing_mode, daemon=True).start()

def start_voice_mode():
    threading.Thread(target=voice_assistant_mode, daemon=True).start()

root = tk.Tk()
root.title("Mini Project - Image Processing & Voice Assistant")
root.geometry("300x200")
root.resizable(False, False)

label = tk.Label(root, text="Choose Mode", font=("Arial", 14))
label.pack(pady=20)

btn_image = tk.Button(root, text="Image Processing (OCR + TTS)", command=start_image_mode, width=30)
btn_image.pack(pady=10)

btn_voice = tk.Button(root, text="Voice Assistant", command=start_voice_mode, width=30)
btn_voice.pack(pady=10)

root.mainloop()