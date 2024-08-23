import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import glob
from pysondb import db
from newselecttable import CanvasApp  # Import the CanvasApp class
from tktooltip import ToolTip

# Initialize the database
db_path = 'my_database.json'
if not os.path.exists(db_path):
    my_db = db.getDb(db_path)
else:
    my_db = db.getDb(db_path)
car_properties = [
    "Odometer",
    "Speedometer",
    "Number Plate",
    "Fuel Level",
    "Engine Temperature",
    "Oil Pressure",
    "Battery Voltage",
    "Tire Pressure",
    "GPS Coordinates",
    "Audio System",
    "Air Conditioning",
    "Headlights",
    "Brake Lights",
    "Turn Signals",
    "Windshield Wipers",
    "Cruise Control",
    "Transmission Status",
    "Drivetrain Type",
    "Seatbelt Status",
    "Airbag Status"
]
# Variables
input_folder_path = ""
output_folder_path = ""

prevIdx = 0
index = 0
all_img_paths = []
TOTAL_IMAGES = 0
FINISHED_IMAGES = 0

# Load saved paths if they exist
if os.path.exists('saved_input_path.txt'):
    with open('saved_input_path.txt', 'r') as f:
        input_folder_path = f.readline().strip()

if os.path.exists('saved_output_path.txt'):
    with open('saved_output_path.txt', 'r') as f:
        output_folder_path = f.readline().strip()

# Functions
def load_images():
    global all_img_paths, TOTAL_IMAGES, FINISHED_IMAGES
    if not input_folder_path:
        messagebox.showwarning("Warning", "Input path not selected")
        return

    all_img_paths = sorted(glob.glob(input_folder_path + "/images/*"))
    TOTAL_IMAGES = len(all_img_paths)

    label_total_images.config(text=f"Total Images: {TOTAL_IMAGES}")
    label_finished_images.config(text=f"Finished Images: {FINISHED_IMAGES}")
    label_rest_images.config(text=f"Remaining Images: {TOTAL_IMAGES - FINISHED_IMAGES}")
    button_frame.pack(pady=20)
    label_image_name.pack()
    show_image(all_img_paths[0])
    label_image.pack()
   
def show_image(image_path):
    global app, root
    image_name = os.path.basename(image_path)

    prevData = get_labeled_data(image_name)
    label_image_name.config(text=f"Image Name: {image_name}")

    # Destroy the previous CanvasApp instance if it exists
    if 'app' in globals() and app:
        print(prevData)
        save_labeled_data()
        app.change_image(image_path,prevData)
        return
    
    # Load and display the image using CanvasApp
    app = CanvasApp(root, image_path,prevData,car_properties)
    app.change_image(image_path,prevData)
    root.update_idletasks()  # Update the GUI to reflect changes

def next_image():
    global index ,prevIdx
    if index == TOTAL_IMAGES - 1:
        messagebox.showinfo("Success", "Hooray! You have explored all the images")
        return
    prevIdx=index
    index += 1
    show_image(all_img_paths[index])

def previous_image():
    global index,prevIdx
    if index == 0:
        messagebox.showwarning("Warning", "Can't go back")
        return
    prevIdx=index
    index -= 1
    show_image(all_img_paths[index])

def save_labeled_data():
    global app, prevIdx
    if app:
        rectangles = app.get_rectangles()
        image_name = os.path.basename(all_img_paths[prevIdx])
        data = my_db.reSearch("image",r""+image_name)
        if data:
            my_db.updateByQuery({"image": image_name}, {"rectangles": rectangles})
        else:
            my_db.add({"image": image_name, "rectangles": rectangles})
def get_labeled_data(image_name):
    data = my_db.reSearch("image",r""+image_name)
    if data:
        return data[0]["rectangles"]
    else:
        return {}
def browse_input_directory():
    global input_folder_path
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        input_folder_path = folder_selected
        btn_input_folder.config(text=f"Selected Folder: {input_folder_path}")
        with open('saved_input_path.txt', 'w') as f:
            f.write(input_folder_path)

def browse_output_directory():
    global output_folder_path
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_folder_path = folder_selected
        btn_output_folder.config(text=f"Selected Folder: {output_folder_path}")
        with open('saved_output_path.txt', 'w') as f:
            f.write(output_folder_path)

# GUI Setup
root = tk.Tk()
root.title("Photo Locator")



# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

btn_input_folder = tk.Button(button_frame, text="Browse Input Folder", command=browse_input_directory)
btn_input_folder.grid(row=0, column=0, padx=10)

btn_output_folder = tk.Button(button_frame, text="Browse Output Folder", command=browse_output_directory)
btn_output_folder.grid(row=0, column=1, padx=10)
btn_load_images = tk.Button(button_frame, text="Load Images", command=load_images)
btn_load_images.grid(row=0, column=2, padx=10)

# Rest of the code...

label_total_images = tk.Label(root, text="Load Images")
label_finished_images = tk.Label(root, text="Load Images")
label_rest_images = tk.Label(root, text="Load Images")

label_image = tk.Label(root)
button_frame = tk.Frame(root)

btn_previous = tk.Button(button_frame, text="Previous", command=previous_image)
btn_previous.grid(row=0, column=0, padx=10)
btn_next = tk.Button(button_frame, text="Next", command=next_image)
btn_next.grid(row=0, column=1, padx=10)


label_image_name = tk.Label(root, text="Image Name: ")

if input_folder_path:
    btn_input_folder.config(text="Change input folder", fg="green")
    ToolTip(btn_input_folder, msg=input_folder_path)
if output_folder_path:
    btn_output_folder.config(text=f"Change output folder", fg="green")
    ToolTip(btn_output_folder, msg=output_folder_path)

root.mainloop()
