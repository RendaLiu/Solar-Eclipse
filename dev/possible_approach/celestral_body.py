'''
本文档定义了CelestralBody类，初始化了各大行星的位置，包含GetInitials等函数
'''

from skyfield.api import load
from past.builtins import xrange
import numpy as np


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

    def update_position(self, dt):
        """
        根据当前速度更新位置
        :param dt: 时间步长 (小时)
        """
        self.pos += self.velocity * dt

    def apply_force(self, force, dt):
        """
        根据合力计算速度变化
        :param force: 作用力 (numpy 数组, 单位 N)
        :param dt: 时间步长 (小时)
        """
        acceleration = force / self.mass  # a = F / m
        self.velocity += acceleration * dt * 3600  # 3600 秒 = 1 小时

    def __str__(self):
        return f"{self.name}: pos={self.position}, vel={self.velocity}"

# 加载 JPL DE 精度表
ephemeris = load('de421.bsp')

# 获取天体对象
sun = ephemeris['sun']
earth = ephemeris['earth']
moon = ephemeris['moon']
venus = ephemeris['venus']
jupiter = ephemeris['jupiter barycenter']  # 木星的质心

# 设定时间为 2025 年 1 月 1 日 00:00 UTC
ts = load.timescale()
t = ts.utc(2025, 1, 1, 0, 0, 0)

t_m1 = ts.utc(2024, 12, 31, 18, 0)
t1 = ts.utc(2025, 1, 1, 6, 0, 0)

t2 = ts.utc(2025, 3, 31, 7, 3, 7)

# 计算相对于太阳的坐标 (单位：AU)
earth_pos = earth.at(t).observe(sun).position.km / 1.496e+8  # AU
earth_posm1 = earth.at(t_m1).observe(sun).position.km / 1.496e+8
earth_pos1 = earth.at(t1).observe(sun).position.km / 1.496e+8  # AU
earth_pos2 = earth.at(t2).observe(sun).position.km / 1.496e+8

earth_velocity = (earth_pos1 - earth_posm1) / 12 #AU/h

'''
print(np.linalg.det([earth_pos, earth_pos1, earth_pos2]))
print(earth_pos @ earth_pos2)
'''

# 归一化：利用(2025, 1, 1, 0, 0, 0)与(2025, 3, 31, 7, 3, 7)的地球数据进行归一化，确保earth_pos为[1, 0, 0]
earth_pos /= np.linalg.norm(earth_pos)
# print(np.linalg.norm(earth_pos2))
earth_pos2 /= np.linalg.norm(earth_pos2)
perp = np.cross(earth_pos,earth_pos2)
# print(perp)
A = np.vstack([earth_pos, earth_pos2, perp])
# print(np.linalg.det(A))
earth_pos = earth_pos @ A.T

moon_pos = (moon.at(t).observe(sun).position.km / 1.496e+8) @ A.T
# 金星和木星在一开始可以忽略
'''
venus_pos = (venus.at(t).observe(sun).position.km / 1.496e+8) @ A.T
jupiter_pos = (jupiter.at(t).observe(sun).position.km / 1.496e+8) @ A.T
'''
# 打印初始位置
'''
print(f"Earth Position (AU): {earth_pos}")
print(f"Moon Position (AU): {moon_pos}")
print(f"Venus Position (AU): {venus_pos}")
print(f"Jupiter Position (AU): {jupiter_pos}")
'''

planet_masses = {
    "Sun": 1.989e30,
    "Mercury": 3.301e23,
    "Venus": 4.867e24,
    "Earth": 5.972e24,
    "Mars": 6.417e23,
    "Jupiter": 1.899e27,
    "Saturn": 5.683e26,
    "Uranus": 8.681e25,
    "Neptune": 1.024e26,
    "Moon": 7.348e22,
}

# 半径 (m)
planet_radii = {
    "Sun": 6.957e8,
    "Mercury": 2.439e6,
    "Venus": 6.052e6,
    "Earth": 6.378e6,
    "Mars": 3.390e6,
    "Jupiter": 7.149e7,
    "Saturn": 6.027e7,
    "Uranus": 2.556e7,
    "Neptune": 2.476e7,
    "Moon": 1.737e6,
}

def getInitials(cb):
    celestral_body = CelestralBody()

    celestral_body.name = cb
    if cb not in planet_radii: 
        raise KeyError(f"Error: '{cb}' is not a valid celestial body! Only Sun and 8 planets are allowed.")
        return
    celestral_body.radius = planet_radii[cb]  # m
    celestral_body.mass = planet_masses[cb] # kg

    if cb == 'Earth':
        celestral_body.pos = earth_pos
        celestral_body.velocity = earth_velocity
        return celestral_body
    
    before = celestral_body.name.at(t_m1).observe(sun).position.km / 1.496e+8
    after = celestral_body.name.at(t1).observe(sun).position.km / 1.496e+8

    celestral_body.velocity = ((after - before) / 12) @ A.T # AU/h
    celestral_body.pos = (celestral_body.name.at(t2).observe(sun).position.km / 1.496e+8) @ A.T

    return celestral_body
