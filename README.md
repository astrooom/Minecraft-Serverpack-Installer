#Curseforge Serverpack Downloader and Installer

<p>
    This is a script made to automatically download and install Minecraft modpacks from <a
        href="https://curseforge.com" target="_blank">Curseforge</a> as intended by the modpack author. Serverpacks provided for modpacks by their authors come in very different format, and this is an attempt to unify the installation of all serverpacks (for both Forge and Fabric).
        <br>
        <br>
        The script will:
        1. Download the modpacks author-provided serverpack from the Curseforge Project ID (works with either the latest modpack version or a specified one)
        2. Run any provided installers through a unification attempt that come with the serverpack if needed.
        3. Remove garbage files.
</p>

## How to use
### 1. Download the repository
### 2. Run "run.py" with required arguments like:
```python run.py "mode" "modpack_id" "modpack_version" "clean_startup_script"```
#### mode
Available modes: ```normal``` and ```pterodactyl```
Normal is intended to use locally on your PC. Pterodactyl is intended to use in conjunction with a pterodactyl egg install script. If you do not know what this means, use "normal".