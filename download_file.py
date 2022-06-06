import sys
import requests
from tqdm import tqdm
import wget

HEADERS = {'user-agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'),}

def bar_progress(current, total, width=80):
    progress_message = "Downloading: %d%% [%d / %d] bytes" % (
        current / total * 100, current, total)
    # Don't use print() as it will print in new line every time.
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


def download_wget(url):
    final_url = requests.head(url, allow_redirects=True).url

    filename = (final_url.split('/')[-1])

    download_filename = wget.download(url, bar=bar_progress)

    print("\nFinished downloading", download_filename)

    return download_filename

def download(url):
    file_name_start_pos = url.rfind("/") + 1
    file_name = url[file_name_start_pos:]

    r = requests.get(url, stream=True, allow_redirects=True, headers=HEADERS)
    if r.status_code == requests.codes.ok:
        total_size_in_bytes= int(r.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(file_name, 'wb') as file:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
    else:
        print("Someting went wrong...")
    print("\nFinished downloading", file_name)
    return file_name