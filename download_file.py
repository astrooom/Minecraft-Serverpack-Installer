import wget
import sys

def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (
        current / total * 100, current, total)
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()

def download(url):
    #final_url = requests.head(url, allow_redirects=True).url

    #filename = (final_url.split('/')[-1])

    download_filename = wget.download(url, bar=bar_progress)

    print("\nFinished downloading", download_filename)

    return download_filename

# download('https://edge.forgecdn.net/files/3012/800/SkyFactory-4_Server_4.2.2.zip')



