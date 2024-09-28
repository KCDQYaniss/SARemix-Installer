import requests
from io import BytesIO
from PIL import Image
import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import shutil
import threading
import re
import zipfile
import io
import logging
from threading import Event
import customtkinter as ctk
import time
from tkinter import messagebox, filedialog
from PIL import Image
from io import BytesIO

logging.basicConfig(filename='sa_remix_installer.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SARemixInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SARemix Installer")
        self.geometry("800x650")
        self.resizable(False, False)

        self.folder_selected = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_welcome_page()

        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def create_welcome_page(self):
        self.welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.welcome_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.welcome_frame.grid_columnconfigure(0, weight=1)
        self.welcome_frame.grid_rowconfigure(4, weight=1)

        welcome_title = ctk.CTkLabel(self.welcome_frame, text="Welcome to the SA Remix Auto-Installer !",
                                     font=ctk.CTkFont(size=28, weight="bold"))
        welcome_title.grid(row=0, column=0, pady=(0, 40))

        info_text = ("Download speed will depend on a lot of stuff, hard drive speeds, your internet, "
                     "github speeds and updates to the mod that could make it heavier.")
        info_label = ctk.CTkLabel(self.welcome_frame, text=info_text, wraplength=700)
        info_label.grid(row=1, column=0, pady=(0, 40))

        contact_text = ("If you have any issues with the app, just ask on the RTX Remix Showcase discord "
                        "GTA SA channel, or contact me on discord : yanisselt")
        contact_label = ctk.CTkLabel(self.welcome_frame, text=contact_text, wraplength=700)
        contact_label.grid(row=2, column=0, pady=(0, 40))

        # Add this code to load and display the image
        image_url = "https://www.cowcotland.com/images.php?url=images/news/2023/06/rtx.jpg"
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(700, 330))
        
        image_label = ctk.CTkLabel(self.welcome_frame, image=ctk_image, text="")
        image_label.grid(row=3, column=0, pady=(0, 20))

        next_button = ctk.CTkButton(self.welcome_frame, text="Next", command=self.show_main_page,
                                    fg_color="transparent", border_width=1, border_color="#FFCC70",
                                    hover_color="#5c5c5a", width=100)
        next_button.grid(row=4, column=0, pady=(0, 10), padx=(0, 10), sticky="se")

    def show_main_page(self):
        self.welcome_frame.grid_forget()
        self.create_main_page()

    def create_main_page(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        self.title_label = ctk.CTkLabel(self, text="SA Remix Auto-Installer", 
                                        font=ctk.CTkFont(size=20, weight="bold"), 
                                        text_color="#FFCC70")
        self.title_label.grid(row=0, column=0, pady=(5, 2), sticky="ew")

        self.directory_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=2, border_color="#FFCC70")
        self.directory_frame.grid(row=1, column=0, pady=(20, 25), padx=20, sticky="ew")
        self.directory_frame.grid_columnconfigure(1, weight=1)

        self.select_button = ctk.CTkButton(self.directory_frame, text="Select Directory", command=self.select_folder, width=150, fg_color="transparent", border_width=1, border_color="#FFCC70", hover_color="#5c5c5a")
        self.select_button.grid(row=0, column=0, padx=(50, 5), pady=(25, 25))

        self.directory_label = ctk.CTkLabel(self.directory_frame, text="No directory selected", anchor='w', width=500)
        self.directory_label.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=5)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, pady=5, padx=20, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", border_width=2, border_color="#FFCC70", width=380, height=400)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_frame.grid_propagate(False)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.Download_all_button = ctk.CTkButton(self.left_frame, text="Download All", command=self.Download_all, fg_color="transparent", border_width=1, border_color="#FFCC70", width=200, hover_color="#5c5c5a")
        self.Download_all_button.grid(row=0, column=0, pady=20)

        self.download_status_label = ctk.CTkLabel(self.left_frame, text="Status: Not started", width=360)
        self.download_status_label.grid(row=1, column=0, pady=2, padx=20)

        self.right_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", border_width=2, border_color="#FFCC70", width=380, height=400)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_frame.grid_propagate(False)
        self.right_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.update1 = ctk.CTkButton(self.right_frame, text="Update SA Remix", command=self.Download_SARemix, fg_color="transparent", border_width=1, border_color="#FFCC70", width=200, hover_color="#5c5c5a")
        self.update1.grid(row=0, column=0, pady=(5, 0))
        self.update1_status = ctk.CTkLabel(self.right_frame, text="Waiting for download", width=200)
        self.update1_status.grid(row=1, column=0, pady=(0, 5))

        self.update2 = ctk.CTkButton(self.right_frame, text="Update SA Remix necessary mods", command=self.Download_SARemix_Necessary_Mods, fg_color="transparent", border_width=1, border_color="#FFCC70", width=200, hover_color="#5c5c5a")
        self.update2.grid(row=2, column=0, pady=(5, 0))
        self.update2_status = ctk.CTkLabel(self.right_frame, text="Waiting for download", width=200)
        self.update2_status.grid(row=3, column=0, pady=(0, 5))

        self.update_rtx_remix = ctk.CTkButton(self.right_frame, text="Update RTX Remix", command=lambda: self.Download_RTX_Remix("NVIDIAGameWorks", "rtx-remix"), fg_color="transparent", border_width=1, border_color="#FFCC70", width=200, hover_color="#5c5c5a")
        self.update_rtx_remix.grid(row=4, column=0, pady=(5, 0))
        self.update_rtx_remix_status = ctk.CTkLabel(self.right_frame, text="Waiting for download", width=200)
        self.update_rtx_remix_status.grid(row=5, column=0, pady=(0, 5))

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=2, border_color="#FFCC70", height=100)
        self.bottom_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        self.bottom_frame.grid_propagate(False)

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, width=760)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(10, 5), padx=20)

        self.download_info_label = ctk.CTkLabel(self.bottom_frame, text="Download Speed: 0 MB/s", width=760)
        self.download_info_label.pack(pady=(0, 10), padx=20)

    def select_folder(self):
        self.folder_selected = filedialog.askdirectory()
        if self.folder_selected:
            self.directory_label.configure(text=f"Selected directory: {self.folder_selected}")
        else:
            messagebox.showwarning("Warning", "No folder selected. Please select a folder to continue.")

    def reset_progress_bar(self):
        self.progress_bar.set(0)

    def disable_buttons(self):
        for button in [self.select_button, self.Download_all_button, self.update1, self.update2, self.update_rtx_remix]:
            button.configure(state="disabled")

    def enable_buttons(self):
        for button in [self.select_button, self.Download_all_button, self.update1, self.update2, self.update_rtx_remix]:
            button.configure(state="normal")

    def disable_button(self, button):
        button.configure(state="disabled")
        self.select_button.configure(state="disabled")

    def enable_button(self, button):
        button.configure(state="normal")
        if all(btn.cget("state") == "normal" for btn in [self.update1, self.update2, self.update_rtx_remix, self.Download_all_button]):
            self.select_button.configure(state="normal")

    def download_file(self, url, file_path, total_size):
        start_time = time.time()
        downloaded_size = 0
        chunk_size = 1024 * 1024  # 1MB chunk size

        with self.session.get(url, stream=True) as response:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = downloaded_size / (1024 * 1024 * elapsed_time)
                            progress = downloaded_size / total_size if total_size > 0 else 0
                            self.after(0, lambda p=progress, s=speed: self.update_progress(p, s))

    def update_download_status(self, status):
        self.after(0, lambda: self.download_status_label.configure(text=f"Status: {status}"))

    def reset_download_status(self):
        self.after(0, lambda: self.download_status_label.configure(text="Status: Not started"))

    def update_progress(self, progress, speed):
        self.after(0, lambda: self.progress_bar.set(progress))
        self.after(0, lambda: self.download_info_label.configure(
            text=f"Download Speed: {speed:.2f} MB/s"
        ))
        self.update_idletasks()

    def download_and_extract_release(self, owner, repo, file_name, repo_name, button):
        def download_thread():
            try:
                api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
                response = self.session.get(api_url)
                response.raise_for_status()
                release_data = response.json()
                
                download_url = next((asset['browser_download_url'] for asset in release_data['assets'] if asset['name'] == file_name), None)
                
                if download_url:
                    file_path = os.path.join(self.folder_selected, file_name)
                    self.download_file(download_url, file_path, int(release_data['assets'][0]['size']))
                    
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(self.folder_selected)
                    
                    os.remove(file_path)
                    
                    self.after(0, lambda: messagebox.showinfo("Success", f"{repo_name} downloaded and extracted successfully."))
                    logging.info(f"{repo_name} downloaded and extracted successfully.")
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Failed to find {file_name} in the latest release."))
                    logging.error(f"Failed to find {file_name} in the latest release.")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"An error occurred while processing {repo_name}: {str(e)}"))
                logging.error(f"An error occurred while processing {repo_name}: {str(e)}")
            finally:
                self.after(0, lambda: self.enable_button(button))

        threading.Thread(target=download_thread).start()

    def Download_SARemix(self, event=None):
        def download_thread():
            self.after(0, lambda: self.update_download_status("Downloading SA Remix"))
            self.after(0, lambda: self.disable_button(self.update1))
            self.after(0, lambda: self.update1_status.configure(text="Updating"))
            owner = "Hemry81"
            repo = "GTASA-Remix"
            
            try:
                # Get the latest commit SHA
                api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/main"
                response = self.session.get(api_url)
                response.raise_for_status()
                commit_data = response.json()
                latest_commit_sha = commit_data['sha']

                # Download the zip file of the latest commit
                download_url = f"https://github.com/{owner}/{repo}/archive/{latest_commit_sha}.zip"
                file_name = f"{repo}-{latest_commit_sha[:7]}.zip"
                file_path = os.path.join(self.folder_selected, file_name)

                # Try to get the file size
                head_response = self.session.head(download_url)
                total_size = int(head_response.headers.get('content-length', 0))

                self.download_file(download_url, file_path, total_size)

                # Extract the downloaded file
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if zip_info.filename.startswith(f'{repo}-{latest_commit_sha}/'):
                            zip_info.filename = zip_info.filename.split('/', 1)[1]
                            if zip_info.filename:  # Skip the root directory itself
                                zip_ref.extract(zip_info, self.folder_selected)
                
                os.remove(file_path)  # Remove the zip file after extraction
                
                self.after(0, lambda: messagebox.showinfo("Success", "SA Remix downloaded and extracted successfully."))
                logging.info("SA Remix downloaded and extracted successfully.")
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                self.after(0, lambda: messagebox.showerror("Error", error_message))
                logging.error(error_message)
            finally:
                self.after(0, lambda: self.update_download_status("SA Remix download complete"))
                self.after(0, lambda: self.enable_button(self.update1))
                self.after(0, lambda: self.update1_status.configure(text="Update complete"))
                logging.info("Update of SA Remix completed")
                if event:
                    event.set()

        threading.Thread(target=download_thread).start()

    def Download_SARemix_Necessary_Mods(self, event=None):
        def download_thread():
            if not self.folder_selected:
                self.after(0, lambda: messagebox.showwarning("Warning", "Please select a directory first."))
                return

            self.after(0, lambda: self.update_download_status("Downloading SA Remix Necessary Mods"))
            self.after(0, lambda: self.disable_button(self.update2))
            self.after(0, lambda: self.update2_status.configure(text="Updating"))
            
            try:
                owner = "KCDQYaniss"
                repo = "SA-Remix-necessary-mods"
                self.download_and_extract_release(owner, repo, "test.zip", "SA Remix necessary mods", self.update2)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                logging.error(f"An error occurred: {str(e)}")
            finally:
                self.after(0, lambda: self.update_download_status("SA Remix Necessary Mods download complete"))
                self.after(0, lambda: self.enable_button(self.update2))
                self.after(0, lambda: self.update2_status.configure(text="Update complete"))
                logging.info("Update of SA Remix necessary mods completed")
                if event:
                    event.set()

        threading.Thread(target=download_thread).start()

    def Download_RTX_Remix(self, owner, repo, event=None):
        def download_thread():
            self.after(0, lambda: self.update_download_status("Downloading RTX Remix"))
            if not self.folder_selected:
                messagebox.showwarning("Warning", "Please select a directory first.")
                return

            self.disable_button(self.update_rtx_remix)
            self.after(0, lambda: self.update_rtx_remix_status.configure(text="Updating"))
            try:
                response = self.session.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest")

                if response.status_code == 200:
                    data = response.json()
                    assets = data.get('assets', [])
                    remix_asset = next((asset for asset in assets if re.match(r'remix-\d+\.\d+\.\d+-release\.zip', asset['name'])), None)
                    
                    if remix_asset:
                        download_url = remix_asset['browser_download_url']
                        file_name = remix_asset['name']
                        
                        file_response = self.session.get(download_url, stream=True)
                        if file_response.status_code == 200:
                            file_path = os.path.join(self.folder_selected, file_name)
                            total_size = int(file_response.headers.get('content-length', 0))
                            self.download_file(download_url, file_path, total_size)
                                                        
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                zip_ref.extractall(self.folder_selected)
                            
                            os.remove(file_path)
                            
                            self.after(0, lambda: messagebox.showinfo("Success", "RTX Remix downloaded and extracted successfully."))
                            logging.info("RTX Remix downloaded and extracted successfully.")
                        else:
                            self.after(0, lambda: messagebox.showerror("Error", f"Failed to download RTX Remix: {file_response.status_code}"))
                            logging.error(f"Failed to download RTX Remix: {file_response.status_code}")
                    else:
                        self.after(0, lambda: messagebox.showerror("Error", "Failed to find RTX Remix asset in the latest release."))
                        logging.error("Failed to find RTX Remix asset in the latest release.")
                else:
                    self.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch release information: {response.status_code}"))
                    logging.error(f"Failed to fetch release information: {response.status_code}")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
                logging.error(f"An error occurred: {str(e)}")
            finally:
                self.after(0, lambda: self.update_download_status("RTX Remix download complete"))
                self.after(0, lambda: self.enable_button(self.update_rtx_remix))
                self.after(0, lambda: self.update_rtx_remix_status.configure(text="Update complete"))
                logging.info("Update of RTX Remix completed")
                if event:
                    event.set()

        threading.Thread(target=download_thread).start()

    def Download_all(self):
        if not self.folder_selected:
            messagebox.showwarning("Warning", "Please select a directory first.")
            return

        self.disable_buttons()
        self.reset_progress_bar()
        self.reset_download_status()

        def download_all_thread():
            try:
                self.after(0, lambda: self.update_download_status("Downloading all components"))
                self.after(0, lambda: self.update1_status.configure(text="Waiting for download"))
                self.after(0, lambda: self.update2_status.configure(text="Waiting for download"))
                self.after(0, lambda: self.update_rtx_remix_status.configure(text="Waiting for download"))
                
                sa_remix_event = Event()
                necessary_mods_event = Event()
                rtx_remix_event = Event()

                self.Download_SARemix(sa_remix_event)
                sa_remix_event.wait()

                self.Download_SARemix_Necessary_Mods(necessary_mods_event)
                necessary_mods_event.wait()

                self.Download_RTX_Remix("NVIDIAGameWorks", "rtx-remix", rtx_remix_event)
                rtx_remix_event.wait()

                self.after(0, lambda: self.update_download_status("All downloads completed"))
                self.after(0, lambda: messagebox.showinfo("Success", "All components downloaded and extracted successfully."))
                logging.info("All components downloaded and extracted successfully.")
            except Exception as e:
                self.after(0, lambda: self.update_download_status("Download failed"))
                self.after(0, lambda: messagebox.showerror("Error", f"An error occurred during the download process: {str(e)}"))
                logging.error(f"An error occurred during the download process: {str(e)}")
            finally:
                self.after(0, lambda: self.enable_buttons())
                self.after(0, lambda: self.update1_status.configure(text="Update complete"))
                self.after(0, lambda: self.update2_status.configure(text="Update complete"))
                self.after(0, lambda: self.update_rtx_remix_status.configure(text="Update complete"))

        threading.Thread(target=download_all_thread).start()

if __name__ == "__main__":
    app = SARemixInstaller()
    app.mainloop()