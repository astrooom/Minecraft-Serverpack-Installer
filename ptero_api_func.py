from pydactyl import PterodactylClient
import requests
import json

new_forge_startup = '''java -Xms128M -Xmx$(({{SERVER_MEMORY}}-512))M -Dterminal.jline=false -Dterminal.ansi=true {{STARTUP_FLAGS}} $( [  ! -f unix_args.txt ] && printf %s "-jar {{SERVER_JARFILE}}" || printf %s "@unix_args.txt" )'''


def get_server_id(uuid, panel_url, application_api_key):

    url = f'{panel_url}/api/application/servers?per_page=99999999999999999999999'
    headers = {
        "Authorization": f"Bearer {application_api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "cookie": "pterodactyl_session=eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%253D%253D"
    }

    response = requests.request('GET', url, headers=headers).json()

    responsedata = response["data"]
    for server in responsedata:
        server_attr = server["attributes"]
        server_uuid = server_attr["uuid"]
        server_id = server_attr["id"]
        if server_uuid == uuid:
            return server_id


# Updates the server in pterodactyl to the new forge versions by changing the startup command and the docker image.
def update_startup(server_id, minecraft_version, panel_url, application_api_key):
    # Get previous egg info required
    egg_info_url = f'{panel_url}/api/application/servers/{server_id}'
    headers = {
        "Authorization": f"Bearer {application_api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "cookie": "pterodactyl_session=eyJpdiI6InhIVXp5ZE43WlMxUU1NQ1pyNWRFa1E9PSIsInZhbHVlIjoiQTNpcE9JV3FlcmZ6Ym9vS0dBTmxXMGtST2xyTFJvVEM5NWVWbVFJSnV6S1dwcTVGWHBhZzdjMHpkN0RNdDVkQiIsIm1hYyI6IjAxYTI5NDY1OWMzNDJlZWU2OTc3ZDYxYzIyMzlhZTFiYWY1ZjgwMjAwZjY3MDU4ZDYwMzhjOTRmYjMzNDliN2YifQ%253D%253D"
    }

    egg_resp = requests.request('GET', egg_info_url, headers=headers).json()
    egg = egg_resp["attributes"]

    egg_container = egg["container"]
    egg_env = egg_container["environment"]
    egg_id = egg["egg"]
    egg_image = egg_container["image"]

    # Update egg startup and docker img using parts of previous egg info and mc version
    update_startup_url = f'{panel_url}/api/application/servers/{server_id}/startup'

    if "1.18" in minecraft_version:
        egg_image = 'ghcr.io/pterodactyl/yolks:java_17'
    elif "1.17" in minecraft_version:
        egg_image = 'ghcr.io/pterodactyl/yolks:java_16'
    elif "1.12" in minecraft_version:
        egg_image = 'ghcr.io/pterodactyl/yolks:java_8'
    else:
        egg_image = 'ghcr.io/pterodactyl/yolks:java_8'

    payload = {
        "startup": f"{new_forge_startup}",
        "environment": egg_env,
        "egg": str(egg_id),
        "image": egg_image,
        "skip_scripts": False
    }

    response = requests.request(
        'PATCH', update_startup_url, data=json.dumps(payload), headers=headers)