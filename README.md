# Minecraft Serverpack Downloader and Installer

This is a Python script made to automatically download and install Minecraft modpacks from 
Curseforge, Technicpack (or a direct download link) as intended by the modpack author. Serverpacks provided for modpacks by their authors come in very different kinds, with many different installers. This is an attempt to unify the installation of all serverpacks (for both Forge and Fabric) as the modpack author intended them to be. [Here's the kinds of serverpack installers the script works with](#installer-types). The script is extensively tested and should work with all modpacks on Curseforge.

#### The script will:
1. Download the modpacks serverpack (or non-serverpack) from the Curseforge Project ID, Technic modpack slug, or a direct download link (url). See details below.

2. Run any provided installers through a unification attempt that come with the serverpack if needed.

3. Remove garbage files.

After the installer is done, the modpack will be fully installed in a separate folder (named after the modpack itself) and ready to be started.

## Compatibility
OS: ```Windows```, ```Linux```  
The script works with both Forge and Fabric modpacks.

## Usage
### 1. Download and unarchive the repository into any directory you want

### 2. Install requirements.txt using ```pip install -r requirements.txt```

### 3. Run "run.py" from your terminal with specified [arguments](#arguments) like:
python run.py ```-provider PROVIDER``` ```-modpack-id MODPACK-ID``` ```[--modpack-version MODPACK-VERSION]``` ```[--pterodactyl]``` ```[--clean-scripts]``` ```[--update]```

### Done!

## Arguments
#### provider
Provider sets from where to fetch the modpack. Available modes are ```curse``` for Curseforge, ```technic``` from Technicpack, and ```direct``` for a direct download link (url) to a modpack (can be from any site).
#### modpack-id
If provider is set to ```curse``` this should be the modpacks project ID found on <a href="https://www.curseforge.com/minecraft/modpacks">the Curseforge website</a> in the top right "About Project" section of your desired modpack.

If provider is set to ```technic```, this should be the modpack slug found on <a href="https://www.technicpack.net/modpacks/official"> the Technicpack website</a>. In the url of each modpack. Fir example, the url for the Attack of the B-Team modpack is https://www.technicpack.net/modpack/attack-of-the-bteam.552556. The slug is the last part of this url minus the dot and the numbers (i.e attack-of-the-bteam).

If provider is set to ```direct```, this should be a direct download link (url), from where to fetch the modpack.
#### modpack-version (optional)
Which version of the modpack to install. Specify a version from the modpacks name. For example, <a href="https://www.curseforge.com/minecraft/modpacks/rlcraft">RLCraft</a> names their releases like "v.2.9", "v.2.8.2" etc. (as you can see by going to the "Files" section). Here, you can use "v.2.8.2" to pull that version. You can also use an exact version ID from Curseforge. For Technic, versions are labeled as "builds" instead of versions. This option is not available if provider is set to ```direct```. If left unspecified, the installer will fetch the latest recommended version of the modpack.

In conjunction with Curseforges' release type system, if no "recommended" version exists, it will pull the latest "beta" serverpack. If no "beta" version exists it will pull the latest "alpha" serverpack. If the modpack has no provided serverpack at all it will pull the latest non-serverpack in the same order. For technic, all modpacks have a recommended version.
#### clean-scripts (optional)
Set to clean (remove) the provided startup scripts (.sh for linux and .bat for Windows) when installing the modpack.
#### update (optional)
Set to remove the /mods, /.fabric and /libraries folders before installing the modpack. This should be set if updating a modpack and not set if it's a first-time install.

#### pterodactyl (optional)
Pterodactyl is intended to use in conjunction with a pterodactyl egg install script ([More details on this](#pterodactyl-mode)).

## Installer types
There is currently no standardization in how serverpacks are uploaded on Curseforge. 
* Some serverpacks include **all** required files to run the server by default
* Some require Forge or Fabric to be installed separately with only the mods and libraries folders included
* Some for mods to be downloaded using the [ServerStarter script by BloodyMods](https://github.com/BloodyMods/ServerStarter) or the somewhat standardized manifest.json file. 

This script is compatible with all different types of installers by identifying and running them as tasks separately if needed. The advantage of using this script over other scripts is that it downloads and installs the serverpack as intended by the modpack author, keeping certain files that they have included which, were the mods installed in any other way, would not have been included. 

The modpack author may, for example, have made modifications to the server.properties file or any mod config file. These modifications would not be carried over using another way of installing the modpack.

For technic, contrary to curse, modpacks are standardized to include all files required to start the server.

## Pterodactyl Mode
The script can also run in the optional ```--pterodactyl``` mode. Pterodactyl mode is intended to be used in conjunction with popular Game Server Panel software [Pterodactyl Panel](https://github.com/pterodactyl/panel) in an egg install script (in bash). Currently, this mode will move the files directly to the root folder of the installation script instead of the modpack installing in it's own subfolder.

## Requirements
```Python 3.7+``` (Might work on earlier versions of python as well - not tested.)  
```python3-pip```  
```Java (11 or later)``` (for Forge/Fabric installers)
