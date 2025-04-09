import numpy as np
from constants import PLANET_RADII, AU

Rs = PLANET_RADII['Sun'] / AU
Re = PLANET_RADII['Earth'] / AU
Rm = PLANET_RADII['Moon'] / AU

def check_sun_eclipse(sun_pos, moon_pos, earth_pos, t_range, type=None):
    sun_pos = np.array(sun_pos, dtype=np.float64)
    moon_pos = np.array(moon_pos, dtype=np.float64)
    earth_pos = np.array(earth_pos, dtype=np.float64)
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
    threshold1 = np.linalg.norm(np.cross(re1, rm1, axis=-1), axis=-1)**2-(Re**2*rm1_norm**2+re1_norm**2*Rm**2+2*Re*Rm*dot1)
    threshold2 = np.linalg.norm(np.cross(re2, rm2, axis=-1), axis=-1)**2-(Re**2*rm2_norm**2+re2_norm**2*Rm**2+2*Re*Rm*dot2)
    conditions = [
        (threshold1 < 0) & (dot1 > 0) & (dot0 > 0),   # 全食
        (threshold1 < 0) & (dot1 <= 0) & (dot0 > 0),   # 环食
        (threshold2 < 0) & (threshold1 >= 0) & (dot0 > 0)   # 偏食
    ]
    choices = ["total", "annular", "partial"]
    eclipse_types = np.select(conditions, choices, default=None)
    if type is None:
        mask = eclipse_types != None
    else:
        mask = eclipse_types == type
    filtered_times = t_range[mask]
    return filtered_times, eclipse_types

def check_moon_eclipse(sun_pos, moon_pos, earth_pos, t_range, type=None):
    sun_pos = np.array(sun_pos, dtype=np.float64)
    moon_pos = np.array(moon_pos, dtype=np.float64)
    earth_pos = np.array(earth_pos, dtype=np.float64)
    # 将坐标原点移到太阳位置
    moon_pos -= sun_pos
    earth_pos -= sun_pos
    
    # 检查月球是否在地球背向太阳的一侧
    dot0 = np.sum((moon_pos-earth_pos)*(earth_pos), axis=-1)
    
    # 计算地球本影锥的顶点
    umbra_vertex = earth_pos * Rs / (Rs - Re)
    
    # 计算月球到两个顶点的向量
    rm_umbra = moon_pos - umbra_vertex
    
    # 计算地球到两个顶点的向量
    re_umbra = earth_pos - umbra_vertex
    
    # 计算向量的范数
    rm_umbra_norm = np.linalg.norm(rm_umbra, axis=-1)
    re_umbra_norm = np.linalg.norm(re_umbra, axis=-1)
    
    # 计算向量的点积
    dot_umbra = np.sum(rm_umbra*re_umbra, axis=-1)
    
    # 计算判定阈值
    threshold_umbra1 = np.linalg.norm(np.cross(re_umbra, rm_umbra, axis=-1), axis=-1)**2-(Rm**2*re_umbra_norm**2+rm_umbra_norm**2*Re**2+2*Re*Rm*dot_umbra)
    threshold_umbra2 = np.linalg.norm(np.cross(re_umbra, rm_umbra, axis=-1), axis=-1)**2-(Rm**2*re_umbra_norm**2+rm_umbra_norm**2*Re**2-2*Re*Rm*dot_umbra)
    
    # 定义月食的条件
    conditions = [
        (threshold_umbra2 < 0) & (dot_umbra > 0) & (dot0 > 0),    # 全食
        (threshold_umbra1 < 0) & (threshold_umbra2 > 0) & (dot0 > 0)
    ]
    
    choices = ["total", "partial"]
    eclipse_types = np.select(conditions, choices, default=None)
    if type is None:
        mask = eclipse_types != None
    else:
        mask = eclipse_types == type
    filtered_times = t_range[mask]
    return filtered_times, eclipse_types

def detect_accurate_times(check_fun, trajectories, filtered_times, eclipse_types, fine_steps):
    eclipse_start = []
    eclipse_type = []
    eclipse_end = []
    fine_t_range = (np.arange(fine_steps+1) / fine_steps)[:, None].repeat(3, axis=-1)
    # 检测发生日/月食的临界点
    for t in filtered_times:
        # 检测开始偏食的时间点
        if eclipse_types[t-1] is None:   
            fine_sun = trajectories['Sun'][t] * fine_t_range + trajectories['Sun'][t-1] * (1-fine_t_range)
            fine_earth = trajectories['Earth'][t] * fine_t_range + trajectories['Earth'][t-1] * (1-fine_t_range)
            fine_moon = trajectories['Moon'][t] * fine_t_range + trajectories['Moon'][t-1] * (1-fine_t_range)
            fine_filtered_times, _ = check_fun(fine_sun, fine_moon, fine_earth, fine_t_range[:, 0])
            eclipse_start.append(t-1+fine_filtered_times[0])
            eclipse_type.append("partial")
        # 检测退出偏食的时间点
        if eclipse_types[t+1] is None:
            fine_sun = trajectories['Sun'][t+1] * fine_t_range + trajectories['Sun'][t] * (1-fine_t_range)
            fine_earth = trajectories['Earth'][t+1] * fine_t_range + trajectories['Earth'][t] * (1-fine_t_range)
            fine_moon = trajectories['Moon'][t+1] * fine_t_range + trajectories['Moon'][t] * (1-fine_t_range)
            fine_filtered_times, _ = check_fun(fine_sun, fine_moon, fine_earth, fine_t_range[:, 0])
            eclipse_end.append(t+fine_filtered_times[-1])
        if eclipse_types[t] != "partial":
            # 检测从偏食转变为全食/环食的时间点
            if eclipse_types[t-1] != eclipse_types[t]:   
                fine_sun = trajectories['Sun'][t] * fine_t_range + trajectories['Sun'][t-1] * (1-fine_t_range)
                fine_earth = trajectories['Earth'][t] * fine_t_range + trajectories['Earth'][t-1] * (1-fine_t_range)
                fine_moon = trajectories['Moon'][t] * fine_t_range + trajectories['Moon'][t-1] * (1-fine_t_range)
                fine_filtered_times, _ = check_fun(fine_sun, fine_moon, fine_earth, fine_t_range[:, 0])
                eclipse_start.append(eclipse_start[-1])
                eclipse_type.append(eclipse_type[-1])
                eclipse_start[-2] = t-1+fine_filtered_times[0]
                eclipse_type[-2] = eclipse_types[t]
            # 检测从全食/环食转变为偏食的时间点
            if eclipse_types[t+1] != eclipse_types[t]:
                fine_sun = trajectories['Sun'][t+1] * fine_t_range + trajectories['Sun'][t] * (1-fine_t_range)
                fine_earth = trajectories['Earth'][t+1] * fine_t_range + trajectories['Earth'][t] * (1-fine_t_range)
                fine_moon = trajectories['Moon'][t+1] * fine_t_range + trajectories['Moon'][t] * (1-fine_t_range)
                fine_filtered_times, _ = check_fun(fine_sun, fine_moon, fine_earth, fine_t_range[:, 0])
                eclipse_end.append(t+fine_filtered_times[-1])
    return eclipse_start, eclipse_type, eclipse_end
