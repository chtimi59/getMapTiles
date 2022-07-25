
import sys
import time
import os

import requests
from dotenv import load_dotenv

from app.geo import getTilesNames, testGeoSearch
from app.cesium import read3dm, getUrl
from app.gltf import concatenate, Job, Jobs

load_dotenv()

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


def _dbgSearchTiles(definition, lng0, lat0, lng1, lat1):

    jsDrawRectangles = []

    #jsDrawRectangles += testGeoSearch(21, lng0, lat0)

    tiles = getTilesNames(definition, lng0, lat0, lng1, lat1)
    count = len(tiles)
    i = 1
    for tile in tiles:
        print(f"{i}/{count}: {tile['name']}")
        i += 1
        try:
            url = getUrl(tile['name'])
            data = fetch(url, 0)
            gltf, feature = read3dm(data)
            f = open(os.path.join(BASE_DIR, f"{tile['name']}.glb"), "wb")
            f.write(gltf)
            tile['center'] = feature['RTC_CENTER']
        except:
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




# 20 tiles (L17)
#_dbgSearchTiles(16, 3.05828278697053, 50.63790367370581, 3.0651009622863867, 50.63476396066108)

# 660 tiles (L20)
#_dbgSearchTiles(19, 3.05828278697053, 50.63790367370581, 3.0651009622863867, 50.63476396066108)

# 2552 tiles (L21 : max)
#_dbgSearchTiles(20, 3.05828278697053, 50.63790367370581, 3.0651009622863867, 50.63476396066108)


list = {       
    "21112330" : [4047698.28041974, 216222.461707754, 4908015.82939969],
    "21112331" : [4047596.02816742, 216217.446670238, 4908098.10250766],
    "21112332" : [4047687.97192605, 216358.110816437, 4908015.95890014],
    "21112333" : [4047588.40181993, 216352.618395999, 4908098.46961172],
    "21112321" : [4047798.21900533, 216227.972881805, 4907936.67154664],    
    "21112323" : [4047789.46320107, 216363.113687055, 4907935.01287448],
    "21130111" : [4047584.19708635, 216488.148722848, 4908098.97454097],
    "21130113" : [4047575.49342492, 216623.651381291, 4908112.89918074],
    "21130131" : [4047568.40736383, 216759.015022034, 4908115.55099103],
    "21130110" : [4047683.70745454, 216493.19870305, 4908019.4619678],
    "21130112" : [4047673.37552413, 216628.89114926, 4908022.41370736],
    "21130130" : [4047668.27827206, 216763.953927383, 4908017.30602783],
    "21130101" : [4047782.76069666, 216498.782374186, 4907936.73125256],
    "21130103" : [4047774.66901914, 216633.978706191, 4907932.98142481],
    "21130121" : [4047768.91773509, 216769.365038236, 4907933.76674225],
    "21131000" : [4047481.63656385, 216482.938892446, 4908179.35852107],
    "21131002" : [4047482.6846789, 216618.859962311, 4908181.65158561],
    "21131020" : [4047478.40887312, 216753.771325021, 4908182.60412905],
    "21113220" : [4047494.97510582, 216212.197323319, 4908181.02462893],
    "21113222" : [4047488.51674042, 216347.248944463, 4908179.14784863],

}

list3D = {
    "3d\\21130110310": [4047648.88693857, 216500.167472988, 4908039.95340062],
    "3d\\21130110311": [4047658.18863001, 216496.975183239, 4908046.77721627],
    "3d\\21130110312": [4047636.2938953, 216499.400206666, 4908050.18653726],
    "3d\\21130110313": [4047642.95498765, 216499.937334055, 4908060.76061349]
}


# ??
keys = []
for k in list: keys.append(k)
def provider(key: str) -> Job:
    return Job(
        open(os.path.join(BASE_DIR, f"{key}.glb"), 'rb').read(-1),
        list[key]
    )


glb = concatenate(Jobs(keys, provider))
f = open(os.path.join(BASE_DIR, f"merge.glb"), "wb")
for data in glb:
    f.write(data)
