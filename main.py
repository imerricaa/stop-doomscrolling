import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Label, Button
import datetime
import threading
import time
import cv2
import mediapipe as mp
from queue import Queue
import pygame

BG_DARK = "#121212"
ACCENT = "#00ff88"
DANGER = "#ff4b2b"
TEXT_COLOR = "#e0e0e0"

pygame.mixer.init()
try:
    alert_sound = pygame.mixer.Sound("doomed.mp3") 
except:
    alert_sound = None

frame_queue = Queue(maxsize=1)
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

def check_attention():
    global studying
    cap = cv2.VideoCapture(0)
    last_alert = 0
    last_sound_time = 0
    alert_cooldown = 30      
    sound_cooldown = 8       
    is_playing = False
    
    while studying:
        ret, frame = cap.read()
        if not ret: break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)
        facing = False
        annotated_frame = frame.copy()
        
        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                x, y = int(bboxC.xmin * iw), int(bboxC.ymin * ih)
                w, h = int(bboxC.width * iw), int(bboxC.height * ih)
                
                center_x = x + w // 2
                center_y = y + h // 2
                
                offset_x = abs(center_x - (iw // 2)) / iw
                offset_y = abs(center_y - (ih // 2)) / ih
                facing = (offset_x < 0.25 and offset_y < 0.25 and w * h > iw * ih * 0.08)
                
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 136), 3)
                break
        
        status_text = "Facing: YES; wow what a tryhard" if facing else "Facing: NO; Doomscrolling AGAIN"
        status_color = (0, 255, 136) if facing else (0, 0, 255)
        cv2.putText(annotated_frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        if not frame_queue.empty():
            try: frame_queue.get_nowait()
            except: pass
        frame_queue.put(annotated_frame)
        
        current_time = time.time()
        
        if not facing:
            if current_time - last_sound_time > sound_cooldown:
                if alert_sound and not is_playing:
                    alert_sound.play(loops=-1)
                    is_playing = True
                last_sound_time = current_time
            if current_time - last_alert > alert_cooldown:
                root.after(0, show_custom_alert)
                last_alert = current_time
        else:
            if alert_sound and is_playing:
                alert_sound.stop()
                is_playing = False
                
        time.sleep(0.03)
    
    if alert_sound:
        alert_sound.stop()
    cap.release()

def show_custom_alert():
    win = Toplevel(root)
    win.title("Focus Alert")
    win.geometry("400x200")
    win.configure(bg=DANGER)
    win.attributes("-topmost", True)
    Label(win, text="EYES ON SCREEN!", font=("Segoe UI", 18, "bold"), bg=DANGER, fg="white").pack(pady=20)
    Button(win, text="I'M BACK", font=("Segoe UI", 12, "bold"), bg="white", fg=DANGER, 
           command=win.destroy, relief="flat", padx=20).pack(pady=10)

def start_study():
    global original_hours, studying
    original_hours = int(hours_var.get())
    studying = True
    start_btn.config(state="disabled")
    update_timer(original_hours * 3600)
    threading.Thread(target=check_attention, daemon=True).start()
    root.after(100, display_preview)

def stop_session():
    global studying
    studying = False
    start_btn.config(state="normal")
    try:
        cv2.destroyAllWindows()
    except:
        pass

def update_timer(remaining):
    if remaining > 0 and studying:
        h, s = divmod(remaining, 3600)
        m, s = divmod(s, 60)
        timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        root.after(1000, update_timer, remaining - 1)
    elif remaining <= 0 and studying:
        log_study(original_hours)
        stop_session()
        messagebox.showinfo("Session End", "Great job focusing!")

def log_study(hours):
    with open("study_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()}: Completed {hours} hour session\n")

def display_preview():
    if not frame_queue.empty():
        frame = frame_queue.get()
        cv2.imshow("Focus Monitor", frame)
        cv2.waitKey(1)
    if studying: root.after(30, display_preview)

root = tk.Tk()
root.title("j*bs")
root.geometry("500x550")
root.configure(bg=BG_DARK)
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background=BG_DARK)
style.configure("TLabel", background=BG_DARK, foreground=TEXT_COLOR)
style.configure("TMenubutton", background="#333", foreground=TEXT_COLOR)
style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"), background=ACCENT, foreground="black")
style.map("Accent.TButton", background=[("active", "#00cc6e")])
style.configure("Danger.TButton", font=("Segoe UI", 12, "bold"), background="#333", foreground=DANGER)

main_container = ttk.Frame(root, padding=40)
main_container.pack(fill="both", expand=True)

ttk.Label(main_container, text="stop doomscrolling in big 26", font=("Segoe UI", 28, "bold"), foreground=ACCENT).pack(pady=(0, 10))
ttk.Label(main_container, text="Set Session Length (Hours)", font=("Segoe UI", 11)).pack()

hours_var = tk.StringVar(value="1")
dropdown = ttk.OptionMenu(main_container, hours_var, "1", *map(str, range(1, 13)))
dropdown.pack(pady=15)

timer_label = tk.Label(main_container, text="00:00:00", font=("Consolas", 50), bg=BG_DARK, fg=TEXT_COLOR)
timer_label.pack(pady=40)

start_btn = ttk.Button(main_container, text="START SESSION", style="Accent.TButton", command=start_study)
start_btn.pack(fill="x", ipady=10, pady=5)

stop_btn = ttk.Button(main_container, text="STOP", style="Danger.TButton", command=stop_session)
stop_btn.pack(fill="x", ipady=5, pady=5)

studying = False
original_hours = 0

root.mainloop()