import sys
import math
import random
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- グローバル変数 ---

# ディスプレイリストのID
ID_SAKURA_PETAL = 1

# アニメーションの更新間隔 (ミリ秒)
TIMER_INTERVAL = 16 

# 描画する図形のリスト
shapes = []

# --- 図形やアニメーションの定義 ---

def build_display_list():
    """
    ディスプレイリストを作成する
    今回は桜の花びらのような形を描画する
    """
    glNewList(ID_SAKURA_PETAL, GL_COMPILE)
    
    # 花びらを三角形の集まりで描画
    glBegin(GL_TRIANGLES)
    
    # 中心点
    v0 = (0.0, 0.0)
    
    # 花びらの先の点
    v1 = (0.0, 0.3)
    
    # 花びらのくびれの点
    v2_left = (-0.05, 0.1)
    v2_right = (0.05, 0.1)
    
    # 花びらの付け根の点
    v3_left = (-0.02, -0.1)
    v3_right = (0.02, -0.1)

    # 上半分
    glVertex2fv(v0)
    glVertex2fv(v2_left)
    glVertex2fv(v1)

    glVertex2fv(v0)
    glVertex2fv(v1)
    glVertex2fv(v2_right)

    # 下半分
    glVertex2fv(v0)
    glVertex2fv(v3_left)
    glVertex2fv(v2_left)

    glVertex2fv(v0)
    glVertex2fv(v2_right)
    glVertex2fv(v3_right)

    glEnd()
    glEndList()

def create_shape():
    """
    ランダムな特性を持つ図形（今回は花びら）を一つ作成する
    """
    return {
        'x': random.uniform(-1.0, 1.0),  # 初期位置X
        'y': random.uniform(-1.0, 1.0),  # 初期位置Y
        'vx': random.uniform(-0.01, 0.01), # 速度X
        'vy': random.uniform(-0.02, -0.005),# 速度Y (少し下向きに)
        'angle': random.uniform(0, 360),   # 初期角度
        'v_angle': random.uniform(-2.0, 2.0), # 角速度
        'scale': random.uniform(0.5, 1.5),   # 大きさ
        'color': (random.uniform(0.8, 1.0), random.uniform(0.6, 0.9), random.uniform(0.6, 0.9)) # 色(ピンク系)
    }

def update_shape(shape):
    """
    図形の位置と角度を更新する
    """
    # 位置を更新
    shape['x'] += shape['vx']
    shape['y'] += shape['vy']
    
    # 角度を更新
    shape['angle'] += shape['v_angle']

    # 画面の端まで来たら反対側に移動させる (ループ)
    if shape['x'] > 1.1: shape['x'] = -1.1
    if shape['x'] < -1.1: shape['x'] = 1.1
    if shape['y'] < -1.1: 
        shape['y'] = 1.1 # 下まで落ちたら上から降ってくる
        shape['x'] = random.uniform(-1.0, 1.0) # X位置はランダムに

# --- GLUTのコールバック関数 ---

def display():
    """
    描画処理
    """
    glClearColor(0.1, 0.1, 0.2, 1.0)  # 背景色 (夜空のような色)
    glClear(GL_COLOR_BUFFER_BIT)

    # 各図形を描画
    for shape in shapes:
        glPushMatrix()  # 現在の座標系を保存

        # 図形ごとに移動、回転、拡大縮小
        glTranslatef(shape['x'], shape['y'], 0.0)
        glRotatef(shape['angle'], 0.0, 0.0, 1.0)
        glScalef(shape['scale'], shape['scale'], 1.0)
        
        # 色を設定
        glColor3f(shape['color'][0], shape['color'][1], shape['color'][2])

        # ディスプレイリストを呼び出して図形を描画
        glCallList(ID_SAKURA_PETAL)

        glPopMatrix()  # 保存した座標系を復元

    glutSwapBuffers()

def timer(value):
    """
    一定時間ごとに呼び出され、アニメーションを更新する
    """
    # 各図形の情報を更新
    for shape in shapes:
        update_shape(shape)

    glutPostRedisplay()  # 再描画を要求
    glutTimerFunc(TIMER_INTERVAL, timer, 0) # 次のタイマーをセット

def reshape(width, height):
    """
    ウィンドウサイズが変更されたときに呼び出される
    """
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # アスペクト比を考慮
    if width > height:
        aspect = width / height
        glOrtho(-aspect, aspect, -1.0, 1.0, -1.0, 1.0)
    else:
        aspect = height / width
        glOrtho(-1.0, 1.0, -aspect, aspect, -1.0, 1.0)
        
    glMatrixMode(GL_MODELVIEW)


# --- メイン処理 ---

if __name__ == "__main__":
    # 図形を複数作成
    for _ in range(30): # 30個の花びらを作成
        shapes.append(create_shape())

    # GLUTの初期化
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Colorful Sakura Fubuki") # ウィンドウタイトルをバイト文字列に

    # ディスプレイリストの作成
    build_display_list()

    # コールバック関数の登録
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(TIMER_INTERVAL, timer, 0)

    # メインループ開始
    glutMainLoop()
