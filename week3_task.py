import sys
import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ============================================================================
# グローバル変数
# ============================================================================
g_WindowWidth = 1200
g_WindowHeight = 800
time_counter = 0
carousel_rotation = 0.0
bloom_enabled = True
time_of_day = 2  # 0:Day, 1:Sunset, 2:Night

# サンプルコードと同じ視点設定
g_EyeCenterY = 9.0
g_EyeCenterZ = 30.0
g_EyeRadius = 8.0
g_EyeY = g_EyeCenterY
g_EyeZ = g_EyeCenterZ


# ============================================================================
# ティーポット描画関数（carousel_horse.pyから移植）
# ============================================================================
def draw_teapot(color_variant=0, animation_phase=0.0):
    """ティーポットを描画（03_kadai_sample.pyを参考）"""
    random.seed(color_variant + 1)

    ambient = [0.2 * random.random(), 0.2 * random.random(), 0.2 * random.random(), 1.]
    diffuse = [0.2 * random.random() + 0.8, 0.2 * random.random() + 0.8, 0.2 * random.random() + 0.8, 1.]
    specular = [0.3 * random.random() + 0.2, 0.3 * random.random() + 0.2, 0.3 * random.random() + 0.2, 1.]
    shininess = 2. + 30 * random.random()
    angle = 15 * (2. * random.random() - 1.)

    glPushMatrix()

    # 上下動アニメーション
    vertical_offset = math.sin(animation_phase) * 0.4
    glTranslatef(0, vertical_offset, 0)

    # マテリアル設定
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)

    # ティーポット本体（小さくした）
    glRotatef(angle, 0, 0, 1)
    glutSolidTeapot(0.5)

    glPopMatrix()


def draw_teapot_stand():
    """ティーポットを支える柱"""
    glPushMatrix()
    glTranslatef(0, -1.0, 0)
    glColor3f(0.7, 0.6, 0.4)

    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.1, 0.1, 1.5, 16, 16)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    glPopMatrix()


# ============================================================================
# 装飾関数（carousel_decorations.pyから移植）
# ============================================================================
def draw_carousel_base(rotation_angle=0.0):
    """回転台"""
    glPushMatrix()
    glRotatef(rotation_angle, 0, 1, 0)

    # 下段プラットフォーム
    glPushMatrix()
    glTranslatef(0, -0.1, 0)
    glColor3f(0.6, 0.4, 0.2)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 5.5, 5.5, 0.2, 32, 32)
    gluDeleteQuadric(quadric)
    glPopMatrix()
    glPopMatrix()

    # 中段プラットフォーム
    glPushMatrix()
    glTranslatef(0, 0.1, 0)
    glColor3f(0.9, 0.7, 0.3)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 5.2, 5.2, 0.15, 32, 32)
    gluDeleteQuadric(quadric)
    glPopMatrix()
    glPopMatrix()

    # エッジ装飾
    for i in range(64):
        angle = i * (2 * math.pi / 64)
        x = math.cos(angle) * 5.3
        z = math.sin(angle) * 5.3
        glPushMatrix()
        glTranslatef(x, 0.05, z)
        glColor3f(1.0, 0.84, 0.0)
        glutSolidSphere(0.08, 8, 8)
        glPopMatrix()

    glPopMatrix()


def draw_carousel_canopy(rotation_angle=0.0, time_counter=0):
    """屋根"""
    glPushMatrix()
    glRotatef(rotation_angle, 0, 1, 0)

    # ストライプ屋根
    stripe_count = 16
    for i in range(stripe_count):
        angle_start = i * (360.0 / stripe_count)
        if i % 2 == 0:
            glColor3f(0.9, 0.1, 0.15)
        else:
            glColor3f(1.0, 0.95, 0.95)

        glPushMatrix()
        glTranslatef(0, 4.5, 0)
        glRotatef(angle_start, 0, 1, 0)

        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        segment_angle = 2 * math.pi / stripe_count
        for j in range(3):
            theta = j * segment_angle / 2
            x = math.sin(theta) * 5.5
            z = math.cos(theta) * 5.5
            glVertex3f(x, -1.5, z)
        glEnd()
        glPopMatrix()

    # 頂上装飾
    glPushMatrix()
    glTranslatef(0, 4.8, 0)
    glColor3f(1.0, 0.84, 0.0)
    glutSolidSphere(0.3, 16, 16)
    glPopMatrix()

    glPopMatrix()


def draw_center_pole():
    """中央支柱"""
    glColor3f(1.0, 0.84, 0.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 0.25, 0.25, 5.0, 24, 24)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    # 装飾リング
    for i in range(5):
        glPushMatrix()
        glTranslatef(0, i * 1.0, 0)
        glColor3f(1.0, 0.9, 0.1)
        glutSolidTorus(0.08, 0.35, 12, 24)
        glPopMatrix()

    # 頂上装飾
    glPushMatrix()
    glTranslatef(0, 5.2, 0)
    glColor3f(1.0, 0.84, 0.0)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.3, 0.6, 16, 16)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0.6, 0)
    glColor3f(1.0, 0.9, 0.1)
    glutSolidSphere(0.2, 16, 16)
    glPopMatrix()
    glPopMatrix()


def draw_led_lights(time_counter=0, rotation_angle=0.0):
    """LEDライト"""
    glPushMatrix()
    glRotatef(rotation_angle, 0, 1, 0)

    led_count = 32
    for i in range(led_count):
        angle = i * (2 * math.pi / led_count)
        x = math.cos(angle) * 5.3
        z = math.sin(angle) * 5.3

        phase = (i + time_counter * 0.1) % led_count / led_count
        r = 0.5 + 0.5 * math.sin(phase * math.pi * 4)
        g = 0.5 + 0.5 * math.sin(phase * math.pi * 4 + 2)
        b = 0.5 + 0.5 * math.sin(phase * math.pi * 4 + 4)

        glPushMatrix()
        glTranslatef(x, 3.5, z)
        glColor3f(r, g, b)
        glutSolidSphere(0.12, 10, 10)
        glPopMatrix()

    glPopMatrix()


# ============================================================================
# 視覚効果関数（visual_effects.pyから移植）
# ============================================================================
def get_sky_color():
    """空の色を取得"""
    if time_of_day == 0:
        return (0.4, 0.6, 0.9)
    elif time_of_day == 1:
        return (0.8, 0.4, 0.2)
    else:
        return (0.05, 0.05, 0.15)


def get_ambient_light():
    """環境光を取得"""
    if time_of_day == 0:
        return (0.5, 0.5, 0.5, 1.0)
    elif time_of_day == 1:
        return (0.6, 0.3, 0.2, 1.0)
    else:
        return (0.1, 0.1, 0.15, 1.0)


def get_main_light_color():
    """メインライトの色を取得"""
    if time_of_day == 0:
        return (1.0, 1.0, 0.95, 1.0)
    elif time_of_day == 1:
        return (1.0, 0.6, 0.3, 1.0)
    else:
        return (0.3, 0.3, 0.4, 1.0)


def apply_lighting():
    """ライティングを適用"""
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, get_ambient_light())
    glLightfv(GL_LIGHT0, GL_DIFFUSE, get_main_light_color())
    sky_color = get_sky_color()
    glClearColor(sky_color[0], sky_color[1], sky_color[2], 1.0)


def draw_bloom_glow(x, y, z, radius, color, intensity=1.0):
    """ブルーム効果"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)

    lighting_enabled = glIsEnabled(GL_LIGHTING)
    if lighting_enabled:
        glDisable(GL_LIGHTING)

    glPushMatrix()
    glTranslatef(x, y, z)

    layers = 5
    for i in range(layers, 0, -1):
        scale = radius * (i / layers)
        alpha = intensity * (0.15 / i)

        glColor4f(color[0], color[1], color[2], alpha)

        glPushMatrix()
        glScalef(scale, scale, scale)
        glutSolidSphere(1.0, 12, 12)
        glPopMatrix()

    glPopMatrix()

    if lighting_enabled:
        glEnable(GL_LIGHTING)

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)


# ============================================================================
# メインシーン描画
# ============================================================================
def draw_teapots(rotation_angle, t):
    """8個のティーポットを配置"""
    glPushMatrix()
    glRotatef(rotation_angle, 0, 1, 0)

    teapot_count = 8
    for i in range(teapot_count):
        angle = i * (2 * math.pi / teapot_count)
        x = math.cos(angle) * 3.0
        z = math.sin(angle) * 3.0

        animation_phase = t * 0.05 + i * 0.5

        glPushMatrix()
        glTranslatef(x, 0.5, z)
        glRotatef(math.degrees(angle), 0, 1, 0)

        draw_teapot_stand()
        draw_teapot(color_variant=i, animation_phase=animation_phase)

        glPopMatrix()

    glPopMatrix()


def draw_bloom_effects(t, rotation_angle):
    """ブルーム効果を描画"""
    led_count = 32
    for i in range(led_count):
        angle = i * (2 * math.pi / led_count) + math.radians(rotation_angle)
        x = math.cos(angle) * 5.3
        z = math.sin(angle) * 5.3

        phase = (i + t * 0.1) % led_count / led_count
        r = 0.5 + 0.5 * math.sin(phase * math.pi * 4)
        g = 0.5 + 0.5 * math.sin(phase * math.pi * 4 + 2)
        b = 0.5 + 0.5 * math.sin(phase * math.pi * 4 + 4)

        draw_bloom_glow(x, 3.5, z, radius=0.3, color=(r, g, b), intensity=1.5)

    draw_bloom_glow(0, 5.2, 0, radius=0.5, color=(1.0, 0.9, 0.2), intensity=2.0)


def draw_ground():
    """地面"""
    # 地面のグリッド
    glPushMatrix()
    glTranslatef(0, -0.5, 0)
    glColor3f(0.3, 0.5, 0.3)

    # 大きな地面
    glBegin(GL_QUADS)
    glVertex3f(-20, 0, -20)
    glVertex3f(20, 0, -20)
    glVertex3f(20, 0, 20)
    glVertex3f(-20, 0, 20)
    glEnd()
    glPopMatrix()


def draw_fence():
    """外周フェンス"""
    fence_count = 24
    fence_radius = 9.0

    for i in range(fence_count):
        angle = i * (2 * math.pi / fence_count)
        x = math.cos(angle) * fence_radius
        z = math.sin(angle) * fence_radius

        glPushMatrix()
        glTranslatef(x, 0.5, z)
        glColor3f(0.7, 0.7, 0.7)
        glPushMatrix()
        glScalef(0.08, 1.0, 0.08)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()

    # 連結バー
    glPushMatrix()
    glTranslatef(0, 0.8, 0)
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidTorus(0.05, fence_radius, 12, fence_count)
    glPopMatrix()
    glPopMatrix()


def draw_scene():
    """シーン全体を描画"""
    global carousel_rotation

    apply_lighting()

    # 地面と柵
    draw_ground()
    draw_fence()

    draw_center_pole()
    draw_carousel_base(carousel_rotation)
    draw_teapots(carousel_rotation, time_counter)
    draw_carousel_canopy(carousel_rotation, time_counter)
    draw_led_lights(time_counter, carousel_rotation)

    if bloom_enabled:
        draw_bloom_effects(time_counter, carousel_rotation)


# ============================================================================
# OpenGL初期化・コールバック関数
# ============================================================================
def init():
    """OpenGLの初期化"""
    sky_color = get_sky_color()
    glClearColor(sky_color[0], sky_color[1], sky_color[2], 1.0)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.95, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.35, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.8, 0.8, 0.8, 1])

    glLightfv(GL_LIGHT1, GL_POSITION, [10, 5, 10, 1])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.6, 1])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.3, 0.3, 0.3, 1])

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    glShadeModel(GL_SMOOTH)

    print("=" * 60)
    print("Teapot Merry-Go-Round Simulator")
    print("=" * 60)
    print("\n[Controls]")
    print("  T        : Change time of day (Day->Sunset->Night)")
    print("  B        : Toggle bloom effect")
    print("  ESC/Q    : Quit")
    print("\n[Features]")
    print("  - 8 rotating teapots (based on 03_kadai_sample.py)")
    print("  - Circular camera motion")
    print("  - Bloom effect (glowing lights)")
    print("  - Time of day changes")
    print("=" * 60)


def display():
    """描画コールバック"""
    global time_counter

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, g_WindowWidth / float(g_WindowHeight), 1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, g_EyeY, g_EyeZ, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    draw_scene()

    glutSwapBuffers()
    time_counter += 1


def reshape(width, height):
    """ウィンドウリサイズコールバック"""
    global g_WindowWidth, g_WindowHeight

    if height > 0:
        glViewport(0, 0, width, height)
        g_WindowWidth = width
        g_WindowHeight = height


def keyboard(key, x, y):
    """キーボードコールバック"""
    global time_of_day, bloom_enabled

    if key == b't' or key == b'T':
        time_of_day = (time_of_day + 1) % 3
        time_names = {0: "Day", 1: "Sunset", 2: "Night"}
        print(f"Time of day: {time_names[time_of_day]}")

    elif key == b'b' or key == b'B':
        bloom_enabled = not bloom_enabled
        print(f"Bloom effect: {'ON' if bloom_enabled else 'OFF'}")

    elif key == b'q' or key == b'Q' or key == b'\x1b':
        print("\nExiting simulator")
        sys.exit(0)


def timer(value):
    """タイマーコールバック"""
    global carousel_rotation, g_EyeY, g_EyeZ

    carousel_rotation += 1.0

    rotation_rad = 2.0 * carousel_rotation * math.pi / 180.0
    g_EyeY = g_EyeCenterY + g_EyeRadius * math.sin(rotation_rad)
    g_EyeZ = g_EyeCenterZ + g_EyeRadius * math.cos(rotation_rad)

    glutPostRedisplay()
    glutTimerFunc(10, timer, 0)


def main():
    """メイン関数"""
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(g_WindowWidth, g_WindowHeight)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Teapot Merry-Go-Round Simulator")

    init()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, timer, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()
