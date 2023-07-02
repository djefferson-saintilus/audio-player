import pygame
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from tkinter import ttk
import random

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Player")
        
        # Load icons
        self.play_icon = self.load_icon("play.png")
        self.pause_icon = self.load_icon("pause.png")
        self.stop_icon = self.load_icon("stop.png")
        
        # Set default window size
        self.root.geometry("500x400")
        
        # Create GUI elements
        self.duration_label = tk.Label(self.root, text="Duration: 00:00")
        self.duration_label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=5)
        
        self.select_button = tk.Button(self.button_frame, text="Select Audio", command=self.select_audio_file)
        self.select_button.pack(side="left", padx=5)
        
        self.play_pause_button = ttk.Button(self.button_frame, image=self.play_icon, command=self.toggle_play_pause)
        self.play_pause_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(self.button_frame, image=self.stop_icon, command=self.stop_audio)
        self.stop_button.pack(side="left", padx=5)
        
        self.audio_label = tk.Label(self.root, text="No audio file selected.")
        self.audio_label.pack(pady=10)
        
        # Audio player variables
        self.audio_file = None
        self.playing = False
        self.paused = False
        self.audio_duration = 0
        self.current_pos = 0  # Added attribute for current position
        
        # Initialize mixer
        pygame.mixer.init()
        
        # Create visualization canvas
        self.visualization_canvas = tk.Canvas(self.root, width=400, height=200)
        self.visualization_canvas.pack(pady=10)
        
        # Load and set the background image
        self.background_image = self.load_image("background.jpg")
        self.visualization_canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
        
        # Animation variables
        self.circle_radius = 50
        self.circle_color = 'white'
        self.circle_x = 200
        self.circle_y = 100
        self.animation_speed = 5
        self.circle_direction = 1

        # Smaller circle variables
        self.smaller_circles = []
        self.max_smaller_circles = 50
        self.smaller_circle_radius = 5


    def load_icon(self, filename):
        icon_path = os.path.join(os.path.dirname(__file__), "./icons", filename)
        icon_image = Image.open(icon_path)
        icon_image = icon_image.resize((24, 24), Image.ANTIALIAS)
        return ImageTk.PhotoImage(icon_image)
    
    def load_image(self, filename):
        image_path = os.path.join(os.path.dirname(__file__), "./", filename)
        image = Image.open(image_path)
        return ImageTk.PhotoImage(image)
    
        
    def select_audio_file(self):
        self.audio_file = filedialog.askopenfilename()
        if self.audio_file:
            filename = os.path.basename(self.audio_file)  # Extract the filename from the path
            self.audio_label.config(text="Selected audio file: {}".format(filename))
            sound = pygame.mixer.Sound(self.audio_file)
            self.audio_duration = sound.get_length()

    def toggle_play_pause(self):
        if self.audio_file:
            if not self.playing:
                if not self.paused:
                    pygame.mixer.music.load(self.audio_file)
                pygame.mixer.music.play(start=self.current_pos)
                self.playing = True
                self.paused = False
                self.play_pause_button.configure(image=self.pause_icon)
                self.update_duration()
                self.update_visual_effect()
                self.update_smaller_circles()
            else:
                if not self.paused:
                    self.current_pos = pygame.mixer.music.get_pos() / 1000
                    pygame.mixer.music.pause()
                    self.paused = True
                    self.play_pause_button.configure(image=self.play_icon)
                else:
                    pygame.mixer.music.unpause()
                    self.paused = False
                    self.play_pause_button.configure(image=self.pause_icon)


                
    def update_duration(self):
        if self.playing:
            current_pos = pygame.mixer.music.get_pos() // 1000  # Convert to seconds
            current_mins = int(current_pos // 60)
            current_secs = int(current_pos % 60)
            current_str = "{:02d}:{:02d}".format(current_mins, current_secs)
            self.duration_label.config(text="Duration: {}".format(current_str))

            # Update progress bar
            progress = (current_pos / self.audio_duration) * 100
            self.progress_bar['value'] = progress

            self.root.after(1000, self.update_duration)  # Update every second
            
    def update_visual_effect(self):
        if self.playing:
            # Update circle position
            self.circle_x += self.animation_speed * self.circle_direction
            if self.circle_x >= 400 - self.circle_radius or self.circle_x <= self.circle_radius:
                self.circle_direction *= -1  # Reverse direction

            # Change circle color randomly
            self.circle_color = random.choice(['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'])

            # Increase or decrease animation speed based on audio progress
            if self.animation_speed > 0:
                self.animation_speed = 5 + int((self.audio_duration - pygame.mixer.music.get_pos() / 1000) / 10)
            else:
                self.animation_speed = -5 - int((self.audio_duration - pygame.mixer.music.get_pos() / 1000) / 10)

            # Clear canvas
            self.visualization_canvas.delete("all")

            # Draw the background image
            self.visualization_canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

            # Draw the main circle on the canvas
            self.visualization_canvas.create_oval(
                self.circle_x - self.circle_radius, self.circle_y - self.circle_radius,
                self.circle_x + self.circle_radius, self.circle_y + self.circle_radius,
                fill=self.circle_color)

            # Create and update smaller circles
            if pygame.mixer.music.get_pos() > 0 and len(self.smaller_circles) < self.max_smaller_circles:
                self.create_random_smaller_circle()
            self.update_smaller_circles()

            if pygame.mixer.music.get_pos() >= self.audio_duration * 1000:
                self.stop_audio()

            self.root.after(50, self.update_visual_effect)  # Update every 50 milliseconds
    
    def create_random_smaller_circle(self):
        x = random.randint(self.circle_x - self.circle_radius, self.circle_x + self.circle_radius)
        y = random.randint(self.circle_y - self.circle_radius, self.circle_y + self.circle_radius)
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        color = random.choice(['red', 'green', 'blue', 'yellow', 'cyan', 'magenta'])
        self.smaller_circles.append((x, y, dx, dy, color))
    
    def update_smaller_circles(self):
        for index, (x, y, dx, dy, color) in enumerate(self.smaller_circles):
            x += dx
            y += dy
            if x < self.circle_x - self.circle_radius or x > self.circle_x + self.circle_radius:
                dx *= -1
            if y < self.circle_y - self.circle_radius or y > self.circle_y + self.circle_radius:
                dy *= -1
            self.smaller_circles[index] = (x, y, dx, dy, color)

        # Draw smaller circles on the canvas
        for x, y, _, _, color in self.smaller_circles:
            self.visualization_canvas.create_oval(
                x - self.smaller_circle_radius, y - self.smaller_circle_radius,
                x + self.smaller_circle_radius, y + self.smaller_circle_radius,
                fill=color)
        
    def stop_audio(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_pause_button.configure(image=self.play_icon)
        self.duration_label.config(text="Duration: 00:00")
        self.progress_bar['value'] = 0
        self.current_pos = 0
        self.visualization_canvas.delete("all")
        self.visualization_canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
        self.smaller_circles.clear()
        self.audio_label.config(text="No audio file selected.")
        
    def run(self):
        self.root.mainloop()

# Create the root window
root = tk.Tk()

# Create an instance of the audio player
audio_player = AudioPlayer(root)

# Run the application
audio_player.run()
