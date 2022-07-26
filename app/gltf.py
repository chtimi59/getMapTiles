import json
import struct
import math
import numpy
from typing import List, Callable
from pygltflib import *

@dataclass
class Job:
    key: str
    blob: bytes
    center: List[float]

class Jobs:
  def __init__(self, keys: list[str], provider: Callable[[str], Optional[Job]]) -> None:
    self._keys = keys
    self._provider = provider

  def __iter__(self):
    self._idx = 0
    return self

  def __next__(self):
    if self._idx < len(self._keys):
        i = self._idx
        self._idx = self._idx + 1       
        return self._provider(self._keys[i])            
    else:
      raise StopIteration


def _getAccessorDataFormat(accessor: Accessor):
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

class DynamicBuffer:

    def __init__(self):
        self.byteOffset = 0
        self.byteLength = 0
        self.blobs : bytes = bytes()
        self.bufferViews = []

    def append(self, blob: bytes, target: int = None):
        self.blobs += blob
        byteLength = len(blob)
        self.bufferViews.append(BufferView(buffer=0, byteOffset=self.byteOffset, byteLength=byteLength, target=target))
        self.byteOffset += byteLength

    def write(self, gltf: GLTF2):
        gltf.bufferViews = self.bufferViews
        #gltf.buffers = [Buffer(byteLength=len(self.blobs))]
        #gltf.set_binary_blob(self.blobs)        
        padding : bytes = bytes([0,0,0,0])            
        gltf.buffers = [Buffer(byteLength=len(self.blobs)+4)]
        gltf.set_binary_blob(self.blobs + padding)

@dataclass
class BlobAccessor:
    blob: bytes
    accessor: Optional[Accessor]

@dataclass
class BlobImage:
    blob: bytes
    image: Image

@dataclass
class ReadData:
    points: BlobAccessor
    textCoord0: BlobAccessor
    indices: BlobAccessor
    texture: BlobImage
    sampler: Sampler

def readGltf(data: bytes) -> ReadData:

    gltf = GLTF2().load_from_bytes(data)

    def readBlobAccessor(accessorIndex: int) -> BlobAccessor:
        accessor = gltf.accessors[accessorIndex]
        [size, format, unitaryFormat] = _getAccessorDataFormat(accessor)

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
        assert(accessor.count == len(npList))
        #assert(accessor.max == npList.max(axis=0).tolist())
        #assert(accessor.min == npList.min(axis=0).tolist())
        return BlobAccessor(blob, accessor)

    def readBlobImage(imageIndex: int) -> BlobImage:
        image = gltf.images[imageIndex]
        bufferView = gltf.bufferViews[image.bufferView]
        buffer = gltf.buffers[bufferView.buffer]
        data = gltf.get_data_from_buffer_uri(buffer.uri)
        blob = data[bufferView.byteOffset: bufferView.byteOffset+bufferView.byteLength]
        return BlobImage(blob, image)


    mesh = gltf.meshes[gltf.scenes[gltf.scene].nodes[0]]
    primitive = mesh.primitives[0]
    
    points = readBlobAccessor(primitive.attributes.POSITION)
    textCoord0 = readBlobAccessor(primitive.attributes.TEXCOORD_0)
    indices = readBlobAccessor(primitive.indices)
    texture = readBlobImage(0)
    sampler = gltf.samplers[0]
    return ReadData(points, textCoord0, indices, texture, sampler)


def concatenate(jobs: Jobs):

    gltf = GLTF2()
    buffer = DynamicBuffer()
    nodeIdx = 0
    origin = None
    children = []

    for job in iter(jobs):
        
        # missing tile ?
        if job is None:
            continue
        
        if origin is None:
            origin = job.center

        input = readGltf(job.blob)
        input.points.accessor.bufferView = nodeIdx*4 + 0 
        input.textCoord0.accessor.bufferView = nodeIdx*4 + 1
        input.indices.accessor.bufferView = nodeIdx*4 + 2
        input.texture.image.bufferView = nodeIdx*4 + 3
        
        gltf.accessors.append(input.points.accessor)
        gltf.accessors.append(input.textCoord0.accessor)
        gltf.accessors.append(input.indices.accessor)

        gltf.images.append(input.texture.image)
        gltf.samplers.append(input.sampler)
        gltf.textures.append(Texture(sampler=nodeIdx, source=nodeIdx))
        gltf.materials.append(Material(
            alphaCutoff=None,
            pbrMetallicRoughness=PbrMetallicRoughness(baseColorTexture=TextureInfo(index=nodeIdx))))

        buffer.append(input.points.blob, ARRAY_BUFFER)
        buffer.append(input.textCoord0.blob, ARRAY_BUFFER)
        buffer.append(input.indices.blob, ELEMENT_ARRAY_BUFFER)
        buffer.append(input.texture.blob)

        gltf.meshes.append(Mesh(
                primitives=[
                    Primitive(
                        attributes=Attributes(POSITION=nodeIdx*3 + 0 , TEXCOORD_0=nodeIdx*3 + 1),
                        indices=nodeIdx*3 + 2,
                        material=nodeIdx 
                    )
                ]
            )
        )

        translation = [job.center[0]-origin[0], job.center[2]-origin[2], -(job.center[1]-origin[1])]

        gltf.nodes.append(Node(mesh=nodeIdx, translation=translation, name=job.key))
        children.append(nodeIdx)
        nodeIdx +=1

    angle = math.pi * (90 - 50.63790367370581)/360
    gltf.nodes.append(Node(children=children, rotation=[0, 0, angle, 1]))

    # add the whole buffer at once ?
    buffer.write(gltf)

    gltf.scenes.append(Scene(nodes=[nodeIdx]))
    gltf.scene = 0
            
    return gltf.save_to_bytes()


#print(json.dumps(readgltf("merge.glb")))
#print(json.dumps(readgltf("3d/21130110310.glb")))

# https://github.com/KhronosGroup/glTF/tree/main/specification/2.0

def _debugReadgltf(filename):

    data = open(filename, 'rb').read(-1)

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

