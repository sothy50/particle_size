import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

import os, tkinter, tkinter.filedialog, tkinter.messagebox
from tkinter import messagebox

def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):


    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

def imwrite(filename, img, params=None): #japanese ok
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def file_read():
    # ファイル選択ダイアログの表示
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("",".tif")]
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo('粒径分布作成','処理画像を選択してください！')
    file = tkinter.filedialog.askopenfilename(filetypes = fTyp,initialdir = iDir)

    # 処理ファイル名の出力
    #tkinter.messagebox.showinfo('プログラム',file)
    return (file)

def file_write(filename):
    # ファイル選択ダイアログの表示
    root = tkinter.Tk()
    root.withdraw()
    fTyp = [("tiff", "*.tif")] #画像の種類を選択
    iDir = os.path.abspath(os.path.dirname(__file__))
    tkinter.messagebox.showinfo('粒径分布作成','保存先を指定してください')
    file = tkinter.filedialog.asksaveasfilename(filetypes = fTyp,initialdir = iDir,initialfile = filename)

    # 処理ファイル名の出力
    #tkinter.messagebox.showinfo('プログラム',file)
    return (file)

def empty(a):
    pass

def getContours(img,filename):
    # 輪郭画像，輪郭(np.array)，輪郭の階層情報=入力画像，contour retrieval mode,輪郭検出方法
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # 面積,等価直径を求める。
    Areas = []
    Eq_diameters = []
    Total_area_px = 0
    total_px = 697686

    for cnt in contours:
        # それぞれのエリアの面積取得
        area_px = cv2.contourArea(cnt)

        # 一定面積以上に絞る#####################################################
        if area_px > 81:  #############(1)
            # 面積(px*px)
            Total_area_px += area_px
            area = (1 / 81) * area_px
            Areas.append(area)

            # 円周
            period = (1 / 9) * cv2.arcLength(cnt, True)

            # 等価直径(px)
            eq_diameter = 2 * area_px / 81 / np.pi
            Eq_diameters.append(float(eq_diameter))

            # 入力画像，輪郭list，何番目の輪郭を描画（-1で全部），色，太さ
            cv2.drawContours(imgContour, cnt, -1, (0, 255, 0), 2)
            # 領域の周囲の長さ (輪郭list，閉じてるか否か)
            period = cv2.arcLength(cnt, True)
            # 輪郭の近似(輪郭list，近似精度のパラメータ，近似曲線を閉じた曲線にするか否か)
            approx = cv2.approxPolyDP(cnt, 0.01 * period, False)

            # 外接矩形計算，座標タプル(左上x,左上y,width,height)
            x, y, w, h = cv2.boundingRect(approx)

            # 外接矩形描画，入力画像，左上座標，右下座標，色，(太さ,ラインタイプ，shift)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (255, 255, 0), 2)

            cv2.putText(imgContour, str(area_px), (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5,(0, 0, 0), 2)

    grain_number = len(Areas)

    Number_density_px =Total_area_px/total_px * 100
    Number_density_px = math.floor(Number_density_px*10**2)/(10**2)
    cv2.rectangle(imgContour,(95,684),(1021,764),(0,0,0),-1)
    cv2.putText(imgContour, 'grain_number:' +str(grain_number), (180, 705), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(imgContour, 'Number_density:' + str(Number_density_px) + '%', (180, 750), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(imgContour, filename, (615, 755), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                (255, 255, 255), 1, cv2.LINE_AA)


    return (Eq_diameters)

path = file_read()
file_name,ext = os.path.splitext(os.path.basename(path))
kernel = np.ones((2,2),np.uint8)

cv2.namedWindow("WINDOWNAME")
cv2.resizeWindow("WINDOWNAME",640,240)

#Trackbar(トラックバー名, ウィンドウ名, 初期値, 最大値, 関数名)
cv2.createTrackbar('threshold','WINDOWNAME',0,255,empty)
cv2.createTrackbar('opening','WINDOWNAME',0,5,empty)

img = imread(path)
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_blur = cv2.GaussianBlur(imgGray, (5, 5), 0)
imgContour = img.copy()

while True:
    shikichi = cv2.getTrackbarPos('threshold', 'WINDOWNAME')
    hanpuku = cv2.getTrackbarPos('opening', 'WINDOWNAME')

    ret, img_thresh = cv2.threshold(img_blur, shikichi, 255, cv2.THRESH_BINARY)
    opening = cv2.morphologyEx(img_thresh, cv2.MORPH_OPEN, kernel, iterations=hanpuku)
    hstack = np.hstack([imgGray, img_thresh, opening])

    cv2.namedWindow("Horizontal Stacking", cv2.WINDOW_NORMAL)
    cv2.imshow('Horizontal Stacking',hstack)

    if cv2.waitKey(1) == 13: #キーコード参照
        break

Eq_diameters = getContours(opening,file_name)
cv2.imshow('contours',imgContour)
cv2.waitKey(0)

ret = messagebox.askyesno('確認', '画像を保存しますか？')
if ret == True:
    path_export = file_write(file_name)
    imwrite(path_export+'.tif',imgContour)

fig = plt.figure(figsize=(8,6))
plt.title("Equal Diameters (μm)")
plt.hist(Eq_diameters,bins = 20,range =(0,10))
plt.show()


