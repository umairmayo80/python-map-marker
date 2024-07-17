import customtkinter
from tkintermapview import TkinterMapView
from tkinter import filedialog, simpledialog, messagebox
import os
import tkinter as tk
import time
from PIL import Image, ImageTk

customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")


def display_files_in_marker(marker):
    folder_path = marker.data.get("folder_path")
    message = f"Marker: {marker.text}\nCoordinates: {marker.position[0]}, {marker.position[1]}\n"
    if folder_path:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if files:
            file_list = "\n".join(files)
            messageFiles = f"Files:\n{file_list}"
        else:
            messageFiles = "No files found in the folder."
    else:
        messageFiles = "No folder path associated with this marker."
    messagebox.showinfo(title="Marker Info", message=message+messageFiles)


class App(customtkinter.CTk):
    APP_NAME = "Vectrino Mapa"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.marker_list = []
        self.current_polygon_markers_count = 0
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Create map widget
        self.map_widget = TkinterMapView(self, width=App.WIDTH, height=App.HEIGHT - 100, corner_radius=0)
        self.map_widget.grid(row=0, column=0, sticky="nsew")

        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_address("Rijeka Hrvatska")

        self.base_layer_url = "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga"
        self.satellite_layer_url = "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga"
        self.terrain_layer_url = "https://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}&s=Ga"

        self.layer_urls = [self.base_layer_url, self.satellite_layer_url, self.terrain_layer_url]
        self.layer_names = ["Base Layer", "Satellite", "Terrain"]
        self.current_layer_index = 0

        self.active_layer = self.layer_urls[self.current_layer_index]

        # Create bottom navigation frame
        self.bottom_frame = customtkinter.CTkFrame(self)
        self.bottom_frame.grid(row=1, column=0, sticky="ew", pady=10)

        self.entry = customtkinter.CTkEntry(self.bottom_frame, placeholder_text="Type address")
        self.entry.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        self.entry.bind("<Return>", self.search_event)

        self.search_button = customtkinter.CTkButton(self.bottom_frame, text="Search", command=self.search_event)
        self.search_button.pack(side="left", padx=10, pady=10)

        self.layer_button = customtkinter.CTkButton(self.bottom_frame, text="Change Layer", command=self.change_layer)
        self.layer_button.pack(side="left", padx=10, pady=10)

        self.polygon_button = customtkinter.CTkButton(self.bottom_frame, text="Create Polygon",
                                                      command=self.create_polygon)
        self.polygon_button.pack(side="left", padx=10, pady=10)

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.bottom_frame, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.set("Dark")
        self.appearance_mode_optionemenu.pack(side="left", padx=10, pady=10)

        # Set map widget right-click menu
        self.map_widget.add_right_click_menu_command(label="Add Marker", command=self.add_marker_event,
                                                     pass_coords=True)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def add_marker_event(self, coords):
        folder_path = filedialog.askdirectory()
        if folder_path:
            marker_name = simpledialog.askstring("Marker Name", "Enter a name for the marker:")
            if marker_name:
                new_marker = self.map_widget.set_marker(coords[0], coords[1], text=marker_name,
                                                        command=display_files_in_marker)
                if new_marker:
                    new_marker.data = {"folder_path": folder_path}
                    print(f"Added marker at: {coords}")
    
    def polygon_add_marker_event(self, args):
        marker = self.map_widget.set_marker(args[0], args[1])
        print(f"Added marker at: {args[0], args[1]}")
        self.marker_list.append(marker)
        if (len(self.marker_list) == self.current_polygon_markers_count):
            # Display marker coordinates
            coordinates = [marker.position for marker in self.marker_list]
            polygon = self.map_widget.set_polygon(coordinates, name="Polygon", command=self.polygon_click)
            self.map_widget.add_left_click_map_command(callback_function=None)

            selected_images = filedialog.askopenfilenames(title="Select Images",
                                                        filetypes=(("Image files", "*.jpg;*.jpeg;*.png"),))
            if selected_images:
                messagebox.showinfo("Selected Images", f"Selected Images:\n{selected_images}")
                polygon.data = {"selected_images" : selected_images}
            else:
                messagebox.showwarning("No Images Selected", "No images were selected.")
        

    def polygon_click(self, polygon):
        if "selected_images" in polygon.data:
            selected_images = polygon.data["selected_images"]
            if selected_images:
                # Create a new window to display the images
                window = tk.Toplevel(self)
                window.title("Selected Images")
                
                # Create a scrollable canvas to hold the image thumbnails
                canvas = tk.Canvas(window, borderwidth=0, background="#ffffff")
                scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                # Create a frame to hold the image thumbnails
                frame = tk.Frame(canvas, background="#ffffff")
                frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
                
                canvas.create_window((0, 0), window=frame, anchor="nw")
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Load and display the image thumbnails
                for image_path in selected_images:
                    image = Image.open(image_path)
                    thumbnail_size = (200, 200)  # Adjust the thumbnail size as needed
                    image.thumbnail(thumbnail_size)
                    photo = ImageTk.PhotoImage(image)
                    label = tk.Label(frame, image=photo)
                    label.image = photo  # Keep a reference to prevent garbage collection
                    label.pack(side="left", padx=10, pady=10)
            else:
                messagebox.showwarning("No Images Selected", "No images were selected.")
        else:
            messagebox.showwarning("No Images Selected", "No images were selected.")


        def display_full_image(image_path):
            # Create a new window to display the full image
            window = tk.Toplevel()
            window.title("Full Image")
            
            # Load the full image
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)
            
            # Create a label to display the full image
            label = tk.Label(window, image=photo)
            label.image = photo  # Keep a reference to prevent garbage collection
            label.pack()


    def change_layer(self):
        self.current_layer_index = (self.current_layer_index + 1) % len(self.layer_urls)
        new_layer_url = self.layer_urls[self.current_layer_index]
        new_layer_name = self.layer_names[self.current_layer_index]
        self.map_widget.set_tile_server(new_layer_url, max_zoom=22)
        self.layer_button.configure(text=f"Layer: {new_layer_name}")

    def create_polygon(self):
        # Prompt user to create at least three markers
        num_markers = simpledialog.askinteger("Create Polygon", "Enter the number of markers (minimum 3):")
        if num_markers and num_markers >= 3:
            self.current_polygon_markers_count = num_markers
            self.map_widget.add_left_click_map_command(callback_function=self.polygon_add_marker_event)
        else:
            messagebox.showwarning("Invalid Number of Markers", "Please enter a valid number of markers (minimum 3).")

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
