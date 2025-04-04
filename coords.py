from skyfield.api import load
import numpy as np
from constants import AU, PLANET_TAG, PLANET_MASS, PLANET_RADII


class CelestialBody:
    def __init__(self, name, mass, position, velocity, radius):
        """
        初始化天体
        :param name: 天体名称 (str)
        :param mass: 质量 (kg)
        :param position: 初始位置 (numpy 数组, 单位 AU)
        :param velocity: 初始速度 (numpy 数组, 单位 AU/h)
        :param radius: 天体半径 (m) ## ！！注意！！ 这里有两个长度单位
        """
        self.name = name
        self.mass = mass
        self.pos = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.radius = radius

    def __str__(self):
        return f"{self.name}: pos={self.pos}, vel={self.velocity}"


# 加载 JPL DE 精度表
ephemeris = load('de421.bsp')

# 获取天体对象
sun = ephemeris['sun']
earth = ephemeris['earth']

# 设定时间为 2025 年 1 月 1 日 00:00 UTC
ts = load.timescale()
t = ts.utc(2025, 1, 1, 0, 0, 0)
t1 = ts.utc(2025, 1, 1, 3, 0, 0)
t_m = ts.utc(2024, 12, 31, 21, 0)
t2 = ts.utc(2025, 3, 31, 7, 3, 7)

# 计算相对于太阳的坐标 (单位：AU)
earth_pos = earth.at(t).observe(sun).position.km / AU  # AU
earth_pos1 = earth.at(t2).observe(sun).position.km / AU  # AU

# 归一化：利用(2025, 1, 1, 0, 0, 0)与(2025, 3, 31, 7, 3, 7)的地球数据进行归一化，确保earth_pos为[1, 0, 0]
earth_pos /= np.linalg.norm(earth_pos)
earth_pos1 /= np.linalg.norm(earth_pos1)
perp = np.cross(earth_pos, earth_pos1)
A = np.vstack([earth_pos, earth_pos1, perp])


def get_initial(cb_name):
    if cb_name not in PLANET_TAG:
        raise KeyError(f"Error: '{cb_name}' is not valid!")

    # 获取对应的星体对象
    cb_obj = ephemeris[PLANET_TAG[cb_name]]

    # 计算位置和速度
    pos_m1 = cb_obj.at(t_m).observe(sun).position.km / 1.496e8
    pos_t1 = cb_obj.at(t1).observe(sun).position.km / 1.496e8
    velocity = ((pos_t1 - pos_m1) / 6) @ A.T  # AU/h

    pos = (cb_obj.at(t).observe(sun).position.km / 1.496e8) @ A.T

    return CelestialBody(
        name=cb_name,
        mass=PLANET_MASS[cb_name],
        position=pos,
        velocity=velocity,
        radius=PLANET_RADII[cb_name]
    )


if __name__ == "__main__": 
    moon = get_initial("Moon")
    print(moon.mass)