# pixel-village

ドット風の3Dの村で、AI キャラが一日を過ごすのを眺める箱庭ゲーム。仕様書は Claude Docs の「AI箱庭ゲーム 仕様書」にある。

## やりとり

- 返答、コミットメッセージ、PR の本文は日本語で書く。

## 構成

- `pixel_village/main.py` — ゲーム本体。画面とカメラ（Pyxel 3 の `pyxel.cube` を使う）
- `pixel_village/village.py` — 村のマップ（地面の文字地図 `GROUND`、建物の一覧 `BUILDINGS`、木の位置 `TREES`）
- `pixel_village/stacking.py` — スプライトスタッキング版の試作（同じ地図を2D の輪切り重ねで描く）。`/stacking/` で公開
- `pixel_village/fps.py` — 画面の隅に FPS を出す（描き方の比較用、一時的）
- `.github/workflows/pages.yml` — `main` への push で HTML に書き出し、GitHub Pages に公開する

## 開発の注意点

- Pyxel は 3.0.3 に固定している。上げるときは `pages.yml` の版も合わせる。
- AI で作る予定やセリフは、事前に生成してデータとしてゲームに同梱する（Pages は静的サイトなので、実行中に API は呼ばない）。
- 動作確認は Web 版で行う: `pyxel package pixel_village pixel_village/main.py` → `pyxel app2html pixel_village.pyxapp` で HTML を作り、ローカルの HTTP サーバーと Playwright で開いてスクリーンショットを撮る。
