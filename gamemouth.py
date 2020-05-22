import numpy as np
import cv2
import os
face_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_frontalface_default.xml'
eye_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_eye.xml'
mouth_cascade_path = r'C:\Users\81903\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\opencv-master\data\haarcascades/haarcascade_mcs_mouth.xml'
face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
mouth_cascade = cv2.CascadeClassifier(mouth_cascade_path)

camera = cv2.VideoCapture(0)


assert os.path.isfile(face_cascade_path), 'haarcascade_frontalface_default.xml がない'
assert os.path.isfile(mouth_cascade_path), 'haarcascade_mouth.xml がない'

import pygame
from pygame.locals import *
import random
import sys
SCR_RECT = Rect(0, 0, 1000, 800)
def mosaic(src, ratio=0.08):
    small = cv2.resize(src, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_NEAREST)
    return cv2.resize(small, src.shape[:2][::-1], interpolation=cv2.INTER_NEAREST)
def mosaic_area(src, x, y, width, height, ratio=0.08):
    dst = src.copy()
    dst[y:y + height, x:x + width] = mosaic(dst[y:y + height, x:x + width], ratio)
    return dst

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCR_RECT.size)
    pygame.display.set_caption("nankadasu")
    all = pygame.sprite.RenderUpdates()
    aliens = pygame.sprite.Group()  # エイリアングループ
    beams = pygame.sprite.Group()   # ビームグループ
    Player.containers = all
    Beam.containers = all, beams
    Alien.containers = all, aliens
    Back_image = load_image("/Users/81903/Downloads/data/Aichi.png ")
    back_rect = Back_image.get_rect()
    ret, frame = camera.read()
    screen.fill([0,0,0])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame =cv2.resize(frame,(750,450))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    x_offset=400
    y_offset=600
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    
    for x, y, w, h in faces:
        #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = frame[y: y + h, x: x + w]
        face_gray = gray[y: y + h, x: x + w]
        eye = eye_cascade.detectMultiScale(face_gray)
        for (ex, ey, ew, eh) in eye:
            cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 0, 0), -1)
        mouth = mouth_cascade.detectMultiScale(face_gray)
        for (ex, ey, ew, eh) in mouth:
            cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (255, 50, 0), -1)
        frame = mosaic_area(frame, x,y,w,h)
    if len(faces) >0:
        for rect in faces:
            frame = frame[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    else :
        frame = Taitai
    frame = frame.swapaxes(0,1)
    frame = pygame.surfarray.make_surface(frame)
    #faces = faces.swapaxes(0,1)
    #faces = pygame.surfarray.make_surface(faces)
    Player.image = frame
    Alien.images = split_image(load_image("Hamburger.png"), 2)
    Beam.image = load_image("taitai.png")
    Taitai=cv2.imread("/Users/81903/Downloads/data/tai.jpg")
    kao=cv2.imread("/Users/81903/Downloads/data/face.png")
    Taitai =cv2.resize(Taitai,(240,320))
    player = Player()
    Alien((50,30))
    clock = pygame.time.Clock()
    try:
        while True:
            ret, frame = camera.read()
            screen.fill([0,0,0])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame =cv2.resize(frame,(750,450))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            
            for x, y, w, h in faces:
                #cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                face = frame[y: y + h, x: x + w]
                face_gray = gray[y: y + h, x: x + w]
                eye = eye_cascade.detectMultiScale(face_gray)
                for (ex, ey, ew, eh) in eye:
                    cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (0, 0, 0), -1)
                mouth = mouth_cascade.detectMultiScale(face_gray)
                for (ex, ey, ew, eh) in mouth:
                    cv2.rectangle(face, (ex, ey), (ex + ew, ey + eh), (255, 50, 0), -1)
                frame = mosaic_area(frame, x,y,w,h)
            if len(faces) >0:
                for rect in faces:
                    frame = frame[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
            else :
                frame = Taitai
            frame = frame.swapaxes(0,1)
            frame = pygame.surfarray.make_surface(frame)
            #faces = faces.swapaxes(0,1)
            #faces = pygame.surfarray.make_surface(faces)
            screen.blit(Back_image, back_rect)
            Player.image = frame
            clock.tick(40)
            all.update()
            collision_detection(player, aliens, beams)
            all.draw(screen)
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
def collision_detection(player, aliens, beams):
    """衝突判定"""
    # プレイヤーとビームの衝突判定
    beam_collided = pygame.sprite.spritecollide(player, beams, True)

class Player(pygame.sprite.Sprite):
    """自機"""
    speed = 30  # 移動速度
    reload_time = 15  # リロード時間
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
        self.rect.clamp_ip(SCR_RECT)

class Alien(pygame.sprite.Sprite):
    """エイリアン"""
    speed = 15  # 移動速度
    animcycle = 18  # アニメーション速度
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
    filename = os.path.join("data", filename)
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