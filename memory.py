from tkinter import *
from tkinter import ttk, messagebox
import json, random, datetime, time

SAVE_FILE = "saved.json"

# Load profanity list
try:
    with open("words.json", "r", encoding="utf-8") as f:
        BAD_WORDS = set(json.load(f))
except Exception as e:
    print("Error loading words.json:", e)
    BAD_WORDS = set()

class MessageBoard:
    def __init__(self, root):
        self.last_submit_time = 0
        self.submit_delay = 3
        self.root = root
        self.root.title("Message Board")
        self.root.attributes("-fullscreen", True)
        self.root.config(bg="#f0f0f0")
        self.messages = self.load_messages()

        # Exit shortcut (Ctrl+Shift+Q)
        self.root.bind("<Control-Shift-q>", lambda e: self.close_application())
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)  # Handle window close button

        self.frame = Frame(self.root, bg="#e0e0e0", bd=2, relief=RIDGE)
        self.frame.pack(fill=BOTH, expand=True, padx=60, pady=60)

        Label(
            self.frame,
            text="Type your message and press ENTER to submit",
            fg="#333333",
            bg="#e0e0e0",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(0, 20))

        self.entry_var = StringVar()
        self.entry = Entry(
            self.frame,
            textvariable=self.entry_var,
            font=("Helvetica", 18),
            width=60,
            bd=4,
            relief=RIDGE,
            bg="white",
            fg="#333333",
            insertbackground="#333333"
        )
        self.entry.pack(pady=10, ipady=6)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.submit_message)

        self.tree = ttk.Treeview(
            self.frame,
            columns=("message", "date"),
            show="headings",
            height=12
        )
        self.tree.heading("message", text="Message")
        self.tree.heading("date", text="Date")
        self.tree.column("message", width=700, anchor=W)
        self.tree.column("date", width=200, anchor=W)
        self.tree.pack(pady=20, fill=BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#333333",
            fieldbackground="#ffffff",
            font=("Helvetica", 16),
            rowheight=40,
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 18, "bold"),
            background="#d0d0d0",
            foreground="#333333"
        )
        style.map("Treeview", background=[("selected", "#b0c4de")])

        self.tree.bind("<Double-1>", self.remove_selected)

        # Periodic random scrolling update
        self.update_display()

        # Ensure entry stays focused
        self.root.bind_all("<Button-1>", self.refocus)

    def load_messages(self):
        """Reads message data from the SAVE_FILE (saved.json)."""
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                # expects a list of lists: [["msg1", "date1"], ["msg2", "date2"]]
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Error reading JSON from {SAVE_FILE}. Starting with empty messages.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}")
            return []

    def save_messages(self):
        """Writes current message data to the SAVE_FILE."""
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data to {SAVE_FILE}: {e}")

    def close_application(self):
        self.save_messages()
        self.root.destroy()

    def submit_message(self, event=None):
        now = time.time()
        text = self.entry_var.get().strip()

        if now - self.last_submit_time < self.submit_delay:
            remaining = int(self.submit_delay - (now - self.last_submit_time)) + 1
            self.temp_disable(f"Please wait {remaining} seconds between messages.")
            return
        if not text:
            return
        if self.contains_profanity(text):
            self.temp_disable("Please use appropriate language.")
            return

        date_str = datetime.datetime.now().strftime("%I:%M %p %m/%d/%Y")
        new_message = ['"' + text + '"', date_str]  # Use a list for JSON compatibility
        self.messages.append(new_message)
        self.entry_var.set("")
        self.refresh_tree()
        self.last_submit_time = now
        self.save_messages()

    def remove_selected(self, event=None):
        selected = self.tree.selection()
        if not selected: return
        for item in selected:
            idx = int(self.tree.index(item))
            del self.messages[idx]
        self.refresh_tree()
        self.save_messages()

    def refocus(self, event=None):
        self.entry.focus_set()

    def temp_disable(self, message, duration=1000):
        original_fg = self.entry.cget("fg")
        self.entry_var.set(message)
        self.entry.config(fg="gray")

        def restore():
            self.entry_var.set("")
            self.entry.config(fg=original_fg)
            self.entry.focus_set()

        self.entry.after(duration, restore)

    def contains_profanity(self, text):
        words = [w.lower().strip(".,!?") for w in text.split()]
        return any(word in BAD_WORDS for word in words)

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        display = random.sample(self.messages, min(len(self.messages), 12))
        for msg, date in display:
            self.tree.insert("", END, values=(msg, date))

    def update_display(self):
        self.refresh_tree()
        self.root.after(5000, self.update_display)

if __name__ == "__main__":
    root = Tk()
    app = MessageBoard(root)
    root.mainloop()