import requests

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.3904.108 Safari/537.36'

def html_download(url, fn=None):
    r = requests.get(url, stream=True, headers={'User-Agent': USER_AGENT})
    if r.status_code != 200:
        return False
    with open(fn, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            f.write(chunk) if chunk else None
    return True