# zoom_game

## 要インストール
### Python モジュール
- cmake (dlibのインストールに必要)
- dlib
  - Python の機械学習モジュール。今回はdlib形式の学習済みモデルを使用する。
- imutils
- pygame
  - Python でゲーム画面を制御するモジュール
- numpy
- opencv-python

### ソフトウェア
- CamTwist
  - 画面キャプチャを仮想カメラとして実現するソフトウェア。

## ゲーム環境の設定
`game/zoom_game.py`のグローバル変数を変更することで、ゲーム環境を指定できる。
変更可能な変数は以下の通り。

- `FLIP_HORIZONTAL`
  - `True`の場合、画面が左右反転する
  - `False`の場合、反転なし
- `camera = cv2.VideoCapture(n)`
  - カメラのポート番号(環境依存)
- `N_PLAYER`
  - プレイヤー数
  - 現在1人・4人に対応
- `SCREEN_WIDTH = 800`
  - ゲーム画面の幅(ピクセル)
- `SCREEN_HEIGHT = 450`
  - ゲーム画面の高さ(ピクセル)
- `FACE_SIZE = 100`
  - ゲーム画面に表示される顔の大きさ(ピクセル)
- `WAITING_TIME = 5000`
  - オブジェクトが出現するまでの時間(ms)
- `GAME_DURATION = WAITING_TIME + 60000`
  - ゲームの継続時間(ms)
- `N_FOOD = int(GAME_DURATION/1000/2)`
  - ゲーム中に出現する加点オブジェクトの総数
- `N_ENEMY = int(GAME_DURATION/1000/4)`
  - ゲーム中に出現する減点オブジェクトの総数
- `spriteduration_min = 10000`
  - オブジェクトの出現時間の最小値(ms)
- `spriteduration_max = 20000`
  - オブジェクトの出現時間の最大値(ms)
