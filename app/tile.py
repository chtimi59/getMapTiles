import math

# Tile organization:
#
#      ^ (y)
#      |
# -----| --- | --- |------> (x)
#      |  1  |  3  |
#      | --- | --- |
#      |  0  |  2  |
#      | --- | --- |
#      |
#


class TileSystem:

    def __init__(self, width=1, height=1, x0=0, y0=0, level=1):
        self.ROOT_TILE = [x0, y0, width, height]
        self.LEVEL = level

    def pos2Tile(self, level, xy, getBBox=False):
        assert(level >= self.LEVEL)
        name = ''
        x, y = xy
        [x0, y0, dx, dy] = self.ROOT_TILE

        bboxes = {}
        lastBox = None
        for l in range(self.LEVEL, level + 1):

            # subtile
            dx = dx / 2
            dy = dy / 2

            isRight = x >= x0 + dx
            isBottom = y <= y0 - dy

            # found its name
            s = '?'
            if isRight and isBottom:
                s = '2'
            if isRight and not isBottom:
                s = '3'
            if not isRight and not isBottom:
                s = '1'
            if not isRight and isBottom:
                s = '0'
            name += s

            if isRight:
                x0 = x0 + dx
            if isBottom:
                y0 = y0 - dy

            lastBox = [x0, y0, x0 + dx, y0 - dy]
            bboxes[f"L{l+1}_{name}"] = lastBox

        if getBBox:
            return name, bboxes, lastBox
        else:
            return name

    def tile2Pos(self, name):

        [x0, y0, width, height] = self.ROOT_TILE
        level = len(name)
        divCount = math.pow(2, level)

        x, y = [0, 0]
        div = divCount
        for idx in range(0, level):
            if idx != level - 1:
                # offset
                div = div / 2
            else:
                # coordinates
                div = div / 2
                x += div / 2
                y -= div / 2

            char = name[idx]
            if char == '2' or char == '3':
                x += div
            if char == '0' or char == '2':
                y -= div

            #print(x, y)

        # scale
        result = [x0 + width * x / divCount, y0 + height * y / divCount]
        # print(result)
        return result


class BasicTileSystem(TileSystem):

    def __init__(self, level=1):
        div = math.pow(2, level + 1)
        self.level = level
        TileSystem.__init__(self, div, div)

    def tile2Pos(self, name):
        assert(len(name) == self.level)
        x, y = TileSystem.tile2Pos(self, name)
        raw = [(x - 1) / 2, -(y + 1) / 2]
        x = int(raw[0])
        assert(x == raw[0])
        y = int(raw[1])
        assert(y == raw[1])
        return [x, y]

    def pos2Tile(self, xy):
        x, y = xy
        x = x * 2 + 1
        y = -y * 2 - 1
        return TileSystem.pos2Tile(self, self.level, [x, y])


if __name__ == "__main__":

    ts = TileSystem(100, 100)

    assert(ts.pos2Tile(1, [0, 0]) == "1")
    assert(ts.pos2Tile(1, [45, -45]) == "1")
    assert(ts.pos2Tile(1, [100, -100]) == "2")
    assert(ts.pos2Tile(1, [0, -100]) == "0")
    assert(ts.pos2Tile(2, [100, 0]) == "33")
    assert(ts.pos2Tile(2, [25, -25]) == "12")
    assert(ts.pos2Tile(2, [25, -50]) == "03")
    assert(ts.pos2Tile(3, [100, -100]) == "222")
    assert(ts.pos2Tile(3, [0, 0]) == "111")
    assert(ts.pos2Tile(3, [62.5, -50]) == "213")

    assert(ts.tile2Pos("1") == [100 * 1 / 4, -100 * 1 / 4])
    assert(ts.tile2Pos("2") == [100 * 3 / 4, -100 * 3 / 4])
    assert(ts.tile2Pos("22") == [100 * 7 / 8, -100 * 7 / 8])
    assert(ts.tile2Pos("0") == [100 * 1 / 4, -100 * 3 / 4])
    assert(ts.tile2Pos("33") == [100 * 7 / 8, -100 * 1 / 8])
    assert(ts.tile2Pos("12") == [100 * 3 / 8, -100 * 3 / 8])
    assert(ts.tile2Pos("03") == [100 * 3 / 8, -100 * 5 / 8])
    assert(ts.tile2Pos("222") == [100 * 15 / 16, -100 * 15 / 16])
    assert(ts.tile2Pos("111") == [100 * 1 / 16, -100 * 1 / 16])
    assert(ts.tile2Pos("213") == [100 * 11 / 16, -100 * 9 / 16])

    ts1 = BasicTileSystem(1)
    assert(ts1.tile2Pos("1") == [0, 0])
    assert(ts1.tile2Pos("3") == [1, 0])
    assert(ts1.tile2Pos("0") == [0, 1])
    assert(ts1.tile2Pos("2") == [1, 1])
    assert(ts1.pos2Tile([0, 0]) == "1")
    assert(ts1.pos2Tile([1, 0]) == "3")
    assert(ts1.pos2Tile([0, 1]) == "0")
    assert(ts1.pos2Tile([1, 1]) == "2")

    ts2 = BasicTileSystem(2)
    assert(ts2.tile2Pos("11") == [0, 0])
    assert(ts2.tile2Pos("33") == [3, 0])
    assert(ts2.tile2Pos("22") == [3, 3])
    assert(ts2.tile2Pos("12") == [1, 1])
    assert(ts2.tile2Pos("21") == [2, 2])
    assert(ts2.pos2Tile([0, 0]) == "11")
    assert(ts2.pos2Tile([3, 0]) == "33")
    assert(ts2.pos2Tile([3, 3]) == "22")
    assert(ts2.pos2Tile([1, 1]) == "12")
    assert(ts2.pos2Tile([2, 2]) == "21")

    ts3 = BasicTileSystem(3)
    assert(ts3.tile2Pos("111") == [0, 0])
    assert(ts3.tile2Pos("222") == [7, 7])
    assert(ts3.tile2Pos("213") == [5, 4])
    assert(ts3.pos2Tile([0, 0]) == "111")
    assert(ts3.pos2Tile([7, 7]) == "222")
    assert(ts3.pos2Tile([5, 4]) == "213")
