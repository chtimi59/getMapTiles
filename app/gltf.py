
import json
from pydoc import describe
import struct
import os
import numpy
from typing import Union,TypeVar

from dotenv import load_dotenv
from pygltflib import *


load_dotenv()

ROOT = os.getenv("ROOT")
BASE_DIR = os.getenv("BASE_DIR")

list = {
    21113220 : [4047494.97510582, 216212.197323319, 4908181.02462893],
    21113222 : [4047488.51674042, 216347.248944463, 4908179.14784863],
    21131000 : [4047481.63656385, 216482.938892446, 4908179.35852107],
    21131002 : [4047482.6846789, 216618.859962311, 4908181.65158561],
    21131020 : [4047478.40887312, 216753.771325021, 4908182.60412905],
    21112331 : [4047596.02816742, 216217.446670238, 4908098.10250766],
    21112333 : [4047588.40181993, 216352.618395999, 4908098.46961172],
    21130111 : [4047584.19708635, 216488.148722848, 4908098.97454097],
    21130113 : [4047575.49342492, 216623.651381291, 4908112.89918074],
    21130131 : [4047568.40736383, 216759.015022034, 4908115.55099103],
    21112330 : [4047698.28041974, 216222.461707754, 4908015.82939969],
    21112332 : [4047687.97192605, 216358.110816437, 4908015.95890014],
    21130110 : [4047683.70745454, 216493.19870305, 4908019.4619678],
    21130112 : [4047673.37552413, 216628.89114926, 4908022.41370736],
    21130130 : [4047668.27827206, 216763.953927383, 4908017.30602783],
    21112321 : [4047798.21900533, 216227.972881805, 4907936.67154664],
    21112323 : [4047789.46320107, 216363.113687055, 4907935.01287448],
    21130101 : [4047782.76069666, 216498.782374186, 4907936.73125256],
    21130103 : [4047774.66901914, 216633.978706191, 4907932.98142481],
    21130121 : [4047768.91773509, 216769.365038236, 4907933.76674225]
}


def getAccessorDataFormat(accessor: Accessor):
    nbFields = 0
    if accessor.type == 'SCALAR':
        nbFields = 1
    elif accessor.type == 'VEC3':
        nbFields = 3
    elif accessor.type == 'VEC2':
        nbFields = 2
    else:
        raise Exception("unsupported accessor type")

    size = 0
    unitaryFormat = ""
    format = ""
    if accessor.componentType == 5123:
        # unsigned short 16bits
        size = nbFields * 2
        unitaryFormat = "<H"
        format = "<" + "H" * nbFields
    elif accessor.componentType == 5126:
        # signed float 32bits
        size = nbFields * 4
        unitaryFormat = "<f"
        format = "<" + "f" * nbFields
    else:
        raise Exception("unsupported accessor componentType")

    return [size, format, unitaryFormat]

# https://github.com/KhronosGroup/glTF/tree/main/specification/2.0


class OLDGLTF:

    def readBufferViewBin(self, dict):
        # {'bufferView': 3, 'mimeType': 'image/jpeg'}
        view = self._json["bufferViews"][dict['bufferView']]
        offset = view["byteOffset"] + self._binStart
        lenght = view["byteLength"]
        data = self.data[offset:offset + lenght]
        return data

    def readBufferView(self, dict):
        # {'bufferView': 2, 'byteOffset': 0, 'componentType': 5123, 'count': 1992, 'type': 'SCALAR'}

        view = self._json["bufferViews"][dict['bufferView']]
        offset = view["byteOffset"] + dict['byteOffset'] + self._binStart

        nbFields = 0
        if dict['type'] == 'SCALAR':
            nbFields = 1
        elif dict['type'] == 'VEC3':
            nbFields = 3
        elif dict['type'] == 'VEC2':
            nbFields = 2
        else:
            raise Exception("unsupported accesor type")

        size = 0
        unpackFormat = ""
        if dict['componentType'] == 5123:
            # unsigned short 16bits
            size = nbFields * 2
            unpackFormat = "<" + "H" * nbFields
        elif dict['componentType'] == 5126:
            # signed float 32bits
            size = nbFields * 4
            unpackFormat = "<" + "f" * nbFields
        else:
            raise Exception("unsupported accessor componentType")

        list = []
        for i in range(dict['count']):
            index = offset + i * size
            v = struct.unpack(unpackFormat, self.data[index:index + size])
            list.append(v)

        # convert a numpy array for some manipulation
        return numpy.array(list)

    def __init__(self, data: bytes):
        self.data = data

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

        self._json = None
        self._binStart = None
        while i < lenght:
            chunkLenght = int.from_bytes(data[i:i + 4], "little")
            i += 4
            chunkType = data[i:i + 4].decode("utf-8")
            i += 4
            chunk = data[i:i + chunkLenght]
            if chunkType == "JSON":
                if not self._json is None:
                    raise Exception('Only one JSON chunk supported')
                self._json = json.loads(chunk.decode("utf-8"))
            else:
                if not self._binStart is None:
                    raise Exception('Only one BIN chunk supported')
                self._binStart = i

            i += chunkLenght

        if self._json is None:
            raise Exception('JSON chunk not found')
        if self._binStart is None:
            raise Exception('BIN chunk not found')

        if (not len(self._json["scenes"]) == 1):
            raise Exception('Only one scene supported')
        self.scene = self._json["scenes"][0]

        if (not len(self.scene['nodes']) == 1):
            raise Exception('Only one node supported')
        self.node = self._json["nodes"][self.scene['nodes'][0]]

        self.mesh = self._json["meshes"][self.node['mesh']]

        if (not len(self.mesh['primitives']) == 1):
            raise Exception('Only one primitive supported')
        self.primitive = self.mesh['primitives'][0]

        if (not len(self._json["images"]) == 1):
            raise Exception('Only one image supported')
        self.image = self._json["images"][0]
        self.textures = self._json["textures"]
        self.materials = self._json["materials"]

        self.accessors = self._json["accessors"]
# tmp = GLTF(open(os.path.join(BASE_DIR, "input.gltf"), 'rb').read(-1))
# indices = tmp.readBufferView(tmp.accessors[tmp.primitive['indices']])
# positions = tmp.readBufferView(tmp.accessors[tmp.primitive['attributes']['POSITION']])
# textcoord = tmp.readBufferView(tmp.accessors[tmp.primitive['attributes']['TEXCOORD_0']])
# imageData = tmp.readBufferViewBin(tmp.image)
# open(os.path.join(BASE_DIR, "image.jpg"), 'wb').write(imageData)


def readgltf(filename):

    data = open(os.path.join(BASE_DIR, filename), 'rb').read(-1)

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

    while i < lenght:
        chunkLenght = int.from_bytes(data[i:i + 4], "little")
        i += 4
        chunkType = data[i:i + 4].decode("utf-8")
        i += 4
        chunk = data[i:i + chunkLenght]
        if chunkType == "JSON":
            return json.loads(chunk.decode("utf-8"))
        i += chunkLenght

@dataclass
class BlobReturn:
    blob: bytes
    accessor: Union[Accessor, None]

@dataclass
class ImageReturn:
    blob: bytes
    image: Image

@dataclass
class ReadReturn:
    points: BlobReturn
    textCoord0: BlobReturn
    indices: BlobReturn
    image: ImageReturn


def read(filename):
    gltf = GLTF2().load(os.path.join(BASE_DIR, filename))

    def readAccessor(accessorIndex: int) -> BlobReturn:
        accessor = gltf.accessors[accessorIndex]
        [size, format, unitaryFormat] = getAccessorDataFormat(accessor)

        bufferView = gltf.bufferViews[accessor.bufferView]
        buffer = gltf.buffers[bufferView.buffer]
        data = gltf.get_data_from_buffer_uri(buffer.uri)
        list = []
        for i in range(accessor.count):
            index = bufferView.byteOffset + accessor.byteOffset + i * size
            d = data[index:index + size]
            v = struct.unpack(format , d)
            list.append(v)
        npList = numpy.array(list, dtype=unitaryFormat)

        blob = npList.tobytes()
        accessor = Accessor(
            type=accessor.type,
            componentType=accessor.componentType,
            count=len(npList),
            max=npList.max(axis=0).tolist(),
            min=npList.min(axis=0).tolist(),
        )
        return BlobReturn(blob, accessor)

    def readImage(image: Image) -> ImageReturn:
        bufferView = gltf.bufferViews[image.bufferView]
        buffer = gltf.buffers[bufferView.buffer]
        data = gltf.get_data_from_buffer_uri(buffer.uri)
        return ImageReturn(data[bufferView.byteOffset: bufferView.byteOffset+bufferView.byteLength],
                    Image(mimeType=image.mimeType))


    mesh = gltf.meshes[gltf.scenes[gltf.scene].nodes[0]]
    primitive = mesh.primitives[0]
    indices = readAccessor(primitive.indices)
    points = readAccessor(primitive.attributes.POSITION)
    textCoord0 = readAccessor(primitive.attributes.TEXCOORD_0)
    image = readImage(gltf.images[0])
    return ReadReturn(points, textCoord0, indices, image)

data = read("3d/21130110310.glb")

inputs = [data]

gltf = GLTF2(
    scene=0,
    scenes=[],
    nodes=[],
    samplers=[Sampler(minFilter=9729)],
    textures=[Texture(sampler=0, source=0)],
)




#print(readgltf("3d/21130110310.glb"))
