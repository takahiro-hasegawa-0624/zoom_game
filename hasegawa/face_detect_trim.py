# https://qiita.com/mamon/items/bb2334eef596f8cacd9b
# https://qiita.com/mimitaro/items/bbc58051104eafc1eb38
def divide_img_4(img):
    '''
    画像を縦2つ×横2つに4分割。[左上, 右上, 左下, 右下]の順に格納した配列を返す。
    '''
    hight=img.shape[0]
    width=img.shape[1]
    return np.array([img[:int(hight*0.5), :int(width*0.5)], img[:int(hight*0.5), int(width*0.5):], img[int(hight*0.5):, :int(width*0.5)], img[int(hight*0.5):, int(width*0.5):]])

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
    # img = cv2.resize(img , (int(1600*mag), int(900*mag)))
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
        img_trim = cv2.resize(img_trim , (int(img_trim.shape[1]/img.shape[1]*800), int(img_trim.shape[0]/img.shape[0]*450)))
        tmp1 = img_trim.shape[1]
        tmp2 = img_trim.shape[0]
        img_trim = cv2.resize(img_trim , (100, 100))
        
        trim_imgs[i] = img_trim
        
        #landmark[:,0] = landmark[:,0] - np.floor(landmark[:,0]/mag)
        #landmark[:,1] = landmark[:,1] - np.floor(landmark[:,1]/mag)
        pos[i] = [int(face.top()/img.shape[0]*450), int(face.bottom()/img.shape[0]*450), int(face.left()/img.shape[1]*800), int(face.right()/img.shape[1]*800)]
        landmark[:,0] = pos[i][2] + (-pos[i][2] + np.floor(landmark[:,0]/img.shape[1]*800))/tmp1*100
        landmark[:,1] = pos[i][0] + (-pos[i][0] + np.floor(landmark[:,1]/img.shape[0]*450))/tmp2*100
        landmarks[i] = landmark
        
        # ランドマーク描画
        #for (x, y) in landmark:
            #cv2.circle(trim_imgs[i], (int(x), int(y)), 3, (0, 0, 255), -1)

    return trim_imgs, np.array(pos), np.array(landmarks)