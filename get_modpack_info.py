import requests
import json
import datetime
from dateutil import parser

#modpack_id = 381671

def get_server_modpack_url(provider, modpack_id, modpack_version):

    if provider == "curse":

        url = f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}'


        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                                'referer': 'https://www.curseforge.com/minecraft/modpacks'}


        response = requests.get(url, timeout=10, headers=HEADERS).json()

        modpack_name = response["name"]

        files = response["latestFiles"]

        newest_date_release = parser.parse('2012-05-01 22:12:41.463000+00:00')
        newest_date_beta = parser.parse('2012-05-01 22:12:41.463000+00:00')
        newest_date_alpha = parser.parse('2012-05-01 22:12:41.463000+00:00') #Sets some random date

        release_serverpack_id = None
        beta_serverpack_id = None
        alpha_serverpack_id = None

        #print(response)



        #If the version is set by the user
        if modpack_version and modpack_version != "latest":
            for version in files:
                version_id = version["id"]
                display_name = version["displayName"]
                release_type = version["releaseType"]
                try:
                    normal_downloadurl = version["downloadUrl"]
                except:
                    normal_downloadurl = ""

                if str(version_id) == str(modpack_version):
                    version_id_downloadurl = requests.get(f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{version_id}/download-url', timeout=10, headers=HEADERS).text
                    urls = {"SpecifiedVersion": version_id_downloadurl, "LatestReleaseServerPack": "", "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

                    return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]
                    return return_list

                date = version["fileDate"]
                date_obj = parser.isoparse(date)

                normal_downloadurl = version["downloadUrl"]

                server_pack_id = version["serverPackFileId"]

                if (len(str(modpack_version)) > 2) and (modpack_version) in str(display_name):
                    try:
                        version_serverpack_url = requests.get(f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{server_pack_id}/download-url', timeout=10, headers=HEADERS).text
                    except:
                        version_serverpack_url = None
                    
                    if version_serverpack_url:
                        urls = {"SpecifiedVersion": version_serverpack_url, "LatestReleaseServerPack": "", "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}
                        return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]

                        return return_list
            else:
                print("This modpack version was not found. Defaulting to latest modpack version...")
                    


        #If the version is set to latest or no version is provided by the user, find the latest release

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

        #print(release_serverpack_id)

        try:
            release_serverpack_url = requests.get(f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{release_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
        except:
            release_serverpack_url = None
            print("No release server pack was found for this modpack")

        try:
            beta_serverpack_url = requests.get(f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{beta_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
        except:
            beta_serverpack_url = None
            print("No beta server pack was found for this modpack")

        try:
            alpha_serverpack_url = requests.get(f'https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}/file/{alpha_serverpack_id}/download-url', timeout=10, headers=HEADERS).text
        except:
            alpha_serverpack_url = None
            print("No alpha server pack was found for this modpack")


        #If modpack has no server pack choose the newest "client" pack
        non_serverpack_url = ''
        try:
            newest_date_release = parser.parse('2012-05-01 22:12:41.463000+00:00') 
            for version in files:
                release_type = version["releaseType"]
                date = version["fileDate"]
                date_obj = parser.isoparse(date)
                if (release_type == 1) and (date_obj > newest_date_release):
                    non_serverpack_url = version["downloadUrl"]
        except:
            non_serverpack_url = ''

        #print(non_serverpack_url)

        

        urls = {"SpecifiedVersion": "", "LatestReleaseServerpack": release_serverpack_url, "LatestBetaServerpack": beta_serverpack_url, "LatestAlphaServerpack": alpha_serverpack_url, "LatestReleaseNonServerpack": non_serverpack_url}

        return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]

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

                version_id_downloadurl = url_link + "/" + url_filename_noversion + "_v" + modpack_version + url_extension

                #Check if url is valid
                response_test = requests.head(url, timeout=10, headers=HEADERS)
                status_code = response_test.status_code
                if not (400 <= int(status_code) <= 500):
                    print("Constructed version URL is invalid. Defaulting to recommended instead.")

                    


                    urls = {"SpecifiedVersion": version_id_downloadurl, "LatestReleaseServerPack": "", "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

                    normal_downloadurl = ""
                    return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]
                    return return_list
                else:
                    print("Constructed version URL is invalid. Defaulting to recommended instead.")
                    pass
            except:
                print("This modpack version was not found or an error appeared while fetching it's downlaod link. Defaulting to latest modpack version...")
                pass

        urls = {"SpecifiedVersion": serverpack_url, "LatestReleaseServerPack": "", "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

        normal_downloadurl = ""
        return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]
        
        return return_list

    if provider == "direct":
        urls = {"SpecifiedVersion": modpack_id, "LatestReleaseServerPack": "", "LatestBetaServerpack": "", "LatestAlphaServerpack": "", "LatestReleaseNonServerpack": ""}

        modpack_name = (modpack_id.rsplit('/', 1)[-1])
        if modpack_name.endswith(".zip"):
            modpack_name = modpack_name.replace(".zip", "")

        normal_downloadurl = ""
        return_list = [modpack_name.replace("  ", " "), urls, normal_downloadurl]
        return return_list

#print(get_server_modpack_url("technic", 'tekkit-legends', "latest"))


def get_modpack_minecraft_version(provider, modpack_id):
    if provider == "curse":
        url = f"https://addons-ecs.forgesvc.net/api/v2/addon/{modpack_id}"

        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                'referer': 'https://www.curseforge.com/minecraft/modpacks'}

        response = requests.get(url, timeout=10, headers=HEADERS).json()

        try:
            latest_file = response["latestFiles"][0]
            game_version = latest_file["gameVersion"][0]
            return game_version
        except:
            print("Could not obtain minecraft version for this modpack. Returning False")
            return False

    if provider == "technic":
        main_url = f"https://solder.technicpack.net/api/modpack/{modpack_id}"
        HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),
                'referer': 'https://www.technicpack.net/'}

        try:
            main_response = requests.get(main_url, timeout=10, headers=HEADERS).json()
            main_response["name"]
        except:
            print("This modpack does not exist on Technic Solder. Attempting to get version from main API instead...")
            try:
                fallback_url = f'https://api.technicpack.net/modpack/{modpack_id}?build=729'
                fallback_response = requests.get(fallback_url, timeout=10, headers=HEADERS).json()
                game_version = fallback_response["minecraft"]
                print("Got minecraft version", game_version)
                return game_version
            except:
                print("Could not obtain recommended build version for this modpack. Returning False")
                return False

        try:
            recommended_build = main_response["recommended"]
        except:
            print("Could not obtain recommended build version for this modpack. Returning False")
            return False
        build_url = f"https://solder.technicpack.net/api/modpack/{modpack_id}/{recommended_build}"

        build_response = requests.get(build_url, timeout=10, headers=HEADERS).json()
        try:
            game_version = build_response["minecraft"]
            return game_version
        except:
            print("Could not get Minecraft version for this modpack. Returning False")
            return False




