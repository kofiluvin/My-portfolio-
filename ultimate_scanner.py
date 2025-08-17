import socket
import threading
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.constants import *
import itertools
import time
import winsound
from queue import Queue

# Number of concurrent threads
MAX_THREADS = 100

# Thread-safe queue for ports
port_queue = Queue()

# Scan a single port
def scan_port(host, text_area):
    while not port_queue.empty():
        port = port_queue.get()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((host, port))
            sock.close()
            app.after(0, update_gui, port, True)
        except:
            app.after(0, update_gui, port, False)
        port_queue.task_done()

# Update GUI safely
def update_gui(port, is_open):
    if is_open:
        text_area.insert(ttk.END, f"[+] Port {port} is OPEN\n", 'open')
        winsound.Beep(1000, 150)
    else:
        text_area.insert(ttk.END, f"[-] Port {port} is closed\n", 'closed')
    text_area.see(ttk.END)
    progress_bar['value'] += 1
    progress_bar['bootstyle'] = f"{['info','success','warning','danger'][progress_bar['value']%4]}-striped"

# Start scanning
def start_scan():
    target = entry_ip.get()
    text_area.delete("1.0", ttk.END)
    progress_bar['value'] = 0
    progress_bar['maximum'] = 1024 - 20 + 1
    text_area.insert(ttk.END, f"💻 Scanning host: {target}\n\n", 'header')

    # Fill queue
    for port in range(20, 1025):
        port_queue.put(port)

    # Start threads
    for _ in range(MAX_THREADS):
        t = threading.Thread(target=scan_port, args=(target, text_area), daemon=True)
        t.start()

# Blinking cursor
def blink_cursor():
    while True:
        if text_area.focus_get() == text_area:
            text_area.config(insertbackground="#00FF00")
        else:
            text_area.config(insertbackground="#0f0f0f")
        time.sleep(0.5)

# Background animation
def animate_bg():
    colors = itertools.cycle(["#0f0f0f", "#111111", "#1a1a1a", "#111111"])
    while True:
        text_area.config(bg=next(colors))
        time.sleep(0.2)

# GUI setup
app = ttk.Window(title="🌐 Ultimate Fast Hacker-Style Port Scanner", themename="darkly", size=(750, 550))
app.configure(bg="#0f0f0f")

ttk.Label(app, text="Target IP:", font=("Consolas", 14), bootstyle="warning").pack(pady=10)
entry_ip = ttk.Entry(app, width=20, font=("Consolas", 12))
entry_ip.pack()
entry_ip.insert(0, "127.0.0.1")

ttk.Button(app, text="Start Scan", bootstyle="success-outline", command=start_scan).pack(pady=10)

progress_bar = ttk.Progressbar(app, bootstyle="info-striped", length=650)
progress_bar.pack(pady=10)

text_area = ScrolledText(app, width=85, height=22, autohide=True, font=("Consolas", 11),
                         bg="#0f0f0f", fg="#00ff00", insertbackground="#00ff00")
text_area.pack(pady=10)

# Color tags
text_area.tag_config('open', foreground='#00FF00')
text_area.tag_config('closed', foreground='#FF5555')
text_area.tag_config('header', foreground='#00FFFF')

# Start animations
threading.Thread(target=blink_cursor, daemon=True).start()
threading.Thread(target=animate_bg, daemon=True).start()

app.mainloop()