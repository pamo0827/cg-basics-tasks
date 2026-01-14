import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

# 制御点を格納する配列
g_ControlPoints = []

# ウィンドウサイズを保持する
g_WindowWidth = 512
g_WindowHeight = 512

# ノットベクトル
# この配列の値を変更することで基底関数が変化する。その結果として形が変わる。
# 下の例では、一定間隔で値が変化するので、「一様Bスプライン曲線」となる
# g_NotVector = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

# 課題(2)では次のノットベクトルを変更する
g_NotVector = [0, 1, 2, 3, 3, 3, 4, 5, 6, 7]

# 基底関数 N{i,n}(t)の値を計算する
def getBaseN(i, n, t):
    if n == 0:
        # n が 0 の時だけ t の値に応じて 0 または 1 を返す
        if g_NotVector[i] <= t < g_NotVector[i + 1]:
            return 1.0
        return 0.0
    else:
        # 係数を計算するときに、ノットが重なる（分母がゼロとなる）ときには、その項を無視する

        # Cox-de Boorの漸化式
        c1 = 0.0
        c2 = 0.0

        # 第1項の計算
        if g_NotVector[i + n] != g_NotVector[i]:
            c1 = (t - g_NotVector[i]) / (g_NotVector[i + n] - g_NotVector[i]) * getBaseN(i, n - 1, t)

        # 第2項の計算
        if g_NotVector[i + n + 1] != g_NotVector[i + 1]:
            c2 = (g_NotVector[i + n + 1] - t) / (g_NotVector[i + n + 1] - g_NotVector[i + 1]) * getBaseN(i + 1, n - 1, t)

        return c1 + c2


#表示部分をこの関数で記入
def display():
    glClearColor(1., 1., 1., 1.) # 消去色指定
    glClear(GL_COLOR_BUFFER_BIT)

	# 制御点の描画
    glPointSize(5)
    glColor3d(0., 0., 0.)
    glBegin(GL_POINTS)
    for point in g_ControlPoints:
        glVertex2dv(point)    
    glEnd()

    # 制御点を結ぶ線分の描画
    glColor3d(1., 0., 0.)   
    glLineWidth(1)
    glBegin(GL_LINE_STRIP)
    for point in g_ControlPoints:
        glVertex2dv(point)    
    glEnd()

    # ここにBスプライン曲線を描画するプログラムコードを入れる
    # ヒント1: 3次Bスプラインの場合は制御点を4つ入れるまでは何も描けない
    # ヒント2: パラメータtの値の取り得る範囲に注意

    # Bスプライン曲線の描画
    n = 3  # 3次Bスプライン
    num_control_points = len(g_ControlPoints)

    # 3次の場合、4つ以上の制御点が必要
    if num_control_points >= 4:
        glColor3d(0., 0., 1.)  # 青色でBスプライン曲線を描画
        glLineWidth(2)

        # セグメント数 = 制御点数 - 3
        num_segments = num_control_points - n

        # 全てのセグメントを1つの連続した曲線として描画
        glBegin(GL_LINE_STRIP)

        for seg in range(num_segments):
            # パラメータtの範囲: [t_{n}, t_{i+n+1}]
            # seg番目のセグメントでは i=seg として、t は [g_NotVector[seg+n], g_NotVector[seg+n+1]] の範囲
            t_start = g_NotVector[seg + n]
            t_end = g_NotVector[seg + n + 1]

            # tを細かく刻んで曲線を描画
            num_steps = 100
            for step in range(num_steps + 1):
                # 最後のセグメントの最後の点以外は、次のセグメントの最初の点と重複するので
                # 最後の点は次のセグメントで描画する（最後のセグメントは全て描画）
                if seg < num_segments - 1 and step == num_steps:
                    continue

                t = t_start + (t_end - t_start) * step / num_steps

                # B(t) = Σ P_i * N_{i,n}(t)
                point = np.array([0.0, 0.0])
                for i in range(num_control_points):
                    basis = getBaseN(i, n, t)
                    point += g_ControlPoints[i] * basis

                glVertex2dv(point)

        glEnd()

    glFlush() #画面出力

# ウィンドウのサイズが変更されたときの処理
def resize(w, h):
    if h > 0:
        glViewport(0, 0, w, h)
        g_WindowWidth = w
        g_WindowHeight = h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # ウィンドウ内の座標系設定
        # マウスクリックの座標と描画座標が一致するような正投影
        glOrtho(0, w, h, 0, -10, 10)
        glMatrixMode(GL_MODELVIEW)


# マウスクリックのイベント処理
def mouse(button, state, x, y):
    if state == GLUT_DOWN: 
        # 左ボタンだったらクリックした位置に制御点を置く
        if button == GLUT_LEFT_BUTTON:
            # ノット数を増やせばいくらでも制御点を追加できるが、今回はノットベクトルが固定されているので
            # いくらでも追加できるわけではない
            if len(g_ControlPoints) < len(g_NotVector) - 4 :
                g_ControlPoints.append(np.array([x, y]))
            
        # 右ボタンだったら末尾の制御点を削除
        if button == GLUT_RIGHT_BUTTON:
            if g_ControlPoints:
                g_ControlPoints.pop()
    glutPostRedisplay()   

# キーが押されたときのイベント処理
def keyboard(key, x, y): 
    if key==b'q':
        pass
    elif key==b'Q':
        pass
    elif key==b'\x1b':
        exit() #b'\x1b'は ESC の ASCII コード
    
    glutPostRedisplay()

def init():
    # アンチエイリアスを有効にする
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

if __name__ == "__main__":
    glutInit(sys.argv) #ライブラリの初期化
    glutInitWindowSize(g_WindowWidth, g_WindowHeight) #ウィンドウサイズを指定
    glutCreateWindow(sys.argv[0]) #ウィンドウを作成
    glutDisplayFunc(display) #表示関数を指定
    glutReshapeFunc(resize) # ウィンドウサイズが変更されたときの関数を指定
    glutMouseFunc(mouse) # マウス関数を指定
    glutKeyboardFunc(keyboard) # キーボード関数を指定
    init() # 初期設定を行う
    glutMainLoop() #イベント待ち