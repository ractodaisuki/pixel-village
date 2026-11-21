"""眺め方の操作（回転・拡大・移動）。pyxel.cube 版とスプライトスタッキング版の両方で使う。

- 画面の「＋」「−」ボタンかマウスホイールで拡大・縮小
- 1倍のときはドラッグで回転、拡大中はドラッグで見る場所を動かす
- 「＜」「＞」ボタンは押している間ずっと回る
- 1倍で何も触らずにしばらくたつと、自動でゆっくり回る

Pyxel はタッチを1本指のマウスとして受け取るので、ピンチ操作は使えない。
"""

import pyxel

AUTO_ROTATE_SPEED = 0.15  # 1フレームで回る角度（度）
AUTO_ROTATE_DELAY = 90  # 触るのをやめてから自動回転に戻るまでのフレーム数
DRAG_ROTATE_SPEED = 0.8  # ドラッグ1ピクセルで回る角度（度）
BUTTON_ROTATE_SPEED = 2.0  # 回転ボタンを押している間、1フレームで回る角度（度）


class Button:
    def __init__(self, x, y, size, label):
        self.x, self.y, self.size, self.label = x, y, size, label

    def hit(self, mx, my):
        return self.x <= mx < self.x + self.size and self.y <= my < self.y + self.size

    def draw(self, pressed):
        s = self.size
        pyxel.rect(self.x, self.y, s, s, 5 if pressed else 1)
        pyxel.rectb(self.x, self.y, s, s, 7)
        pyxel.text(self.x + s // 2 - 1, self.y + s // 2 - 2, self.label, 7)


class ViewControl:
    """角度・拡大率・注目点（見ている場所のワールド座標 fx, fz）を持つ。

    screen_to_world(dx, dy, view) は、画面上の移動量（ピクセル）を地面の上の移動量 (dwx, dwz) に
    直す関数。描き方ごとに違うので、それぞれの版から渡す。
    rotate_sign はドラッグの向きと回る向きを合わせるための符号。
    """

    def __init__(self, zoom_levels, bounds, screen_to_world, rotate_sign=1.0, angle=30.0, button_size=20):
        self.zoom_levels = zoom_levels
        self.zoom_index = 0
        self.half_w, self.half_d = bounds
        self.screen_to_world = screen_to_world
        self.rotate_sign = rotate_sign
        self.angle = angle
        self.fx = 0.0
        self.fz = 0.0
        self.idle = AUTO_ROTATE_DELAY
        self.drag = None  # ドラッグ中の直前のマウス位置
        self.held = None  # 押している最中のボタン

        s, m = button_size, 4
        w, h = pyxel.width, pyxel.height
        self.btn_left = Button(m, h - s - m, s, "<")
        self.btn_right = Button(m * 2 + s, h - s - m, s, ">")
        self.btn_out = Button(w - (s + m) * 2, h - s - m, s, "-")
        self.btn_in = Button(w - s - m, h - s - m, s, "+")
        self.buttons = [self.btn_left, self.btn_right, self.btn_out, self.btn_in]

    @property
    def zoom(self):
        return self.zoom_levels[self.zoom_index]

    def set_zoom_index(self, index):
        self.zoom_index = max(0, min(len(self.zoom_levels) - 1, index))
        if self.zoom_index == 0:
            self.fx = self.fz = 0.0
        self.clamp_focus()

    def clamp_focus(self):
        self.fx = max(-self.half_w, min(self.half_w, self.fx))
        self.fz = max(-self.half_d, min(self.half_d, self.fz))

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        pressing = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.held = next((b for b in self.buttons if b.hit(mx, my)), None)
            if self.held is self.btn_in:
                self.set_zoom_index(self.zoom_index + 1)
            elif self.held is self.btn_out:
                self.set_zoom_index(self.zoom_index - 1)
            self.drag = None if self.held else (mx, my)
        elif not pressing:
            self.held = None
            self.drag = None

        if pressing:
            self.idle = 0
            if self.held is self.btn_left:
                self.angle -= BUTTON_ROTATE_SPEED * self.rotate_sign
            elif self.held is self.btn_right:
                self.angle += BUTTON_ROTATE_SPEED * self.rotate_sign
            elif self.drag is not None:
                dx, dy = mx - self.drag[0], my - self.drag[1]
                if self.zoom_index == 0:
                    self.angle += dx * DRAG_ROTATE_SPEED * self.rotate_sign
                else:
                    dwx, dwz = self.screen_to_world(dx, dy, self)
                    self.fx -= dwx
                    self.fz -= dwz
                    self.clamp_focus()
                self.drag = (mx, my)
        else:
            self.idle += 1
            if self.zoom_index == 0 and self.idle >= AUTO_ROTATE_DELAY:
                self.angle += AUTO_ROTATE_SPEED * self.rotate_sign

        wheel = pyxel.mouse_wheel
        if wheel:
            self.set_zoom_index(self.zoom_index + (1 if wheel > 0 else -1))
            self.idle = 0

        for key, step in ((pyxel.KEY_EQUALS, 1), (pyxel.KEY_PLUS, 1), (pyxel.KEY_MINUS, -1)):
            if pyxel.btnp(key):
                self.set_zoom_index(self.zoom_index + step)

    def draw(self):
        for b in self.buttons:
            b.draw(b is self.held)
        if self.zoom_index:
            label = f"x{self.zoom:g}"
            pyxel.text(self.btn_out.x - len(label) * 4 - 4, self.btn_out.y + self.btn_out.size // 2 - 2, label, 7)
