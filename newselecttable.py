import tkinter as tk
from tkinter import ttk, simpledialog , StringVar , Toplevel , Entry ,OptionMenu,Label
from PIL import Image, ImageTk
import uuid
last_selected_category = None
class CustomDialog:
    def __init__(self, parent, title, categories):
        self.top = Toplevel(parent)
        self.top.title(title)
        self.top.geometry("300x200")
        
        self.result = None
        global last_selected_category
        # Label and dropdown for categories
        Label(self.top, text="Select Category:").pack(pady=10)
        self.category_var = StringVar(self.top)
        self.category_var.set(last_selected_category if last_selected_category in categories else categories[0])
        self.category_menu = OptionMenu(self.top, self.category_var, *categories)
        self.category_menu.pack()
        
        # Label and text input for value
        Label(self.top, text="Enter Value:").pack(pady=10)
        self.value_entry = Entry(self.top)
        self.value_entry.pack()
        
        # OK and Cancel buttons

        self.ok_button = tk.Button(self.top, text="OK", command=self.ok)
        self.ok_button.pack(side='left', padx=10, pady=10)
        
        self.cancel_button = tk.Button(self.top, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side='right', padx=10, pady=10)
        self.top.bind('<Return>', self.on_enter_key)
    def ok(self):
        global last_selected_category
        self.result = (self.category_var.get(), self.value_entry.get())
        last_selected_category = self.category_var.get()
        self.top.destroy()
    def on_enter_key(self, event):
        self.ok()
    def cancel(self):
        self.top.destroy()

    def show(self):
        self.top.grab_set()
        self.top.wait_window()
        return self.result

class CanvasApp:
    def __init__(self, root, input_file_path,new_rect_data,categories):
        self.categories = categories
        self.root = root
        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.pack()

        # self.button = tk.Button(root, text="Start", command=self.start_listening)
        # self.button.pack()

        self.delete_button = tk.Button(root, text="Delete", command=self.delete_selected_rectangle)
        

        self.load_image(input_file_path)
        self.rectangles = new_rect_data
        self.clicks = 0
        self.selected_rectangle = None

        self.tree = ttk.Treeview(root, columns=("Id","Value", "Category","Coordinates"), show="headings")
        self.tree.heading("Id",text="Id")
        self.tree.heading("Value", text="Value")
        self.tree.heading("Category",text="Category")
        self.tree.heading("Coordinates", text="Coordinates")
        self.tree.pack()
        self.delete_button.pack(pady=3)
        self.canvas.bind("<Button-1>", self.on_click)
        self.tree.bind("<Button-3>", self.on_tree_click)
        self.tree.bind("<Button-1>", self.on_tree_select)

    def load_image(self, file_path):
        self.image = Image.open(file_path)
        self.image = self.image.resize((300, 300))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

    def change_image(self, file_path, new_rect_data):
        self.image = Image.open(file_path)
        self.image = self.image.resize((300, 300))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.rectangles={}
        # Remove all items from the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
        for name, data in new_rect_data.items():
            print(data["coordinates"]["x_start"], data["coordinates"]["y_start"], data["coordinates"]["x_end"], data["coordinates"]["y_end"])
            rect = self.canvas.create_rectangle(data["coordinates"]["x_start"], data["coordinates"]["y_start"], data["coordinates"]["x_end"], data["coordinates"]["y_end"], outline="yellow", width=3)
            self.rectangles[name] = {"rect": rect, "coordinates": data["coordinates"],"value":data.get("value", ""), "category":data.get("category", ""), }
            self.canvas.tag_bind(rect, "<Button-3>", lambda event, name=name: self.delete_rectangle(name))
            coordinates_str = f"Start: ({data['coordinates']['x_start']}, {data['coordinates']['y_start']}), End: ({data['coordinates']['x_end']}, {data['coordinates']['y_end']})"
            self.tree.insert("", "end", values=(name, data.get("value", ""), data.get("category", ""), coordinates_str))

    def start_listening(self):
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        self.clicks += 1
        if self.clicks == 1:
            self.start_x = event.x
            self.start_y = event.y
        elif self.clicks == 2:
            self.clicks = 0
            self.end_x = event.x
            self.end_y = event.y
            self.create_rectangle()

    def create_rectangle(self):
        # name = simpledialog.askstring("Input", "Enter the name of the rectangle:")
        dialog = CustomDialog(self.root, "Create Rectangle", self.categories)
        result = dialog.show()
        name=result[1]
        category=result[0]
        if name is not None and name != "":
            rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y,outline="pink",width=3)
            coordinates = {"x_start": self.start_x, "y_start": self.start_y, "x_end": self.end_x, "y_end": self.end_y}
            unique_id=uuid.uuid4()
            unique_id=str(unique_id)
            self.rectangles[unique_id] = {"rect": rect, "coordinates": coordinates,"category":category,"value":name}

            self.canvas.tag_bind(rect, "<Button-3>", lambda event, name=name: self.delete_rectangle(name))

            coordinates_str = f"Start: ({self.start_x}, {self.start_y}), End: ({self.end_x}, {self.end_y})"
            self.tree.insert("", "end", values=(unique_id,name, category,coordinates_str))

    def delete_selected_rectangle(self):
        selected_item = self.tree.selection()
        if selected_item:
            name = self.tree.item(selected_item)["values"][0]
            self.delete_rectangle(name)

    def delete_rectangle(self, name):
        rect_info = self.rectangles[name]
        rect = rect_info["rect"]
        self.canvas.delete(rect)
        del self.rectangles[name]

        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == name:
                self.tree.delete(item)
                break

    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            name = self.tree.item(item)["values"][0]
            self.delete_rectangle(name)

    def on_tree_select(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            name = self.tree.item(item)["values"][0]
            rect_info = self.rectangles[name]
            rect = rect_info["rect"]
            self.canvas.itemconfig(rect, outline="green")

            if self.selected_rectangle:
                self.canvas.itemconfig(self.selected_rectangle, outline="yellow")

            self.selected_rectangle = rect
        else:
            if self.selected_rectangle:
                self.canvas.itemconfig(self.selected_rectangle, outline="yellow")

    def get_rectangles(self):
        return self.rectangles


# Example usage:
# root = tk.Tk()
# app = CanvasApp(root, "path/to/image.jpg")
# root.mainloop()
# rectangles = app.get_rectangles()

