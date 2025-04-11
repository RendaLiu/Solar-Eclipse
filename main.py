import numpy as np
import matplotlib.pyplot as plt
import time
from astropy.time import Time
from astropy import units as u
from simulate import ThreeBodySimulator
from coords import get_initial
from check_eclipse import check_sun_eclipse, check_moon_eclipse, detect_accurate_times
import sys

sys.stdout = open('record.log', mode='w', encoding='utf-8')

coarse_step = 0.5
fine_steps = 100
total_lenth = 50


def double_accuracy_simulation():
    # 初始化天体
    sun_body = get_initial("Sun")
    earth_body = get_initial("Earth")
    moon_body = get_initial("Moon")
    jupiter_body = get_initial("Jupiter")
    venus_body = get_initial("Venus")
    saturn_body = get_initial("Saturn")
    planet_list = [sun_body, earth_body, moon_body]
    aux_planet_list = [jupiter_body, venus_body, saturn_body]
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
    # 运行绘图
    # plot_trajectories(trajectories)
    print("Coarse simulation time:", time.time()-start_time)
    print("Start detecting solar eclipses...")
    start_time = time.time()
    filtered_times, eclipse_types = check_sun_eclipse(trajectories['Sun'],
                                                      trajectories['Moon'],
                                                      trajectories['Earth'],
                                                      t_range)
    solar_eclipse_start, solar_eclipse_type, solar_eclipse_end = detect_accurate_times(
        check_sun_eclipse, trajectories, filtered_times, eclipse_types, fine_steps)
    print("Solar eclipse calculation time:", time.time()-start_time)
    print("Start detecting lunar eclipses...")
    start_time = time.time()
    filtered_times, eclipse_types = check_moon_eclipse(trajectories['Sun'],
                                                       trajectories['Moon'],
                                                       trajectories['Earth'],
                                                       t_range)
    lunar_eclipse_start, lunar_eclipse_type, lunar_eclipse_end = detect_accurate_times(
        check_moon_eclipse, trajectories, filtered_times, eclipse_types, fine_steps)
    print("Lunar eclipse calculation time:", time.time()-start_time)
    return solar_eclipse_start, solar_eclipse_type, solar_eclipse_end, lunar_eclipse_start, lunar_eclipse_type, lunar_eclipse_end


def plot_trajectories(trajectories):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    for name, pos_list in trajectories.items():
        positions = np.array(pos_list)
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                label=name, alpha=0.7)

    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.set_title('8 Year Orbital Trajectories')
    ax.legend()
    plt.show()


START = Time(2025, format='jyear') + 6 * u.hour
print(f"Simulate solar and lunar eclipses during year 2025 and {2025+total_lenth}")
print("Initial time:", START.iso)
solar_eclipse_start, solar_eclipse_type, solar_eclipse_end, lunar_eclipse_start, lunar_eclipse_type, lunar_eclipse_end = double_accuracy_simulation()
print("Simulation ended. Print results:")
print("=" * 60)
print("Times of solar eclipses:")
for start_time, type, end_time in zip(solar_eclipse_start, solar_eclipse_type, solar_eclipse_end):
    print("-" * 60)
    print("Start time:", (START + start_time * coarse_step * u.hour).iso)
    print("Type:", type)
    print("Max time:", (START + (start_time + end_time) / 2 * coarse_step * u.hour).iso)
    print("End time", (START + end_time * coarse_step * u.hour).iso)
print("=" * 60)
print("Times of lunar eclipses:")
for start_time, type, end_time in zip(lunar_eclipse_start, lunar_eclipse_type, lunar_eclipse_end):
    print("-" * 60)
    print("Start time:", (START + start_time * coarse_step * u.hour).iso)
    print("Type:", type)
    print("Max time:", (START + (start_time + end_time) / 2 * coarse_step * u.hour).iso)
    print("End time", (START + end_time * coarse_step * u.hour).iso)
