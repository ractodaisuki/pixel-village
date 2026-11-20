# Pixel Village

ドット風の3Dの村で、AI キャラが一日を過ごすのを眺める箱庭ゲーム。[Pyxel](https://github.com/kitao/pyxel) 3 の `pyxel.cube` で作っています。

## 遊ぶ

GitHub Pages で公開しています: https://ractodaisuki.github.io/pixel-village/

## 手元で動かす

```sh
pip install pyxel==3.0.3
pyxel run pixel_village/main.py
```

## 公開の仕組み

`main` に push すると、GitHub Actions（`.github/workflows/pages.yml`）が HTML に書き出して GitHub Pages に公開します。
