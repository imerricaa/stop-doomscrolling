# Study Focus Timer with Face Tracking (Lowkenuinely Brainrot)

A simple desktop app to help you stay focused during study sessions.  
It uses your webcam to detect if you're doomscrolling. If not, "We are Charlie Kirk" will be played.

## Features
- Choose study duration (1–12 hours)
- Countdown timer
- Periodic "focus" reminders
- Face detection with green bounding box
- Audio alert when not facing the screen
- Custom pop-up messages
- Logs completed sessions to `study_log.txt`

## Requirements
- Python 3.12+
- Libraries: `opencv-python`, `mediapipe`, `pygame`, `tkinter` (usually built-in)

```bash
pip install opencv-python mediapipe pygame
```

## Run
```bash
python main.py
```
