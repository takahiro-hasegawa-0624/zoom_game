# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
import numpy as np
import math

screenheight = 720
screenwidth = 1440
SCREEN = Rect(0, 0, screenwidth, screenheight)   # 画面サイズ
n_apple = 5   #リンゴの数
n_enemy = 5   #敵の数
gameduration = 20000    #ゲームの所要時間(ms)
appleduration_min = 20000   
appleduration_max = 21000
v_apple = 20   #リンゴの速さ(pixel / frame)

enemyduration_min = 20000   
enemyduration_max = 21000
v_enemy = 40   #敵の速さ(pixel / frame)

# スプライトのクラス
class Sprite(pygame.sprite.Sprite):
    # スプライトを作成(画像ファイル名, 位置xy(x, y), 速さvxy(vx, vy), 回転angle, 出現消滅時刻duration(appeartime, disappeartime))
    def __init__(self, filename, xy, vxy, angle, duration, exist):
        x, y = xy
        vx, vy = vxy
        appeartime, disappeartime = duration
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        if angle != 0: self.image = pygame.transform.rotate(self.image, angle)
        w = self.image.get_width()
        h = self.image.get_height()
        self.rect = Rect(x, y, w, h)
        self.vx = vx
        self.vy = vy
        self.angle = angle
        self.appeartime = appeartime
        self.disappeartime = disappeartime
        self.exist = False

    def update(self):
        if self.exist:
            self.rect.move_ip(self.vx, self.vy)
        # 壁と衝突時の処理(跳ね返り)
        if self.rect.left < 0 or self.rect.right > SCREEN.width:
            self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > SCREEN.height:
            self.vy = -self.vy
        # 壁と衝突時の処理(壁を超えないように)
        self.rect = self.rect.clamp(SCREEN)


# メイン
def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    # 全てのスプライトが入ったスプライトグループの作成
    group = pygame.sprite.RenderUpdates()

    # 画面上に表示されているスプライトからなるグループ
    # ゲーム画面に表示するのはこっち
    group_exist = pygame.sprite.RenderUpdates()

    # スプライト(リンゴ)の追加
    for _ in range(n_apple):
        #出現方向
        appeardirection = np.random.choice(['l','r','u','d'])

        #初速
        theta = (np.random.random_sample() * (2.0 / 3.0) + (1.0 / 6.0)) * math.pi
        vx_init = v_apple * math.cos(theta)
        vy_init = v_apple * math.sin(theta)
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
        apple = Sprite("../images/apple.png",(x_init, y_init), (vx_init,vy_init), 0, (appeartime, disappeartime), False)
        group.add(apple)

    # スプライト(敵)の追加
    for _ in range(n_enemy):
        #出現方向
        appeardirection = np.random.choice(['l','r','u','d'])

        #初速
        theta = (np.random.random_sample() * (2.0 / 3.0) + (1.0 / 6.0)) * math.pi
        vx_init = v_apple * math.cos(theta)
        vy_init = v_apple * math.sin(theta)
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
        disappeartime = min(gameduration, appeartime + np.random.randint(enemyduration_min,enemyduration_max))
        enemy = Sprite("../images/enemy.png",(x_init, y_init), (vx_init,vy_init), 0, (appeartime, disappeartime), False)
        group.add(enemy)
    clock = pygame.time.Clock()

    while (1):
        clock.tick(30)  # フレームレート(30fps)
        time = pygame.time.get_ticks()
        screen.fill((0, 20, 0)) # 画面の背景色
        font = pygame.font.Font(None, 24)  # 経過時間表示の文字
        for obj in group:
            # obj.appeartimeになったらgroup_existに入れる
            if obj.exist == False and time >= obj.appeartime:
                group_exist.add(obj)
                obj.exist = True
            # obj.disappeartimeになったらgroup_existから消す
            if obj.exist == True and time > obj.disappeartime:
                group_exist.remove(obj)
                obj.exist = False

        # スプライトグループを更新
        group_exist.update()
        # スプライトを描画
        group_exist.draw(screen)

        # 経過時間を表示
        if time <= gameduration:
            text = font.render("time(ms): " + str(time), True, (255,255,255))   # 描画する文字列の設定
            screen.blit(text, [screenwidth-150,screenheight-50])# 文字列の表示位置
        else:
            text = font.render("GAME OVER", True, (255,255,255))   # 描画する文字列の設定
            screen.blit(text, [screenwidth//2 - 50, screenheight//2 - 10])# 文字列の表示位置

        # 画面更新
        pygame.display.update()

        # イベント処理
        for event in pygame.event.get():
            # 終了用のイベント処理
            if time > gameduration + 10000:
                pygame.quit()
                sys.exit()
            if event.type == QUIT:          # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:       # キーを押したとき
                if event.key == K_ESCAPE:   # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()


main()