"""村のマップ。地面のタイルと建物・木などの置き物を描く。

座標の約束:
- マップはタイル単位（列 col が東西、行 row が南北）。1タイルは TILE ワールド単位。
- ワールド座標は x が東、z が南、y が上。マップの中心がワールドの原点。
"""

import pyxel
from pyxel.cube import Mat4, Node, Vec3

TILE = 16
MAP_W = 16
MAP_H = 12

# 色（Pyxel の標準パレット）
GRASS = 11
PATH = 15
STONE = 13
WATER = 6
SOIL = 4
WOOD = 4
LEAF = 3
CROP = 3
DARK = 0
WINDOW = 10

# 地面の文字: . 草 / # 道 / s 石畳（広場） / w 川 / = 橋 / f 畑
# fmt: off
GROUND = [
    "......#....ww...",
    "......#....wwfff",
    "......#....wwfff",
    "......#....wwfff",
    "....sssss..wwfff",
    "....sssss..ww...",
    "#####sss###==###",
    "....sssss..ww...",
    "....sssss..ww...",
    "......#....ww...",
    "......#....ww...",
    "......#....ww...",
]
# fmt: on

GROUND_STYLE = {
    ".": (GRASS, 0.0),
    "#": (PATH, 0.4),
    "s": (STONE, 0.6),
    "w": (WATER, -2.0),
    "=": (WOOD, 2.0),
    "f": (SOIL, 0.8),
}


def tile_pos(col, row, y=0.0):
    """タイルの中心のワールド座標。col/row は小数でもよい。"""
    return Vec3(
        (col - MAP_W / 2 + 0.5) * TILE,
        y,
        (row - MAP_H / 2 + 0.5) * TILE,
    )


def box_at(node, center, size, color):
    node.box(Mat4.from_translation(center), size, color)


class Ground(Node):
    """地面。同じ種類が横に続くタイルは1つの箱にまとめて描く（描く数を減らすため）。"""

    def __init__(self):
        super().__init__()
        self.runs = []
        for row, line in enumerate(GROUND):
            col = 0
            while col < MAP_W:
                ch = line[col]
                end = col
                while end + 1 < MAP_W and line[end + 1] == ch:
                    end += 1
                if ch != ".":
                    self.runs.append((ch, col, end, row))
                col = end + 1

    def on_draw(self):
        # 土台の側面だけ陰影をつけ、上の面は平らな色で塗る（陰影のまだら模様を避ける）
        box_at(self, Vec3(0, -4.5, 0), Vec3(MAP_W * TILE, 8, MAP_H * TILE), LEAF)
        self.shaded(False)
        box_at(self, Vec3(0, -0.25, 0), Vec3(MAP_W * TILE, 0.5, MAP_H * TILE), GRASS)
        for ch, start, end, row in self.runs:
            color, top = GROUND_STYLE[ch]
            length = end - start + 1
            center = tile_pos((start + end) / 2, row)
            if ch == "w":
                # 川は少しへこませる
                box_at(self, Vec3(center.x, -1.5, center.z), Vec3(length * TILE, 3.2, TILE), color)
            elif ch == "=":
                # 橋は板と手すり
                box_at(self, Vec3(center.x, 1.0, center.z), Vec3(length * TILE, 2, TILE), color)
                for dz in (-TILE / 2 + 1, TILE / 2 - 1):
                    box_at(self, Vec3(center.x, 4.0, center.z + dz), Vec3(length * TILE, 1.5, 1.5), color)
            elif ch == "f":
                box_at(self, Vec3(center.x, top / 2, center.z), Vec3(length * TILE, top, TILE), color)
                # 作物の列
                for dz in (-4, 0, 4):
                    box_at(
                        self,
                        Vec3(center.x, top + 1.5, center.z + dz),
                        Vec3(length * TILE - 4, 3, 2),
                        CROP,
                    )
            else:
                box_at(self, Vec3(center.x, top / 2, center.z), Vec3(length * TILE, top, TILE), color)
        self.shaded(True)


class Building(Node):
    """箱型の建物。壁・二段の屋根・ドア・窓で作る。

    col/row は建物の北西のタイル、w/d はタイル数での幅と奥行き。
    door は入口の向き（"n" / "s" / "e" / "w"）。
    """

    def __init__(self, name, col, row, w, d, wall, roof, door, height=18, chimney=False):
        super().__init__()
        self.name = name
        self.center = tile_pos(col + (w - 1) / 2, row + (d - 1) / 2)
        self.size_x = w * TILE - 4
        self.size_z = d * TILE - 4
        self.wall = wall
        self.roof = roof
        self.door = door
        self.height = height
        self.chimney = chimney

    def on_draw(self):
        c = self.center
        sx, sz, h = self.size_x, self.size_z, self.height
        # 壁
        box_at(self, Vec3(c.x, h / 2, c.z), Vec3(sx, h, sz), self.wall)
        # 屋根（下段は少し張り出し、上段は細く）
        box_at(self, Vec3(c.x, h + 2, c.z), Vec3(sx + 4, 4, sz + 4), self.roof)
        box_at(self, Vec3(c.x, h + 6, c.z), Vec3(sx - 2, 4, sz * 0.5), self.roof)
        if self.chimney:
            box_at(self, Vec3(c.x + sx / 4, h + 9, c.z - sz / 4), Vec3(3, 8, 3), STONE)

        # ドアと窓は入口の面に貼る
        nx, nz = {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}[self.door]
        half = (sx / 2) if nx else (sz / 2)
        face = Vec3(c.x + nx * (half + 0.5), 0, c.z + nz * (half + 0.5))
        thin = Vec3(1.0, 0, 0) if nx else Vec3(0, 0, 1.0)
        along = Vec3(0, 0, 1) if nx else Vec3(1, 0, 0)
        span = sz if nx else sx

        def face_box(offset, y, width, height, color):
            pos = Vec3(face.x + along.x * offset, y, face.z + along.z * offset)
            size = Vec3(
                thin.x + along.x * width,
                height,
                thin.z + along.z * width,
            )
            box_at(self, pos, size, color)

        face_box(0, 5, 5, 10, DARK)
        for offset in (-span / 4 - 1, span / 4 + 1):
            if abs(offset) + 3 < span / 2:
                face_box(offset, 11, 5, 4, WINDOW)


class Tree(Node):
    def __init__(self, col, row):
        super().__init__()
        self.pos = tile_pos(col, row)

    def on_draw(self):
        p = self.pos
        box_at(self, Vec3(p.x, 4, p.z), Vec3(3, 8, 3), WOOD)
        box_at(self, Vec3(p.x, 12, p.z), Vec3(11, 9, 11), LEAF)
        box_at(self, Vec3(p.x, 18, p.z), Vec3(7, 5, 7), LEAF)


class Fountain(Node):
    def __init__(self, col, row):
        super().__init__()
        self.pos = tile_pos(col, row)

    def on_draw(self):
        p = self.pos
        box_at(self, Vec3(p.x, 2.5, p.z), Vec3(22, 4, 22), 7)
        box_at(self, Vec3(p.x, 4.6, p.z), Vec3(18, 0.6, 18), WATER)
        box_at(self, Vec3(p.x, 7, p.z), Vec3(4, 10, 4), 7)
        # 水しぶき（上下に少し揺れる）
        bob = pyxel.sin(pyxel.frame_count * 12) * 1.0
        box_at(self, Vec3(p.x, 13 + bob, p.z), Vec3(3, 3, 3), WATER)


# 建物の一覧。後でキャラの行き先（予定の場所）として名前で引く。
BUILDINGS = [
    # 名前, 列, 行, 幅, 奥行き, 壁, 屋根, 入口, 高さ, 煙突
    ("bakery", 3, 1, 2, 2, 15, 4, "e", 18, True),
    ("store", 7, 1, 3, 2, 7, 12, "s", 18, False),
    ("diner", 7, 9, 3, 2, 9, 8, "n", 20, True),
    ("house_a", 1, 3, 2, 2, 7, 14, "s", 16, False),
    ("house_b", 1, 8, 2, 2, 15, 2, "n", 16, False),
    ("house_c", 3, 10, 2, 2, 7, 5, "n", 16, True),
    ("farm_house", 13, 8, 2, 2, 15, 9, "n", 16, True),
]

TREES = [
    (0, 0), (2, 0), (9, 4), (10, 5), (0, 11), (9, 11), (15, 11),
    (13, 11), (15, 5), (4, 3), (8, 3),
]


class Village(Node):
    def __init__(self):
        super().__init__()
        self.add_child(Ground())
        for args in BUILDINGS:
            self.add_child(Building(*args))
        for col, row in TREES:
            self.add_child(Tree(col, row))
        self.add_child(Fountain(6, 6))
