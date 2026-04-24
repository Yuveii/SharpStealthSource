import pydirectinput
from PIL import ImageGrab
import tkinter as tk
from tkinter import ttk, font
import threading
import time
import math
import keyboard 
import os
import urllib.request
import sys

class SharpUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("Sharp Macro Updater")
        self.root.geometry("400x250")
        self.root.configure(bg='#0f0f0f')
        self.root.overrideredirect(True) 

        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)

        self.setup_ui()

    def setup_ui(self):
        title_font = font.Font(family="Segoe UI", size=18, weight="bold")
        tk.Label(self.root, text="SHARP MACRO UPDATER", fg="#ffffff", bg="#0f0f0f", font=title_font).pack(pady=(40, 10))

        self.status_label = tk.Label(self.root, text="Ready to update", fg="#888888", bg="#0f0f0f", font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 30))

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TButton", foreground="white", background="#222222", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[('active', '#333333')])

        self.update_btn = ttk.Button(self.root, text="Download and launch newest macro version", width=40, command=self.start_update_thread)
        self.update_btn.pack(pady=10)

        close_btn = tk.Label(self.root, text="✕", fg="#555555", bg="#0f0f0f", cursor="hand2")
        close_btn.place(x=370, y=10)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

    def start_update_thread(self):
        self.update_btn.state(['disabled'])
        threading.Thread(target=self.download_and_launch, daemon=True).start()

    def download_and_launch(self):
        try:
            self.status_label.config(text="Fetching download link...", fg="#3498db")

            pastebin_url = "https://pastebin.com/raw/"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            req = urllib.request.Request(pastebin_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                download_url = response.read().decode('utf-8').strip()

            original_filename = download_url.split("/")[-1].split("?")[0] 
            if not original_filename:
                original_filename = "macro_update.exe"

            self.status_label.config(text=f"Downloading {original_filename}...", fg="#f1c40f")

            file_req = urllib.request.Request(download_url, headers=headers)
            with urllib.request.urlopen(file_req) as response, open(original_filename, 'wb') as out_file:
                out_file.write(response.read())

            self.status_label.config(text="Success! Launching...", fg="#2ecc71")
            time.sleep(1)
            os.startfile(original_filename)
            
            self.root.destroy()
            sys.exit()

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="#e74c3c")
            self.update_btn.state(['!disabled'])

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        self.root.geometry(f"+{self.root.winfo_x() + deltax}+{self.root.winfo_y() + deltay}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SharpUpdater(root)
    root.mainloop()