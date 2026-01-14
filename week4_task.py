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

	# ベジェ曲線の描画
    glColor3d(0., 0., 0.)
    glLineWidth(2)
    # 【ここにベジェ曲線を描画するためのコードを記述する】

    def bezier_point(t, p0, p1, p2, p3):
        """3次ベジェ曲線上の点を返す"""
        return (
            (1 - t)**3 * p0 +
            3 * (1 - t)**2 * t * p1 +
            3 * (1 - t) * t**2 * p2 +
            t**3 * p3
        )

    def bezier_tangent(t, p0, p1, p2, p3):
        """3次ベジェ曲線の接線ベクトルを返す"""
        return (
            3 * (1 - t)**2 * (p1 - p0) +
            6 * (1 - t) * t * (p2 - p1) +
            3 * t**2 * (p3 - p2)
        )

    def bezier_second_derivative(t, p0, p1, p2, p3):
        """3次ベジェ曲線の2階微分ベクトルを返す"""
        return (
            6 * (1 - t) * (p2 - 2 * p1 + p0) +
            6 * t * (p3 - 2 * p2 + p1)
        )

    def bezier_curvature(t, p0, p1, p2, p3):
        """3次ベジェ曲線の曲率を返す"""
        first = bezier_tangent(t, p0, p1, p2, p3)
        second = bezier_second_derivative(t, p0, p1, p2, p3)

        # κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
        numerator = abs(first[0] * second[1] - first[1] * second[0])
        denominator = (first[0]**2 + first[1]**2)**(3/2)

        if denominator == 0:
            return 0
        return numerator / denominator

    # 制御点が4点以上あれば描画
    if len(g_ControlPoints) >= 4:
        # P0〜P3, P3〜P6, P6〜P9… と3点ずつ共有して描画
        for i in range(0, len(g_ControlPoints) - 3, 3):
            p0, p1, p2, p3 = g_ControlPoints[i:i + 4]

            # --- ベジェ曲線本体 ---
            glBegin(GL_LINE_STRIP)
            for t in np.linspace(0, 1, 100):
                p = bezier_point(t, p0, p1, p2, p3)
                glVertex2dv(p)
            glEnd()

            # --- 法線の描画 ---
            glColor3d(0., 0., 1.)
            glLineWidth(0.8)
            glBegin(GL_LINES)
            for t in np.linspace(0, 1, 100):
                p = bezier_point(t, p0, p1, p2, p3)
                tangent = bezier_tangent(t, p0, p1, p2, p3)
                norm = np.linalg.norm(tangent)
                if norm == 0:
                    continue
                tangent /= norm

                # 曲率を計算
                curvature = bezier_curvature(t, p0, p1, p2, p3)
                # 曲率に応じて法線の長さを調整（倍率を掛ける）
                normal_length = curvature * 5000  # 適当な倍率

                # 時計回りに90度回転 (x, y) → (y, -x)
                normal = np.array([tangent[1], -tangent[0]]) * normal_length
                glVertex2dv(p)
                glVertex2dv(p + normal)
            glEnd()

            # 曲線の描画色を戻す（青）
            glColor3d(0., 0., 1.)

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