import numpy as np
from scipy.linalg import eigvals
import time
from astropy.time import Time
from astropy import units as u
from simulate import ThreeBodySimulator
from coords import get_initial
import matplotlib.pyplot as plt


plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用 SimHei 字体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

def A_block(r_i, r_j, m_j):
    r = r_j - r_i
    dist = np.linalg.norm(r)
    #print("dist:", dist)
    if dist < 1e-30:
        return np.zeros((3, 3))
    I = np.eye(3)
    outer = np.outer(r, r)
    return m_j * (I / dist**3 - 3 * outer / dist**5)

def compute_jacobian(y0, masses):
    J = np.zeros((18, 18))

    # 速度对位置的导数为 0，位置对速度导数为单位阵
    for i in range(3):
        J[i*6:i*6+3, i*6+3:i*6+6] = np.eye(3)  # dr/dv = I

    # 加速度部分雅可比块 A_ij
    for i in range(3):
        r_i = y0[i*6:i*6+3]
        for j in range(3):
            if i == j:
                continue
            r_j = y0[j*6:j*6+3]
            Aij = A_block(r_i, r_j, masses[j])
            J[i*6+3:i*6+6, j*6:j*6+3] = Aij

    # A_ii = - sum_{j≠i} A_ij
    for i in range(3):
        Aii = np.zeros((3, 3))
        for j in range(3):
            if i == j:
                continue
            Aii -= J[i*6+3:i*6+6, j*6:j*6+3]
        J[i*6+3:i*6+6, i*6:i*6+3] = Aii

    return J



sun_body = get_initial("Sun")
earth_body = get_initial("Earth")
moon_body = get_initial("Moon")

planet_list = [sun_body, earth_body, moon_body]


'''
# 示例：地球、月球、太阳
masses = [5.972e24, 7.348e22, 1.989e30]  # kg

# 初始位置（简化）
r1 = np.array([0.0, 0.0, 0.0])                  # 地球
r2 = np.array([384400e3, 0.0, 0.0])             # 月球
r3 = np.array([1.496e11, 0.0, 0.0])             # 太阳

# 初始速度
v1 = np.array([0.0, 0.0, 0.0])
v2 = np.array([0.0, 1022.0, 0.0])               # 月球绕地
v3 = np.array([0.0, 0.0, 0.0])                  # 太阳静止
'''
aux_planet_list = []
coarse_step = 1 
simulator = ThreeBodySimulator(
    bodies=planet_list,
    aux_list=aux_planet_list,
    dt=coarse_step
)
# 构造 y0 向量
s = 0
max_eigenvalue = []
for i in range(600):
    y0 = np.hstack([sun_body.pos, sun_body.velocity, earth_body.pos, earth_body.velocity, moon_body.pos, moon_body.velocity])  # 共18维
    masses = [sun_body.mass, earth_body.mass, moon_body.mass]
    #print(y0)
    # 计算雅可比矩阵
    J = compute_jacobian(y0, masses)

    # 输出信息
    #print("雅可比矩阵 J:")
    #np.set_printoptions(formatter={'all': lambda x: f'{x:.g}'})
    #print(J)
    # 最大特征值模
    eig_mod = np.abs(eigvals(J))
    #a = eigvals(J)[np.argmax(eig_mod)]
    #if np.abs(1+a) > 1:
     #   print("时间：", i, "，不稳定", np.abs(1+a), "大于1")
    max_eigenvalue = np.append(max_eigenvalue, np.max(eig_mod))
    if s < np.max(eig_mod):
        s = np.max(eig_mod)
        print("时间：", i, "，最大特征值模 λ_max ≈", s)

    trajectories, t_range = simulator.simulate_rk4(years=1/12)
# 轨迹可视化
time_steps = np.arange(0, 600)  

plt.figure(figsize=(10, 6))
plt.plot(time_steps, np.ones(600), color = 'red', linestyle = '-')
plt.plot(time_steps, max_eigenvalue, label='最大特征值模')
plt.xlabel('时间步数')
plt.ylabel('log(最大特征值模)（步长为月）') 
plt.legend()
plt.show()




