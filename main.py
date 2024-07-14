import customtkinter
from tkintermapview import TkinterMapView
from tkinter import filedialog, simpledialog, messagebox
import os
import tkinter as tk

customtkinter.set_default_color_theme("green")
customtkinter.set_appearance_mode("dark")

def tempF(temp):
    print("tempf", temp)

class App(customtkinter.CTk):
    APP_NAME = "Vectrino Mapa"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)

        self.marker_list = []
        self.polygon_list = []

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

        self.polygon_button = customtkinter.CTkButton(self.bottom_frame, text="Create Polygon", command=self.create_polygon)
        self.polygon_button.pack(side="left", padx=10, pady=10)

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.bottom_frame, values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.set("Dark")
        self.appearance_mode_optionemenu.pack(side="left", padx=10, pady=10)

        # Set map widget right-click menu
        self.map_widget.add_right_click_menu_command(label="Add Marker", command=self.add_marker_event, pass_coords=True)

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def add_marker_event(self, coords):
        folder_path = filedialog.askdirectory()
        if folder_path:
            marker_name = simpledialog.askstring("Marker Name", "Enter a name for the marker:")
            if marker_name:
                new_marker = self.map_widget.set_marker(coords[0], coords[1], text=marker_name)
                new_marker.command = tempF
                if new_marker:
                    self.marker_list.append(new_marker)
                    print(f"Added marker at: {coords}, total markers: {len(self.marker_list)}")  # Debug print

    def display_files_in_marker(self, marker):
        folder_path = marker.data.get("folder_path")
        if folder_path:
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if files:
                file_list = "\n".join(files)
                marker.tooltip = f"Files:\n{file_list}"
            else:
                marker.tooltip = "No files found in the folder."
        else:
            marker.tooltip = "No folder path associated with this marker."

    def change_layer(self):
        self.current_layer_index = (self.current_layer_index + 1) % len(self.layer_urls)
        new_layer_url = self.layer_urls[self.current_layer_index]
        new_layer_name = self.layer_names[self.current_layer_index]
        self.map_widget.set_tile_server(new_layer_url, max_zoom=22)
        self.layer_button.configure(text=f"Layer: {new_layer_name}")

    def create_polygon(self):
        if len(self.marker_list) < 3:
            messagebox.showerror("Error", "At least 3 markers are required to create a polygon.")
            return

        coords = [(marker.position[0], marker.position[1]) for marker in self.marker_list]
        print(f"Creating polygon with coordinates: {coords}")  # Debug print

        if self.polygon_list:
            for polygon in self.polygon_list:
                self.map_widget.delete_line(polygon)
            self.polygon_list = []


        for i in range(len(coords)):
            start_point = coords[i]
            end_point = coords[(i + 1) % len(coords)]
            line = self.map_widget.set_path([start_point, end_point])
            self.polygon_list.append(line)

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def start(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()
