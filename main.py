
import tkinter as tk
import os
from PIL import Image, ImageTk
from lists import item_images, orte
import sys

# Function to handle dropping images into the main window
def on_drop(event):
    widget = event.widget
    if not hasattr(widget, '_drag_data'):
        widget._drag_data = {"x": 0, "y": 0}
    x = widget.winfo_x() - widget._drag_data["x"] + event.x
    y = widget.winfo_y() - widget._drag_data["y"] + event.y
    widget.place(x=x, y=y)

def on_drag_start(event):
    widget = event.widget
    widget._drag_data = {"x": event.x, "y": event.y}

def on_drag_motion(event):
    widget = event.widget
    x = widget.winfo_x() - widget._drag_data["x"] + event.x
    y = widget.winfo_y() - widget._drag_data["y"] + event.y
    widget.place(x=x, y=y)
    
# Erstelle ein Fenster
fenster = tk.Tk()
fenster.configure(bg='black')
fenster.title("Ishizakis Location Tracker")
fenster.resizable(False, False)  # Prevent the window from being resized

# Define the base path for the images
base_path = os.path.join(os.path.dirname(__file__), 'images')

# Create a menu bar
menubar = tk.Menu(fenster)

# Create a "Program" menu
program_menu = tk.Menu(menubar, tearoff=0)
program_menu.add_command(label="Restart", command=lambda: os.execv(sys.executable, ['python'] + sys.argv))

# Add the "Program" menu to the menu bar
menubar.add_cascade(label="Program", menu=program_menu)

# Configure the window to use the menu bar
fenster.config(menu=menubar)

# Create a main frame to hold all other frames
main_frame = tk.Frame(fenster, bg='black')
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Add 4 additional columns with the Gossip Stone image
gossip_image_path = os.path.join(base_path, 'Miscellaneous', 'Gossip-Stone.png')
gossip_img = Image.open(gossip_image_path)
gossip_img = gossip_img.resize((20, 20), Image.LANCZOS)  # Resize the image to 30x30 pixels
gossip_photo = ImageTk.PhotoImage(gossip_img)

for row in range(18):
    for col in range(1):
        label = tk.Label(main_frame, text=f"{orte[row]}", font=("Helvetica", 12), bg='black', fg='white')
        label.grid(row=row, column=0, padx=1, pady=5)


for row in range(18):
    for col in range(2, 6): 
        label = tk.Label(main_frame, image=gossip_photo, bg='black')
        label.image = gossip_photo  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, padx=1, pady=1)

for row in range(18, 35):
    for col in range(6):
        label = tk.Label(main_frame, text=f"{orte[row]}", font=("Helvetica", 12), bg='black', fg='white')
        label.grid(row=row-18, column=6, padx=1, pady=5)

for row in range(18):
    for col in range(7, 11): 
        label = tk.Label(main_frame, image=gossip_photo, bg='black')
        label.image = gossip_photo  # Keep a reference to avoid garbage collection
        label.grid(row=row, column=col, padx=1, pady=1)

row = 0
col = 0

for item, image_path in item_images.items():
    img = Image.open(image_path)
    img = img.resize((20, 20), Image.LANCZOS)  # Resize the image to 30x30 pixels
    photo = ImageTk.PhotoImage(img)
    label = tk.Label(main_frame, image=photo, bg='black')
    label.image = photo  # Keep a reference to avoid garbage collection
    label.grid(row=row, column=col + 12, padx=1, pady=1, sticky='e')  # Start from column 6 and align right
    col += 1
    if col == 4:  # Adjust the number of columns to 4
        col = 0
        row += 1
        
# Make the images draggable, except for the gossip images
for widget in main_frame.winfo_children():
    if isinstance(widget, tk.Label) and widget.cget("image") != str(gossip_photo):
        widget.bind("<Button-1>", on_drag_start)
        widget.bind("<B1-Motion>", on_drag_motion)

fenster.geometry("500x650")

# Starte die Hauptereignisschleife
fenster.mainloop()




