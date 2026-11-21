"""スプライトスタッキング版の試作。

村の地図（village.py の GROUND / BUILDINGS / TREES）はそのまま使い、描き方だけを変える。
物は「輪切りの絵」を下から順に1ピクセルずつ上へずらし、カメラの角度だけ回して重ねて描く。
輪切りの絵はコードで作る（手描きの素材はまだ使わない）。

pyxel.init() を呼ばなくても画像に描けるように、描画は render(dst, ...) に分けてある。
"""

import functools
import math

import pyxel

from controls import ViewControl
from fps import FpsCounter
from village import BUILDINGS, GROUND, MAP_H, MAP_W, TILE, TREES

SCREEN_W = 352
SCREEN_H = 352

TRANSPARENT = 0  # 輪切りの絵の透明色。黒の代わりに紺（1）を使う
DOOR = 1
WINDOW = 10
LEAF = 3
LEAF_LIGHT = 11
LEAF_DARK = 5
WOOD = 4

GROUND_COLORS = {".": 11, "#": 15, "s": 13, "w": 6, "=": 4, "f": 4}
ZOOM_LEVELS = (1, 2, 3)


# ---------------------------------------------------------------------------
# 輪切りの絵を作る
# ---------------------------------------------------------------------------


class Stack:
    """輪切りの絵の束。size×size の絵を縦に count 枚並べた1枚の画像として持つ。"""

    def __init__(self, size, count):
        self.size = size
        self.count = count
        self.image = pyxel.Image(size, size * count)
        self.image.cls(TRANSPARENT)

    def layer(self, k):
        """k 段目の絵を描くための (画像, 左上の y) を返す。"""
        return self.image, k * self.size


def make_building(w_tiles, d_tiles, wall, roof, door, height, chimney):
    sx = w_tiles * TILE - 4
    sz = d_tiles * TILE - 4
    roof_h = 9
    size = max(sx, sz) + 8
    stack = Stack(size, height + roof_h + (4 if chimney else 0))
    ox = (size - sx) // 2
    oz = (size - sz) // 2
    dark = {7: 13, 15: 9, 9: 4}.get(wall, 13)

    # 入口の面: どの辺にドアと窓を描くか
    def front_pixels(img, top, lo, hi, color):
        # lo..hi は面に沿った位置（0〜面の長さ）
        for t in range(lo, hi):
            if door == "s":
                img.pset(ox + t, top + oz + sz - 1, color)
            elif door == "n":
                img.pset(ox + t, top + oz, color)
            elif door == "e":
                img.pset(ox + sx - 1, top + oz + t, color)
            else:
                img.pset(ox, top + oz + t, color)

    span = sx if door in "ns" else sz
    for k in range(height):
        img, top = stack.layer(k)
        img.rect(ox, top + oz, sx, sz, wall)
        img.rectb(ox, top + oz, sx, sz, dark if k < 2 or k == height - 1 else wall)
        # ドア（下から10段）と窓（9〜12段目）
        if k < 10:
            front_pixels(img, top, span // 2 - 2, span // 2 + 2, DOOR)
        if 8 <= k <= 11:
            for c in (span // 4, span * 3 // 4):
                front_pixels(img, top, c - 2, c + 1, WINDOW)

    # 切妻屋根: 棟（むね）の向きに沿って長さはそのまま、奥行きを1段ごとに狭める
    ridge_along_x = sx >= sz
    for r in range(roof_h):
        img, top = stack.layer(height + r)
        shrink = r * 2
        stripe = roof if r % 2 == 0 else {8: 2, 9: 4, 12: 5, 14: 8, 2: 1, 5: 1, 4: 2}.get(roof, roof)
        if ridge_along_x:
            d = sz + 4 - shrink * 2
            if d <= 0:
                break
            img.rect(ox - 2, top + oz - 2 + shrink, sx + 4, d, stripe)
        else:
            d = sx + 4 - shrink * 2
            if d <= 0:
                break
            img.rect(ox - 2 + shrink, top + oz - 2, d, sz + 4, stripe)

    if chimney:
        cx, cz = ox + sx * 3 // 4, oz + sz // 4
        for k in range(height + 2, stack.count):
            img, top = stack.layer(k)
            img.rect(cx, top + cz, 3, 3, 13)
    return stack


def make_tree():
    stack = Stack(14, 22)
    c = 7
    for k in range(22):
        img, top = stack.layer(k)
        if k < 7:
            img.rect(c - 1, top + c - 1, 3, 3, WOOD)
        else:
            # 下が太く上が細い丸い葉。外周は濃い色にして段の境目を見せる
            t = (k - 7) / 14
            r = 6.5 * math.sin(math.pi * (0.25 + 0.75 * t)) if t < 1 else 1
            r = max(1.0, r)
            img.circ(c, top + c, r, LEAF if k % 3 else LEAF_DARK)
            if r > 2:
                img.circ(c - 1, top + c - 1, r - 2, LEAF)
            if k >= 18:
                img.circ(c - 1, top + c - 1, max(0, r - 2), LEAF_LIGHT)
    return stack


def make_fountain():
    stack = Stack(24, 14)
    c = 12
    for k in range(14):
        img, top = stack.layer(k)
        if k < 4:
            img.rect(1, top + 1, 22, 22, 7)
            img.rectb(1, top + 1, 22, 22, 13)
            if k == 3:
                img.rect(3, top + 3, 18, 18, 6)
        if 2 <= k < 11:
            img.rect(c - 2, top + c - 2, 4, 4, 7)
        if k >= 11:
            img.rect(c - 1, top + c - 1, 3, 3, 6)
    return stack


def make_villager(shirt, hair):
    """8×8 の輪切り14段の住人。顔は輪切りの「下辺」（向いている方向）に描く。"""
    stack = Stack(8, 14)
    for k in range(14):
        img, top = stack.layer(k)
        if k < 4:  # 足
            img.rect(2, top + 3, 1, 2, 4)
            img.rect(5, top + 3, 1, 2, 4)
        elif k < 9:  # 胴と腕
            img.rect(2, top + 2, 4, 4, shirt)
            if 5 <= k <= 7:
                img.pset(1, top + 4, 15)
                img.pset(6, top + 4, 15)
        elif k < 13:  # 頭
            img.rect(2, top + 2, 4, 4, 15)
            if k in (11,):
                img.pset(3, top + 5, DOOR)
                img.pset(4, top + 5, DOOR)
            if k >= 11:
                img.rect(2, top + 2, 4, 2, hair)
        else:  # 髪の上
            img.rect(2, top + 2, 4, 4, hair)
    return stack


def make_ground():
    img = pyxel.Image(MAP_W * TILE, MAP_H * TILE)
    for row, line in enumerate(GROUND):
        for col, ch in enumerate(line):
            x, y = col * TILE, row * TILE
            img.rect(x, y, TILE, TILE, GROUND_COLORS[ch])
            if ch == "f":
                for dy in (2, 7, 12):
                    img.rect(x, y + dy, TILE, 2, LEAF)
            elif ch == "=":
                for dx in range(0, TILE, 4):
                    img.line(x + dx, y + 1, x + dx, y + TILE - 2, 2)
                img.rect(x, y, TILE, 1, 2)
                img.rect(x, y + TILE - 1, TILE, 1, 2)
            elif ch == "w" and (row + col) % 3 == 0:
                img.line(x + 4, y + 6, x + 8, y + 6, 7)
    slab = pyxel.Image(MAP_W * TILE, MAP_H * TILE)
    slab.cls(LEAF)
    return img, slab


# ---------------------------------------------------------------------------
# 村の物と住人
# ---------------------------------------------------------------------------


def tile_world(col, row):
    """タイル中心の座標（マップ中心を原点としたピクセル）。"""
    return ((col - MAP_W / 2 + 0.5) * TILE, (row - MAP_H / 2 + 0.5) * TILE)


class Prop:
    """村に置く物。hx / hz は敷地（足元の四角）の半分の幅と奥行き。建物の前後判定に使う。"""

    walks = False

    def __init__(self, stack, wx, wz, heading=0.0, hx=0.0, hz=0.0):
        self.stack = stack
        self.wx = wx
        self.wz = wz
        self.heading = heading
        self.hx = hx
        self.hz = hz
        self.lift = 0


class Walker(Prop):
    """道に沿って決まった道順をぐるぐる歩く（ステップ3の仮）。"""

    walks = True

    def __init__(self, stack, route, speed, offset=0.0):
        self.route = [tile_world(c, r) for c, r in route]
        self.speed = speed
        self.dist = offset
        super().__init__(stack, *self.route[0])

    def update(self):
        self.dist += self.speed
        lengths = []
        for i in range(len(self.route)):
            ax, az = self.route[i]
            bx, bz = self.route[(i + 1) % len(self.route)]
            lengths.append(math.hypot(bx - ax, bz - az))
        d = self.dist % sum(lengths)
        for i, length in enumerate(lengths):
            if d <= length:
                ax, az = self.route[i]
                bx, bz = self.route[(i + 1) % len(self.route)]
                t = d / length
                self.wx = ax + (bx - ax) * t
                self.wz = az + (bz - az) * t
                # 絵の「下辺」が進む向きを向くように回す
                self.heading = math.degrees(math.atan2(-(bx - ax), bz - az))
                break
            d -= length
        self.lift = 1 if int(self.dist / 3) % 2 else 0


class World:
    def __init__(self):
        self.ground, self.slab = make_ground()
        self.props = []
        for name, col, row, w, d, wall, roof, door, height, chimney in BUILDINGS:
            stack = make_building(w, d, wall, roof, door, height, chimney)
            wx, wz = tile_world(col + (w - 1) / 2, row + (d - 1) / 2)
            # 敷地は壁より屋根の張り出し分だけ広く取る
            self.props.append(Prop(stack, wx, wz, hx=w * TILE / 2, hz=d * TILE / 2))
        tree = make_tree()
        for col, row in TREES:
            self.props.append(Prop(tree, *tile_world(col, row)))
        self.props.append(Prop(make_fountain(), *tile_world(6, 6)))

        self.walkers = [
            Walker(make_villager(8, 4), [(3.5, 6), (3.5, 6), (6, 3.5), (8.5, 6), (6, 8.5)], 0.5),
            Walker(make_villager(12, 9), [(0, 6), (10, 6), (13.5, 6), (10, 6)], 0.4, 40),
        ]
        self.props.extend(self.walkers)

    def update(self):
        for w in self.walkers:
            w.update()

    def render(self, dst, angle, zoom=1, fx=0.0, fz=0.0):
        """角度 angle、拡大率 zoom、注目点 (fx, fz) で村を描く。"""
        dst.cls(12)
        w, h = dst.width, dst.height
        cx, cy = w / 2, h / 2 + 8
        cos_a = math.cos(math.radians(angle))
        sin_a = math.sin(math.radians(angle))

        def to_screen(wx, wz):
            rx, rz = wx - fx, wz - fz
            return cx + (rx * cos_a - rz * sin_a) * zoom, cy + (rx * sin_a + rz * cos_a) * zoom

        # 地面の厚み（濃い緑を数枚重ねる）と地面
        gw, gh = self.ground.width, self.ground.height
        gx, gy = to_screen(0, 0)
        for k in range(-5, 0):
            dst.blt(gx - gw / 2, gy - gh / 2 - k * zoom, self.slab, 0, 0, gw, gh, TRANSPARENT, rotate=angle, scale=zoom)
        dst.blt(gx - gw / 2, gy - gh / 2, self.ground, 0, 0, gw, gh, None, rotate=angle, scale=zoom)

        placed = []
        for p in self.props:
            sx, sy = to_screen(p.wx, p.wz)
            reach = p.stack.size * zoom
            if -reach < sx < w + reach and -reach < sy < h + reach + p.stack.count * zoom:
                placed.append((sy, sx, p))
        # 奥（画面の上）から順に描く。歩く人と建物の前後だけは敷地の形で決める
        placed.sort(key=functools.cmp_to_key(lambda a, b: draw_order(a, b, sin_a, cos_a)))

        for sy, sx, p in placed:
            st = p.stack
            rot = angle + p.heading
            half = st.size / 2
            for k in range(st.count):
                img, top = st.layer(k)
                y = sy - half - (k + p.lift) * zoom
                dst.blt(sx - half, y, img, 0, top, st.size, st.size, TRANSPARENT, rotate=rot, scale=zoom)


# ---------------------------------------------------------------------------
# アプリ
# ---------------------------------------------------------------------------


def walker_in_front(walker, prop, sin_a, cos_a):
    """歩く人が建物より手前にいれば True、奥なら False、画面上で重ならなければ None。

    人の足元から画面の奥行き方向に引いた線が敷地の四角を通る範囲を調べる。
    """
    if prop.hx <= 0 or prop.hz <= 0:
        return None
    px, pz = walker.wx - prop.wx, walker.wz - prop.wz
    t_lo, t_hi = -math.inf, math.inf
    for pos, step, half in ((px, sin_a, prop.hx), (pz, cos_a, prop.hz)):
        if abs(step) < 1e-9:
            if abs(pos) > half:
                return None
            continue
        a, b = (-half - pos) / step, (half - pos) / step
        t_lo, t_hi = max(t_lo, min(a, b)), min(t_hi, max(a, b))
    if t_lo > t_hi:
        return None
    return t_hi <= 0


def draw_order(a, b, sin_a, cos_a):
    """placed の要素 (画面 y, 画面 x, 物) どうしの描く順番。"""
    pa, pb = a[2], b[2]
    if pa.walks != pb.walks:
        walker, other = (pa, pb) if pa.walks else (pb, pa)
        front = walker_in_front(walker, other, sin_a, cos_a)
        if front is not None:
            walker_later = 1 if front else -1
            return walker_later if pa.walks else -walker_later
    return (a[0] > b[0]) - (a[0] < b[0])


def screen_to_world(dx, dy, view):
    """画面上の移動量を、地面の上の移動量に直す（描くときの回転の逆）。"""
    cos_a = math.cos(math.radians(view.angle))
    sin_a = math.sin(math.radians(view.angle))
    return (cos_a * dx + sin_a * dy) / view.zoom, (-sin_a * dx + cos_a * dy) / view.zoom


class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Pixel Village (stacking)", fps=30)
        self.world = World()
        self.view = ViewControl(
            ZOOM_LEVELS,
            bounds=(MAP_W * TILE / 2, MAP_H * TILE / 2),
            screen_to_world=screen_to_world,
            button_size=24,
        )
        self.fps = FpsCounter()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.view.update()
        self.world.update()

    def draw(self):
        v = self.view
        self.world.render(pyxel.screen, v.angle, v.zoom, v.fx, v.fz)
        pyxel.text(4, 4, "PIXEL VILLAGE (SPRITE STACKING)", 7)
        self.fps.draw(4, 12)
        v.draw()


if __name__ == "__main__":
    App()
