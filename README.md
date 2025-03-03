# SARemix-Installer
With the app you can go from a clean GTA SA install to a fully working remixed one with Hemry's and I mod + all necessary's mod to fix issues the game has when using remix and of course remix runtime.

For the remix runtime part, it just downloads the latest release stable version, if there is updates on the bridge or dxvk that are needed, it will need to be done by hand, this is more a way for people that just want to play to have a simpler access to all that complicated part of modding.

You can also update each of them separately.

Discord : yanisselt  or just come here https://discord.gg/rtxremix in GTA SA channel if you have any question about the app or the mod.

Enjoy the mod !

Thanks to :

DK22Pac for Pedspec and Improved Vehicle Features (ImVehFt)

ThirteenAG and Junior_Djjr for Essentials, Mixsets, Improved Streaming, OpenLimitAdjuster and VehFuncs

If any of you wants me to remove the mods from here or if I forgot someone in the credits, contact me on Discord : yanisselt

![screenshot](https://github.com/user-attachments/assets/b3adf851-30ef-406c-bdbb-36e53d9c60fc)


# SARemix Installer

An automated installer for SA Remix and RTX Remix.

## Development

### Requirements
- Python 3.10 or higher
- Dependencies listed in requirements.txt

### Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Building
The application is automatically built using GitHub Actions when pushing to the main branch.
You can find the latest build in the Actions tab under artifacts.

To build locally:
```bash
pyinstaller --noconfirm --onefile --windowed --add-data "7zip;7zip/" SARemix_InstallerV1.3.py
```

## Usage
1. Download the latest release from the Releases page
2. Run the executable
3. Follow the in-app instructions to install SA Remix and RTX Remix

Enjoy ! :) 