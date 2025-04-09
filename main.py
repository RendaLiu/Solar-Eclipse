import numpy as np
import matplotlib.pyplot as plt
import time
from astropy.time import Time
from astropy import units as u
from simulate import ThreeBodySimulator
from coords import get_initial
from check_eclipse import check_sun_eclipse, check_moon_eclipse, detect_accurate_times
import sys
 
sys.stdout = open('record.log', mode = 'w',encoding='utf-8')

coarse_step = 1
fine_steps = 100
total_lenth = 50

def double_accuracy_simulation():
    # 初始化天体
    sun_body = get_initial("Sun")
    earth_body = get_initial("Earth")
    moon_body = get_initial("Moon")
    jupiter_body = get_initial("Jupiter")
    venus_body = get_initial("Venus")
    planet_list = [sun_body, earth_body, moon_body, jupiter_body]
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
    print("Moon eclipse calculation time:", time.time()-start_time)
    return sun_eclipse_start, sun_eclipse_type, sun_eclipse_end, moon_eclipse_start, moon_eclipse_type, moon_eclipse_end
        

def plot_trajectories(trajectories):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    for name, pos_list in trajectories.items():
        positions = np.array(pos_list)
        ax.plot(positions[:,0], positions[:,1], positions[:,2],
                label=name, alpha=0.7)

    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.set_title('8 Year Orbital Trajectories')
    ax.legend()
    plt.show()

# 运行绘图
# plot_trajectories(trajectories)

START = Time(2025, format='jyear') + 6 * u.hour
print(f"Simulate solar eclipses during year 2025 and {2025+total_lenth}")
print("Initial time:", START.iso)
sun_eclipse_start, sun_eclipse_type, sun_eclipse_end, moon_eclipse_start, moon_eclipse_type, moon_eclipse_end = double_accuracy_simulation()
print("Simulation ended. Print results:")
print("=" * 60)
print("Times of sun eclipses:")
for start_time, type, end_time in zip(sun_eclipse_start, sun_eclipse_type, sun_eclipse_end):
    print("-" * 60)
    print("Start time:", (START + start_time * coarse_step * u.hour).iso)
    print("Type:", type)
    print("Max time:", (START + (start_time + end_time) / 2 * coarse_step * u.hour).iso)
    print("End time", (START + end_time * coarse_step * u.hour).iso)
print("=" * 60)
print("Times of moon eclipses:")
for start_time, type, end_time in zip(moon_eclipse_start, moon_eclipse_type, moon_eclipse_end):
    print("-" * 60)
    print("Start time:", (START + start_time * coarse_step * u.hour).iso)
    print("Type:", type)
    print("Max time:", (START + (start_time + end_time) / 2 * coarse_step * u.hour).iso)
    print("End time", (START + end_time * coarse_step * u.hour).iso)
