# basic
import os
import sys
import random
import numpy as np

# face recognition
import dlib
from imutils import face_utils
import cv2
import mss
monitor = {"top": 60, "left":  1100, "width": 325, "height": 184}

# game
import pygame
from pygame.locals import *

# dlib�w�K�ς݃��f��
face_detector = dlib.get_frontal_face_detector()
predictor_path = 'shape_predictor_68_face_landmarks.dat'
face_predictor = dlib.shape_predictor(predictor_path)

###################################################
# �O���[�o���ϐ�
camera = cv2.VideoCapture(2)    #�J�����̃|�[�g�ԍ�

N_PLAYER = 4    #�v���C���[��

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
SCR_RECT = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

FACE_SIZE = 100
SPRITE_SIZE = 30

WAITING_TIME = 5000    #�I�u�W�F�N�g���o������܂ł̎���
GAME_DURATION = WAITING_TIME + 60000    #�Q�[���̌p������(ms)

N_FOOD = int(GAME_DURATION/1000/2)   #�����S�̐�
N_ENEMY = int(GAME_DURATION/1000/4)   #�G�̐�

spriteduration_min = 10000   
spriteduration_max = 20000
###################################################

def divide_img(img):
    '''
    �摜���c2�~��2��4�����B[����, �E��, ����, �E��]�̏��Ɋi�[�����z���Ԃ��B

    Parameters
    ----------
    img : np.ndarray : img[height, width, color]
        �摜

    Returns
    -------
    imgs : list : imgs[area] = [height, width, color]
        �c2�~��2��4���������摜�B[����E�E��E�����E�E��]�̏��Ɋi�[����Ă���B
    '''
    height=img.shape[0]
    width=img.shape[1]
    if N_PLAYER == 4:
        return np.array([img[:int(height*0.5), :int(width*0.5)], img[:int(height*0.5), int(width*0.5):], img[int(height*0.5):, :int(width*0.5)], img[int(height*0.5):, int(width*0.5):]])
    elif N_PLAYER == 1:
        return np.array([img])


# https://qiita.com/mamon/items/bb2334eef596f8cacd9b
# https://qiita.com/mimitaro/items/bbc58051104eafc1eb38
# https://woraise.com/2019/03/21/desert-shooting/
# https://gist.github.com/radames/1e7c794842755683162b
def face_detect_trim(img, error_img, pos=[[0,0,0,0]]*N�QPLAYER, landmarks=[[[0,0]]]*N�QPLAYER):
    '''
    ����E�E��E�����E�E����4�l���ʂ��Ă���摜����A4�l�̊���g���~���O���A��̍��W�ƌ��̍��W���v�Z����

    Parameters
    ----------
    img : np.ndarray : img[height, width, color]
        �摜
    error_img : np.ndarray : img[player] = [height, width, color]
        �炪�F������Ȃ��ꍇ�ɑ}������摜

    Returns
    -------
    imgs : list : imgs[player] = [height, width, color]
        ��̕������g���~���O�����摜�B(����̐l�E�E��̐l�E�����̐l�E�E���̐l)�̏��Ɋi�[����Ă���B
    pos : np.array : pos[player] = [top, bottom, left, right]
        4�����������ꂼ��̉摜�̍�������_�Ƃ����A�g���~���O�����摜�̍��W���i�[����Ă���B
    landmarks : np.array : landmark[player] = [landmarks, position]
        4�����������ꂼ��̉摜�̍�������_�Ƃ����A���̍��W���i�[����Ă���B
    '''
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgs = divide_img(img)
    
    trim_imgs=[[0]]*N�QPLAYER
    
    for i, img in enumerate(imgs):
        height = img.shape[0]
        width = img.shape[1]

        # �猟�o
        img_gry = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = face_detector(img_gry, 1)

        if len(faces)==0:
            trim_imgs[i] = error_img[i]
            continue    #�炪���o����Ȃ��ꍇ�͏�����ł��؂�
        face = faces[0]    #�炪�������o���ꂽ�ꍇ�ɂ́A�擪���̗p
    
        # ��̃����h�}�[�N���o
        landmark = face_predictor(img_gry, face)
        # �����������̂��߃����h�}�[�N�Q��NumPy�z��ɕϊ�
        landmark = face_utils.shape_to_np(landmark)[60:68]

        # �g�O�̍��W���ۂ߂�
        top = max(face.top(), 0)
        bottom = min(face.bottom(), img.shape[0])
        left = max(face.left(), 0)
        right = min(face.right(), img.shape[1])
        
        img_trim = img[top:bottom, left:right]

        height_trim = int(img_trim.shape[0]/height*SCREEN_HEIGHT)    #�Q�[����ʂ̏k�ڂɍ��킹�Ċg��
        width_trim = int(img_trim.shape[1]/width*SCREEN_WIDTH)    #�Q�[����ʂ̏k�ڂɍ��킹�Ċg��

        img_trim = cv2.resize(img_trim , (FACE_SIZE, FACE_SIZE))    #�v���C���[�̉摜�T�C�Y��100*100�ɌŒ�
        trim_imgs[i] = img_trim

        pos[i] = [int(top / height * SCREEN_HEIGHT), int(bottom / height * SCREEN_HEIGHT), int(left / width * SCREEN_WIDTH), int(right / width * SCREEN_WIDTH)]    #�Q�[����ʂ̏k�ڂɍ��킹�Ċg��

        landmark[:,0] = pos[i][2] + (-pos[i][2] + np.floor(landmark[:,0] / width * SCREEN_WIDTH)) / width_trim * FACE_SIZE
        landmark[:,1] = pos[i][0] + (-pos[i][0] + np.floor(landmark[:,1] / height * SCREEN_HEIGHT)) / height_trim * FACE_SIZE
        landmarks[i] = landmark

    return trim_imgs, np.array(pos), np.array(landmarks)

class Food(pygame.sprite.Sprite):
    # �X�v���C�g���쐬(�摜�t�@�C����, �l���X�R�A)
    def __init__(self, img, score, v):
        # �o�������E�p�x
        appeardirection = np.random.choice(['l','r','u','d'])
        theta = (np.random.random_sample() * (2.0 / 3.0) + (1.0 / 6.0)) * np.pi
        vx_init = v * np.cos(theta)
        vy_init = v * np.sin(theta)
        
        # �I�u�W�F�N�g�̓��_
        self.score = score

        # �����ʒu�Ə���
        if appeardirection =='u':
            x_init = np.random.randint(0,SCREEN_WIDTH)
            y_init = 0
        elif appeardirection == 'd':
            x_init = np.random.randint(0,SCREEN_WIDTH)
            y_init = SCREEN_HEIGHT
            vy_init = -vy_init
        elif appeardirection == 'l':
            x_init = 0
            y_init = np.random.randint(0,SCREEN_HEIGHT)
            vx_init,vy_init = vy_init,vx_init
        else:
            x_init = SCREEN_WIDTH
            y_init = np.random.randint(0,SCREEN_HEIGHT)
            vx_init,vy_init = -vy_init,vx_init

        # �o������
        appeartime = np.random.randint(WAITING_TIME, GAME_DURATION)
        # ���Ŏ����@�@�@�@
        disappeartime = min(GAME_DURATION, appeartime + np.random.randint(spriteduration_min,spriteduration_max))

        pygame.sprite.Sprite.__init__(self)
        self.image = img
        w = self.image.get_width()
        h = self.image.get_height()
        self.rect = Rect(x_init, y_init, w, h)
        self.vx = vx_init
        self.vy = vy_init
        self.appeartime = appeartime
        self.disappeartime = disappeartime
        self.exist = False

    def update(self,time):
        if self.exist:
            self.rect.move_ip(self.vx, self.vy)
        # �ǂƏՓˎ��̏���(���˕Ԃ�)
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            if time>self.disappeartime:
                self.exist = False
                self.kill()
            else:
                self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            if time>self.disappeartime:
                self.exist = False
                self.kill()
            else:
                self.vy = -self.vy
        # �ǂƏՓˎ��̏���(�ǂ𒴂��Ȃ��悤��)
        self.rect = self.rect.clamp(SCR_RECT)
    
class Player(pygame.sprite.Sprite):
    """���@"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)

    def init(self, pos):
        self.rect = self.image.get_rect()
        self.rect.top = pos[0]
        self.rect.left = pos[2]
        self.reload_timer = 0
        self.pos=pos
    def pos_update(self,pos):
        self.pos=pos
    def update(self):
        self.rect.top = self.pos[0]
        self.rect.left = self.pos[2]

def collision_detection(player, group_sprite_exist,landmark):
    """�Փ˔���"""
    c=0
    minplot=np.min(landmark,axis=0)
    maxplot=np.max(landmark,axis=0)
    is_hit = False
    for Sprite in group_sprite_exist:
        if minplot[0] <= Sprite.rect.left + Sprite.rect.width and Sprite.rect.left  <= maxplot[0] and minplot[1] <= Sprite.rect.top + Sprite.rect.height and Sprite.rect.top <= maxplot[1]:
            Sprite.kill()
            is_hit = True
            c += Sprite.score
    return c, is_hit

def load_image(filename, colorkey=None):
    """�摜�����[�h���ĉ摜�Ƌ�`��Ԃ�"""
    #filename = os.path.join("data", filename)
    try:
        image = pygame.image.load(filename)
    except pygame.error as message:
        print("Cannot load image:", filename)
        raise SystemExit(message)
    image = image.convert_alpha()
    return image

def sprite_init():
    group_sprite_all = pygame.sprite.RenderUpdates()    #�Q�[�����ɕ\������S�ẴX�v���C�g���i�[����N���X
    group_sprite_exist = pygame.sprite.RenderUpdates()    #���ۂɕ\������Ă���X�v���C�g���i�[����N���X

    # ���_�X�v���C�g
    apple_fig = pygame.transform.scale(pygame.image.load("../images/apple1.png").convert_alpha(),(30, 30))
    grape_fig = pygame.transform.scale(pygame.image.load("../images/grape3.png").convert_alpha(),(50, 50))
    watermelon_fig = pygame.transform.scale(pygame.image.load("../images/watermelon5.png").convert_alpha(),(60, 60))
    hamburger_fig = pygame.transform.scale(pygame.image.load("../images/hamburger10.png").convert_alpha(),(70, 70))
    plus_sprite_list = np.array([[0.6,apple_fig,1,15],[0.25,grape_fig,3,10],[0.1,watermelon_fig,5,5],[0.05,hamburger_fig,10,3]])
    '''plus_sprite_list[food] = [probability, figure, score, speed]'''
    for _ in range(N_FOOD):
        prob = np.random.rand()
        for j in range(len(plus_sprite_list)):
            if prob<=plus_sprite_list[j,0]:
                plus_sprite = Food(plus_sprite_list[j,1],plus_sprite_list[j,2],plus_sprite_list[j,3])
                break
            else:
                prob -= plus_sprite_list[j,0]
        group_sprite_all.add(plus_sprite)

    # ���_�X�v���C�g
    poison_apple_fig = pygame.transform.scale(pygame.image.load("../images/poison_apple-2.png").convert_alpha(),(40, 40))
    spider_fig = pygame.transform.scale(pygame.image.load("../images/spider-10.png").convert_alpha(),(70, 70))
    minus_sprite_list = np.array([[0.8,poison_apple_fig,-2,10],[0.2,spider_fig,-10,40]])
    '''minus_sprite_list[food] = [probability, figure, score, speed]'''
    for _ in range(N_ENEMY):
        prob = np.random.rand()
        for j in range(len(minus_sprite_list)):
            if prob<=minus_sprite_list[j,0]:
                minus_sprite = Food(minus_sprite_list[j,1],minus_sprite_list[j,2],minus_sprite_list[j,3])
                break
            else:
                prob -= minus_sprite_list[j,0]
        group_sprite_all.add(minus_sprite)

    return group_sprite_all, group_sprite_exist


def main():
    # pygame�����ݒ� ###########################################################################################
    pygame.init()
    pygame.display.set_caption("meal_time")

    all = pygame.sprite.RenderUpdates()
    Player.containers = all

    screen = pygame.display.set_mode(SCR_RECT.size)
    screen.fill([0,0,0])

    # �w�i�����ݒ� ###########################################################################################
    Back_image = load_image("../images/background.png")
    Back_image = pygame.transform.scale(Back_image,(SCREEN_WIDTH, SCREEN_HEIGHT))
    back_rect = Back_image.get_rect()
    
    # �X�v���C�g�����ݒ� ###########################################################################################
    group_sprite_all, group_sprite_exist = sprite_init()

    # ���_�����ݒ� ###########################################################################################
    score = np.zeros(N_PLAYER, np.int8)

    # �v���C���[�����ݒ� ###########################################################################################
    # ��F���Ɏ��s�����ۂɕ\������摜
    error_img = cv2.resize(cv2.imread("../images/owl.jpg"), (FACE_SIZE,FACE_SIZE))

    mss_instance = mss.mss()
    img_np = numpy.array(mss_instance.grab(monitor))
    #_, frame = camera.read()    #�J�����摜�擾
    frame,pos,landmark = face_detect_trim(img_np, [error_img]*N_PLAYER)
    
    player = []
    for i in range(N_PLAYER):
        player.append(Player())

    for i, fr in enumerate(frame):
        player[i].image = pygame.surfarray.make_surface(fr.swapaxes(0,1))
        player[i].init(pos[i])
        
    # �I���R�}���h�܂ŃQ�[�����p�� ###########################################################################################
    clock = pygame.time.Clock()
    reset_time = 0
    try:
        while True:
            dirty_rect = []
            time = pygame.time.get_ticks() - reset_time

            # �摜�擾->��F��->�Q�[����ʂɕ\��
            prev_frame = frame
            #_, frame = camera.read()
            img_np = numpy.array(mss_instance.grab(monitor))
            frame, pos, landmark  = face_detect_trim(img_np, prev_frame, pos, list(landmark))
            for i in range(N_PLAYER):
                player[i].pos_update(pos[i])

                player[i].image = pygame.surfarray.make_surface(frame[i].swapaxes(0,1))
                screen.blit(Back_image, back_rect)

                #player[i].update()
                #dirty_rect += player[i].containers.draw(screen)

            # �X�v���C�g�̕\���Ə���
            for obj in group_sprite_all:
                # obj.appeartime�ɂȂ�����group_sprite_exist�ɓ����
                if obj.exist == False and time >= obj.appeartime:
                    group_sprite_exist.add(obj)
                    obj.exist = True

                # obj.disappeartime�ɂȂ�����group_sprite_exist�������
                if obj.exist == True and time > GAME_DURATION:
                    group_sprite_exist.remove(obj)
                    obj.exist = False
            
            # �ҋ@����
            clock.tick(10)

            # update����ʂɔ��f
            all.update()
            dirty_rect = all.draw(screen)
            group_sprite_exist.update(time)
            dirty_rect += group_sprite_exist.draw(screen)

            # �X�R�A�̍X�V
            if len(group_sprite_exist)>0:
                for i in range(N_PLAYER):
                    c, is_hit =collision_detection(player[i], group_sprite_exist, landmark[i])
                    score[i] = score[i] + c
                    if is_hit:
                        text = pygame.font.Font(None, 60).render(str(c), True, (255,0,0))
                        screen.blit(text, [pos[i,2]+FACE_SIZE*0.7, pos[i,1]-FACE_SIZE*0.3])

            # �c�莞�Ԃ̕\��
            if time<WAITING_TIME:    #�Q�[���J�n�O
                text = pygame.font.Font(None, 50).render("TIME: "+str(int((GAME_DURATION-WAITING_TIME)/1000)), True, (255,255,255))
                text2 = pygame.font.Font(None, 500).render(str(int((WAITING_TIME-time)/1000)+1), True, (255,0,0))
                screen.blit(text2, [SCREEN_WIDTH*0.4, SCREEN_HEIGHT*0.2])
            elif time>GAME_DURATION:    #�Q�[���I����
                text = pygame.font.Font(None, 50).render("TIME: "+str(0), True, (255,255,255))
            else:
                text = pygame.font.Font(None, 50).render("TIME: "+str(int((GAME_DURATION-time)/1000+1)), True, (255,255,255))
            screen.blit(text, [SCREEN_WIDTH*0.45, 5])

            # �X�R�A�̕\��
            for i in range(N_PLAYER):
                text1 = pygame.font.Font(None, 24).render("Player"+str(i+1)+": " + str(score[i]), True, (255,255,255))
                screen.blit(text1, [SCREEN_WIDTH * i / 4. + 10, SCREEN_HEIGHT * 0.95])
                text2 = pygame.font.Font(None, 32).render(str(score[i]), True, (255,255,255))
                screen.blit(text2, [pos[i,2]+FACE_SIZE*0.4, pos[i,0]+FACE_SIZE*0.1])

            pygame.display.update(dirty_rect)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_SPACE:
                    group_sprite_all, group_sprite_exist = sprite_init()
                    score = np.zeros(N_PLAYER, np.int8)
                    reset_time = pygame.time.get_ticks()

    except (KeyboardInterrupt,SystemExit):
        pygame.quit()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()