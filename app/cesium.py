
import json
import os

from dotenv import load_dotenv
load_dotenv()

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


# ex: tileName 21112330 return {ROOT}/Data/211/123/L17_21112330.b3dm
def getUrl(tileName):
    level = len(tileName)
    path = "/"
    idx = 0

    nbPath, reminder = divmod(level, 3)
    if reminder == 0:
        nbPath -= 1

    for _ in range(0, nbPath):
        path += tileName[idx:idx + 3] + "/"
        idx += 3
    
    return "/Data" + path + f"L{level+9}_{tileName}.b3dm"


if __name__ == "__main__":

    assert(getUrl("21112330") == "/Data/211/123/L17_21112330.b3dm")
