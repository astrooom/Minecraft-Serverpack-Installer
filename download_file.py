import wget
import requests
import html
import os

def download(url):
    #final_url = requests.head(url, allow_redirects=True).url
    
    #filename = (final_url.split('/')[-1])

    download_filename = wget.download(url)

    print("\nFinished downloading", download_filename)

    return download_filename


#download('https://edge.forgecdn.net/files/3012/800/SkyFactory-4_Server_4.2.2.zip')


