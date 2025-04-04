import numpy as np
from constants import PLANET_RADII, AU

Rs = PLANET_RADII['Sun'] / AU
Re = PLANET_RADII['Earth'] / AU
Rm = PLANET_RADII['Moon'] / AU

def check_sun_eclipse(sun_pos, moon_pos, earth_pos, t_range):
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
    mask = eclipse_types != None
    filtered_times = t_range[mask]
    filtered_types = eclipse_types[mask]
    return filtered_times, filtered_types

def check_moon_eclipse(sun_pos, moon_pos, earth_pos):
    pass
