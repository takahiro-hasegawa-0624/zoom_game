# basic
import numpy as np

# face recognition
import dlib
from imutils import face_utils
import cv2









########↓↓↓追加↓↓↓####################
import math
########↑↑↑追加↑↑↑####################













face_detector = dlib.get_frontal_face_detector()
predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_predictor = dlib.shape_predictor(predictor_path)

# https://qiita.com/mamon/items/bb2334eef596f8cacd9b
# https://qiita.com/mimitaro/items/bbc58051104eafc1eb38
def face_detect_trim(img):
    '''
    左上・右上・左下・右下に4人が写っている画像から、4人の顔をトリミングし、顔の座標と口の座標を計算する
    Parameters
    ----------
    img : np.ndarray : (height, width, color)
        画像
    Returns
    -------
    imgs : list : (player, height, width, color)
        顔の部分をトリミングした画像。(左上の人・右上の人・左下の人・右下の人)の順に格納されている。
    pos : np.array : (player, [top, bottom, left, light])
        4分割したそれぞれの画像の左上を原点とした、トリミングした画像の座標が格納されている。
    landmarks : np.array : (player, the number of landmarks, position)
        4分割したそれぞれの画像の左上を原点とした、口の座標が格納されている。
    '''
    height=img.shape[0]
    width=img.shape[1]
    
    # 顔検出
    img_gry = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_detector(img_gry, 1)

    player=0 # playerをとりあえず0としておく。
    
    imgs=[[0]]*4
    pos = [[0,0,0,0]]*4
    landmarks = [0]*4
    
    # 検出した全顔に対して処理
    for i, face in enumerate(faces):
        # 顔のランドマーク検出
        landmark = face_predictor(img_gry, face)
        # 処理高速化のためランドマーク群をNumPy配列に変換(必須)
        landmark = face_utils.shape_to_np(landmark)[60:68]
        
        # 顔が画面の第何象限にあるかでプレイヤー番号をつける
        # 左上 : 0, 右上 : 1, 左下 : 2, 右下 : 3 をインデックスとしている
        if int(face.top()/(height/2)) >= 1:
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
        img_trim = cv2.resize(img_trim, (int(img_trim.shape[1]/width*800), int(img_trim.shape[0]/height*450)))
        imgs[player] = img_trim
        
        landmark[:,0] -= int(face.left()/(width/2))*int((width/2))
        landmark[:,1] -= int(face.top()/(height/2))*int((height/2))
        pos[player] = [face.top()%(int(height/2)), face.bottom()%(int(height/2))+1, face.left()%(int(width/2)), face.right()%(int(width/2))+1]
        landmarks[player] = landmark
        
        # ランドマーク描画
        for (x, y) in landmark:
            cv2.circle(imgs[player], (x, y), 3, (0, 0, 255), -1)
            
        if i == 3:
            break

    return imgs, np.array(pos), np.array(landmarks)

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

#if __name__ == "__main__":
    #capture_trim()

#face_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_frontalface_default.xml'
#eye_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_eye.xml'
#mouth_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_mcs_mouth.xml'
face_cascade_path = r'../game_base/data/haar_face.xml'
eye_cascade_path = r'../game_base/data/haar_eye.xml'
mouth_cascade_path = r'../game_base/data/haar_mouth.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)

import os

import pygame
from pygame.locals import *
import random
import sys













########↓↓↓追加↓↓↓####################
import math
screenwidth = 800; screenheight = 450
SCR_RECT = Rect(0, 0, screenwidth, screenheight)
########↑↑↑追加↑↑↑####################















def mosaic(src, ratio=0.08):
    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
def mosaic_area(src, x, y, width, height, ratio=0.08):
    dst = src.copy()
    dst[y:y + height, x:x + width] = mosaic(dst[y:y + height, x:x + width], ratio)
    return dst












#######↓↓↓追加しました↓↓↓###########
n_apple = 5   #リンゴの数
n_enemy = 5   #敵の数
gameduration = 20000    #ゲームの所要時間(ms)
appleduration_min = 20000   
appleduration_max = 21000
v_apple = 20   #リンゴの速さ(pixel / frame)

enemyduration_min = 20000   
enemyduration_max = 21000
v_enemy = 40   #敵の速さ(pixel / frame)

# リンゴおよび敵のクラス
class Apple(pygame.sprite.Sprite):
    # スプライトを作成(画像ファイル名, 獲得スコア)
    def __init__(self, filename, score):
        #出現方向
        appeardirection = np.random.choice(['l','r','u','d'])

        theta = (np.random.random_sample() * (2.0 / 3.0) + (1.0 / 6.0)) * math.pi
        vx_init = v_apple * math.cos(theta)
        vy_init = v_apple * math.sin(theta)

        #初期位置と初速
        if appeardirection =='u':
            x_init = np.random.randint(0,screenwidth)
            y_init = 0
        elif appeardirection == 'd':
            x_init = np.random.randint(0,screenwidth)
            y_init = screenheight
            vy_init = -vy_init
        elif appeardirection == 'l':
            x_init = 0
            y_init = np.random.randint(0,screenheight)
            vx_init,vy_init = vy_init,vx_init
        else:
            x_init = screenwidth
            y_init = np.random.randint(0,screenheight)
            vx_init,vy_init = -vy_init,vx_init

        #出現時刻
        appeartime = np.random.randint(2000,gameduration)
        #消滅時刻　　　　
        disappeartime = min(gameduration, appeartime + np.random.randint(appleduration_min,appleduration_max))

        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        w = self.image.get_width()
        h = self.image.get_height()
        self.rect = Rect(x_init, y_init, w, h)
        self.vx = vx_init
        self.vy = vy_init
        self.appeartime = appeartime
        self.disappeartime = disappeartime
        self.exist = False

    def update(self):
        if self.exist:
            self.rect.move_ip(self.vx, self.vy)
        # 壁と衝突時の処理(跳ね返り)
        if self.rect.left < 0 or self.rect.right > screenwidth:
            self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > screenheight:
            self.vy = -self.vy
        # 壁と衝突時の処理(壁を超えないように)
        self.rect = self.rect.clamp(SCR_RECT)
#######↑↑↑追加しました↑↑↑###########














def main():
    camera = cv2.VideoCapture(0)
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("nankadasu")
    all = pygame.sprite.RenderUpdates()
















######↓↓↓追加↓↓↓###########
    # 全てのスプライトが入ったスプライトグループの作成
    group_apple_all = pygame.sprite.RenderUpdates()

    # 画面上に表示されているスプライトからなるグループ
    # ゲーム画面に表示するのはこっち
    group_apple_exist = pygame.sprite.RenderUpdates()

    # スプライト(リンゴ)の追加
    for _ in range(n_apple):
        apple = Apple("apple.png",1)
        group_apple_all.add(apple)

    # スプライト(敵)の追加
    for _ in range(n_enemy):
        enemy = Apple("enemy.png",-3)
        group_apple_all.add(enemy)
######↑↑↑追加↑↑↑#############



















    clock = pygame.time.Clock()
    aliens = pygame.sprite.Group()  # エイリアングループ
    beams = pygame.sprite.Group()   # ビームグループ
    Player.containers = all
    Beam.containers = all, beams
    Alien.containers = all, aliens
    #Back_image = load_image("../images/bg.png")
    #back_rect = Back_image.get_rect()
    #et = camera.read()
    #frame = capture_trim()
    ret, frame = camera.read()
    screen.fill([0,0,0])

    x_offset=400
    y_offset=600

    Alien.images = split_image(load_image("images/hamburger.png"), 2)
    Beam.image = load_image("images/bullet.png")
    Taitai=cv2.imread("images/owl.jpg")
    Taitai =cv2.resize(Taitai,(240,320))
    
    imgs, pos_prev, landmarks_prev  = face_detect_trim(frame)
    
    for i in range(1):
        frame = imgs[i]
        
        if len(frame)==1: #顔が認識されないに表示する画像を指定
            frame=Taitai
        frame = frame.swapaxes(0,1)
        frame = pygame.surfarray.make_surface(frame)
        Player.image = frame
        player = Player(pos_prev[i],pos_prev[i])
        
    Alien((50,30))
    clock = pygame.time.Clock()
    try:
        while True:
            time = pygame.time.get_ticks()
            ret, frame = camera.read()
            screen.fill([0,0,0])
            imgs, pos, landmarks  = face_detect_trim(frame)











#####↓↓↓追加↓↓↓############
            for obj in group_apple_all:
                    # obj.appeartimeになったらgroup_apple_existに入れる
                if obj.exist == False and time >= obj.appeartime:
                    group_apple_exist.add(obj)
                    obj.exist = True
                # obj.disappeartimeになったらgroup_apple_existから消す
                if obj.exist == True and time > obj.disappeartime:
                    group_apple_exist.remove(obj)
                    obj.exist = False

            # スプライトグループを更新
            group_apple_exist.update()
            # スプライトを描画
            group_apple_exist.draw(screen)
######↑↑↑追加↑↑↑#############













            
            for i in range(1):
                frame = imgs[i]
                if len(frame)==1:
                    frame=Taitai

                frame = frame.swapaxes(0,1)
                frame = pygame.surfarray.make_surface(frame)
                #screen.blit(Back_image, back_rect)
                Player.image = frame
                player.pos_update(pos[i], pos_prev[i])
                clock.tick(40)
                all.update()
                collision_detection(player, aliens, beams)
                all.draw(screen)
                pygame.display.update()
                
            pos_prev = pos
            landmarks_prev = landmarks

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            #screen.blit(Back_image, back_rect)
    except (KeyboardInterrupt,SystemExit):
        pygame.quit()
        cv2.destroyAllWindows()
        
        
def collision_detection(player, aliens, beams):
    """衝突判定"""
    # プレイヤーとビームの衝突判定
    beam_collided = pygame.sprite.spritecollide(player, beams, True)

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 30  # 移動速度
    reload_time = 15  # リロード時間
    def __init__(self, pos, pos_prev):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.top = pos[0]
        self.rect.left = pos[2]
        self.reload_timer = 0
        self.pos=pos
        self.pos_prev=pos_prev
    def pos_update(self,pos, pos_prev):
        self.pos=pos
        self.pos_prev=pos_prev
    def update(self):
        self.rect.move_ip(self.pos[0]-self.pos_prev[0], self.pos[1]-self.pos_prev[1])

class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    speed = 50  # 移動速度
    animcycle = 50  # アニメーション速度
    frame = 0
    move_width = 700  # 横方向の移動範囲
    prob_beam = 0.05  # ビームを発射する確率
    def __init__(self, pos):
        # imagesとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.left = pos[0]  # 移動できる左端
        self.right = self.left + self.move_width  # 移動できる右端
    def update(self):
        # 横方向への移動
        self.rect.move_ip(self.speed, 0)
        if self.rect.center[0] < self.left or self.rect.center[0] > self.right:
            self.speed = -self.speed
        # ビームを発射
        if random.random() < self.prob_beam:
            Beam(self.rect.center)
        # キャラクターアニメーション
        self.frame += 1
#        self.image = self.images[self.frame/self.animcycle%2]
        self.image = self.images[self.frame//self.animcycle%2]

class Beam(pygame.sprite.Sprite):
    """エイリアンが発射するビーム"""
    speed = 5  # 移動速度
    def __init__(self, pos):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(0, self.speed)  # 下へ移動
        if self.rect.bottom > SCR_RECT.height:  # 下端に達したら除去
            self.kill()

def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:", filename)
        raise SystemExit(message)
#    image = image.convert()
    image = image.convert_alpha()
    return image

def split_image(image, n):
    """横に長いイメージを同じ大きさのn枚のイメージに分割
    分割したイメージを格納したリストを返す"""
    image_list = []
    w = image.get_width()
    h = image.get_height()
    w1 = w / n
#    for i in range(0, w, w1):
    for i in range(0, w, 22):        
        surface = pygame.Surface((w1,h))
        surface.blit(image, (0,0), (i,0,w1,h))
        surface.set_colorkey(surface.get_at((0,0)), RLEACCEL)
        surface.convert()
        image_list.append(surface)
    return image_list

def load_sound(filename):
    filename = os.path.join("data", filename)
    return pygame.mixer.Sound(filename)

if __name__ == "__main__":
    main()