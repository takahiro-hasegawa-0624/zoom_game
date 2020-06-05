# basic
import numpy as np

# face recognition
import dlib
from imutils import face_utils
import cv2

face_detector = dlib.get_frontal_face_detector()
predictor_path = '/Users/takahiro/Downloads/shape_predictor_68_face_landmarks.dat'
face_predictor = dlib.shape_predictor(predictor_path)

# https://qiita.com/mamon/items/bb2334eef596f8cacd9b
# https://qiita.com/mimitaro/items/bbc58051104eafc1eb38
def face_detect_trim(img):
    # 顔検出
    img_gry = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_detector(img_gry, 1)

    pos = [0,0,0,0]
    landmark = [[]]
    # 検出した全顔に対して処理
    for face in faces:
        # 顔のランドマーク検出
        landmark = face_predictor(img_gry, face)
        # 処理高速化のためランドマーク群をNumPy配列に変換(必須)
        landmark = face_utils.shape_to_np(landmark)[60:68]

        img = img[face.top():face.bottom(), face.left():face.right()]
        #cv2.rectangle(img, tuple([face.left(),face.top()]), tuple([face.right(),face.bottom()]), (0, 0,255), thickness=2)
        
        landmark[:,0] -= face.left()
        landmark[:,1] -= face.top()
        pos.append([face.top(),face.bottom(),face.left(),face.right()])
        # ランドマーク描画
        for (x, y) in landmark:
            cv2.circle(img, (x, y), 3, (0, 0, 255), -1)

        break

    return img, pos, landmark

def capture_trim():
    # カメラ画像の表示 ('q'入力で終了)
    cap = cv2.VideoCapture(0)
    while(True):
        ret, img = cap.read()
        #img = cv2.resize(img , (int(img.shape[1]), int(img.shape[0])))

        # 顔のランドマーク検出(2.の関数呼び出し)
        img,_,_ = face_detect_trim(img)
        #img = face_recog(img)

        # 結果の表示
        cv2.imshow('img', cv2.resize(img , (int(img.shape[1]*2), int(img.shape[0]*2))))
        #cv2.imshow('img', img)

        # 'q'が入力されるまでループ
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 後処理
    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    capture_trim()