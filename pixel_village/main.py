"""Pixel Village: AI キャラの一日を眺める箱庭ゲーム"""

import pyxel
from pyxel.cube import Camera, Mat4, Node, Shading, Vec3

from village import Village

SCREEN_W = 256
SCREEN_H = 192

CAMERA_DISTANCE = 400.0
CAMERA_PITCH = 35.0  # 見下ろす角度（度）
AUTO_ROTATE_SPEED = 0.15  # 1フレームで回る角度（度）
AUTO_ROTATE_DELAY = 90  # 指を離してから自動回転に戻るまでのフレーム数


class Scene(Node):
    def __init__(self):
        super().__init__()
        self.shading = Shading(pyxel.colors)
        self.shading.direction = Vec3(0.5, -1.0, 0.3)

        self.camera = Camera()
        self.camera.clear_color = 12
        self.camera.ortho_size = 230.0
        self.camera.near = 1.0
        self.camera.far = 2000.0

        self.yaw = 30.0
        self.drag_x = None
        self.idle = AUTO_ROTATE_DELAY

        self.add_child(Village())

    def on_update(self):
        # ドラッグ（スマホは指でなぞる）で回す。離してしばらくすると自動で回る。
        if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if self.drag_x is not None:
                self.yaw -= (pyxel.mouse_x - self.drag_x) * 0.8
            self.drag_x = pyxel.mouse_x
            self.idle = 0
        else:
            self.drag_x = None
            self.idle += 1
            if self.idle >= AUTO_ROTATE_DELAY:
                self.yaw += AUTO_ROTATE_SPEED

        horizontal = CAMERA_DISTANCE * pyxel.cos(CAMERA_PITCH)
        eye = Vec3(
            pyxel.sin(self.yaw) * horizontal,
            CAMERA_DISTANCE * pyxel.sin(CAMERA_PITCH),
            pyxel.cos(self.yaw) * horizontal,
        )
        self.camera.transform = Mat4.look_at(eye, Vec3.ZERO)


class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Pixel Village", fps=30)
        self.scene = Scene()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.scene.update()

    def draw(self):
        self.scene.draw(0, 0, pyxel.width, pyxel.height)
        pyxel.text(4, 4, "PIXEL VILLAGE", 7)


App()
