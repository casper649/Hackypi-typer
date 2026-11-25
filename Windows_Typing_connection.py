import json
import time
import threading
import tkinter as tk
from tkinter import messagebox
import serial

PORT = "COM8"
BAUD = 115200

pico = None
typing = False

root = tk.Tk()
root.title("HackyPi - Text Entry")
root.geometry("700x580")
root.minsize(550, 450)

status = tk.StringVar(value="Not connected")
speed = tk.IntVar(value=40)


# =====================================
# TEXT BOX SHORTCUTS AND MENU
# =====================================

def select_all(event=None):
    text_box.tag_add("sel", "1.0", "end-1c")
    return "break"


def show_context_menu(event):
    context_menu.tk_popup(event.x_root, event.y_root)
    return "break"


def paste_text(event=None):
    try:
        content = root.clipboard_get()
        text_box.insert("insert", content)
    except tk.TclError:
        pass
    return "break"


def copy_text(event=None):
    try:
        selected = text_box.get("sel.first", "sel.last")
        root.clipboard_clear()
        root.clipboard_append(selected)
    except tk.TclError:
        pass
    return "break"


def cut_text(event=None):
    copy_text()
    try:
        text_box.delete("sel.first", "sel.last")
    except tk.TclError:
        pass
    return "break"


# =====================================
# CONNECTION
# =====================================

def connect():
    global pico

    try:
        status.set("Connecting to COM8...")
        root.update_idletasks()

        if pico and pico.is_open:
            pico.close()

        pico = serial.Serial(
            PORT,
            BAUD,
            timeout=0.5,
            write_timeout=3
        )

        time.sleep(1)
        pico.reset_input_buffer()
        pico.write(b'{"action":"ping"}\n')

        deadline = time.monotonic() + 8

        while time.monotonic() < deadline:
            response = pico.readline().decode(
                "utf-8", errors="replace"
            ).strip()

            if response == "READY":
                status.set("Connected to HackyPi on COM8")

                threading.Thread(
                    target=read_messages,
                    daemon=True
                ).start()
                return

        pico.close()
        pico = None

        status.set("Connection failed")

        messagebox.showerror(
            "HackyPi Connection",
            "The Pico did not respond.\n"
            "Check that COM8 is available."
        )

    except Exception as error:
        if pico and pico.is_open:
            pico.close()

        pico = None
        status.set("Not connected")

        messagebox.showerror(
            "Connection Error",
            str(error)
        )


# =====================================
# READ PICO MESSAGES
# =====================================

def read_messages():
    while pico and pico.is_open:
        try:
            response = pico.readline().decode(
                "utf-8", errors="replace"
            ).strip()

            if response == "STARTED":
                root.after(
                    0,
                    lambda: status.set("Typing...")
                )

            elif response == "COMPLETE":
                root.after(0, typing_complete)

            elif response.startswith("ERROR"):
                root.after(
                    0,
                    lambda msg=response: typing_error(msg)
                )

        except Exception:
            break


def typing_complete():
    global typing

    typing = False
    status.set("Text entry complete!")

    send_button.config(state="normal")
    root.deiconify()


def typing_error(error):
    global typing

    typing = False
    status.set(error)

    send_button.config(state="normal")
    root.deiconify()

    messagebox.showerror("HackyPi Error", error)


# =====================================
# SEND TEXT
# =====================================

def send_text():
    global typing

    if not pico or not pico.is_open:
        messagebox.showwarning(
            "HackyPi",
            "Connect to HackyPi first."
        )
        return

    content = text_box.get("1.0", "end-1c")

    if not content.strip():
        messagebox.showwarning(
            "Missing Text",
            "Please enter some text."
        )
        return

    try:
        wpm = int(speed.get())

        if not 10 <= wpm <= 100:
            raise ValueError(
                "Typing speed must be between 10 and 100 WPM."
            )

        payload = {
            "action": "type",
            "text": content,
            "wpm": wpm
        }

        pico.write(
            (json.dumps(payload) + "\n").encode("utf-8")
        )

        typing = True
        send_button.config(state="disabled")

        status.set(
            "Starting... Select your destination window."
        )

        root.iconify()

    except Exception as error:
        messagebox.showerror("Error", str(error))


# =====================================
# CLOSE APPLICATION
# =====================================

def cancel():
    global pico

    if typing:
        messagebox.showinfo(
            "HackyPi",
            "Please wait for typing to finish."
        )
        return

    if pico and pico.is_open:
        pico.close()

    root.destroy()


# =====================================
# INTERFACE
# =====================================

tk.Label(
    root,
    text="HackyPi",
    font=("Segoe UI", 24, "bold")
).pack(pady=(15, 2))

tk.Label(
    root,
    text="USB Text Entry",
    font=("Segoe UI", 11)
).pack(pady=(0, 15))

tk.Label(
    root,
    text="Enter or paste your text below:",
    font=("Segoe UI", 10)
).pack(anchor="w", padx=18)

text_box = tk.Text(
    root,
    height=13,
    font=("Consolas", 11),
    wrap="word",
    undo=True
)

text_box.pack(
    fill="both",
    expand=True,
    padx=18,
    pady=8
)


# =====================================
# RIGHT-CLICK MENU
# =====================================

context_menu = tk.Menu(root, tearoff=0)

context_menu.add_command(label="Cut", command=cut_text)
context_menu.add_command(label="Copy", command=copy_text)
context_menu.add_command(label="Paste", command=paste_text)
context_menu.add_separator()
context_menu.add_command(label="Select All", command=select_all)

text_box.bind("<Button-3>", show_context_menu)


# =====================================
# KEYBOARD SHORTCUTS
# =====================================

text_box.bind("<Control-a>", select_all)
text_box.bind("<Control-A>", select_all)
text_box.bind("<Control-c>", copy_text)
text_box.bind("<Control-C>", copy_text)
text_box.bind("<Control-x>", cut_text)
text_box.bind("<Control-X>", cut_text)
text_box.bind("<Control-v>", paste_text)
text_box.bind("<Control-V>", paste_text)


# =====================================
# TYPING SETTINGS
# =====================================

settings = tk.Frame(root)
settings.pack(fill="x", padx=18, pady=10)

tk.Label(
    settings,
    text="Typing speed (WPM):"
).pack(side="left")

tk.Spinbox(
    settings,
    from_=10,
    to=100,
    width=7,
    textvariable=speed
).pack(side="left", padx=8)

tk.Label(
    settings,
    text="US keyboard layout"
).pack(side="right")


# =====================================
# BUTTONS
# =====================================

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="Connect",
    width=13,
    command=connect
).pack(side="left", padx=5)

send_button = tk.Button(
    buttons,
    text="Send",
    width=13,
    command=send_text
)

send_button.pack(side="left", padx=5)

tk.Button(
    buttons,
    text="Close",
    width=13,
    command=cancel
).pack(side="left", padx=5)


# =====================================
# STATUS
# =====================================

tk.Label(
    root,
    textvariable=status,
    font=("Segoe UI", 10)
).pack(pady=12)


# =====================================
# APPLICATION START
# =====================================

root.protocol("WM_DELETE_WINDOW", cancel)

root.mainloop()
