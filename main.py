import numpy as np
import matplotlib.pyplot as plt
import time
from astropy.time import Time
from simulate import ThreeBodySimulator
from coords import get_initial
from check_eclipse import check_sun_eclipse, check_moon_eclipse
from constants import YEAR

# 初始化天体
sun_body = get_initial("Sun")
earth_body = get_initial("Earth")
moon_body = get_initial("Moon")

# 创建模拟器（时间步长设为6小时）
simulator = ThreeBodySimulator(
    bodies=[sun_body, earth_body, moon_body],
    dt=1
)

# 运行8年模拟
start_time = time.time()
trajectories, t_range = simulator.simulate_rk4(years=8)
print("time: ", time.time()-start_time)

def plot_trajectories():
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
plot_trajectories()

filtered_times, filtered_types = check_sun_eclipse(trajectories['Sun'], 
                                                   trajectories['Moon'], 
                                                   trajectories['Earth'],
                                                   t_range)
filtered_times = filtered_times / YEAR + 2025.0
for time, type in zip(filtered_times, filtered_types):
    print(Time(time, format='jyear').iso, ": ", type)
