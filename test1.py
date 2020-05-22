# -*- coding:utf-8 -*-
import pygame
from pygame.locals import *
import sys
import numpy as np

apple_movetime = []
apple_obj = []
apple_rect = []
filename_apple = "apple.png"

def obj_init(n_apple):
    for i in range(n_apple):
        apple_movetime.append(np.random.randint(1000,20000))
        obj_tmp = pygame.image.load(filename_apple).convert()
        apple_obj.append(obj_tmp)
        rect_tmp = obj_tmp.get_rect()
        rect_tmp.center = (np.random.randint(100,300),0)
        apple_rect.append(rect_tmp)
    return (apple_movetime, apple_obj, apple_rect)


def main():
    w,h = (400,400)
    x,y = (200,200)
    n_apple = 10
    
    
    pygame.init()
    
    pygame.display.set_mode((w,h), 0, 32)
    obj_init(n_apple)
    print(apple_movetime)
    screen = pygame.display.get_surface()
    screen.fill((255,255,255))

    pygame.display.set_caption("Test")                        # タイトルバーに表示する文字
    bg = pygame.image.load("bg.png").convert()    
    rect_bg = bg.get_rect()
    font = pygame.font.Font(None, 55)
    
    while (1):
        #screen.fill((255,255,255))        # 画面を黒色(#000000)に塗りつぶし
        pygame.time.wait(30)
        time = pygame.time.get_ticks()
        pygame.display.update()             # 画面更新
        screen.fill((0, 20, 0, 0))          # 画面の背景色
        screen.blit(bg, rect_bg)            # 背景画像の描画
        for i in range(n_apple):            # i番目のリンゴの描画
            if time == apple_movetime[i]:
                screen.blit(apple_obj[i],apple_rect[i])
            elif time > apple_movetime[i]:
                apple_rect[i].move_ip(0,5)
                screen.blit(apple_obj[i],apple_rect[i])
        text = font.render(str(time), True, (255,255,255))   # 描画する文字列の設定
        screen.blit(text, [w-150,h-50])# 文字列の表示位置

        # イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()       # Pygameの終了(画面閉じられる)
                sys.exit()


if __name__ == "__main__":
    main()
