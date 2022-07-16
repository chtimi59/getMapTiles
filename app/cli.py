
import json
import sys
import time
import os

import requests
from dotenv import load_dotenv

from app.geo import getTilesNames, testGeoSearch


load_dotenv()

ROOT = os.getenv("ROOT")
BASE_DIR = os.getenv("BASE_DIR")


def fetch(url, retry=5):
    try:
        r = requests.get(url)
        if r.status_code == 404:
            raise ConnectionError()
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


# https://github.com/CesiumGS/3d-tiles/blob/main/specification/TileFormats/Batched3DModel/README.md


def read3dm(data: bytes):
    i = 0
    magic = data[i:i + 4]
    i += 4
    if not magic == b'b3dm':
        raise Exception('Invalid b3dm format')
    version = int.from_bytes(data[i:i + 4], "little")
    i += 4
    if not version == 1:
        raise Exception('Invalid b3dm version')
    bytesLenght = int.from_bytes(data[i:i + 4], "little")
    i += 4
    featureTableJSONBytesLenght = int.from_bytes(data[i:i + 4], "little")
    i += 4
    featureTableBinaryBytesLenght = int.from_bytes(data[i:i + 4], "little")
    i += 4
    batchTableJSONBytesLenght = int.from_bytes(data[i:i + 4], "little")
    i += 4
    batchTableBinaryBytesLenght = int.from_bytes(data[i:i + 4], "little")
    i += 4

    feature = {}
    if featureTableJSONBytesLenght > 0:
        feature = json.loads(data[i:i + featureTableJSONBytesLenght].decode("utf-8"))

    i += featureTableJSONBytesLenght + featureTableBinaryBytesLenght + batchTableJSONBytesLenght + batchTableBinaryBytesLenght

    # By default embedded glTFs use a right handed coordinate system where the y-axis is up.
    # For consistency with the z-up coordinate system of 3D Tiles, glTFs must be transformed at runtime.
    # See [glTF transforms](https://github.com/CesiumGS/3d-tiles/blob/main/specification/README.md#gltf-transforms) for more details.
    # Vertex positions may be defined relative-to-center for high-precision rendering,
    # see Precisions, Precisions.
    # If defined, RTC_CENTER specifies the center position that all vertex positions are relative to after the coordinate system transform
    # and glTF node hierarchy transforms have been applied.
    gltf = data[i:]
    if not len(gltf) + i == bytesLenght :
        raise Exception('Invalid size')
    return gltf, feature

# https://github.com/KhronosGroup/glTF/tree/main/specification/2.0


def readgltf(data: bytes):
    i = 0
    magic = data[i:i + 4]
    i += 4
    if not magic == b'glTF':
        raise Exception('Invalid gltf format')
    version = int.from_bytes(data[i:i + 4], "little")
    i += 4
    if not version == 2:
        raise Exception('Invalid gltf version')
    lenght = int.from_bytes(data[i:i + 4], "little")
    i += 4
    if not len(data) == lenght :
        raise Exception('Invalid size')

    chunks = []
    chunksOffset = []
    while i < lenght:
        chunkLenght = int.from_bytes(data[i:i + 4], "little")
        i += 4
        chunkType = data[i:i + 4].decode("utf-8")
        i += 4
        chunk = data[i:i + chunkLenght]
        chunksOffset.append(i)
        if chunkType == "JSON":
            chunks.append(json.loads(chunk.decode("utf-8")))
        else:
            chunks.append(chunk)
        i += chunkLenght

    # extra image extractor
    img = None
    if len(chunks[0]["images"]) == 1:
        bufferView = chunks[0]["images"][0]["bufferView"]
        view = chunks[0]["bufferViews"][bufferView]
        offset = view["byteOffset"] + chunksOffset[1]
        lenght = view["byteLength"]
        img = data[offset:offset + lenght]

    return img


# def readfile(filename):
#    f = open(filename, 'rb')
#    return f.read(-1)


def savefile(filename, data: bytes):
    f = open(filename, 'wb')
    return f.write(data)


def download(tile):
    level = len(tile)
    path = "/"
    idx = 0

    nbPath, reminder = divmod(level, 3)
    if reminder == 0:
        nbPath -= 1

    for _ in range(0, nbPath):
        path += tile[idx:idx + 3] + "/"
        idx += 3

    try:
        data = fetch(ROOT + "/Data" + path + f"L{level+9}_{tile}.b3dm", 0)
        gltf, feature = read3dm(data)
        img = readgltf(gltf)
        savefile(os.path.join(BASE_DIR, tile + ".jpg"), img)
        savefile(os.path.join(BASE_DIR, tile + ".gltf"), gltf)
        return feature['RTC_CENTER']
    except:
        return None


def searchTiles(lng0, lat0, lng1, lat1):
    jsDrawRectangles = []

    #jsDrawRectangles += testGeoSearch(21, lng0, lat0)

    # https://gltf-viewer.donmccurdy.com/

    # 20 tiles (L17)
    tiles = getTilesNames(16, lng0, lat0, lng1, lat1)
    # 660 tiles (L20)
    #tiles = getTilesNames(19, lng0, lat0, lng1, lat1)
    # 2552 tiles (L21 : max)
    #tiles = getTilesNames(20, lng0, lat0, lng1, lat1)

    count = len(tiles)
    i = 1
    for tile in tiles:
        print(f"{i}/{count}: {tile['name']}")
        i += 1
        center = download(tile['name'])
        if not center is None:
            tile['center'] = center
        else:
            tile['color'] = "#F00"

        jsDrawRectangles.append(tile)

    # center
    jsDrawRectangles.append({
        'name': 'center',
        'data': [lat0, lng0, lat1, lng1],
        'color': "#F00"
    })

    listJSFilemane = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "googleMap", "list.js")
    listJSFile = open(listJSFilemane, 'w')
    listJSFile.write("window.DATA=" + str(jsDrawRectangles))
    listJSFile.write("\n")


#searchTiles(3.05828278697053, 50.63790367370581, 3.0651009622863867, 50.63476396066108)
