import sys
import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

# 3次元ベクトルを作る
def vec3(x, y, z):
	return np.array([x, y, z], dtype=np.float64)

# 長さを1に正規化する
def normalize(v):
	norm = np.linalg.norm(v)
	return v / norm if norm > 0.0 else v

# 球体
class Sphere:
	def __init__(self, center, radius, color):
		self.center = center	# 中心座標
		self.radius = radius	# 半径
		self.color = color	# Red, Green, Blue 値 0.0～1.0

	# 点pを通り、v方向のRayとの交わりを判定する。
	# 交点が p+tv として表せる場合の t の値を返す。交わらない場合は-1を返す
	def getIntersect(self, p, v):
		# A*t^2 + B*t + C = 0 の形で表す
		A = v.dot(v)
		B = 2.0 * (v.dot(p - self.center))
		C = p.dot(p) - 2.0 * p.dot(self.center) + self.center.dot(self.center) - self.radius * self.radius
		D = B * B - 4 * A * C	# 判別式

		if D > 0.0:	# 交わる
			t1 = (-B - np.sqrt(D)) / (2.0 * A)
			t2 = (-B + np.sqrt(D)) / (2.0 * A)
			return t1 if t1 >= 0.0 else t2
		else:
			return -1.0

g_WindowID = 0	# ウィンドウ識別子
g_HalfWidth = 200    # 描画領域の横幅/2
g_HalfHeight = 200   # 描画領域の縦幅/2

# 各種定数
g_Distance = 1000  # 視点と投影面との距離
g_Shininess = 32  # 鏡面反射の指数
g_Kd = 0.8  # 拡散反射定数
g_Ks = 0.8  # 鏡面反射定数
g_Iin = 1.0 # 入射光の強さ 
g_Ia  = 0.2 # 環境光

g_Viewpoint = vec3(0., 0., 0.)	# 視点位置
g_LightDirection = vec3(-2., -4., -2.)	# 入射光の進行方向

g_Sphere = Sphere(vec3(0, 0, -1500.),	# 中心座標
		  150.0,		# 半径
		  vec3(0.2, 0.9, 0.9))	# RGB 値


# x, y で指定されたスクリーン座標での色 (RGB) を計算する
def getPixelColor(x, y):
	# 原点からスクリーン上のピクセルへ飛ばすレイの方向
	ray = vec3(x, y, -g_Distance) - g_Viewpoint
	ray = normalize(ray)	# レイの長さの正規化

	# レイを飛ばして球との交点を求める
	t = g_Sphere.getIntersect(g_Viewpoint, ray)

	if t > 0.0:	# 球との交点がある
		Is = 0.0	# 鏡面反射光
		Id = 0.0	# 拡散反射光

		p_intersect = g_Viewpoint + t * ray # 交点の座標
		normal = normalize(p_intersect - g_Sphere.center) # 球の法線ベクトル
		L = -g_LightDirection # 光源方向のベクトル
		cos_alpha = normal.dot(L)

		if cos_alpha > 0.0:
			Id = g_Iin * g_Kd * cos_alpha
		
		R = 2.0 * cos_alpha * normal - L # 反射光のベクトル
		V = normalize(g_Viewpoint - p_intersect) # 視線方向の逆ベクトル
		cos_gamma = R.dot(V)

		if cos_gamma > 0.0:
			Is = g_Iin * g_Ks * (cos_gamma ** g_Shininess)

		I = Id * g_Sphere.color + Is + g_Ia
		I = np.minimum(I, 1.0)	# 1.0 を超えないようにする
		return I
	
	# 何とも交差しない
	return vec3(0.0, 0.0, 0.0)	# 背景色


def display():
	glClear(GL_COLOR_BUFFER_BIT)

	glBegin(GL_POINTS)
	for y in range(-g_HalfHeight, g_HalfHeight+1):
		for x in range(-g_HalfWidth, g_HalfWidth+1):
			colorVec = getPixelColor(x, y)	# 座標 (x, y) の色を取得する
			glColor3dv(colorVec)	# (x, y) の画素を描画
			glVertex2i(x, y)
	glEnd()
	glFlush()


# ウィンドウのサイズが変更されたときの処理
def resize(w, h):
    if h > 0:
        glViewport(0, 0, w, h)
        g_HalfWidth = w / 2
        g_HalfHeight = h / 2
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # ウィンドウ内の座標系設定
        glOrtho(-g_HalfWidth, g_HalfWidth, -g_HalfHeight, g_HalfHeight, -10, 10)
        glMatrixMode(GL_MODELVIEW)

# キーが押されたときのイベント処理
def keyboard(key, x, y): 
	if key in [b'q', b'Q', b'\x1b']: #b'\x1b'は ESC の ASCII コード
		glutDestroyWindow(g_WindowID)
		return

	glutPostRedisplay()

if __name__ == "__main__":
	glutInit(sys.argv) #ライブラリの初期化
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
	glutInitWindowSize(400, 400) #ウィンドウサイズを指定
	g_WindowID = glutCreateWindow(sys.argv[0]) #ウィンドウを作成
	glutDisplayFunc(display) #表示関数を指定
	glutReshapeFunc(resize) # ウィンドウサイズが変更されたときの関数を指定
	glutKeyboardFunc(keyboard) # キーボード関数を指定

	g_LightDirection = normalize(g_LightDirection)
	glClearColor(1., 1., 1., 1.) # 消去色指定

	glutMainLoop() #イベント待ち
