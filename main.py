'''
 sign_language_player.py
 -----------------------
 A minimal demo that listens to the microphone, converts speech to text, and sequentially
 plays sign‑language videos (or images) that correspond to each recognized word.

 Dependencies
 ------------
 pip install opencv-python speechrecognition pyaudio pillow

 Folder Layout
 -------------
 project_root/
 ├── signs/
 │   ├── hello.mp4  # or .gif / .jpg
 │   ├── world.mp4
 │   └── ...
 └── sign_language_player.py

 Usage
 -----
 1. Make sure your sign videos/images are inside the **signs/** folder and that their
    filenames match the keys in `SIGN_DICT` below (lower‑case, no spaces).
 2. Run the script:
        python sign_language_player.py
 3. Speak a short sentence (e.g. "Hello world").  When silence is detected, the program
    will find each word in the sentence and play the corresponding signs one after
    another.  Press **q** at any time during playback to stop the current video or image.
 4. To exit completely, use Ctrl‑C in the terminal.

 Notes
 -----
 • For best accuracy, use a decent microphone in a quiet room.
 • The default recognizer is Google Web Speech API (free, requires Internet).
 • If a sign for a particular word is not found, the word is skipped and a message is
   printed to the console.
'''

import os
import sys
import time
from typing import Dict, List

import cv2
import speech_recognition as sr

# ---------------------------- Configuration ---------------------------- #
SIGN_FOLDER: str = "signs"  # relative path to directory that stores sign files

# Map words ➜ sign file names (add your own!)
SIGN_DICT: Dict[str, str] = {
    "how": "how.mp4",
    "can": "can.mp4",
    "i": "I.mp4",
    "help": "help.mp4",
}

# Delay (seconds) to wait between consecutive sign clips/images
INTER_SIGN_DELAY: float = 0.4

# ---------------------------------------------------------------------- #

def play_video(path: str) -> None:
    """Play a video (or display a single image) in an OpenCV window."""
    ext = os.path.splitext(path)[1].lower()

    if ext in {".jpg", ".jpeg", ".png", ".gif", ".bmp"}:
        # Static image → show for 1.5 seconds
        frame = cv2.imread(path)
        if frame is None:
            print(f"[WARN] Cannot open image: {path}")
            return
        cv2.imshow("Sign Language Player", frame)
        cv2.waitKey(int(1500))  # milliseconds
        return

    # Otherwise treat as a video
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"[WARN] Cannot open video: {path}")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Sign Language Player", frame)
        # Break if user presses 'q'
        if cv2.waitKey(25) & 0xFF == ord("q"):
            break
    cap.release()


def sentence_to_sign_paths(sentence: str) -> List[str]:
    """Lower‑case + split sentence, map each word to its corresponding sign path."""
    paths: List[str] = []
    for raw_word in sentence.split():
        word = raw_word.strip().lower()
        filename = SIGN_DICT.get(word)
        if filename:
            full_path = os.path.join(SIGN_FOLDER, filename)
            paths.append(full_path)
        else:
            print(f"[INFO] No sign found for '{word}'. Skipping …")
    return paths


def listen_for_sentence(recognizer: sr.Recognizer, mic: sr.Microphone) -> str:
    """Listen from microphone until silence, then return recognized sentence (lower‑case)."""
    with mic as source:
        print("Speak now … (Ctrl‑C to quit)")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        sentence = recognizer.recognize_google(audio)
        print(f"[STT] '{sentence}'")
        return sentence.lower()
    except sr.UnknownValueError:
        print("[ERROR] Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"[ERROR] Speech Recognition service error: {e}")
        return ""


def main() -> None:
    # Check that the signs folder exists
    if not os.path.isdir(SIGN_FOLDER):
        print(f"[FATAL] Sign folder '{SIGN_FOLDER}' not found. Exiting.")
        sys.exit(1)

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("\n=== Sign‑Language Player ===\n")
    print("• Press Ctrl‑C in the terminal to exit.")
    print("• Press 'q' in the video window to stop playback of the current sign.\n")

    try:
        while True:
            sentence = listen_for_sentence(recognizer, mic)
            if not sentence:
                continue

            sign_paths = sentence_to_sign_paths(sentence)
            if not sign_paths:
                print("[INFO] No playable signs found in the sentence.\n")
                continue

            for path in sign_paths:
                play_video(path)
                time.sleep(INTER_SIGN_DELAY)

            cv2.destroyAllWindows()
            print("[READY] Listening again …\n")

    except KeyboardInterrupt:
        print("\n[EXIT] Bye!")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
