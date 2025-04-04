import numpy as np
import matplotlib.pyplot as plt
import time
from astropy.time import Time
from simulate import ThreeBodySimulator
from coords import get_initial
from constants import YEAR

def run_eclipse_simulation(years=10, coarse_dt=3600):
    """运行日食月食模拟
    Args:
        years: 模拟年数
        coarse_dt: 粗略时间步长（秒）
    """
    # 初始化天体
    sun_body = get_initial("Sun")
    earth_body = get_initial("Earth")
    moon_body = get_initial("Moon")
    
    # 创建模拟器
    simulator = ThreeBodySimulator(
        bodies=[sun_body, earth_body, moon_body],
        dt=coarse_dt
    )
    
    # 运行模拟
    print(f"开始计算{years}年的日食和月食预测...")
    start_time = time.time()
    trajectories, eclipse_events = simulator.simulate_rk4(
        years=years, 
        coarse_dt=coarse_dt
    )
    computation_time = time.time() - start_time
    print(f"计算完成！计算耗时: {computation_time:.2f}秒\n")
    
    return trajectories, eclipse_events

def print_eclipse_events(eclipse_events, start_year=2024):
    """打印日食月食事件
    Args:
        eclipse_events: 食事件字典
        start_year: 起始年份
    """
    # 打印日食事件
    print("日食事件预报：")
    print("=" * 50)
    for event in eclipse_events['solar']:
        start_time = Time(event['start_time']/YEAR + start_year, format='jyear').iso
        max_time = Time(event['max_time']/YEAR + start_year, format='jyear').iso
        end_time = Time(event['end_time']/YEAR + start_year, format='jyear').iso
        
        print(f"日食类型: {event['type']}")
        print(f"初亏时刻: {start_time}")
        print(f"食甚时刻: {max_time}")
        print(f"复圆时刻: {end_time}")
        print(f"持续时间: {event['duration']/3600:.1f}小时")
        print("-" * 50)

    # 打印月食事件
    print("\n月食事件预报：")
    print("=" * 50)
    for event in eclipse_events['lunar']:
        start_time = Time(event['start_time']/YEAR + start_year, format='jyear').iso
        max_time = Time(event['max_time']/YEAR + start_year, format='jyear').iso
        end_time = Time(event['end_time']/YEAR + start_year, format='jyear').iso
        
        print(f"月食类型: {event['type']}")
        print(f"初亏时刻: {start_time}")
        print(f"食甚时刻: {max_time}")
        print(f"复圆时刻: {end_time}")
        print(f"持续时间: {event['duration']/3600:.1f}小时")
        print("-" * 50)

    # 打印统计信息
    solar_count = len(eclipse_events['solar'])
    lunar_count = len(eclipse_events['lunar'])
    print(f"\n统计信息：")
    print(f"预测期间（{start_year}-{start_year+10}）将发生：")
    print(f"日食：{solar_count}次")
    print(f"月食：{lunar_count}次")
    print(f"食现象总计：{solar_count + lunar_count}次")

def plot_trajectories(trajectories, years):
    """绘制轨道图
    Args:
        trajectories: 轨道字典
        years: 模拟年数
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    for name, pos_list in trajectories.items():
        positions = np.array(pos_list)
        ax.plot(positions[:,0], positions[:,1], positions[:,2],
                label=name, alpha=0.7)

    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.set_title(f'{years}年轨道演化图')
    ax.legend()
    plt.show()

def main():
    # 设置参数
    YEARS = 10          # 模拟10年
    START_YEAR = 2024   # 从2024年开始
    COARSE_DT = 21600   # 粗略时间步长6小时
    FINE_DT = 1         # 精细时间步长1秒
    
    print(f"开始计算{START_YEAR}年至{START_YEAR + YEARS}年的日月食预报...")
    
    # 初始化天体
    sun_body = get_initial("Sun")
    earth_body = get_initial("Earth")
    moon_body = get_initial("Moon")
    
    # 创建模拟器
    simulator = ThreeBodySimulator(
        bodies=[sun_body, earth_body, moon_body],
        dt=COARSE_DT
    )
    
    # 运行模拟并计时
    start_time = time.time()
    trajectories, eclipse_events = simulator.simulate_with_eclipse_detection(
        years=YEARS, 
        coarse_dt=COARSE_DT
    )
    computation_time = time.time() - start_time
    
    # 打印计算信息
    print(f"计算完成！耗时：{computation_time:.1f}秒")
    print(f"使用参数：粗略时间步长 = {COARSE_DT/3600:.1f}小时，精细时间步长 = {FINE_DT}秒\n")
    
    # 打印日食事件
    print(f"未来{YEARS}年的日食预报：")
    print("=" * 60)
    if not eclipse_events['solar']:
        print("未检测到日食事件")
    else:
        for i, event in enumerate(eclipse_events['solar'], 1):
            start_time = Time(event['start_time']/YEAR + START_YEAR, format='jyear').iso
            max_time = Time(event['max_time']/YEAR + START_YEAR, format='jyear').iso
            end_time = Time(event['end_time']/YEAR + START_YEAR, format='jyear').iso
            
            print(f"第{i}次日食：")
            print(f"类型：{event['type']}")
            print(f"初亏：{start_time}")
            print(f"食甚：{max_time}")
            print(f"复圆：{end_time}")
            print(f"持续时间：{event['duration']/60:.1f}分钟")
            print("-" * 60)
    
    # 打印月食事件
    print(f"\n未来{YEARS}年的月食预报：")
    print("=" * 60)
    if not eclipse_events['lunar']:
        print("未检测到月食事件")
    else:
        for i, event in enumerate(eclipse_events['lunar'], 1):
            start_time = Time(event['start_time']/YEAR + START_YEAR, format='jyear').iso
            max_time = Time(event['max_time']/YEAR + START_YEAR, format='jyear').iso
            end_time = Time(event['end_time']/YEAR + START_YEAR, format='jyear').iso
            
            print(f"第{i}次月食：")
            print(f"类型：{event['type']}")
            print(f"初亏：{start_time}")
            print(f"食甚：{max_time}")
            print(f"复圆：{end_time}")
            print(f"持续时间：{event['duration']/60:.1f}分钟")
            print("-" * 60)
    
    # 打印统计信息
    print("\n统计信息：")
    print("=" * 60)
    print(f"预测时段：{START_YEAR}年 至 {START_YEAR + YEARS}年")
    print(f"日食总数：{len(eclipse_events['solar'])}次")
    print(f"月食总数：{len(eclipse_events['lunar'])}次")
    print(f"食现象总数：{len(eclipse_events['solar']) + len(eclipse_events['lunar'])}次")
    
    # 按类型统计
    solar_types = {}
    lunar_types = {}
    for event in eclipse_events['solar']:
        solar_types[event['type']] = solar_types.get(event['type'], 0) + 1
    for event in eclipse_events['lunar']:
        lunar_types[event['type']] = lunar_types.get(event['type'], 0) + 1
    
    print("\n日食类型统计：")
    for type_name, count in solar_types.items():
        print(f"- {type_name}食：{count}次")
    
    print("\n月食类型统计：")
    for type_name, count in lunar_types.items():
        print(f"- {type_name}食：{count}次")

if __name__ == "__main__":
    main()
