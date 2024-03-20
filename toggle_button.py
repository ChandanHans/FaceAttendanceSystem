import customtkinter as ctk
from tkinter import Tk

class ToggleButton(ctk.CTkButton):
    def __init__(self, master=None, **kw):
        self.state = False  # Start with the initial state
        self.texts = kw.pop('texts', ('State 1', 'State 2'))  # Default texts for two states
        self.callbacks = kw.pop('callbacks', (None, None))  # Callbacks for each state
        kw['text'] = self.texts[0]  # Initial text
        super().__init__(master, **kw)
        self.configure(command=self.toggle_and_execute)  # Set the command
        
    def toggle_and_execute(self):
        # Toggle the state
        self.state = not self.state
        new_text = self.texts[self.state]
        self.configure(text=new_text)  # Update the button text

        # Execute the callback for the current state
        if callable(self.callbacks[self.state]):
            self.callbacks[self.state]()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Toggling Button Example")

        # Create the toggling button with callbacks for each state
        self.toggle_button = ToggleButton(root, texts=('Click Me', 'Click Again'), callbacks=(self.state_1_action, self.state_2_action))
        self.toggle_button.pack(pady=20)

    def state_1_action(self):
        print("State 1 action executed")

    def state_2_action(self):
        print("State 2 action executed")

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
