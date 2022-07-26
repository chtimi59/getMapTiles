from typing import MutableSequence
from pyproj import CRS, Transformer
from app.tile import TileSystem, BasicTileSystem

crs_llh = CRS("EPSG:4979")
crs_xyz = CRS("EPSG:4978")
xyz2llh = Transformer.from_crs(crs_from=crs_xyz, crs_to=crs_llh).transform
llh2xyz = Transformer.from_crs(crs_from=crs_llh, crs_to=crs_xyz, always_xy=True).transform


crs_ll = CRS("EPSG:4326")
# crs_xy = CRS("EPSG:3857")  # Web Mercator
crs_xy = CRS("EPSG:2154")  # Lambert 93
xy2ll = Transformer.from_crs(crs_from=crs_xy, crs_to=crs_ll).transform
ll2xy = Transformer.from_crs(crs_from=crs_ll, crs_to=crs_xy, always_xy=True).transform


def xy2ll_rectangle(bbox):
    x0, y0, x1, y1 = bbox
    lat0, lng0 = xy2ll(x0, y0)
    lat1, lng1 = xy2ll(x1, y1)
    return [lat0, lng0, lat1, lng1]


def dec2dms(dd: float):
    mult = -1 if dd < 0 else 1
    mnt, sec = divmod(abs(dd) * 3600, 60)
    deg, mnt = divmod(mnt, 60)
    return f"{round(mult*deg)}°{round(mult*mnt)}'{round(mult*sec,3)}"


def strll(ll: MutableSequence[float]):
    return dec2dms(ll[0]) + ", " + dec2dms(ll[1])


# L12_21
# TOP LEFT
# tile: L20_21111111111
# catersian: [4046850.44102724, 214219.260762576, 4908790.13901585]
# lat/long:  (50.646993960909164, 3.0301131155001353, 68.36377274151891)
# dms:       50°38'49.178, 3°1'48.407
AX, AY = ll2xy(3.0301131155001353, 50.646993960909164)
# BOTTOM RIGHT
# tile: L20_21222222222
# catersian: [4052795.71053559, 223199.559304975, 4903539.99016507]
# lat/long:  (50.57243526433171, 3.1522652309582746, 85.52446734998375)
# dms:       #50°34'20.767, 3°9'8.155
BX, BY = ll2xy(3.1522652309582746, 50.57243526433171)

# L9 bounding box
WIDTH = abs(AX - BX) * 4
HEIGHT = abs(AY - BY) * 4
LEFT = min(AX, BX) - WIDTH / 2
TOP = max(AY, BY) + HEIGHT / 2
ts = TileSystem(WIDTH, HEIGHT, LEFT, TOP, 9)


def testGeoSearch(level, lngLeft, latTop):
    _, test, _ = ts.pos2Tile(level, ll2xy(lngLeft, latTop), True)
    list = []
    for layer in test:
        list.append({
            'name': layer,
            'data': xy2ll_rectangle(test[layer]),
        })
    return list


def getTilesNames(level, lngLeft, latTop, lngRight, latBottom, dbgData = False):

    nameTL = ts.pos2Tile(level, ll2xy(lngLeft, latTop))
    nameBR = ts.pos2Tile(level, ll2xy(lngRight, latBottom))

    simpleTs = BasicTileSystem(level - 8)
    x1, y1 = simpleTs.tile2Pos(nameTL)
    x2, y2 = simpleTs.tile2Pos(nameBR)

    list = []
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            tile = simpleTs.pos2Tile([x, y])

            _, _, bbox = ts.pos2Tile(level, ts.tile2Pos(tile), True)
            if dbgData:
                list.append({
                    'name': tile,
                    'data': xy2ll_rectangle(bbox),
                })
            else:
                list.append(tile)

    return list


# print(strll(xy2ll(*ts.tile2Pos("21130110310"))))
