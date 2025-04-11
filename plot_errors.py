import matplotlib.pyplot as plt
import numpy as np
from evaluate import parse_log_file, load_nasa_data, compare_events
import matplotlib as mpl

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def plot_error_distribution(log_path, nasa_path):
    # 获取评估数据
    simulated_data = parse_log_file(log_path)
    nasa_data = load_nasa_data(nasa_path)

    # 比较日食和月食数据
    solar_results = compare_events(simulated_data['solar_eclipses'], nasa_data['solar_eclipses'], 'solar')
    lunar_results = compare_events(simulated_data['lunar_eclipses'], nasa_data['lunar_eclipses'], 'lunar')

    # 提取时间差数据
    solar_errors = [match['time_diff'] for match in solar_results['matches']]
    lunar_errors = [match['time_diff'] for match in lunar_results['matches']]

    # 创建图形
    plt.figure(figsize=(12, 6))

    # 设置子图
    plt.subplot(1, 2, 1)
    plt.hist(solar_errors, bins=20, color='orange', alpha=0.7)
    plt.title('日食预测误差分布')
    plt.xlabel('时间误差（小时）')
    plt.ylabel('事件数量')
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.hist(lunar_errors, bins=20, color='blue', alpha=0.7)
    plt.title('月食预测误差分布')
    plt.xlabel('时间误差（小时）')
    plt.ylabel('事件数量')
    plt.grid(True, alpha=0.3)

    # 调整布局
    plt.tight_layout()

    # 保存图片
    plt.savefig('error_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    plot_error_distribution('record.log', 'nasa_eclipse_data.json')
