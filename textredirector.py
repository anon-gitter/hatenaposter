import tkinter as tk
import sys

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert(tk.END, str, (self.tag))
        self.widget.see(tk.END)

def main():
    root = tk.Tk()
    text = tk.Text(root)
    text.pack()
    sys.stdout = TextRedirector(text, "stdout")
    sys.stderr = TextRedirector(text, "stderr")

    print("This messsage output to Textbox")

if __name__ == '__main__':
    main()
