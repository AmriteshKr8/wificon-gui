import tkinter as tk
import subprocess
import threading

BG_COLOR = "#121212"
FG_COLOR = "#FFFFFF"
ACCENT_COLOR = "#1DE9B6"
BTN_BG = "#1E1E1E"
BTN_ACTIVE = "#2C2C2C"

def dark_messagebox(title, message, mtype="info"):
    top = tk.Toplevel(root)
    top.title(title)
    top.configure(bg=BG_COLOR)
    top.grab_set()
    top.geometry("300x150")
    top.resizable(False, False)
    tk.Label(top, text=message, bg=BG_COLOR, fg=FG_COLOR, wraplength=280, justify="center").pack(expand=True, padx=10, pady=20)
    def close():
        top.destroy()
    tk.Button(top, text="OK", command=close, bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_ACTIVE, activeforeground=ACCENT_COLOR, relief="flat", bd=0, highlightthickness=0).pack(pady=10)
    root.wait_window(top)

def password_dialog(ssid):
    popup = tk.Toplevel(root)
    popup.title("Enter Password")
    popup.configure(bg=BG_COLOR)
    popup.geometry("300x150")
    popup.resizable(False, False)

    tk.Label(popup, text=f"Password for {ssid}:", bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
    entry = tk.Entry(popup, show="*", font=("JetBrains Mono", 11), bg=BTN_BG, fg=FG_COLOR, insertbackground=ACCENT_COLOR, relief="flat", bd=0, highlightthickness=1, highlightbackground=ACCENT_COLOR)
    entry.pack(pady=5, padx=20, fill="x")

    passwd = {"value": None}
    def submit():
        passwd["value"] = entry.get()
        popup.destroy()

    btn = tk.Button(popup, text="Connect", command=submit, bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_ACTIVE, activeforeground=ACCENT_COLOR, relief="flat", bd=0, highlightthickness=0, padx=10, pady=5)
    btn.pack(pady=10)

    popup.transient(root)
    popup.grab_set()
    root.wait_window(popup)
    return passwd["value"]

def scan_networks():
    s = "nmcli dev wifi rescan"
    subprocess.run(s, shell=True, capture_output=False, text=True)
    command = "nmcli -t -f SSID dev wifi"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        ssids = result.stdout.strip().split('\n')
        ssids = list(filter(None, ssids))
        return ssids if ssids else None
    return None

def populate_listbox():
    listbox.delete(0, tk.END)
    listbox.insert(tk.END, "Scanning...")
    def do_scan():
        ssids = scan_networks()
        listbox.delete(0, tk.END)
        if not ssids:
            dark_messagebox("Error", "No networks found.\nCheck rfkill or Wi-Fi status.", "error")
            return
        for ssid in ssids:
            listbox.insert(tk.END, ssid)
    threading.Thread(target=do_scan, daemon=True).start()

def connect_network():
    try:
        selected_index = listbox.curselection()[0]
    except IndexError:
        dark_messagebox("No Selection", "Please select a network first.", "warning")
        return
    ssid = listbox.get(selected_index)
    passwd = password_dialog(ssid)
    if not passwd:
        return
    execr = f"nmcli dev wifi connect '{ssid}' password '{passwd}'"
    out = subprocess.run(execr, shell=True, capture_output=True, text=True)
    if out.returncode == 0:
        dark_messagebox("Connected", f"Connected to {ssid}")
    else:
        dark_messagebox("Connection Failed", f"Could not connect to {ssid}\n\nError:\n{out.stderr}", "error")

root = tk.Tk()
root.title("Wificon")
root.geometry("420x320")
root.configure(bg=BG_COLOR)

app_font = ("JetBrains Mono", 11, "normal")
root.option_add("*Font", app_font)
root.option_add("*Background", BG_COLOR)
root.option_add("*Foreground", FG_COLOR)

frame = tk.Frame(root, bg=BG_COLOR)
frame.pack(padx=10, pady=10, fill="both", expand=True)

listbox = tk.Listbox(frame, width=50, height=10, bg=BTN_BG, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground=BG_COLOR, highlightthickness=0, bd=0, relief="flat")
listbox.pack(side="top", fill="both", expand=True, pady=5)

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=5)

def style_button(btn):
    btn.configure(bg=BTN_BG, fg=FG_COLOR, activebackground=BTN_ACTIVE, activeforeground=ACCENT_COLOR, relief="flat", bd=0, highlightthickness=0, padx=10, pady=5)
    btn.pack_propagate(False)

scan_btn = tk.Button(btn_frame, text="Rescan", command=populate_listbox)
style_button(scan_btn)
scan_btn.grid(row=0, column=0, padx=5)

connect_btn = tk.Button(btn_frame, text="Connect", command=connect_network)
style_button(connect_btn)
connect_btn.grid(row=0, column=1, padx=5)

exit_btn = tk.Button(btn_frame, text="Exit", command=root.quit)
style_button(exit_btn)
exit_btn.grid(row=0, column=2, padx=5)

populate_listbox()
root.mainloop()
