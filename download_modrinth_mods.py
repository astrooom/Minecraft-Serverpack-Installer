import os
from shutil import move
import json
from time import sleep
import requests

from download_file import download


def download_modrinth_mods(path):
    with open(path, encoding="UTF-8") as f:
        data = json.load(f)
        print("Starting download of modrinth modpack server mods...")
        for mod in data['files']:
            try:
                mod_filename = os.path.basename(mod['path'])
            except:
                mod_filename = "Undefined Name"
            if mod['env']:
                if mod['env']['server']:
                    if mod['env']['server'] == "unsupported":
                        print(
                            f"Detected unsupported server mod {mod_filename}. Skipping download.")
                        continue
            if mod['downloads']:
                download(mod['downloads'][0])

        sleep(1)
        print("Finished downloading all server mods for modrinth modpack.")


def move_modrinth_overrides(modpack_folder):
    overrides_files = os.listdir(f"{modpack_folder}/overrides")
    for f in overrides_files:
        sleep(1)
        print(f"Moving modpack override {f}")
        move(f"{modpack_folder}/overrides/{f}", f"{modpack_folder}/{f}")


def grab_modrinth_serverjars(path):
    with open(path, encoding="UTF-8") as f:
        data = json.load(f)

        print("Starting download of modpack server jars.")

        dependencies = data['dependencies']
        dependency_names = []
        for key, value in dependencies.items():
            dependency_names.append(key)
        if 'minecraft' in dependency_names:
            minecraft_version = dependencies['minecraft']

            if "forge" not in dependency_names:
                launchermeta_url = f"https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
                HEADERS = {
                    'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'), }

                launchermeta_response = requests.get(
                    launchermeta_url, timeout=10, headers=HEADERS).json()
                for version in launchermeta_response['versions']:
                    if version['id'] == minecraft_version:
                        print(
                            f"Found minecraft version {version['id']}. Preparing to download this minecraft server jar...")
                        launchermeta_specifiedversion_url = version["url"]

                        launchermeta_specifiedversion_response = requests.get(
                            launchermeta_specifiedversion_url, timeout=10, headers=HEADERS).json()

                        minecraft_version_downloads = launchermeta_specifiedversion_response[
                            "downloads"]

                        for dkey, dvalue in minecraft_version_downloads.items():
                            if dkey == "server":
                                serverjar_downloadurl = dvalue['url']
                                vanilla_jar_filename = download(
                                    serverjar_downloadurl)
                                sleep(1)
                                move(vanilla_jar_filename, 'vanilla.jar')

        if "fabric-loader" in dependency_names:
            fabric_loader_version = dependencies['fabric-loader']
            print(
                f"Found Fabric version {fabric_loader_version}. Preparing to download and install this Fabric server jar...")
            fabric_installer_url = 'https://maven.fabricmc.net/net/fabricmc/fabric-installer/0.10.2/fabric-installer-0.10.2.jar'
            fabric_installer_filename = download(fabric_installer_url)
            sleep(1)
            os.system(
                f"java -jar {fabric_installer_filename} server -loader {fabric_loader_version}")
            move('fabric-server-launch.jar', 'server.jar')
            try:
                os.system(
                    'echo serverJar=vanilla.jar > fabric-server-launcher.properties')
                print(
                    "Changed fabric-server-launcher jar to downloaded vanilla.jar")
            except:
                pass

        if "forge" in dependency_names:
                forge_version = dependencies['forge']
                print(
                    f"Found Forge version {forge_version}. Preparing to download and install this Forge server jar...")
                forge_url = f'https://maven.minecraftforge.net/net/minecraftforge/forge/{minecraft_version}-{forge_version}/forge-{minecraft_version}-{forge_version}-installer.jar'
                forge_installer_filename = download(forge_url)
                print("Running Forge Installer. This may take a minute or two...")
                os.system(
                    f"java -jar {forge_installer_filename} --installServer")
                os.remove(forge_installer_filename)
                sleep(1)
