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

# 板。xz平面に平行な面とする
class Board:
	def __init__(self, y):
		self.y = y	# y座標値
	
	# 点pを通り、v方向のRayとの交わりを判定する。
	# 交点が p+tv として表せる場合の t の値を返す。交わらない場合は負の値を返す
	def getIntersect(self, p, v):
		if abs(v[1]) < 1.0e-6:	# 水平なRayは交わらない
			return -1.0

		# y = self.y の平面との交点を求める
		# p[1] + t * v[1] = self.y より t = (self.y - p[1]) / v[1]
		t = (self.y - p[1]) / v[1]

		# 交点のz座標を計算
		z_intersect = p[2] + t * v[2]

		# z座標が-3000より小さいなら交わらない
		if z_intersect < -3000:
			return -1.0

		return t
	
	# x と z の値から床の色を返す（格子模様になるように）
	def getColorVec(self, x, z):
		# 100x100の格子模様を作成
		# x座標とz座標をそれぞれ100で割った商の和が偶数か奇数かで色を変える
		grid_x = int(x // 100)
		grid_z = int(z // 100)

		if (grid_x + grid_z) % 2 == 0:
			return vec3(1.0, 1.0, 0.7)  # 明るい黄色
		else:
			return vec3(0.6, 0.6, 0.6)  # 灰色

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

# アンチエイリアシングの設定
g_AntiAliasing = True  # True: アンチエイリアシング有効, False: 無効

g_Viewpoint = vec3(0., 0., 0.)	# 視点位置
g_LightDirection = vec3(-2., -4., -2.)	# 入射光の進行方向

g_Sphere = Sphere(vec3(0, 0, -1500.),	# 中心座標
		  150.0,		# 半径
		  vec3(0.2, 0.9, 0.9))	# RGB 値

# 球体の置かれている床
g_Board = Board(-150)	# y座標値を -150 にする。（球と接するようにする）

# x, y で指定されたスクリーン座標での色 (RGB) を計算する
def getPixelColor(x, y):
	# 原点からスクリーン上のピクセルへ飛ばすレイの方向
	ray = vec3(x, y, -g_Distance) - g_Viewpoint
	ray = normalize(ray)	# レイの長さの正規化

	# レイを飛ばして球との交点を求める
	t = g_Sphere.getIntersect(g_Viewpoint, ray)

	if t > 0.0:	# 球との交点がある
		# 交点の座標を計算
		intersection = g_Viewpoint + t * ray

		# 法線ベクトル（球の中心から交点へのベクトル）
		normal = normalize(intersection - g_Sphere.center)

		# 光源方向（光の進行方向の逆ベクトル）
		light_dir = normalize(-g_LightDirection)

		# 拡散反射光の計算
		cos_theta = max(0.0, normal.dot(light_dir))
		Id = g_Kd * g_Iin * cos_theta

		# 反射ベクトル R = 2(N・L)N - L
		reflect_vec = 2.0 * normal.dot(light_dir) * normal - light_dir

		# 視線方向（視点から交点へのベクトル）
		view_dir = normalize(-ray)

		# 鏡面反射光の計算
		cos_alpha = max(0.0, reflect_vec.dot(view_dir))
		Is = g_Ks * g_Iin * (cos_alpha ** g_Shininess)

		I = Id * g_Sphere.color + Is + g_Ia
		I = np.minimum(I, 1.0)	# 1.0 を超えないようにする
		return I
	
	# レイを飛ばして床と交差するか求める
	t = g_Board.getIntersect(g_Viewpoint, ray)

	if t > 0.0:	# 床との交点がある
		# 交点の座標を計算
		intersection = g_Viewpoint + t * ray

		# 床の色を取得（格子模様）
		floor_color = g_Board.getColorVec(intersection[0], intersection[2])

		# 床の法線ベクトル（上向き）
		normal = vec3(0., 1., 0.)

		# 光源方向（光の進行方向の逆ベクトル）
		light_dir = normalize(-g_LightDirection)

		# 拡散反射光の計算
		cos_theta = max(0.0, normal.dot(light_dir))
		Id = g_Kd * g_Iin * cos_theta

		# 床の表面色を計算
		I = Id * floor_color + g_Ia

		# 影の判定：交点から光源方向にレイを飛ばして球と交わるかチェック
		shadow_ray_origin = intersection + 0.001 * light_dir  # 微小量だけずらす（数値誤差対策）
		t_shadow = g_Sphere.getIntersect(shadow_ray_origin, light_dir)

		if t_shadow > 0.0:  # 球に遮られる場合（影になる）
			I = I * 0.5

		I = np.minimum(I, 1.0)	# 1.0 を超えないようにする
		return I
	
	# 何とも交差しない
	return vec3(0.0, 0.0, 0.0)	# 背景色

def display():
	glClear(GL_COLOR_BUFFER_BIT)

	glBegin(GL_POINTS)
	for y in range(-g_HalfHeight, g_HalfHeight+1):
		for x in range(-g_HalfWidth, g_HalfWidth+1):
			if g_AntiAliasing:
				# 3x3スーパーサンプリング
				# 各ピクセルを9分割してサンプリング
				color_sum = vec3(0., 0., 0.)
				for dy in [-1./3., 0., 1./3.]:
					for dx in [-1./3., 0., 1./3.]:
						color_sum += getPixelColor(x + dx, y + dy)
				colorVec = color_sum / 9.0  # 9つの平均値
			else:
				# アンチエイリアシングなし
				colorVec = getPixelColor(x, y)

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
	global g_AntiAliasing

	if key in [b'q', b'Q', b'\x1b']:
		glutDestroyWindow(g_WindowID)
		return
	elif key in [b'a', b'A']:
		# アンチエイリアシングの切り替え
		g_AntiAliasing = not g_AntiAliasing
		print(f"AntiAliasing: {'ON' if g_AntiAliasing else 'OFF'}")

	glutPostRedisplay()

if __name__ == "__main__":
	glutInit(sys.argv) #ライブラリの初期化
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
	glutInitWindowSize(400, 400) #ウィンドウサイズを指定
	g_WindowID = glutCreateWindow("課題(4): アンチエイリアシング") #ウィンドウを作成
	glutDisplayFunc(display) #表示関数を指定
	glutReshapeFunc(resize) # ウィンドウサイズが変更されたときの関数を指定
	glutKeyboardFunc(keyboard) # キーボード関数を指定

	g_LightDirection = normalize(g_LightDirection)
	glClearColor(1., 1., 1., 1.) # 消去色指定

	glutMainLoop() #イベント待ち
