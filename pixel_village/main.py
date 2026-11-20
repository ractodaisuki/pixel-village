"""Pixel Village: AI キャラの一日を眺める箱庭ゲーム（ステップ1: 空のプロジェクト）"""

import pyxel
from pyxel.cube import Camera, Mat4, Node, Shading, Vec3

SCREEN_W = 256
SCREEN_H = 192


class Ground(Node):
    """村の地面。今は芝生の板と、目印の家を1軒置くだけ。"""

    def on_draw(self):
        # 芝生
        self.box(Mat4.from_translation(Vec3(0, -2, 0)), Vec3(160, 4, 160), 11)
        # 家の壁と屋根
        self.box(Mat4.from_translation(Vec3(0, 12, 0)), Vec3(28, 24, 24), 15)
        self.box(Mat4.from_translation(Vec3(0, 28, 0)), Vec3(32, 8, 28), 8)


class Scene(Node):
    def __init__(self):
        super().__init__()
        self.shading = Shading(pyxel.colors)
        self.camera = Camera()
        self.camera.clear_color = 12
        self.add_child(Ground())

    def on_update(self):
        # カメラを村の周りでゆっくり回す
        angle = pyxel.frame_count * 0.3
        eye = Vec3(pyxel.sin(angle) * 160, 110, pyxel.cos(angle) * 160)
        self.camera.transform = Mat4.look_at(eye, Vec3(0, 8, 0))


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
