"""
Game Launcher
Python 3.13.5
pip install customtinkter
pip install configparser
pip install CTkMessagebox
"""
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import configparser
import os
import subprocess

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Game Launcher")
        self.geometry("900x700")

        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"

        # Create a main frame with two columns
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left sidebar for profiles
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Profile buttons container (using a scrollable frame)
        self.profile_frame = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, sticky="nsew")

        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Add a "New Profile" button to the sidebar
        self.new_profile_button = ctk.CTkButton(self.sidebar_frame, text="NEW PROFILE", command=self.show_new_profile_ui)
        self.new_profile_button.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.load_profiles()

    def clear_main_frame(self):
        """Clears all widgets from the main content frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def load_profiles(self):
        """Loads profiles from config.ini and updates the sidebar."""
        # Clear existing profile buttons
        for widget in self.profile_frame.winfo_children():
            widget.destroy()

        self.config.read(self.config_file)
        profiles = [s for s in self.config.sections() if s != "DEFAULT"]
        
        for profile in profiles:
            button = ctk.CTkButton(self.profile_frame, text=profile, command=lambda p=profile: self.show_profile_details(p))
            button.pack(fill="x", padx=10, pady=5)

    def show_new_profile_ui(self):
        """Displays the UI for creating a new profile."""
        self.show_edit_profile_ui(is_new=True)

    def show_edit_profile_ui(self, profile_name="", game_location="", parameters="", is_new=False):
        """Displays the UI for creating a new or editing an existing profile."""
        self.clear_main_frame()
        self.main_frame.grid_rowconfigure(5, weight=1)

        title = "Create New Profile" if is_new else f"Editing: {profile_name}"
        ctk.CTkLabel(self.main_frame, text=title, font=("Roboto", 24)).pack(pady=10)

        # Profile name
        if is_new:
            ctk.CTkLabel(self.main_frame, text="Profile Name:").pack(pady=(10, 0))
            self.profile_name_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Enter profile name")
            self.profile_name_entry.pack(fill="x", padx=20)
        else:
            ctk.CTkLabel(self.main_frame, text="Profile Name:").pack(pady=(10, 0))
            profile_name_label = ctk.CTkLabel(self.main_frame, text=profile_name)
            profile_name_label.pack(fill="x", padx=20)

        # Game location
        ctk.CTkLabel(self.main_frame, text="Game Location (optional):").pack(pady=(10, 0))
        self.game_location_entry = ctk.CTkEntry(self.main_frame, placeholder_text="e.g., C:\\Games\\Game.exe")
        self.game_location_entry.insert(0, game_location)
        self.game_location_entry.pack(fill="x", padx=20)

        # General Parameters
        ctk.CTkLabel(self.main_frame, text="Parameters (optional):").pack(pady=(10, 0))
        self.general_parameters_entry = ctk.CTkEntry(self.main_frame, placeholder_text="e.g., -fullscreen -highres")
        self.general_parameters_entry.insert(0, parameters)
        self.general_parameters_entry.pack(fill="x", padx=20)

        # Multiple Servers Checkbox
        self.multi_server_var = ctk.BooleanVar(value=self.config.getboolean(profile_name, 'multiple_servers', fallback=False))
        self.multi_server_checkbox = ctk.CTkCheckBox(self.main_frame, text="Can this exe directly connect to multiple game servers?", variable=self.multi_server_var, command=self.toggle_server_options)
        self.multi_server_checkbox.pack(pady=(20, 10), padx=20, anchor="w")

        # Server options container frame
        self.server_options_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.server_options_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Game Parameters
        ctk.CTkLabel(self.server_options_frame, text="Game Start Parameters (optional):").pack(pady=(10, 0))
        self.parameters_entry = ctk.CTkEntry(self.server_options_frame, placeholder_text="e.g., -fullscreen -highres")
        self.parameters_entry.insert(0, parameters)
        self.parameters_entry.pack(fill="x", padx=20)

        # Server list display
        self.server_entries = []
        if self.multi_server_var.get():
            self.show_server_entry_grid(profile_name)

        # Save button
        save_button_text = "Save Profile" if is_new else "Save Changes"
        save_button = ctk.CTkButton(self.main_frame, text=save_button_text, command=lambda: self.save_profile(profile_name, is_new))
        save_button.pack(pady=20)

        self.toggle_server_options()
        
    def toggle_server_options(self):
        """Hides or shows the server entry grid if multiple servers are enabled."""
        self.clear_server_grid()
        if self.multi_server_var.get():
            self.show_server_entry_grid()

    def show_server_entry_grid(self, profile_name=None):
        """Displays the input grid for multiple servers."""
        self.clear_server_grid()
        self.server_options_frame.grid_columnconfigure(0, weight=1)
        self.server_options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.server_options_frame, text="Server Name", font=("Roboto", 14, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(self.server_options_frame, text="Parameters", font=("Roboto", 14, "bold")).grid(row=0, column=1, padx=5, pady=5)
        
        servers = []
        if profile_name and self.config.has_option(profile_name, 'server_list'):
            server_str = self.config[profile_name]['server_list']
            servers = [s.split(',', 1) for s in server_str.split(';')]

        # Add default server first if it exists
        try:
            default_params = self.config[profile_name].get("start_parameters", "")
            if default_params and not self.config.getboolean(profile_name, 'multiple_servers', fallback=False):
                self.add_server_row(1, "DEFAULT", default_params)
        except:
            pass
        
        # Add other servers
        for i, (name, params) in enumerate(servers):
            # ... logic to add other rows
            self.add_server_row(i + 2 if default_params else i + 1, name, params)

        add_button = ctk.CTkButton(self.server_options_frame, text="+ Add Server", command=lambda: self.add_server_row(len(self.server_entries) + 1))
        add_button.grid(row=len(self.server_entries) + 1, column=0, columnspan=2, pady=10)

    def add_server_row(self, row_num, name="", params=""):
        """Adds a new row of server name and parameters entries."""
        name_entry = ctk.CTkEntry(self.server_options_frame, placeholder_text="Server Name")
        name_entry.insert(0, name)
        name_entry.grid(row=row_num, column=0, padx=50, pady=5, sticky="ew")

        params_entry = ctk.CTkEntry(self.server_options_frame, placeholder_text="Parameters")
        params_entry.insert(0, params)
        params_entry.grid(row=row_num, column=1, padx=50, pady=5, sticky="ew")
        
        self.server_entries.append((name_entry, params_entry))
    
    def clear_server_grid(self):
        """Removes all server-related widgets."""
        for widget in self.server_options_frame.winfo_children():
            widget.destroy()
        self.server_entries = []

    def save_profile(self, profile_name, is_new):
        """Saves or updates a profile to the config file."""
        if is_new:
            profile_name = self.profile_name_entry.get().strip()
            if not profile_name:
                CTkMessagebox(title="Error", message="Profile name cannot be empty.")
                return
            if self.config.has_section(profile_name):
                CTkMessagebox(title="Error", message=f"Profile '{profile_name}' already exists.")
                return
            self.config[profile_name] = {}

        self.config[profile_name]["game_location"] = self.game_location_entry.get().strip()
        self.config[profile_name]["multiple_servers"] = str(self.multi_server_var.get())
        self.config[profile_name]["start_parameters"] = self.general_parameters_entry.get().strip()

        if self.multi_server_var.get():
            server_list = []
            # Add the general parameters as a DEFAULT server
            general_params = self.general_parameters_entry.get().strip()
            if general_params:
                server_list.append(f"DEFAULT,{general_params}")
            
            for name_entry, params_entry in self.server_entries:
                server_list.append(f"{name_entry.get().strip()},{params_entry.get().strip()}")
            
            self.config[profile_name]["server_list"] = ";".join(server_list)
            # Note: 'start_parameters' would no longer be a separate field
        else:
            self.config[profile_name]["start_parameters"] = self.general_parameters_entry.get().strip()
            if "server_list" in self.config[profile_name]:
                del self.config[profile_name]["server_list"]

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

        self.load_profiles()  # Refresh the sidebar
        self.show_profile_details(profile_name) # Show the newly created/edited profile

    def show_profile_details(self, profile_name):
        """Displays details and options for a selected profile."""
        self.clear_main_frame()
        profile_data = self.config[profile_name]
        game_location = profile_data.get("game_location", "")
        multiple_servers = self.config.getboolean(profile_name, 'multiple_servers', fallback=False)

        ctk.CTkLabel(self.main_frame, text=f"Profile: {profile_name}", font=("Roboto", 24)).pack(pady=10)

        # Option 1: Start game (Raw)
        start_raw_button = ctk.CTkButton(self.main_frame, text="Start Game (Raw)", command=lambda: self.start_game(game_location))
        start_raw_button.pack(pady=10, fill="x", padx=20)

        # Option 2: Start game with parameters / Server Picklist
        if multiple_servers:
            server_list_str = profile_data.get("server_list", "")
            if server_list_str:
                servers = [s.split(',', 1) for s in server_list_str.split(';')]
                server_names = [s[0] for s in servers]
                
                ctk.CTkLabel(self.main_frame, text="Select Server:").pack(pady=(10, 0), padx=20)
                server_combobox = ctk.CTkComboBox(self.main_frame, values=server_names)
                server_combobox.pack(fill="x", padx=20)
                
                start_button = ctk.CTkButton(self.main_frame, text="Connect to Server", command=lambda: self.start_game_from_combobox(profile_name, server_combobox.get()))
                start_button.pack(pady=10, fill="x", padx=20)
            else:
                ctk.CTkLabel(self.main_frame, text="No servers configured for this profile.").pack(pady=10, padx=20)
        else:
            parameters = profile_data.get("start_parameters", "")
            start_params_button = ctk.CTkButton(self.main_frame, text="Start Game with Parameters", command=lambda: self.start_game_with_params(game_location, parameters, profile_name))
            start_params_button.pack(pady=10, fill="x", padx=20)

        # Option 3: Edit profile
        edit_button = ctk.CTkButton(self.main_frame, text="Edit Profile", command=lambda: self.show_edit_profile_ui(profile_name, game_location, profile_data.get('start_parameters', '')))
        edit_button.pack(pady=10, fill="x", padx=20)

        # Option 4: Delete profile
        delete_button = ctk.CTkButton(self.main_frame, text="Delete Profile", fg_color="red", hover_color="darkred", command=lambda: self.delete_profile(profile_name))
        delete_button.pack(pady=10, fill="x", padx=20)

    def start_game(self, game_location):
        """Starts the game executable without any parameters."""
        if not game_location:
            CTkMessagebox(title="Error", message="No game location specified for this profile.")
            return

        try:
            subprocess.Popen([game_location])
            print(f"Starting {game_location}")
        except FileNotFoundError:
            CTkMessagebox(title="Error", message=f"Executable not found at: {game_location}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to start game: {e}")

    def start_game_from_combobox(self, profile_name, selected_server):
        """Starts the game with parameters based on the selected server."""
        profile_data = self.config[profile_name]
        game_location = profile_data.get("game_location", "")
        server_list_str = profile_data.get("server_list", "")
        
        servers = {s.split(',', 1)[0]: s.split(',', 1)[1] for s in server_list_str.split(';')}
        parameters = servers.get(selected_server, "")
        
        self.start_game_with_params(game_location, parameters, selected_server)

    def start_game_with_params(self, game_location, parameters, profile_name):
        """
        Starts the game executable with parameters.
        Creates and runs a temporary batch file for more robust handling.
        """
        if not game_location:
            CTkMessagebox(title="Error", message="No game location specified for this profile.")
            return
        
        # Create a temporary batch file
        bat_content = f'"{game_location}" {parameters}\n'
        bat_file_path = os.path.join(os.getcwd(), f"{profile_name}_start_game.bat")
        
        with open(bat_file_path, "w") as bat_file:
            bat_file.write(bat_content)
        
        try:
            # Use subprocess to run the batch file
            subprocess.Popen([bat_file_path])
            print(f"Starting {game_location} with parameters: {parameters}")
        except FileNotFoundError:
            CTkMessagebox(title="Error", message=f"Batch file not found: {bat_file_path}")
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to start game with batch file: {e}")

    def delete_profile(self, profile_name):
        """Deletes a profile from the config file."""
        if self.config.has_section(profile_name):
            self.config.remove_section(profile_name)

            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            
            self.load_profiles()
            self.clear_main_frame()
            CTkMessagebox(title="Success", message=f"Profile '{profile_name}' has been deleted.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
