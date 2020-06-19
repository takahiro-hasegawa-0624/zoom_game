# basic
# -*- coding: utf-8 -*-
import numpy as np

# face recognition
import dlib
from imutils import face_utils
import cv2

########↓↓↓追加↓↓↓####################
import math
########↑↑↑追加↑↑↑####################

face_detector = dlib.get_frontal_face_detector()
predictor_path = '/Users/tanakaakira/zoom_game-hasegawa/hasegawa/shape_predictor_68_face_landmarks.dat'
face_predictor = dlib.shape_predictor(predictor_path)

# https://qiita.com/mamon/items/bb2334eef596f8cacd9b
# https://qiita.com/mimitaro/items/bbc58051104eafc1eb38
#https://woraise.com/2019/03/21/desert-shooting/
#https://gist.github.com/radames/1e7c794842755683162b

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
    mag = 1
    img = cv2.resize(img , (int(1600*mag), int(900*mag)))
    #height=img.shape[0]
    #width=img.shape[1]
    
    imgs = divide_img_4(img)
    
    trim_imgs=[[0]]*4
    pos = [[0,0,0,0]]*4
    landmarks = [0]*4
    
    for i, img in enumerate(imgs):
        height=img.shape[0]
        width=img.shape[1]
        # 顔検出
        img_gry = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = face_detector(img_gry, 1)
        if len(faces)==0:
            continue
        face = faces[0]
    
        # 顔のランドマーク検出
        landmark = face_predictor(img_gry, face)
        # 処理高速化のためランドマーク群をNumPy配列に変換(必須)
        landmark = face_utils.shape_to_np(landmark)[60:68]

        img_trim = img[face.top():face.bottom(), face.left():face.right()]
        img_trim = cv2.resize(img_trim , (int(img_trim.shape[1]/mag), int(img_trim.shape[0]/mag)))
        tmp1 = int(img_trim.shape[1]/mag)
        tmp2 = int(img_trim.shape[0]/mag)
        img_trim = cv2.resize(img_trim , (100, 100))
        
        trim_imgs[i] = img_trim
        
        #landmark[:,0] = landmark[:,0] - np.floor(landmark[:,0]/mag)
        #landmark[:,1] = landmark[:,1] - np.floor(landmark[:,1]/mag)
        pos[i] = [int(face.top()/mag), int(face.bottom()/mag), int(face.left()/mag), int(face.right()/mag)]
        landmark[:,0] = pos[i][2] + (-pos[i][2] + np.floor(landmark[:,0]/mag))/tmp1*100
        landmark[:,1] = pos[i][0] + (-pos[i][0] + np.floor(landmark[:,1]/mag))/tmp2*100
        landmarks[i] = landmark
        
        # ランドマーク描画
        #for (x, y) in landmark:
            #cv2.circle(trim_imgs[i], (int(x), int(y)), 3, (0, 0, 255), -1)

    return trim_imgs, np.array(pos), np.array(landmarks)

def capture_trim():
    # カメラ画像の表示 ('q'入力で終了)
    cap = cv2.VideoCapture(0)
    while(True):
        ret, img = cap.read()

        # 顔のランドマーク検出(2.の関数呼び出し)
        img,_,_ = face_detect_trim(img)

        # 結果の表示
        cv2.imshow('img', cv2.resize(img , (int(img.shape[1]*2), int(img.shape[0]*2))))

        # 'q'が入力されるまでループ
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 後処理
    cap.release()
    cv2.destroyAllWindows()
    return None

camera = cv2.VideoCapture(0)
import os


import pygame
from pygame.locals import *
import random
import sys
########↓↓↓追加↓↓↓####################
screenwidth = 1000; screenheight = 800
########↑↑↑追加↑↑↑####################

SCR_RECT = Rect(0, 0, screenwidth, screenheight)


#######↓↓↓追加しました↓↓↓###########
n_apple = 5   #リンゴの数
n_enemy = 5   #敵の数
gameduration = 30000    #ゲームの所要時間(ms)
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
        ###ここからaquiracheが書き直しました
        self.score = score
        ###ここまでaquiracheが書き直しました
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
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("nankadasu")
    all = pygame.sprite.RenderUpdates()
    #aliens = pygame.sprite.Group()  # エイリアングループ
    #beams = pygame.sprite.Group()   # ビームグループ

    ######↓↓↓追加↓↓↓###########
    # 全てのスプライトが入ったスプライトグループの作成
    group_apple_all = pygame.sprite.RenderUpdates()

    # 画面上に表示されているスプライトからなるグループ
    # ゲーム画面に表示するのはこっち
    
    #Texts = pygame.sprite.RenderUpdates()
    # スプライト(リンゴ)の追加
    group_apple_exist = pygame.sprite.RenderUpdates()

    for _ in range(n_apple):
        apple = Apple("/Users/tanakaakira/zoomgame/data/apple.png",1)
        group_apple_all.add(apple)

    # スプライト(敵)の追加
    for _ in range(n_enemy):
        enemy = Apple("/Users/tanakaakira/zoomgame/data/enemy.png",-3)
        group_apple_all.add(enemy)

    ######↑↑↑追加↑↑↑#############

    Player.containers = all
    #Beam.containers = all, beams
    #Alien.containers = all, aliens


    ####kokokaratuika
    #Apple.containers = all
    ####kokomadetuika

    Back_image = load_image("/Users/tanakaakira/zoomgame/data/Aichi.png")
    back_rect = Back_image.get_rect()
    #et = camera.read()
    #frame = capture_trim()
    ret, frame = camera.read()
    screen.fill([0,0,0])
    Taitai=cv2.imread(r"/Users/tanakaakira/zoomgame/data/tai.jpg")

    font = pygame.font.Font(None, 24)  # 経過時間表示の文字


    if type(face_detect_trim(frame)) is tuple:
        frame,_,_  = face_detect_trim(frame)
        _,_,landmark = face_detect_trim(frame)
    else:
        frame = Taitai
        landmark = [[0,0]]
    
    #x_offset=400
    #y_offset=600
    score = 0

    frame = frame.swapaxes(0,1)
    frame = pygame.surfarray.make_surface(frame)
    Player.image = frame
    #Alien.images = split_image(load_image("/Users/tanakaakira/zoomgame/data/Hamburger.png"), 2)
    #Beam.image = load_image("/Users/tanakaakira/zoomgame/data/taitai.png")
    #Taitai=cv2.imread("/Users/tanakaakira/zoomgame/data/tai.jpg")
    Taitai =cv2.resize(Taitai,(240,320))
    player = Player()
    #Alien((50,30))
    clock = pygame.time.Clock()
    try:
        while True:
            time = pygame.time.get_ticks()
            #ret = camera.read()
            #frame = capture_trim()
            ret, frame = camera.read()
            screen.fill([0,0,0])
            
            '''
            if type(face_detect_trim(frame)) is tuple:
                frame,_,_  = face_detect_trim(frame)
                _,_,landmark = face_detect_trim(frame)
            else:
                frame = Taitai
                landmark = [[0,0]]
            '''
            
            frame,_,landmark  = face_detect_trim(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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

            if len(landmark[0])==0:
                landmark = [[0,0]]


            minplot=(player.rect.left + np.min(landmark,axis=0)[0], player.rect.top + np.min(landmark,axis=0)[1])
            maxplot=(player.rect.left + np.max(landmark,axis=0)[0], player.rect.top + np.max(landmark,axis=0)[1])
            
            
            frame = frame.swapaxes(0,1)
            frame = pygame.surfarray.make_surface(frame)
            
            screen.blit(Back_image, back_rect)
            Player.image = frame
            clock.tick(30)

            ###ここからaquiracheが書き直しました
            
            

            if len(group_apple_exist)>0:
                #collision_detection(player, group_apple_exist , minplot, maxplot,screen)
                score = score +collision_detection(player, group_apple_exist , minplot, maxplot,screen)
                #print(score)
                #collision_detection(player, group_apple_exist , minplot, maxplot,screen)
            group_apple_exist.update()
            all.update()
            

            all.draw(screen)
            group_apple_exist.draw(screen)
            text = font.render("Score:" + str(score), True, (120,0,120))
            screen.blit(text, [900,750])
            ###ここまでaquiracheが書き直しました
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            screen.blit(Back_image, back_rect)
            
            

    except (KeyboardInterrupt,SystemExit):
        pygame.quit()
        cv2.destroyAllWindows()

###ここから書き直しました
def collision_detection(player, group_apple_exist , minplot, maxplot,screen):
    """衝突判定"""
    c=0
    for Apple in group_apple_exist:
        #print(Apple.rect.left,Apple.rect.top,c)
        if minplot[0] <= Apple.rect.left + Apple.rect.width and Apple.rect.left  <= maxplot[0] and minplot[1] <= Apple.rect.top + Apple.rect.height and Apple.rect.top <= maxplot[1]:
            Apple.kill()
            #print("食べたね, えらいえらい")
            c += Apple.score
    return c        
###ここまで書き直しました
    
    

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 50  # 移動速度
    reload_time = 20  # リロード時間
    def __init__(self):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.bottom = SCR_RECT.bottom  # プレイヤーが画面の一番下
        self.reload_timer = 0
    def update(self):
        # 押されているキーをチェック
        pressed_keys = pygame.key.get_pressed()
        # 押されているキーに応じてプレイヤーを移動
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        elif pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        elif pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        elif pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)
        #self.rect.clamp_ip(SCR_RECT)

'''
class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    speed = 50  # 移動速度
    animcycle = 50  # アニメーション速度
    frame = 0
    move_width = 700  # 横方向の移動範囲
    prob_beam = 0.3  # ビームを発射する確率
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
    speed = 25  # 移動速度
    def __init__(self, pos):
        # imageとcontainersはmain()でセット
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    def update(self):
        self.rect.move_ip(0, self.speed)  # 下へ移動
        if self.rect.bottom > SCR_RECT.height:  # 下端に達したら除去
            self.kill()

'''


def load_image(filename, colorkey=None):
    """画像をロードして画像と矩形を返す"""
    filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:", filename)
        raise SystemExit(message)
#    image = image.convert()
    image = image.convert_alpha()
    return image

'''
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
'''
if __name__ == "__main__":
    main()