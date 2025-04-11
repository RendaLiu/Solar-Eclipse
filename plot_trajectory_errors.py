import numpy as np
import matplotlib.pyplot as plt
import time
from astropy.time import Time
from astropy import units as u
import sys
import json
from jplephem.spk import SPK
from constants import AU
from simulate import ThreeBodySimulator
from coords import get_initial
from check_eclipse import check_sun_eclipse, check_moon_eclipse, detect_accurate_times

 
sys.stdout = open('record.log', mode = 'w',encoding='utf-8')

coarse_step = 1
fine_steps = 100
total_lenth = 50

def load_de440_data(start_time, time_steps, step_hours=1):
    """
    读取DE440星历表数据
    
    参数:
    start_time: astropy Time对象，起始时间
    time_steps: int, 总时间步数
    step_hours: float, 每步的小时数
    
    返回:
    dict: 包含各个天体位置的字典，格式与trajectories相同
    """
    # 加载DE421星历表
    kernel = SPK.open('de440.bsp')
    
    # 创建时间序列
    times = start_time + np.arange(time_steps) * step_hours * u.hour
    
    # 转换为Julian日期
    jd = times.jd
    
    # 初始化结果字典
    positions = {
        'Sun': [],
        'Earth': [],
        'Moon': [],
        'Jupiter': []
    }
    
    # DE440中的ID对照:
    # Sun = 10
    # Earth-Moon barycenter = 3
    # Moon (relative to Earth) = 301
    # Jupiter = 5
    
    for t in jd:
        # 获取太阳相对于太阳系重心的位置 (转换为AU)
        sun_pos = kernel[0,10].compute(t) / AU  # km to AU
        
        # 获取地球-月亮质心相对于太阳系重心的位置
        earth_moon_pos = kernel[0,3].compute(t) / AU
        
        # 获取月球相对于地球的位置
        moon_rel_earth = kernel[3,301].compute(t) / AU
        
        # 计算地球和月球的绝对位置
        earth_mass = 5.97237e24  # kg
        moon_mass = 7.342e22     # kg
        
        earth_pos = earth_moon_pos - (moon_mass/earth_mass) * moon_rel_earth
        moon_pos = earth_pos + moon_rel_earth
        
        # 获取木星相对于太阳系重心的位置
        jupiter_pos = kernel[0,5].compute(t) / AU
        
        # 存储位置数据
        positions['Sun'].append(sun_pos)
        positions['Earth'].append(earth_pos)
        positions['Moon'].append(moon_pos)
        positions['Jupiter'].append(jupiter_pos)
    
    # 转换为numpy数组
    for body in positions:
        positions[body] = np.array(positions[body])
    
    return positions

def compare_and_plot(de440_positions, simulated_positions, start_time, step_hours=1):
    """
    比较模拟结果与DE440数据并绘图，展示位置误差随时间变化
    
    参数:
    de440_positions: dict, DE440数据
    simulated_positions: dict, 模拟数据
    start_time: astropy Time对象，起始时间
    step_hours: float, 每步的小时数
    """
    bodies = ['Earth', 'Moon']
    time_steps = len(simulated_positions['Sun'])
    # 将时间转换为天数
    times = np.arange(time_steps) * step_hours / 24  
    plt.figure(figsize=(12, 8))
    for body in bodies:
        # 计算每个时间点上的位置差的模
        diff = np.linalg.norm(
            - (de440_positions[body]-de440_positions['Sun']) - (simulated_positions[body]-simulated_positions['Sun']),
            axis=1
        )
        
        # 使用半对数坐标绘制
        plt.semilogy(times, diff, label=body)
    
    plt.xlabel('时间 (天)')
    plt.ylabel('位置误差 (AU)')
    plt.title('轨道位置误差随时间变化')
    plt.grid(True)
    plt.legend()
    plt.savefig('position_errors.png')
    plt.close()

# 初始化天体
sun_body = get_initial("Sun")
earth_body = get_initial("Earth")
moon_body = get_initial("Moon")
jupiter_body = get_initial("Jupiter")
venus_body = get_initial("Venus")
saturn_body = get_initial("Saturn")
planet_list = [sun_body, earth_body, moon_body, jupiter_body, venus_body]
aux_planet_list = []
# 创建模拟器（时间步长为粗步长）
simulator = ThreeBodySimulator(
    bodies=planet_list,
    aux_list=aux_planet_list,
    dt=coarse_step
)
# 运行50年模拟
print("Start coarse simulation...")
start_time = time.time()
trajectories, t_range = simulator.simulate_rk4(years=total_lenth)
print("Coarse simulation time:", time.time()-start_time)
print("Start detecting sun eclipses...")
start_time = time.time()
filtered_times, eclipse_types = check_sun_eclipse(trajectories['Sun'], 
                                                trajectories['Moon'], 
                                                trajectories['Earth'],
                                                t_range)
sun_eclipse_start, sun_eclipse_type, sun_eclipse_end = detect_accurate_times(check_sun_eclipse, trajectories, filtered_times, eclipse_types, fine_steps)
print("Sun eclipse calculation time:", time.time()-start_time)
print("Start detecting moon eclipses...")
start_time = time.time()
filtered_times, eclipse_types = check_moon_eclipse(trajectories['Sun'], 
                                                trajectories['Moon'], 
                                                trajectories['Earth'],
                                                t_range)
moon_eclipse_start, moon_eclipse_type, moon_eclipse_end = detect_accurate_times(check_moon_eclipse, trajectories, filtered_times, eclipse_types, fine_steps)

# 保存轨道数据到文件
with open('trajectories.json', 'w') as f:
        # 将轨道数据转换为可序列化的格式
    serializable_trajectories = {}
    for body, positions in trajectories.items():
        # 将numpy数组转换为列表
        serializable_trajectories[body] = positions.tolist()
    json.dump(serializable_trajectories, f)

# 假设您已经有了模拟得到的trajectories数据
# 使用相同的起始时间和时间步数获取DE421数据
START = Time(2025, format='jyear') + 6 * u.hour
time_steps = len(trajectories['Sun'])

# 读取DE440数据
de440_positions = load_de440_data(START, time_steps, step_hours=coarse_step)

# 比较并绘图
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
compare_and_plot(de440_positions, trajectories, START, step_hours=coarse_step)