from customtkinter import *
import tkinter as tk

class LoadingAnimation(CTkFrame):
    def __init__(self, parent : CTkFrame, radius=90, circle_width=15, speed=40, circle_color="#B188A8"):
        super().__init__(parent, corner_radius=10)
        self.canvas = CTkCanvas(self, bg="gray20")
        self.radius = radius
        self.circle_width = circle_width
        self.speed = speed
        self.circle_color = circle_color
        self.angle = 0
        self.running = True
        
        self.text_label = CTkLabel(self,text="",fg_color="transparent", bg_color="gray20",font=("Arial", 15, "bold"),)
        self.text_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.canvas.pack()

        frame_size = 2 * (radius + circle_width)
        self.canvas.config(width=frame_size, height=frame_size)
        self.animate()
        self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def change_text(self,text):
        self.text_label.configure(text = text)
    
    def draw_circle(self, angle):
        self.canvas.delete("all")
        self.canvas.create_arc(self.circle_width, self.circle_width, 2 * self.radius + self.circle_width,
                               2 * self.radius + self.circle_width, start=angle, extent=120,
                               style=tk.ARC, outline=self.circle_color, width=self.circle_width)

    def animate(self):
        if not self.running:
            self.destroy()
            return
        self.draw_circle(self.angle)
        self.angle = (self.angle + 10) % 360
        self.after(self.speed, self.animate)

    def stop(self):
        self.running = False
