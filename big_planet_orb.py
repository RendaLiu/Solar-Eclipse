import numpy as np
from constants import PLANET_MASS
from coords import get_initial

M_SUN = PLANET_MASS['Sun']


def circular_orbit_3d_params(r0, v0):
    """
    根据初始位置和速度确定三维正圆轨道参数
    :param r0: 初始位置 [x, y, z] (单位一致即可)
    :param v0: 初始速度 [vx, vy, vz]
    :return: 轨道半径, 角速度, 倾角, 升交点经度, 初始相位角
    """
    h = np.cross(r0, v0)
    n = h / np.linalg.norm(h)

    # 轨道倾角 (rad)
    i = np.arccos(n[2])

    # 升交点经度 (rad)
    Omega = np.arctan2(n[0], -n[1])

    # 轨道半径和角速度
    r0_norm = np.linalg.norm(r0)
    v0_norm = np.linalg.norm(v0)
    a = 1 / (2 / r0_norm - v0_norm**2 / M_SUN)
    omega = np.sqrt(M_SUN / a ** 3)

    # 初始相位角 (从升交点起算)
    x, y, z = r0
    theta0 = np.arctan2(z / np.sin(i),
                        x * np.cos(Omega) + y * np.sin(Omega))

    return a, omega, i, Omega, theta0


def circular_orbit_3d_position(a, omega, i, Omega, theta0, t):
    """
    计算三维正圆轨道在时间 t 的位置
    :param a: 轨道半径
    :param omega: 角速度 (rad/s)
    :param i: 轨道倾角 (rad)
    :param Omega: 升交点经度 (rad)
    :param theta0: 初始相位角 (rad)
    :param t: 时间
    :return: 位置向量 [x, y, z]
    """
    theta = theta0 + omega * t

    # 旋转到惯性系 (3-1-3欧拉旋转)
    R = np.array([
        [np.cos(Omega)*np.cos(theta) - np.sin(Omega)*np.sin(theta)*np.cos(i),
         -np.cos(Omega)*np.sin(theta) - np.sin(Omega)*np.cos(theta)*np.cos(i),
         np.sin(Omega)*np.sin(i)],

        [np.sin(Omega)*np.cos(theta) + np.cos(Omega)*np.sin(theta)*np.cos(i),
         -np.sin(Omega)*np.sin(theta) + np.cos(Omega)*np.cos(theta)*np.cos(i),
         -np.cos(Omega)*np.sin(i)],

        [np.sin(theta)*np.sin(i),
         np.cos(theta)*np.sin(i),
         np.cos(i)]
    ])

    return R @ np.array([a, 0, 0])


def get_jupiter_orb_fn(Jupiter):
    a, omega, i, Omega, theta0 = circular_orbit_3d_params(Jupiter.pos, Jupiter.velocity)

    def orb_fn(t):
        return circular_orbit_3d_position(a, omega, i, Omega, theta0, t)
    return orb_fn


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # 生成轨道点
    times = np.linspace(0, 8*365*24, 1000)  # 12年周期
    orb_fn = get_jupiter_orb_fn(get_initial("Jupiter"))
    positions = np.array([orb_fn(t) for t in times])

    # 绘制
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], label="Jupiter's Orbit")
    ax.scatter([0], [0], [0], color='yellow', s=200, label='Sun')
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.legend()
    plt.show()
