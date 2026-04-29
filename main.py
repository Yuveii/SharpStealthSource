import customtkinter as ctk
import tkinter as tk
import pyautogui
import time
import threading
import ctypes
import sys
import os
import keyboard
import requests

STATUS_URL = "https://pastebin.com/raw/dMcqsqT6"

running = True
detections = 0
last_detection_time = 0

box_size = 220
recast_cooldown = 0.3
detecting_enabled = False

scan_offset = 0


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def restart_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()


if not is_admin():
    res = ctypes.windll.user32.MessageBoxW(0, "Restart as Administrator?", "Admin Recommended", 4)
    if res == 6:
        restart_as_admin()


def check_service():
    global running
    try:
        r = requests.get(STATUS_URL, timeout=5)
        if "false" in r.text.lower():
            running = False
            os._exit(0)
    except:
        running = False
        os._exit(0)


check_service()


def force_close():
    global running
    running = False
    os._exit(0)


keyboard.add_hotkey("shift+e", force_close)


def click_mouse():
    pyautogui.click()
    time.sleep(recast_cooldown)
    pyautogui.click()


def is_red(r, g, b):
    return r > 80 and r >= g and r >= b and (r - min(g, b)) > 25


def detect_red():
    global running, detections, last_detection_time, detecting_enabled

    while running:
        if not detecting_enabled:
            time.sleep(0.05)
            continue

        try:
            x = box.winfo_x()
            y = box.winfo_y()
            w = box.winfo_width()
            h = box.winfo_height()

            screenshot = pyautogui.screenshot(region=(x, y, w, h))
            pixels = screenshot.load()

            red_pixels = 0
            total = 0

            step = max(1, int(min(w, h) / 60))

            for i in range(0, w, step):
                for j in range(0, h, step):
                    r, g, b = pixels[i, j]
                    total += 1
                    if is_red(r, g, b):
                        red_pixels += 1

            ratio = red_pixels / total if total else 0

            if ratio > 0.02:
                now = time.time()
                if now - last_detection_time >= 1:
                    last_detection_time = now
                    detections += 1
                    app.after(0, update_ui)
                    threading.Thread(target=click_mouse, daemon=True).start()

        except:
            pass

        time.sleep(0.01)


def update_ui():
    det_label.configure(text=str(detections))
    cd_value.configure(text=f"{recast_cooldown:.1f}s")


def update_box(val):
    global box_size
    box_size = int(float(val))
    box.geometry(f"{box_size}x{box_size}+{box.winfo_x()}+{box.winfo_y()}")


def update_cd(val):
    global recast_cooldown
    recast_cooldown = max(0.1, float(val))
    update_ui()


def toggle_detection():
    global detecting_enabled
    detecting_enabled = not detecting_enabled
    toggle_btn.configure(text="ON" if detecting_enabled else "OFF")


def toggle_topmost():
    app.wm_attributes("-topmost", topmost_var.get())


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.geometry("340x380")
app.title("Sharp Stealth")
app.resizable(False, False)

try:
    app.iconbitmap(default="")
except:
    pass

ctk.CTkLabel(app, text="Sharp Stealth", font=("Arial", 18, "bold")).pack(pady=15)

frame = ctk.CTkFrame(app)
frame.pack(pady=5, padx=10, fill="x")

ctk.CTkLabel(frame, text="Detections").pack(side="left", padx=10)
det_label = ctk.CTkLabel(frame, text="0", font=("Arial", 16, "bold"))
det_label.pack(side="right", padx=10)

ctk.CTkLabel(app, text="Cooldown").pack(pady=(15, 0))
cd_value = ctk.CTkLabel(app, text="0.3s")
cd_value.pack()

ctk.CTkSlider(app, from_=0.1, to=1.5, command=update_cd).pack(padx=20, pady=5)

ctk.CTkLabel(app, text="Box Size").pack(pady=(15, 0))
ctk.CTkSlider(app, from_=150, to=350, command=update_box).pack(padx=20)

toggle_btn = ctk.CTkButton(app, text="OFF", command=toggle_detection)
toggle_btn.pack(pady=10)

topmost_var = tk.BooleanVar(value=False)

ctk.CTkCheckBox(app, text="Settings Always On Top", variable=topmost_var, command=toggle_topmost).pack(pady=10)


box = tk.Toplevel()
box.overrideredirect(True)
box.geometry(f"{box_size}x{box_size}+500+300")
box.attributes("-topmost", True)
box.attributes("-alpha", 0.35)
box.configure(bg="black")

canvas = tk.Canvas(box, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

scan_offset = 0


def draw_box_animation():
    global scan_offset

    canvas.delete("all")

    w = box.winfo_width()
    h = box.winfo_height()

    canvas.create_rectangle(2, 2, w-2, h-2, outline="white", width=2)

    y = scan_offset % h
    canvas.create_line(0, y, w, y, fill="white", width=2)

    for i in range(0, w, 30):
        canvas.create_line(i, 0, i, h, fill="#222222")
    for j in range(0, h, 30):
        canvas.create_line(0, j, w, j, fill="#222222")

    scan_offset += 2
    box.after(16, draw_box_animation)


drag_x = 0
drag_y = 0


def start_move(e):
    global drag_x, drag_y
    drag_x = e.x
    drag_y = e.y


def move(e):
    x = box.winfo_x() + e.x - drag_x
    y = box.winfo_y() + e.y - drag_y
    box.geometry(f"+{x}+{y}")


canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", move)

draw_box_animation()

threading.Thread(target=detect_red, daemon=True).start()

app.mainloop()
