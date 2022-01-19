import os
import pathlib
import shutil
import json

def get_forge_or_fabric_version_from_manifest(path):
    with open(path, encoding="UTF-8") as f:
        data = json.load(f)
        modloaders = (data["minecraft"]["modLoaders"])
        minecraft_version = data["minecraft"]["version"]
        for modloader in modloaders:
            if modloader["primary"] == True:

                if "fabric" in modloader["id"].lower():
                    #return "fabric", minecraft_version + "-" + modloader["id"][7:]
                    return "fabric", minecraft_version

                if "forge" in modloader["id"].lower():
                    return "forge", minecraft_version + "-" + modloader["id"][6:]


#print(get_forge_or_fabric_version_from_manifest("manifest-fabric.json"))

