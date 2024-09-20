import os
import shutil
import subprocess
import threading
from pathlib import Path
from tkinter import Tk, filedialog, messagebox, Label, StringVar, ttk, Button, Frame
import re
import requests
import zipfile

# Global repository URLs
repo1 = "https://github.com/Hemry81/GTASA-Remix"
repo2 = "https://github.com/KCDQYaniss/SA-Remix-necessary-mods"

# Function to update the progress bar and label from git output
def update_progress(line, progress_var, progress_bar):
    match = re.search(r'(\d+)%', line)
    if match:
        progress = int(match.group(1))
        progress_var.set(f"Cloning: {progress}%")
        progress_bar['value'] = progress
        root.update_idletasks()

# Function to delete specific files from the target directory
def delete_unwanted_files(target_dir):
    files_to_delete = ['.gitattributes', '.gitignore', 'LICENSE', 'README.md']
    for file_name in files_to_delete:
        file_path = Path(target_dir) / file_name
        if file_path.exists():
            try:
                os.remove(file_path)
                print(f"Deleted {file_name}")
            except Exception as e:
                print(f"Error deleting {file_name}: {e}")

def move_files(temp_dir, target_dir):
    for item in os.listdir(temp_dir):
        src = os.path.join(temp_dir, item)
        dst = os.path.join(target_dir, item)

        if os.path.isdir(src):
            if os.path.exists(dst) and os.path.isdir(dst):
                for file in os.listdir(src):
                    file_src = os.path.join(src, file)
                    file_dst = os.path.join(dst, file)
                    if os.path.isdir(file_src):
                        if not os.path.exists(file_dst):
                            shutil.copytree(file_src, file_dst, dirs_exist_ok=True)
                        else:
                            move_files(file_src, file_dst)
                    else:
                        if os.path.exists(file_dst):
                            os.remove(file_dst)
                        shutil.move(file_src, file_dst)
            else:
                shutil.move(src, dst)
        else:
            if os.path.exists(dst):
                os.remove(dst)
            shutil.move(src, dst)

# Function to clone a repo and extract its contents into the target directory
def clone_and_extract_repo(repo_url, temp_dir, target_dir, progress_var, progress_bar):
    try:
        process = subprocess.Popen(['git', 'clone', '--no-checkout', '--progress', repo_url, temp_dir],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)

        for line in process.stderr:
            update_progress(line, progress_var, progress_bar)

        process.wait()

        if process.returncode == 0:
            subprocess.run(['git', '-C', temp_dir, 'checkout'], check=True)
            move_files(temp_dir, target_dir)
        else:
            raise subprocess.CalledProcessError(process.returncode, process.args)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error cloning {repo_url}: {e}")
        progress_var.set("Error during cloning.")
    except Exception as e:
        messagebox.showerror("Error", f"Error during file operations: {e}")
        progress_var.set("Error during file operations.")

# Function to download and extract the latest release of rtx-remix
def download_and_extract_latest_release(owner, repo, download_dir, progress_var, progress_bar):
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Error fetching release: {response.status_code} - {response.text}")

        release_data = response.json()
        assets = release_data.get("assets", [])

        if not assets:
            raise Exception(f"No assets found in the latest release of '{repo}'")

        for asset in assets:
            asset_name = asset["name"]
            if asset_name.endswith("release.zip"):
                asset_url = asset["browser_download_url"]
                print(f"Downloading {asset_name}...")
                download_asset(asset_url, download_dir, asset_name)
                print(f"Downloaded {asset_name} to {download_dir}")
                
                progress_var.set("Download complete!")
                progress_bar['value'] = 100
                return

        raise Exception(f"No asset ending with 'release.zip' found in the latest release of '{repo}'")

    except Exception as e:
        messagebox.showerror("Error", f"Error downloading the latest release: {e}")
        progress_var.set("Error during download.")

def download_asset(url, download_dir, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        os.makedirs(download_dir, exist_ok=True)
        file_path = os.path.join(download_dir, filename)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        print(f"Extracted {filename} to {download_dir}")

    else:
        raise Exception(f"Failed to download file: {response.status_code} - {response.text}")

def clone_and_extract_repositories():
    global temp1_dir, temp2_dir, directory, progress_var, progress_bar

    temp1_dir = Path(directory) / "temp_repo_1"
    temp2_dir = Path(directory) / "temp_repo_2"

    try:
        clone_and_extract_repo(repo1, temp1_dir, directory, progress_var, progress_bar)
        delete_unwanted_files(directory)
        clone_and_extract_repo(repo2, temp2_dir, directory, progress_var, progress_bar)
        delete_unwanted_files(directory)
        download_and_extract_latest_release("NVIDIAGameWorks", "rtx-remix", directory, progress_var, progress_bar)

    finally:
        if temp1_dir.exists():
            shutil.rmtree(temp1_dir, ignore_errors=True)
            print(f"Deleted temporary directory: {temp1_dir}")
        if temp2_dir.exists():
            shutil.rmtree(temp2_dir, ignore_errors=True)
            print(f"Deleted temporary directory: {temp2_dir}")

# Function to disable or enable all buttons
def set_button_state(state):
    download_button.config(state=state)
    update_button_repo1.config(state=state)
    update_button_repo2.config(state=state)
    update_button_rtx_remix.config(state=state)

# Function to update the repository
def update_repository(repo_url, target_dir, progress_var, progress_bar):
    temp_dir = Path(target_dir) / "temp_update_repo"
    os.makedirs(temp_dir, exist_ok=True)

    clone_and_extract_repo(repo_url, temp_dir, target_dir, progress_var, progress_bar)

    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"Deleted temporary directory: {temp_dir}")

# Update repository functions
def update_repo1():
    global directory, progress_var, progress_bar
    progress_var.set("Updating repo 1...")
    set_button_state('disabled')
    update_thread = threading.Thread(target=update_repository, args=(repo1, directory, progress_var, progress_bar))
    update_thread.start()
    
    def check_thread():
        if update_thread.is_alive():
            root.after(100, check_thread)
        else:
            set_button_state('normal')
            messagebox.showinfo("Update Complete", "Repo 1 has been updated successfully!")

    check_thread()

def update_repo2():
    global directory, progress_var, progress_bar
    progress_var.set("Updating repo 2...")
    set_button_state('disabled')
    update_thread = threading.Thread(target=update_repository, args=(repo2, directory, progress_var, progress_bar))
    update_thread.start()
    
    def check_thread():
        if update_thread.is_alive():
            root.after(100, check_thread)
        else:
            set_button_state('normal')
            messagebox.showinfo("Update Complete", "Repo 2 has been updated successfully!")

    check_thread()

def update_rtx_remix():
    global directory, progress_var, progress_bar
    progress_var.set("Updating RTX Remix...")
    set_button_state('disabled')
    update_thread = threading.Thread(target=download_and_extract_latest_release, args=("NVIDIAGameWorks", "rtx-remix", directory, progress_var, progress_bar))
    update_thread.start()
    
    def check_thread():
        if update_thread.is_alive():
            root.after(100, check_thread)
        else:
            set_button_state('normal')
            messagebox.showinfo("Update Complete", "RTX Remix has been updated successfully!")

    check_thread()

# Directory selection function
def select_directory():
    global directory
    directory = filedialog.askdirectory(title="Select Directory")
    if directory:
        directory_label.config(text=f"Selected Directory: {directory}")
    else:
        messagebox.showwarning("Warning", "No directory selected.")

# Start the download process on button click
def start_download():
    global directory

    if not directory:
        messagebox.showwarning("Warning", "Please select a directory first.")
        return

    target_path = Path(directory)
    if not target_path.exists():
        messagebox.showerror("Error", f"The directory {directory} does not exist.")
        return

    download_button.config(state="disabled")
    
    clone_thread = threading.Thread(target=clone_and_extract_repositories)
    clone_thread.start()

    def check_thread():
        if clone_thread.is_alive():
            root.after(100, check_thread)
        else:
            messagebox.showinfo("Success", "Repositories have been cloned and extracted successfully.")
            download_button.config(state="normal")

    check_thread()

# Create the welcome page
def create_welcome_page():
    global root, welcome_frame, main_frame

    root = Tk()
    root.title("SA Remix Auto-Installer")

    welcome_frame = Frame(root)
    welcome_frame.pack(fill='both', expand=True)

    Label(welcome_frame, text="  Welcome to SA Remix Auto-Installer !  ", font=("Helvetica", 16)).pack(pady=20)
    Label(welcome_frame, text="Made by Yaniss", font=("Helvetica", 12)).pack(pady=10)
    Label(welcome_frame, text="Download speed will depend on your internet, your disk speed and github speed.").pack(pady=5)

    Button(welcome_frame, text="Next", command=create_main_app_page).pack(pady=20)

# Create the main app page where cloning and directory selection happen
def create_main_app_page():
    global welcome_frame, main_frame, progress_var, progress_bar, directory_label, download_button
    global update_button_repo1, update_button_repo2, update_button_rtx_remix

    welcome_frame.pack_forget()

    main_frame = Frame(root)
    main_frame.pack(fill='both', expand=True)

    directory_label = Label(main_frame, text="No directory selected")
    directory_label.pack(pady=5)

    Button(main_frame, text="Select your GTA SA root folder", command=select_directory).pack(pady=5)

    download_button = Button(main_frame, text="Download and Install", command=start_download)
    download_button.pack(pady=20)

    update_button_repo1 = Button(main_frame, text="Update SA Remix (~6GB)", command=update_repo1)
    update_button_repo1.pack(pady=5)

    update_button_repo2 = Button(main_frame, text="Update Necessary Mods", command=update_repo2)
    update_button_repo2.pack(pady=5)

    update_button_rtx_remix = Button(main_frame, text="Update RTX Remix", command=update_rtx_remix)
    update_button_rtx_remix.pack(pady=5)

    progress_var = StringVar()
    progress_var.set("Waiting...")
    Label(main_frame, textvariable=progress_var).pack(pady=5)

    progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=300, mode='determinate')
    progress_bar.pack(pady=10)

# Main function to initialize the GUI
def main():
    create_welcome_page()
    root.mainloop()

if __name__ == "__main__":
    main()
