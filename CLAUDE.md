# pixel-village

ドット風の3Dの村で、AI キャラが一日を過ごすのを眺める箱庭ゲーム。仕様書は Claude Docs の「AI箱庭ゲーム 仕様書」にある。

## やりとり

- 返答、コミットメッセージ、PR の本文は日本語で書く。

## 構成

- `pixel_village/main.py` — ゲーム本体（Pyxel 3 の `pyxel.cube` を使う）
- `.github/workflows/pages.yml` — `main` への push で HTML に書き出し、GitHub Pages に公開する

## 開発の注意点

- Pyxel は 3.0.3 に固定している。上げるときは `pages.yml` の版も合わせる。
- AI で作る予定やセリフは、事前に生成してデータとしてゲームに同梱する（Pages は静的サイトなので、実行中に API は呼ばない）。
- 動作確認は Web 版で行う: `pyxel package pixel_village pixel_village/main.py` → `pyxel app2html pixel_village.pyxapp` で HTML を作り、ローカルの HTTP サーバーと Playwright で開いてスクリーンショットを撮る。
