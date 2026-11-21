"""Pixel Village: AI キャラの一日を眺める箱庭ゲーム"""

import pyxel
from pyxel.cube import Camera, Mat4, Node, Shading, Vec3

from controls import ViewControl
from fps import FpsCounter
from village import MAP_H, MAP_W, TILE, Village

SCREEN_W = 256
SCREEN_H = 192

CAMERA_DISTANCE = 400.0
CAMERA_PITCH = 35.0  # 見下ろす角度（度）
ORTHO_SIZE = 230.0  # 1倍のときに画面の縦に映る広さ（ワールド単位）
ZOOM_LEVELS = (1, 2, 3)


def screen_to_world(dx, dy, view):
    """画面上の移動量を、地面の上の移動量に直す（正射影カメラ用）。"""
    per_pixel = ORTHO_SIZE / view.zoom / SCREEN_H
    yaw = view.angle
    # 画面の右 = カメラの右向き、画面の下 = カメラの手前向き（地面では縦が縮んで見える分を戻す）
    right_x, right_z = pyxel.cos(yaw), -pyxel.sin(yaw)
    back_x, back_z = pyxel.sin(yaw), pyxel.cos(yaw)
    depth = per_pixel / pyxel.sin(CAMERA_PITCH)
    return (
        right_x * dx * per_pixel + back_x * dy * depth,
        right_z * dx * per_pixel + back_z * dy * depth,
    )


class Scene(Node):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.shading = Shading(pyxel.colors)
        self.shading.direction = Vec3(0.5, -1.0, 0.3)

        self.camera = Camera()
        self.camera.clear_color = 12
        self.camera.ortho_size = ORTHO_SIZE
        self.camera.near = 1.0
        self.camera.far = 2000.0

        self.add_child(Village())

    def on_update(self):
        view = self.view
        target = Vec3(view.fx, 0, view.fz)
        horizontal = CAMERA_DISTANCE * pyxel.cos(CAMERA_PITCH)
        eye = target + Vec3(
            pyxel.sin(view.angle) * horizontal,
            CAMERA_DISTANCE * pyxel.sin(CAMERA_PITCH),
            pyxel.cos(view.angle) * horizontal,
        )
        self.camera.transform = Mat4.look_at(eye, target)
        self.camera.ortho_size = ORTHO_SIZE / view.zoom


class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Pixel Village", fps=30)
        self.view = ViewControl(
            ZOOM_LEVELS,
            bounds=(MAP_W * TILE / 2, MAP_H * TILE / 2),
            screen_to_world=screen_to_world,
            rotate_sign=-1.0,
            button_size=18,
        )
        self.scene = Scene(self.view)
        self.fps = FpsCounter()
        pyxel.run(self.update, self.draw)

    def update(self):
        self.view.update()
        self.scene.update()

    def draw(self):
        self.scene.draw(0, 0, pyxel.width, pyxel.height)
        pyxel.text(4, 4, "PIXEL VILLAGE", 7)
        self.fps.draw(4, 12)
        self.view.draw()


App()
