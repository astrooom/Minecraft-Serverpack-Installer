import os
from os.path import join
from os import listdir
import subprocess
from time import sleep
import glob
from shutil import move, rmtree, copy
from get_modpack_info import get_server_modpack_url, get_modpack_minecraft_version
from get_forge_or_fabric_version import get_forge_or_fabric_version_from_manifest
from download_modrinth_mods import download_modrinth_mods, move_modrinth_overrides, grab_modrinth_serverjars
from download_file import download, download_wget
from unzip_modpack import unzip
from serverstarter_func import change_installpath
import psutil
import pathlib
import platform
import sys
import argparse

parser = argparse.ArgumentParser(
    description="Set options for modpack installer.")

# Required arguments
# Provider modes: "curse", "technic", "ftb", "modrinth", and "direct".
parser.add_argument("-provider", type=str, required=True)
# if provider is curse, provide curse modpack ID. If technic, provide technic modpack slug. If ftb, provide modpack ID. If modrinth provide modpack slug or modpack project ID. If direct, provide direct download url.
parser.add_argument("-modpack-id", type=str, required=True)

# Version to match. Can be an ID or a version name. Will not work with provider direct.
parser.add_argument("--modpack-version", type=str,
                    default=False, action="store")
# pterodactyl mode will move the modpack files into a folder named modpack_folder regardless of modpack.
parser.add_argument("--pterodactyl", default="normal", action="store_true")
# If to clean (remove) the provided startup scripts (.sh for linux and .bat for Windows) when installing the server modpack.
parser.add_argument("--clean-scripts", default=False, action="store_true")
# If to remove the /mods, /.fabric and /libraries folders before installing the modpack. This should be set if updating a modpack and not set if it's a first-time install.
parser.add_argument("--update", default=False, action="store_true")
# Set predefined name of output folder (does not work with pterodactly mode)
parser.add_argument("--folder-name", default=False, type=str, action="store")
# Set working path where modpack should download and install
parser.add_argument("--working-path", default=False, type=str, action="store")

args = parser.parse_args()

provider = args.provider
modpack_id = args.modpack_id
mode = args.pterodactyl
if mode == True:
    mode = "pterodactyl"
modpack_version = args.modpack_version
output = args.folder_name
working_path = args.working_path
clean_startup_script = args.clean_scripts
remove_old_files = args.update

interpreter_path = sys.executable
if provider == "curse" or provider == "technic" or provider == "ftb" or provider == "modrinth":
    minecraft_version = str(
        get_modpack_minecraft_version(provider, modpack_id))
    if minecraft_version == False:
        minecraft_version = "unknown"
elif provider == "direct":
    minecraft_version = "unknown"

print("Installer running in", mode, "mode.")
print("Fetching modpack from", provider + ".")
print("Received arguments to download modpack with ID", modpack_id, "from provider",
        provider, "with version", modpack_version, "using minecraft version", minecraft_version)

# Checks OS to know which install file to execute (.bat or .sh)
operating_system = platform.system()
print("Detected OS", operating_system)
architecture = platform.machine()
print("Detected Architecture", architecture)

if working_path:
    this_dir = working_path
    os.chdir(working_path)
else:
    this_dir = os.path.dirname(os.path.realpath(__file__))


def up_one_directory(root, parent):
    for filename in os.listdir(join(root, parent)):
        try:
            if os.path.isfile(join(root, filename)):
                os.remove(join(root, filename))
                print("Replaced Already Existing File:", filename)
            if os.path.isdir(join(root, filename)):
                delete_tree_directory(join(root, filename))
                print("Replaced Already Existing Folder:", filename)
        except:
            pass
        move(join(root, parent, filename), join(root, filename))
    sleep(2)


def delete_directory(dir):
    os.rmdir(dir)
    print("Deleted directory in:", dir)


def delete_tree_directory(dir):
    rmtree(dir)
    print("Deleted tree directory in:", dir)


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
    sleep(3)

# -EXAMPLE MODPACK PROJECT (Addon) IDs on CurseForge-
# SevTech_Ages_of_the_Sky = 403521
# All_the_Mods_6 = 381671
# SkyFactory_4 = 296062
# Roguelike_Adventures_And_Dungeons = 289267
# #The_Pixelmon_Modpack = 389615 #Technic Serverpack
# MC_Eternal = 349129
# Enigmatica_6 = 389471
# Dungeons_Dragons_And_Space_Shuttles = 301717
# Life_In_The_Village_2 = 402412
# Zombie_Apocalypse = 445369
# Better_Minecraft_Forge = 429793
# Better_Minecraft_Fabric = 452013
# #FTB_Revelation = 283861 #FTB Serverpack


modpack_info = get_server_modpack_url(
    provider, modpack_id, modpack_version, operating_system, architecture)
if modpack_info:
    modpack_name = modpack_info[0]
    modpack_urls = modpack_info[1]
    modpack_normal_downloadurl = modpack_info[2]
else:
    print("Modpack info not provided. Exiting.")
    sys.exit()

print(modpack_info)

# print(modpack_urls)
# Grab URLs to modpack and download
if (modpack_urls["SpecifiedVersion"]):
    print("Downloading Specified Version of", modpack_name + "...")
    if provider == "ftb":
        filename = download_wget(modpack_urls["SpecifiedVersion"])
    else:
        filename = download(modpack_urls["SpecifiedVersion"])

elif (modpack_urls["LatestReleaseServerpack"]):
    print("Downloading Latest Release of", modpack_name + "...")
    if provider == "ftb":
        filename = download_wget(modpack_urls["LatestReleaseServerpack"])
    else:
        filename = download(modpack_urls["LatestReleaseServerpack"])

elif not modpack_urls["LatestReleaseServerpack"] and modpack_urls["LatestBetaServerpack"]:
    print("Downloading Latest Beta of", modpack_name + "...")
    if provider == "ftb":
        filename = download_wget(modpack_urls["LatestBetaServerpack"])
    else:
        filename = download(modpack_urls["LatestBetaServerpack"])

elif not modpack_urls["LatestReleaseServerpack"] and not modpack_urls["LatestBetaServerpack"] and modpack_urls["LatestAlphaServerpack"]:
    print("Downloading Latest Alpha of", modpack_name + "...")
    if provider == "ftb":
        filename = download_wget(modpack_urls["LatestAlphaServerpack"])
    else:
        filename = download(modpack_urls["LatestAlphaServerpack"])

elif not modpack_urls["LatestReleaseServerpack"] and not modpack_urls["LatestBetaServerpack"] and not modpack_urls["LatestAlphaServerpack"] and modpack_urls["LatestReleaseNonServerpack"]:
    print("Downloading Latest Non-Serverpack of", modpack_name + "...")
    if provider == "ftb":
        filename = download_wget(modpack_urls["LatestReleaseNonServerpack"])
    else:
        filename = download(modpack_urls["LatestReleaseNonServerpack"])

file_ext = pathlib.Path(filename).suffix

# For Modrinth modpacks.
if file_ext == '.mrpack':
    print("Detected modpack with .mrpack extension. Renaming to .zip...")
    move(filename, filename.replace('.mrpack', '.zip'))
    filename = filename.replace('.mrpack', '.zip')

if "?" in file_ext:
    new_file_ext = file_ext.partition(".zip")[1]
    new_filename = filename.replace(file_ext, new_file_ext)
    print("Renaming", filename, "to", new_filename)
    move(filename, new_filename)
    filename = new_filename

sleep(2)

if provider == "ftb":
    modpack_name = modpack_name.replace(
        ":", "_").replace(" ", "_").replace(",", "")
    if output:
        folder_name = output
    else:
        folder_name = modpack_name
    if os.path.isdir(this_dir + "/" + folder_name):
        delete_tree_directory(this_dir + "/" + folder_name)
    os.mkdir(this_dir + "/" + folder_name)
    move(filename, this_dir + "/" + folder_name + "/" + filename)
    os.chdir(f"{this_dir}/{folder_name}")

    if operating_system == "Linux":
        os.system(f"chmod +x {filename}")
    p = subprocess.Popen(f"./{filename}", stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, shell=True)
    p.communicate(input=b"\n")
    try:
        p.wait(timeout=15)
    except subprocess.TimeoutExpired:
        print("Timeout reached for binary subprocess. Killing.")
        kill(p.pid)
    print("Removing FTB server install binary")
    os.remove(filename)


# Unzip downloaded modpack zip
else:
    print("Extracting downloaded modpack archive...")
    folder_name = unzip(filename, modpack_name, file_ext, this_dir, output=output)
    print(folder_name)

    modpack_folder = os.listdir(join(this_dir, folder_name))

    # Count number of files
    file_count = 0
    for modpack_file in modpack_folder:
        file_count += 1

    #print(filename[:-8].replace("+", " "))

    # Move subdirectory to main directory if zip file is double-foldered
    existing_subdir = False
    for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*"):
        if os.path.isdir(name):
            folder_list = listdir(name)
            for file in folder_list:
                # print(file)
                if (file.endswith(".sh") or file.endswith(".bat") or file == "mods") and file != "kubejs":
                    existing_subdir = True
                    existing_subdir_path = name

    if existing_subdir:
        print("Found nested folder, moving contents to parent directory...")
        #print(this_dir + "/" + folder_name + "/" + folder_name)
        subfolder_path = pathlib.PurePath(existing_subdir_path)
        subfolder_name = subfolder_path.name
        up_one_directory(this_dir + "/" + folder_name, this_dir +
                         "/" + folder_name + "/" + subfolder_name)
        sleep(2)
        delete_directory(this_dir + "/" + folder_name + "/" + subfolder_name)

    # Deletes existing libraries and user jvm args file (required for forge 1.17+)
    if remove_old_files == True:
        print("Update command enabled. Cleaning old mods and libraries...")
        for libraries in glob.glob(glob.escape(this_dir + "/") + "libraries"):
            print("Found and deleting old libraries folder",
                  libraries, ". Deleting")
            delete_tree_directory(libraries)
        for mods in glob.glob(glob.escape(this_dir + "/") + "mods"):
            print("Found and deleting old mods folder", mods, ". Deleting")
            delete_tree_directory(mods)
        for coremods in glob.glob(glob.escape(this_dir + "/") + "coremods"):
            print("Found and deleting old coremods folder",
                  coremods, ". Deleting")
            delete_tree_directory(coremods)
        for fabric_folder in glob.glob(glob.escape(this_dir + "/") + ".fabric"):
            print("Found and deleting old .fabric folder",
                  fabric_folder, ". Deleting")
            delete_tree_directory(fabric_folder)
        for user_jvm_args in glob.glob(glob.escape(this_dir + "/") + "user_jvm_args.txt"):
            print("Found and deleting old user_jvm_args", user_jvm_args)
            os.remove(user_jvm_args)
    else:
        print("Skipping deleting old server folders.")

    if provider == "modrinth":
        for name in glob.glob(this_dir + "/" + folder_name + "/" + "modrinth.index.json"):
            os.chdir(f"{this_dir}/{folder_name}")
            grab_modrinth_serverjars(name)
            mods_folder_exists = os.path.exists(
                f"{this_dir}/{folder_name}/mods")
            if not mods_folder_exists:
                os.mkdir(f"{this_dir}/{folder_name}/mods")

            os.chdir(f"{this_dir}/{folder_name}/mods")
            download_modrinth_mods(name)
            os.chdir(f"{this_dir}/{folder_name}")
        do_override = False
        for override in glob.glob(this_dir + "/" + folder_name + "/" + "overrides"):
            if override:
                do_override = True
        if do_override == True:
            move_modrinth_overrides(f"{this_dir}/{folder_name}")
            os.chdir(f"{this_dir}/{folder_name}")
            delete_tree_directory(
                this_dir + "/" + folder_name + "/" + "overrides")
    else:
        # Check if forge installer exists in serverpack dir. If does, run it.
        forge_installer = False
        for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*forge*installer*.jar"):
            if name:
                forge_installer = True
                if "1.12.2-14.23.5" not in name:
                    print("Changing Directory for included forge installer")
                    os.chdir(f"{this_dir}/{folder_name}")
                    print("Running Forge Installer. This may take a minute or two...")
                    os.system(f"java -jar {name} --installServer")
                    print("Finished running forge installer")
                    os.remove(name)
                    print("Removed forge installer")
                    try:
                        os.remove(name + ".log")
                        print("Removed forge installer log")
                    except:
                        pass
                if "1.12.2-14.23.5" in name:
                    print(
                        "Found outdated and broken version of Forge 1.12.2. Downloading newest.")
                    os.remove(name)
                    twelvetwoforge = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2860/forge-1.12.2-14.23.5.2860-installer.jar"
                    print("Changing Directory for downloading forge installer")
                    os.chdir(f"{this_dir}/{folder_name}")
                    forge_installer_dl = download(twelvetwoforge)
                    forge_installer_dl_path = os.path.join(
                        this_dir, folder_name, forge_installer_dl)
                    print("Running Forge Installer. This may take a minute or two...")
                    os.system(
                        f"java -jar {forge_installer_dl_path} --installServer")
                    os.remove(forge_installer_dl_path)
                    print("Removed forge installer")
                    try:
                        os.remove(forge_installer_dl_path + ".log")
                        print("Removed forge installer log")
                    except:
                        pass

        # Check if fabric installer exists in serverpack dir. If does, run it.
        fabric_installer = False
        for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*fabric*installer*.jar"):
            if name:
                fabric_installer = True
                print("Changing Directory for included fabric installer")
                os.chdir(f"{this_dir}/{folder_name}")
                print("Running Fabric Installer. This may take a minute or two...")
                # Downloads the minecraft server version as well with -downloadMinecraft
                os.system(f"java -jar {name} server -downloadMinecraft")
                print("Finished running fabric installer")
                os.remove(name)
                print("Removed fabric installer")
                try:
                    os.remove(name + ".log")
                    print("Removed fabric installer log")
                except:
                    pass
        renamed_serverjar = False
        if fabric_installer:
            try:
                move("server.jar", "vanilla.jar")
                print("Renamed server.jar to vanilla.jar")
            except:
                pass
            try:
                move("fabric-server-launch.jar", "server.jar")
                renamed_serverjar = True
                print("Renamed fabric-server-launch.jar to server.jar")
            except:
                pass
            try:
                os.system(
                    'echo serverJar=vanilla.jar > fabric-server-launcher.properties')
                print("Changed fabric-server-launcher jar to downloaded vanilla.jar")
            except:
                pass

        # Check if serverstarter installer exists in serverpack dir. If does, run it.
        serverstarter_installer = False
        serverstarter_fabric = False
        for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.yaml"):
            if name:
                serverstarter_installer = True
                serverstarter_installpath = f"{this_dir}/{folder_name}/"
                print("Changing serverstarter install path to modpack directory")
                # Changes the installpath of the serverstarter script to base directory instead of the default /setup
                change_installpath(name, serverstarter_installpath)

                if operating_system == "Windows":
                    file_ext = "*.bat"
                    print("Detected Windows Operating System")
                if operating_system == "Linux":
                    file_ext = "*.sh"
                    print("Detected Linux Operating System")
                if operating_system == "Mac OS":
                    file_ext = "*.sh"
                    print("Detected Mac OS Operating System")
                for file in glob.glob(this_dir + "/" + folder_name + "/" + f"{file_ext}"):
                    print("Changing Directory for serverstarter installer")
                    os.chdir(f"{this_dir}/{folder_name}")
                    print(
                        "Running Serverstarter Installer. This may take a minute or two...")
                    if file_ext == "*.sh":
                        os.system(f"chmod +x {file}")
                    p = subprocess.Popen(
                        f"{file}", stdout=subprocess.PIPE, shell=True)
                    for line in p.stdout:
                        print(line.decode())
                        if b"fabric-server-launch.jar" in line:
                            serverstarter_fabric = True
                        if b"The server installed successfully" in line or b"Done installing loader" in line or b"deleting installer" in line or b"EULA" in line or b"eula" in line:
                            # Terminates script when script has successfully installed all mods and forge files etc. and stops it from running the server
                            print("Got Installer Finished Message")
                            break
                    kill(p.pid)
                    print("Terminated serverstarter installer")
                    print("Deleting leftover serverstarter installer file")
                    os.remove(file)

        if serverstarter_fabric:
            try:
                move("server.jar", "vanilla.jar")
                print("Renamed server.jar to vanilla.jar")
            except:
                pass
            try:
                move("fabric-server-launch.jar", "server.jar")
                renamed_serverjar = True
                print("Renamed fabric-server-launch.jar to server.jar")
            except:
                pass
            try:
                os.system(
                    'echo serverJar=vanilla.jar > fabric-server-launcher.properties')
                print("Changed fabric-server-launcher jar to downloaded vanilla.jar")
            except:
                pass

        # Check if mods.csv file is found. If so, run its install script.
        mods_csv_installer = False
        if not forge_installer and not serverstarter_installer:
            for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.csv"):
                if name:
                    print("Detected mods.csv installer.")
                    mods_csv_installer = True
                    if operating_system == "Windows":
                        file_ext = "*.bat"
                        print("Detected Windows Operating System")
                    if operating_system == "Linux":
                        file_ext = "*.sh"
                        print("Detected Linux Operating System")
                for file in glob.glob(this_dir + "/" + folder_name + "/" + f"{file_ext}"):
                    if operating_system == "Linux":
                        os.system(f"chmod +x {file}")
                    print("Changing Directory for mods.csv installer")
                    os.chdir(f"{this_dir}/{folder_name}")
                    print(
                        "Running mods.csv installer. This may take a minute or two...")
                    p = subprocess.Popen(f"{file}", stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, shell=True)
                    p.communicate(input=b"\n")
                    try:
                        p.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        print(
                            "Timeout reached for mods.csv installer subprocess. Killing.")
                        kill(p.pid)
                    print("Removing mods.csv server installer")
                    os.remove(file)

        if (forge_installer or serverstarter_installer or fabric_installer) and not renamed_serverjar:
            server_jar_found = False
            for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*"):
                if "server.jar" in name:
                    print(name)
                    server_jar_found = True
                    sever_jar_path = name
            if server_jar_found:
                print("Found old server.jar file. Deleting.")
                os.remove(sever_jar_path)

        # If there is no forge, fabric or serverstarter installer, but a manifest.json file. Download the mods manually using a separate script.
        manifest_installer = False
        if not forge_installer and not serverstarter_installer and not mods_csv_installer:
            for name in glob.glob(this_dir + "/" + folder_name + "/" + "manifest.json"):
                if name:
                    manifest_installer = True
                    print("Running manifest installer...")
                    os.system(
                        f'''java -jar "{this_dir}/ModpackDownloader-cli-0.7.2.jar" -manifest "{this_dir}/{folder_name}/manifest.json" -folder "{this_dir}/{folder_name}/mods"''')

        # If there was no included forge/fabric or serverstarter installer, as well as no manifest.json provided in the serverpack, look for existing forge or fabric server jar. If they don't exist, get the manifest file and download the correct forge/fabric version and install it.
        server_jar_found = False
        if not forge_installer and not serverstarter_installer and not fabric_installer and not mods_csv_installer:
            print("Neither a forge installer or a serverstarter installer was found for the downloaded pack. Checking if forge/fabric jar already exists...")
            for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*"):
                if ".jar" in name.lower() and "minecraft" not in name.lower():
                    server_jar_found = True
                    print(
                        "Found Server Jar. Renaming it to server.jar if it has other name.")
                    sever_jar_path = name
                    move(sever_jar_path, (os.path.dirname(
                        sever_jar_path)) + '/server.jar')

            # if server_jar_found:
            #     print("Found old server.jar.")
            #     os.remove(sever_jar_path)

            modpack_jar_type = None
            if not server_jar_found:
                manifest_file_found = False
                print("No forge or fabric file found. Checking for manifest.json...")
                for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "manifest.json"):
                    if name:
                        manifest_file_found = True
                        print(
                            "Found manifest file in modpack folder. Grabbing forge or fabric version...")
                        grabbed_manifest_version = get_forge_or_fabric_version_from_manifest(
                            name)
                        modpack_jar_type = grabbed_manifest_version[0]
                        modpack_jar_version = grabbed_manifest_version[1]

                if not manifest_file_found:
                    if modpack_normal_downloadurl:
                        print(
                            "No manifest.json was found. Checking for it with normal downloadurl link...")
                        filename = download(modpack_normal_downloadurl)
                        if "?" in filename:
                            new_file_ext = file_ext.partition(".zip")[1]
                            new_filename = filename.replace(
                                file_ext, new_file_ext)
                            print("Renaming", filename, "to", new_filename)
                            move(filename, new_filename)
                            filename = new_filename
                        temp_folder = unzip(
                            filename, "manifest_check", file_ext, this_dir)
                        for name in glob.glob(glob.escape(this_dir + "/" + temp_folder + "/") + "manifest.json"):
                            if name:
                                print(
                                    "Found manifest.json file in normal (non-serverpack) folder. Grabbing forge or fabric version...")
                                grabbed_manifest_version = get_forge_or_fabric_version_from_manifest(
                                    name)
                                modpack_jar_type = grabbed_manifest_version[0]
                                modpack_jar_version = grabbed_manifest_version[1]
                                delete_tree_directory(
                                    this_dir + "/" + temp_folder)
                                print("Deleted temp folder")

                if modpack_jar_type:
                    if modpack_jar_type == "forge":
                        if "1.12.2-14.23.5" in modpack_jar_version:
                            print(
                                "Found outdated and broken version of forge 1.12.2. Downloading latest for 1.12.2 instead.")
                            forge_installer_url = 'https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2860/forge-1.12.2-14.23.5.2860-installer.jar'
                        else:
                            forge_installer_url = f'https://files.minecraftforge.net/maven/net/minecraftforge/forge/{modpack_jar_version}/forge-{modpack_jar_version}-installer.jar'
                        os.chdir(f"{this_dir}/{folder_name}")
                        filename = download(forge_installer_url)
                        for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + filename):
                            if name:
                                print(
                                    "Changing Directory to not-included forge installer")
                                os.chdir(f"{this_dir}/{folder_name}")
                                print(
                                    "Running Forge Installer. This may take a minute or two...")
                                os.system(
                                    f'java -jar "{name}" --installServer')
                                print("Finished running forge installer")
                                os.remove(name)
                                print("Removed forge installer")
                                try:
                                    os.remove(name + ".log")
                                    print("Removed forge installer log")
                                except:
                                    pass
                    elif modpack_jar_type == "fabric":
                        # ! Will manually have to be changed as there is no hosted link to always get the latest fabric loader
                        fabric_installer_url = 'https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.10.2/fabric-installer-0.10.2.jar'
                        os.chdir(f"{this_dir}/{folder_name}")
                        filename = download(fabric_installer_url)
                        for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + filename):
                            print(name)
                            if name:
                                print(
                                    "Changing Directory to not-included fabric installer")
                                os.chdir(f"{this_dir}/{folder_name}")
                                print(
                                    "Running Fabric Loader. This may take a minute or two...")
                                os.system(
                                    f'java -jar "{name}" server -mcversion {modpack_jar_version} -downloadMinecraft')
                                print("Finished running Fabric Loader")
                                os.remove(name)
                                print("Removed Fabric Loader jar")
                                try:
                                    move("server.jar", "vanilla.jar")
                                    print("Renamed server.jar to vanilla.jar")
                                except:
                                    pass
                                try:
                                    move("fabric-server-launch.jar", "server.jar")
                                    renamed_serverjar = True
                                    print(
                                        "Renamed fabric-server-launch.jar to server.jar")
                                except:
                                    pass
                                try:
                                    os.system(
                                        'echo serverJar=vanilla.jar > fabric-server-launcher.properties')
                                    print(
                                        "Changed fabric-server-launcher jar to renamed vanilla.jar")
                                except:
                                    pass


# Garbage files cleanup
print("Running garbage cleanup...")
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*installer.jar"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.log"):
    if name:
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*download.zip"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.yaml"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "serverstarter*"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*mods.csv"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*README*"):
    if name:
        print("Removing", name)
        os.remove(name)
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "overrides"):
    if name:
        print("Removing tree directory", name)
        delete_tree_directory(name)


# If set to true, script will delete provided server startup script (.sh for linux and .bat or .ps1 for Windows).
if clean_startup_script:
    print("Clean startup scripts enabled.")
    for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.sh"):
        if name:
            print("Removing", name)
            os.remove(name)
    for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.bat"):
        if name:
            print("Removing", name)
            os.remove(name)
    for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "*.ps1"):
        if name:
            print("Removing", name)
            os.remove(name)
# for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "manifest.json"):
#     if name:
#         print("Removing", name)
#         os.remove(name)

for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "forge*.jar"):
    if name:
        print("Renaming", name, "to server.jar")
        os.chdir(f"{this_dir}/{folder_name}")
        os.rename(name, "server.jar")

has_properties = False
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "server.properties"):
    if name:
        has_properties = True
        print("server.properties file already found. Skipping download.")
if not has_properties:
    try:
        os.chdir(f"{this_dir}/{folder_name}")
        print("No server.properties file was found. Downloading...")
        download(
            'https://raw.githubusercontent.com/parkervcp/eggs/master/minecraft/java/server.properties')
    except:
        pass

has_eula = False
for name in glob.glob(glob.escape(this_dir + "/" + folder_name + "/") + "eula.txt"):
    if name:
        has_eula = True
        print("eula.txt file already found. Skipping download.")
if not has_eula:
    try:
        os.chdir(f"{this_dir}/{folder_name}")
        print("No eula.txt file was found. Downloading...")
        download(
            "https://raw.githubusercontent.com/kaboomserver/server/master/eula.txt")
    except:
        pass

# Forge 1.17+ section with new startup mechanism for non-ptero (symlink after not moving files)
if not mode == "pterodactyl":
    new_forge_ver = False
    for user_jvm_args in glob.glob(glob.escape(this_dir + "/") + "user_jvm_args.txt"):
        if user_jvm_args:
            print("Detected user_jvm_args.txt file indicating newer forge version.")
            new_forge_ver = True
            if operating_system == "Linux":
                for name in glob.glob(glob.escape(this_dir + "/") + "run.sh"):
                    if name:
                        os.system(f"chmod +x {name}")
            for forge_ver_folder in glob.glob(glob.escape(this_dir + "/" + "libraries" + "/" + "net" + "/" + "minecraftforge" + "/" + "forge" + "/") + "*"):
                if forge_ver_folder:
                    forge_ver = os.path.basename(forge_ver_folder)
                    print("Forge version is:", forge_ver)

                    link_from = join(
                        this_dir, "libraries", "net", "minecraftforge", "forge", forge_ver, "unix_args.txt")
                    link_to = join(this_dir, "unix_args.txt")

                    print(
                        f"Creating symbolic link for unix_args.txt to root folder from {link_from} to {link_to}")

                    if operating_system == "Linux":
                        os.system(f"ln -sf {link_from} {link_to}")
                        #os.symlink(link_from, link_to)
                    # Requires enabling developer mode in windows 10.
                    elif operating_system == "Windows":
                        os.symlink(link_from, link_to)


if mode == "pterodactyl":
    # For Pterodactyl eggs only. Will move all modpack files into a folder called modpack_folder regardless of modpack downloaded.
    sleep(3)
    os.chdir(this_dir)
    try:
        os.mkdir("modpack_folder")
        print("Created modpack_folder")
    except:
        print("Modpack_folder already exists.")
    modpack_folder_files = os.listdir(join(this_dir, folder_name))
    for f in modpack_folder_files:
        sleep(1)
        if os.path.isdir:
            try:
                delete_tree_directory(join(this_dir, "modpack_folder", f))
            except:
                pass
        if os.path.isfile:
            try:
                os.remove(join(this_dir, "modpack_folder", f))
            except:
                pass
        try:
            move(join(this_dir, folder_name, f),
                 join(this_dir, "modpack_folder", f))
        except:
            sleep(2)
            move(join(this_dir, folder_name, f),
                 join(this_dir, "modpack_folder", f))
    delete_directory(join(this_dir, folder_name))

    # Done in egg install script instead.
    # os.system("rsync -a /mnt/server/modpack_folder/ /mnt/server/")
    # os.system("rm -rf /mnt/server/modpack_folder/*")
    # os.system("rm -r /mnt/server/modpack_folder")

    # Forge 1.17+ section with new startup mechanism for ptero (symlink after moving files)
    new_forge_ver = False
    for user_jvm_args in glob.glob(glob.escape(this_dir + "/") + "user_jvm_args.txt"):
        if user_jvm_args:
            print("Detected user_jvm_args.txt file indicating newer forge version.")
            new_forge_ver = True
            if operating_system == "Linux":
                for name in glob.glob(glob.escape(this_dir + "/") + "run.sh"):
                    if name:
                        os.system(f"chmod +x {name}")
            for forge_ver_folder in glob.glob(glob.escape(this_dir + "/" + "libraries" + "/" + "net" + "/" + "minecraftforge" + "/" + "forge" + "/") + "*"):
                if forge_ver_folder:
                    forge_ver = os.path.basename(forge_ver_folder)
                    print("Forge version is:", forge_ver)

                    link_from = join(
                        this_dir, "libraries", "net", "minecraftforge", "forge", forge_ver, "unix_args.txt")
                    link_to = join(this_dir, "unix_args.txt")

                    #print(f"Creating symbolic link for unix_args.txt to root folder from {link_from} to {link_to}")

                    if operating_system == "Linux":
                        os.system(f"ln -sf {link_from} {link_to}")
                        #os.symlink(link_from, link_to)
                    # Requires enabling developer mode in windows 10.
                    elif operating_system == "Windows":
                        os.symlink(link_from, link_to)

print("Finished downloading and installing modpack", modpack_name + "! :)")
