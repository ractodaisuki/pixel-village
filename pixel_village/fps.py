"""画面の隅に実際のフレーム数（1秒あたり）を出す。描き方の重さを比べるための一時的なもの。"""

import time

import pyxel


class FpsCounter:
    def __init__(self, interval=2.0):
        self.interval = interval
        self.frames = 0
        self.start = time.time()
        self.value = 0.0

    def draw(self, x, y, color=7):
        self.frames += 1
        elapsed = time.time() - self.start
        if elapsed >= self.interval:
            self.value = self.frames / elapsed
            self.frames = 0
            self.start = time.time()
        pyxel.text(x, y, f"FPS {self.value:.1f}", color)
