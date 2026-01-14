import numpy as np
import math

# 出力ファイル名
OUTPUT_FILENAME = "parametric_surface_plane.obj"

# 定数
NUM_U = 50  # U方向の分割数
NUM_V = 50  # V方向の分割数

# 配列をnumpyで定義 (x, y, z座標)
x = np.zeros((NUM_U + 1, NUM_V + 1))
y = np.zeros((NUM_U + 1, NUM_V + 1))
z = np.zeros((NUM_U + 1, NUM_V + 1))

# u,v の値から3次元座標を返す関数
def function(u, v):
    # 平面の場合
    x = u * 100
    y = v * 100
    z = 0
    return x, y, z

# 配列に座標値を設定する
def setCoordinates():
    for i in range(NUM_U + 1):
        for j in range(NUM_V + 1):
            # u と v の値を 0.0 ～ 1.0 に正規化する
            u = 1.0 / NUM_U * i
            v = 1.0 / NUM_V * j
            # 座標値の設定
            x[i][j], y[i][j], z[i][j] = function(u, v)

# OBJ 形式でのファイル出力
def exportOBJ():
    try:
        # ファイルを開く
        with open(OUTPUT_FILENAME, 'w') as fout:
            # 頂点情報の出力
            fout.write("# Vertices\n")
            for i in range(NUM_U + 1):
                for j in range(NUM_V + 1):
                    # 各頂点の座標値を出力する
                    fout.write(f"v {x[i][j]} {y[i][j]} {z[i][j]}\n")
            
            # 面情報の出力
            fout.write("\n# Faces\n")
            for i in range(NUM_U):
                for j in range(NUM_V):
                    # 頂点(i, j)のインデックスは i * (NUM_V + 1) + j + 1
                    lb_index = i * (NUM_V + 1) + j + 1
                    rb_index = (i + 1) * (NUM_V + 1) + j + 1
                    lt_index = i * (NUM_V + 1) + (j + 1) + 1
                    rt_index = (i + 1) * (NUM_V + 1) + (j + 1) + 1

                    # 三角形を構成する頂点番号を出力 (反時計回り)
                    fout.write(f"f {lb_index} {rb_index} {rt_index}\n")
                    fout.write(f"f {lb_index} {rt_index} {lt_index}\n")

    except IOError as e:
        print(f"Error: {e}")
        exit(0)

# メイン処理
if __name__ == "__main__":
    setCoordinates()
    exportOBJ()
    print(f"Generated {OUTPUT_FILENAME}")
