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
    #画像を縦2つ×横2つに4分割。[左上, 右上, 左下, 右下]の順に格納した配列を返す。
    hight=img.shape[0]
    width=img.shape[1]
    
    # 顔検出
    img_gry = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_detector(img_gry, 1)

    player=0
    imgs=[0]*4
    pos = [0]*4
    landmarks = [0]*4
    # 検出した全顔に対して処理
    for face in faces[:4]:
        # 顔のランドマーク検出
        landmark = face_predictor(img_gry, face)
        # 処理高速化のためランドマーク群をNumPy配列に変換(必須)
        landmark = face_utils.shape_to_np(landmark)[60:68]
        
        if int(face.top()/(hight/2)) >= 1:
            if int(face.left()/(width/2)) >= 1:
                player = 3
            else:
                player = 2
        else:
            if int(face.left()/(width/2)) >= 1:
                player = 1
            else:
                player = 0

        img_trim = img[face.top():face.bottom(), face.left():face.right()]
        imgs[player] = img_trim
        #cv2.rectangle(img, tuple([face.left(),face.top()]), tuple([face.right(),face.bottom()]), (0, 0,255), thickness=2)
        
        landmark[:,0] -= int(face.left()/(width/2))*int((width/2))
        landmark[:,1] -= int(face.top()/(hight/2))*int((hight/2))
        pos[player] = [face.top()%(int(hight/2)), face.bottom()%(int(hight/2))+1, face.left()%(int(width/2)), face.right()%(int(width/2))+1]
        landmarks[player] = landmark
        
        print(player)
        # ランドマーク描画
        for (x, y) in landmark:
            cv2.circle(imgs[player], (x, y), 3, (0, 0, 255), -1)

    return imgs, np.array(pos), np.array(landmarks), player

def capture_trim():
    # カメラ画像の表示 ('q'入力で終了)
    cap = cv2.VideoCapture(1)
    while(True):
        ret, img = cap.read()
        #img = cv2.resize(img , (int(img.shape[1]), int(img.shape[0])))
        
        #4分割するsomethingを作りたい
        
        # 顔のランドマーク検出
        img,pos,landmark,player_num = face_detect_trim(img)
        #img = face_recog(img)

        # 結果の表示
        #cv2.imshow('img', cv2.resize(img , (int(img.shape[1]*2), int(img.shape[0]*2))))
        cv2.imshow('img', img[player_num])

        # 'q'が入力されるまでループ
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 後処理
    cap.release()
    cv2.destroyAllWindows()
    return None

if __name__ == "__main__":
    capture_trim()