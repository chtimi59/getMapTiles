
import sys
import time
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

from app.geo import getTilesNames, testGeoSearch
from app.cesium import read3dm, getUrl
from app.gltf import concatenate, Job, Jobs, _debugReadgltf

load_dotenv()

BASE_DIR = os.getenv("BASE_DIR")
ROOT = os.getenv("ROOT")

def fetch(url, retry=5):
    fileCache = BASE_DIR + url.replace("/", os.sep) + '.glb'
    
    if Path(fileCache).is_file():
        f = open(fileCache, "rb")
        return f.read(-1)

    head, _ = os.path.split(fileCache)
    Path(head).mkdir(parents=True, exist_ok=True)
    try:
        r = requests.get(ROOT + url)
        if r.status_code == 404:
            raise ConnectionError()
        f = open(fileCache, "wb")
        f.write(r.content)
        return r.content
    except ConnectionError as e:
        print(f"failed! retry({retry}) ${url}")
        retry = retry - 1
        if retry <= 0:
            print(e)
            sys.exit(1)
        else:
            time.sleep(5)
            return fetch(url, retry)

def convert(position, definition=17):
    [lng0, lat0, lng1, lat1] = position
    tiles = getTilesNames(definition-1, lng0, lat0, lng1, lat1)
    progress = [1, len(tiles)]

    def provider(tile: str) -> Job:
        print(f"{progress[0]}/{progress[1]}: {tile}")
        progress[0] += 1
        try:
            url = getUrl(tile)
            data = fetch(url, 0)
            gltf, feature = read3dm(data)
            return Job(
                tile,
                gltf,
                feature['RTC_CENTER']
            )
        except:
            print(f"failed!")
            return None

    glb = concatenate(Jobs(tiles, provider))
    f = open(os.path.join(BASE_DIR, f"merge.glb"), "wb")
    for data in glb:
        f.write(data)


convert([3.05828278697053, 50.63790367370581, 3.0651009622863867, 50.63476396066108])