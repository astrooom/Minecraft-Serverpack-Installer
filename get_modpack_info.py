import requests
import json
import datetime
from dateutil import parser


def contains_number(value):
    if True in [char.isdigit() for char in value]:
        return True
    return False


#modpack_id = 381671

def get_server_modpack_url(provider, modpack_id, modpack_version, operating_system):

    if provider == "curse":

        # OLD CURSE API:
        #url = f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}'

        url = f'https://api.curseforge.com/v1/mods/{modpack_id}'

        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://www.curseforge.com/minecraft/modpacks',
                   'x-api-key': '$2a$10$Ynz1tT6cTV7vz1OUBS.lgOHanAXskT7KqCq6jXyRSGgk9DPA9mjEG',
                   }

        response = requests.get(url, timeout=10, headers=HEADERS).json()["data"]

        modpack_name = response["name"]

        files = response["latestFiles"]

        newest_date_release = parser.parse('2012-05-01 22:12:41.463000+00:00')
        newest_date_beta = parser.parse('2012-05-01 22:12:41.463000+00:00')
        newest_date_alpha = parser.parse(
            '2012-05-01 22:12:41.463000+00:00')  # Sets some random date

        release_serverpack_id = None
        beta_serverpack_id = None
        alpha_serverpack_id = None

        # print(response)

        # If the version is set by the user
        if modpack_version and modpack_version != "latest":
            for version in files:
                version_id = version["id"]
                # is_server_pack = version["isServerPack"]
                try:
                    server_pack_id = version["serverPackFileId"]
                except:
                    server_pack_id = 'someRandomValueBecauseSomeModpackVersionsDontHaveAServerPackId'
                display_name = version["displayName"]
                release_type = version["releaseType"]
                try:
                    normal_downloadurl = version["downloadUrl"]
                except:
                    normal_downloadurl = ""

                if modpack_version.isnumeric():
                    print("Matching version ID:", version_id,
                          "against goal:", modpack_version)
                    print("Matching serverpack version ID:",
                          server_pack_id, "against goal:", modpack_version)

                    if str(version_id) == str(modpack_version):
                        print("Found matching pack")
                        #/v1/mods/{modId}/files/{fileId}
                        version_id_downloadurl = requests.get(
                            # OLD CURSE API:
                            # f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{version_id}/download-url', timeout=10, headers=HEADERS).text
                            f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{version_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
                        urls = {"SpecifiedVersion": version_id_downloadurl, "LatestReleaseServerpack": "",
                                "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

                        return_list = [modpack_name.replace(
                            "  ", " "), urls, normal_downloadurl]
                        return return_list

                    elif str(server_pack_id) == str(modpack_version):
                        print("Found matching serverpack")
                        version_id_downloadurl = requests.get(
                            # OLD CURSE API:
                            # f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{server_pack_id}/download-url', timeout=10, headers=HEADERS).text
                            f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{server_pack_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
                        urls = {"SpecifiedVersion": version_id_downloadurl, "LatestReleaseServerpack": "",
                                "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

                        return_list = [modpack_name.replace(
                            "  ", " "), urls, normal_downloadurl]
                        return return_list

                if not modpack_version.isnumeric():
                    print(
                        "Could not match modpack version with id. Searching by version name instead.")

                    date = version["fileDate"]
                    date_obj = parser.isoparse(date)

                    normal_downloadurl = version["downloadUrl"]

                    server_pack_id = version["serverPackFileId"]

                    if (len(str(modpack_version)) > 2) and (modpack_version) in str(display_name):
                        try:
                            version_serverpack_url = requests.get(
                                # OLD CURSE API:
                                # f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{server_pack_id}/download-url', timeout=10, headers=HEADERS).text
                                f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{server_pack_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
                        except:
                            version_serverpack_url = None

                        if version_serverpack_url:
                            urls = {"SpecifiedVersion": version_serverpack_url, "LatestReleaseServerpack": "",
                                    "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}
                            return_list = [modpack_name.replace(
                                "  ", " "), urls, normal_downloadurl]

                            return return_list
            print(
                "This modpack version was not found. Defaulting to latest modpack version...")

        # If the version is set to latest or no version is provided by the user, find the latest release

        for version in files:
            #print(version, "\n")
            release_type = version["releaseType"]

            date = version["fileDate"]
            date_obj = parser.isoparse(date)

            normal_downloadurl = version["downloadUrl"]

            server_pack_id = version["serverPackFileId"]

            if (release_type == 1) and (date_obj > newest_date_release):
                newest_date_release = date_obj
                release_serverpack_id = server_pack_id

            if (release_type == 2) and (date_obj > newest_date_beta):
                newest_date_beta = date_obj
                beta_serverpack_id = server_pack_id

            if (release_type == 3) and (date_obj > newest_date_alpha):
                newest_date_alpha = date_obj
                alpha_serverpack_id = server_pack_id

        # print(release_serverpack_id)

        try:
            release_serverpack_url = requests.get(
                # OLD CURSE API:
                # f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{release_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
                f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{release_serverpack_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
        except:
            release_serverpack_url = None
            print("No release server pack was found for this modpack")

        try:
            beta_serverpack_url = requests.get(
                # OLD CURSE API:
                #f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{beta_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
                f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{beta_serverpack_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
        except:
            beta_serverpack_url = None
            print("No beta server pack was found for this modpack")

        try:
            alpha_serverpack_url = requests.get(
                # OLD CURSE API:
                #f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{alpha_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
                f'https://api.curseforge.com/v1/mods/{modpack_id}/files/{alpha_serverpack_id}/download-url', timeout=10, headers=HEADERS).json()["data"]
        except:
            alpha_serverpack_url = None
            print("No alpha server pack was found for this modpack")

        # If modpack has no server pack choose the newest "client" pack
        non_serverpack_url = ''
        try:
            newest_date_release = parser.parse(
                '2012-05-01 22:12:41.463000+00:00')
            for version in files:
                release_type = version["releaseType"]
                date = version["fileDate"]
                date_obj = parser.isoparse(date)
                if (release_type == 1) and (date_obj > newest_date_release):
                    non_serverpack_url = version["downloadUrl"]
        except:
            non_serverpack_url = ''

        # print(non_serverpack_url)

        urls = {"SpecifiedVersion": "", "LatestReleaseServerpack": release_serverpack_url, "LatestBetaServerpack": beta_serverpack_url,
                "LatestAlphaServerpack": alpha_serverpack_url, "LatestReleaseNonServerpack": non_serverpack_url}

        return_list = [modpack_name.replace(
            "  ", " "), urls, normal_downloadurl]

        return return_list

    if provider == "technic":
        url = f"https://api.technicpack.net/modpack/{modpack_id}?build=729"
        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://www.technicpack.net/'}

        response = requests.get(url, timeout=10, headers=HEADERS).json()

        modpack_name = response["displayName"]

        serverpack_url = response["serverPackUrl"]

        if not serverpack_url.endswith(".zip"):
            print("This modpack does not provide a direct download URL to it's serverpack on the Technic website. It has provided a link to an external website. This modpack therefore has to be installed manually. Sorry!")
            return False

        if modpack_version and modpack_version != "latest":
            try:
                url_split = serverpack_url.rsplit("/", 1)
                url_lastpart = url_split[-1]
                url_filename = url_lastpart.rsplit('.', 1)[0]
                url_extension = '.' + url_lastpart.rsplit('.', 1)[-1]
                url_link = url_split[0]

                #url_filename_version = url_filename.rsplit("_", 1)[-1]
                url_filename_noversion = url_filename.rsplit("_", 1)[0]

                # print(url_link, url_filename, url_extension, url_filename_noversion)

                version_id_downloadurl = url_link + "/" + \
                    url_filename_noversion + "_v" + modpack_version + url_extension

                # Check if url is valid
                response_test = requests.head(
                    version_id_downloadurl, timeout=10, headers=HEADERS)
                status_code = response_test.status_code
                if not (400 <= int(status_code) <= 500):
                    print("Constructed version URL",
                          version_id_downloadurl, "is valid.")
                    urls = {"SpecifiedVersion": version_id_downloadurl, "LatestReleaseServerpack": "",
                            "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

                    normal_downloadurl = ""
                    return_list = [modpack_name.replace(
                        "  ", " "), urls, normal_downloadurl]
                    return return_list
                else:
                    print(
                        "Constructed version URL is invalid. Defaulting to recommended instead.")
                    pass
            except:
                print("This modpack version was not found or an error appeared while fetching it's download link. Defaulting to latest modpack version...")
                pass

        urls = {"SpecifiedVersion": "", "LatestReleaseServerpack": serverpack_url,
                "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

        normal_downloadurl = ""
        return_list = [modpack_name.replace(
            "  ", " "), urls, normal_downloadurl]

        return return_list

    if provider == "ftb":
        url = f"https://api.modpacks.ch/public/modpack/{modpack_id}"
        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://api.modpacks.ch/'}

        response = requests.get(url, timeout=10, headers=HEADERS).json()

        modpack_name = response["name"]

        if modpack_version and modpack_version != "latest":
            for version in response["versions"]:
                if str(version["id"]) == str(modpack_version):
                    serverbinary_url = f"https://api.modpacks.ch/public/modpack/{modpack_id}/{modpack_version}/server/{operating_system.lower()}"

            urls = {"SpecifiedVersion": serverbinary_url, "LatestReleaseServerpack": "",
                    "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}
            normal_downloadurl = ""
            return_list = [modpack_name.replace(
                "  ", " "), urls, normal_downloadurl]

            return return_list

        version_id_release = False
        version_id_beta = False
        version_id_alpha = False
        find_version = False
        while not find_version:
            for version in reversed(response["versions"]):
                if version['type'].lower() == "release":
                    version_id_release = version["id"]
                    find_version = True

            for version in reversed(response["versions"]):
                if version['type'].lower() == "beta":
                    version_id_beta = version["id"]
                    find_version = True

            for version in reversed(response["versions"]):
                if version['type'].lower() == "alpha":
                    version_id_alpha = version["id"]
                    find_version = True
        find_version = True

        if version_id_release:
            release_serverbinary_url = f"https://api.modpacks.ch/public/modpack/{modpack_id}/{version_id_release}/server/{operating_system.lower()}"
        else:
            release_serverbinary_url = ""
        if version_id_beta:
            beta_serverbinary_url = f"https://api.modpacks.ch/public/modpack/{modpack_id}/{version_id_beta}/server/{operating_system.lower()}"
        else:
            beta_serverbinary_url = ""
        if version_id_alpha:
            alpha_serverbinary_url = f"https://api.modpacks.ch/public/modpack/{modpack_id}/{version_id_alpha}/server/{operating_system.lower()}"
        else:
            alpha_serverbinary_url = ""

        urls = {"SpecifiedVersion": "", "LatestReleaseServerpack": release_serverbinary_url, "LatestBetaServerpack":
                beta_serverbinary_url, "LatestAlphaServerpack": alpha_serverbinary_url, "LatestReleaseNonServerpack": ""}
        normal_downloadurl = ""
        return_list = [modpack_name.replace(
            "  ", " "), urls, normal_downloadurl]
        return return_list

    if provider == "direct":
        urls = {"SpecifiedVersion": modpack_id, "LatestReleaseServerpack": "",
                "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

        modpack_name = (modpack_id.rsplit('/', 1)[-1])
        if modpack_name.endswith(".zip"):
            modpack_name = modpack_name.replace(".zip", "")

        normal_downloadurl = ""
        return_list = [modpack_name.replace(
            "  ", " "), urls, normal_downloadurl]
        return return_list

#print(get_server_modpack_url("technic", 'tekkit-legends', "latest"))


def get_modpack_minecraft_version(provider, modpack_id):
    if provider == "curse":
        # OLD CURSE API:
        # url = f"https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}"
        url = f'https://api.curseforge.com/v1/mods/{modpack_id}'

        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://www.curseforge.com/minecraft/modpacks',
                   'x-api-key': '$2a$10$Ynz1tT6cTV7vz1OUBS.lgOHanAXskT7KqCq6jXyRSGgk9DPA9mjEG',
                   }

        response = requests.get(url, timeout=10, headers=HEADERS).json()["data"]

        try:
            latest_file = response["latestFilesIndexes"][0]
            return latest_file['gameVersion']
        except:
            print("Could not obtain minecraft version for this modpack. Returning False")
            return False

    if provider == "technic":
        main_url = f"https://solder.technicpack.net/api/modpack/{modpack_id}"
        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://www.technicpack.net/'}

        try:
            main_response = requests.get(
                main_url, timeout=10, headers=HEADERS).json()
            main_response["name"]
        except:
            print("This modpack does not exist on Technic Solder. Attempting to get version from main API instead...")
            try:
                fallback_url = f'https://api.technicpack.net/modpack/{modpack_id}?build=729'
                fallback_response = requests.get(
                    fallback_url, timeout=10, headers=HEADERS).json()
                game_version = fallback_response["minecraft"]
                print("Got minecraft version", game_version)
                return game_version
            except:
                print(
                    "Could not obtain recommended build version for this modpack. Returning False")
                return False

        try:
            recommended_build = main_response["recommended"]
        except:
            print(
                "Could not obtain recommended build version for this modpack. Returning False")
            return False
        build_url = f"https://solder.technicpack.net/api/modpack/{modpack_id}/{recommended_build}"

        build_response = requests.get(
            build_url, timeout=10, headers=HEADERS).json()
        try:
            game_version = build_response["minecraft"]
            return game_version
        except:
            print("Could not get Minecraft version for this modpack. Returning False")
            return False

    if provider == "ftb":
        url = f"https://api.modpacks.ch/public/modpack/{modpack_id}"
        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                   'referer': 'https://feed-the-beast.com/'}

        response = requests.get(url, timeout=10, headers=HEADERS).json()

        versions = response["versions"]
        versions_len = len(versions)

        index = 1
        game_version = False
        while not game_version:
            for versions in versions[versions_len - index]["targets"]:
                if versions["name"].lower() == "minecraft":
                    game_version = versions["version"]
        index -= 1

        return game_version
