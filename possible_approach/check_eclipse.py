import numpy as np
from constants import PLANET_RADII, AU

Rs = PLANET_RADII['Sun'] / AU
Re = PLANET_RADII['Earth'] / AU
Rm = PLANET_RADII['Moon'] / AU

def check_sun_eclipse(sun_pos, moon_pos, earth_pos):
    """检测日食
    Args:
        sun_pos: 太阳位置 shape=(n,3)
        moon_pos: 月球位置 shape=(n,3)
        earth_pos: 地球位置 shape=(n,3)
        t_range: 时间序列 shape=(n,) (这个参数可以移除，因为不再需要)
    Returns:
        eclipse_types: 日食类型，如果没有发生日食则为None
    """
    moon_pos = moon_pos.copy()
    earth_pos = earth_pos.copy()
    
    moon_pos -= sun_pos
    earth_pos -= sun_pos
    dot0 = np.sum((earth_pos-moon_pos)*earth_pos, axis=-1)
    center1 = moon_pos * Rs / (Rs - Rm)
    center2 = moon_pos * Rs / (Rs + Rm)
    re1 = earth_pos - center1
    re2 = earth_pos - center2
    re1_norm = np.linalg.norm(re1, axis=-1)
    re2_norm = np.linalg.norm(re2, axis=-1)
    rm1 = moon_pos - center1
    rm2 = moon_pos - center2
    rm1_norm = np.linalg.norm(rm1, axis=-1)
    rm2_norm = np.linalg.norm(rm2, axis=-1)
    dot1 = np.sum(re1*rm1, axis=-1)
    dot2 = np.sum(re2*rm2, axis=-1)
    threshold1 = (re1_norm**2*rm1_norm**2-dot1**2)-(Re**2*rm1_norm**2+re1_norm**2*Rm**2+2*Re*Rm*dot1)
    threshold2 = (re2_norm**2*rm2_norm**2-dot2**2)-(Re**2*rm2_norm**2+re2_norm**2*Rm**2+2*Re*Rm*dot2)
    
    conditions = [
        (threshold1 < 0) & (dot1 > 0) & (dot0 > 0),   # 全食
        (threshold1 < 0) & (dot1 <= 0) & (dot0 > 0),   # 环食
        (threshold2 < 0) & (threshold1 >= 0) & (dot0 > 0)   # 偏食
    ]
    
    choices = ["total", "annular", "partial"]
    eclipse_types = np.select(conditions, choices, default=None)
    
    return eclipse_types

def check_moon_eclipse(sun_pos, moon_pos, earth_pos):
    # 将坐标原点移到太阳位置
    moon_pos -= sun_pos
    earth_pos -= sun_pos
    
    # 检查月球是否在地球背向太阳的一侧
    dot0 = np.sum((moon_pos-earth_pos)*(earth_pos), axis=-1)
    
    # 计算地球本影锥的顶点
    umbra_vertex = earth_pos * Rs / (Rs - Re)
    
    # 计算地球半影锥的顶点
    penumbra_vertex = earth_pos * Rs / (Rs + Re)
    
    # 计算月球到两个顶点的向量
    rm_umbra = moon_pos - umbra_vertex
    rm_penumbra = moon_pos - penumbra_vertex
    
    # 计算地球到两个顶点的向量
    re_umbra = earth_pos - umbra_vertex
    re_penumbra = earth_pos - penumbra_vertex
    
    # 计算向量的范数
    rm_umbra_norm = np.linalg.norm(rm_umbra, axis=-1)
    rm_penumbra_norm = np.linalg.norm(rm_penumbra, axis=-1)
    re_umbra_norm = np.linalg.norm(re_umbra, axis=-1)
    re_penumbra_norm = np.linalg.norm(re_penumbra, axis=-1)
    
    # 计算向量的点积
    dot_umbra = np.sum(rm_umbra*re_umbra, axis=-1)
    dot_penumbra = np.sum(rm_penumbra*re_penumbra, axis=-1)
    
    # 计算判定阈值
    threshold_umbra = (rm_umbra_norm**2*re_umbra_norm**2-dot_umbra**2)-(Rm**2*re_umbra_norm**2+rm_umbra_norm**2*Re**2+2*Re*Rm*dot_umbra)
    threshold_penumbra = (rm_penumbra_norm**2*re_penumbra_norm**2-dot_penumbra**2)-(Rm**2*re_penumbra_norm**2+rm_penumbra_norm**2*Re**2+2*Re*Rm*dot_penumbra)
    
    # 定义月食的条件
    conditions = [
        (threshold_umbra < 0) & (dot_umbra > 0) & (dot0 < 0),    # 全食
        (threshold_penumbra < 0) & (threshold_umbra >= 0) & (dot0 < 0)    # 偏食
    ]
    
    choices = ["total", "partial"]
    eclipse_types = np.select(conditions, choices, default=None)
    
    return eclipse_types