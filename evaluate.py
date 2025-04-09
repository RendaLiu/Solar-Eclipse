import json
from datetime import datetime
import re

def parse_log_file(log_path):
    """解析日志文件，提取日食和月食信息"""
    with open(log_path, 'r') as f:
        content = f.read()
    
    # 初始化存储日食和月食事件的列表
    sun_eclipses = []
    moon_eclipses = []
    
    # 使用正则表达式从日志中提取日食部分
    sun_section = re.search(r'Times of sun eclipses:(.*?)Times of moon eclipses:', content, re.DOTALL)
    if sun_section:
        # 匹配每个日食事件的详细信息
        sun_events = re.findall(r'Start time: (.*?)\.000\nType: (.*?)\nMax time: (.*?)\.000\nEnd time (.*?)\.000\n-{60}', sun_section.group(1))
        
        # 将所有事件转换为包含完整时间信息的列表
        temp_events = []
        for event in sun_events:
            max_datetime = datetime.strptime(event[2], '%Y-%m-%d %H:%M:%S')
            eclipse_type = event[1].strip()
            temp_events.append({
                'datetime': max_datetime,
                'date': max_datetime.strftime('%Y-%m-%d'),
                'type': eclipse_type,
                'max_time': max_datetime.strftime('%H:%M:%S')
            })
        
        # 按时间排序
        temp_events.sort(key=lambda x: x['datetime'])
        
        # 处理每个事件
        i = 0
        while i < len(temp_events):
            current_event = temp_events[i]
            should_keep = True
            
            # 向前和向后检查2小时内的事件
            for j in range(len(temp_events)):
                if i != j:
                    time_diff = abs((temp_events[j]['datetime'] - current_event['datetime']).total_seconds() / 3600)
                    
                    # 如果在2小时内有全食或环食，且当前是偏食，则跳过当前事件
                    if (time_diff <= 2 and 
                        current_event['type'] == 'partial' and 
                        temp_events[j]['type'] in ['total', 'annular']):
                        should_keep = False
                        break
            
            if should_keep:
                sun_eclipses.append({
                    'date': current_event['date'],
                    'type': current_event['type'],
                    'max_time': current_event['max_time']
                })
            i += 1
    
    # 月食部分使用相同的逻辑
    moon_section = re.search(r'Times of moon eclipses:(.*?)$', content, re.DOTALL)
    if moon_section:
        moon_events = re.findall(r'Start time: (.*?)\.000\nType: (.*?)\nMax time: (.*?)\.000\nEnd time (.*?)\.000\n-{60}', moon_section.group(1))
        
        temp_events = []
        for event in moon_events:
            max_datetime = datetime.strptime(event[2], '%Y-%m-%d %H:%M:%S')
            eclipse_type = event[1].strip()
            temp_events.append({
                'datetime': max_datetime,
                'date': max_datetime.strftime('%Y-%m-%d'),
                'type': eclipse_type,
                'max_time': max_datetime.strftime('%H:%M:%S')
            })
        
        temp_events.sort(key=lambda x: x['datetime'])
        
        i = 0
        while i < len(temp_events):
            current_event = temp_events[i]
            should_keep = True
            
            for j in range(len(temp_events)):
                if i != j:
                    time_diff = abs((temp_events[j]['datetime'] - current_event['datetime']).total_seconds() / 3600)
                    
                    if (time_diff <= 2 and 
                        current_event['type'] == 'partial' and 
                        temp_events[j]['type'] in ['total', 'annular']):
                        should_keep = False
                        break
            
            if should_keep:
                moon_eclipses.append({
                    'date': current_event['date'],
                    'type': current_event['type'],
                    'max_time': current_event['max_time']
                })
            i += 1
    
    return {
        'solar_eclipses': sun_eclipses,
        'lunar_eclipses': moon_eclipses
    }

def load_nasa_data(nasa_path):
    """加载NASA数据"""
    with open(nasa_path, 'r') as f:
        data = json.load(f)
        # 将按年份组织的数据转换为扁平列表
        solar_eclipses = []
        lunar_eclipses = []
        
        # 处理日食数据
        for year, events in data['solar_eclipses'].items():
            solar_eclipses.extend(events)
            
        # 处理月食数据
        for year, events in data['lunar_eclipses'].items():
            lunar_eclipses.extend(events)
            
        return {
            'solar_eclipses': solar_eclipses,
            'lunar_eclipses': lunar_eclipses
        }

def compare_events(simulated, nasa, event_type):
    """比较模拟结果和NASA数据"""
    results = {
        'total_simulated': len(simulated),
        'total_nasa': len(nasa),
        'matches': [],
        'missed': [],
        'extra': []
    }
    
    # 将事件转换为完整的datetime对象进行比较
    nasa_events = []
    for event in nasa:
        nasa_datetime = datetime.strptime(f"{event['date']} {event['max_time']}", '%Y-%m-%d %H:%M:%S')
        nasa_events.append({
            'datetime': nasa_datetime,
            'date': event['date'],
            'type': event['type'],
            'max_time': event['max_time']
        })
    
    simulated_events = []
    for event in simulated:
        sim_datetime = datetime.strptime(f"{event['date']} {event['max_time']}", '%Y-%m-%d %H:%M:%S')
        simulated_events.append({
            'datetime': sim_datetime,
            'date': event['date'],
            'type': event['type'],
            'max_time': event['max_time']
        })
    
    # 对每个NASA事件，寻找最近的模拟事件
    matched_sim_events = set()  # 用于记录已匹配的模拟事件
    
    for nasa_event in nasa_events:
        best_match = None
        min_time_diff = float('inf')
        
        for sim_event in simulated_events:
            if sim_event['type'] != nasa_event['type']:
                continue
                
            # 计算时间差（小时）
            time_diff = abs((nasa_event['datetime'] - sim_event['datetime']).total_seconds() / 3600)
            
            # 检查跨日期情况
            if time_diff > 12:  # 如果时间差大于12小时，可能是跨日期事件
                # 使用timedelta来安全地计算前一天和后一天
                from datetime import timedelta
                prev_day = sim_event['datetime'] - timedelta(days=1)
                next_day = sim_event['datetime'] + timedelta(days=1)
                
                prev_day_diff = abs((nasa_event['datetime'] - prev_day).total_seconds() / 3600)
                next_day_diff = abs((nasa_event['datetime'] - next_day).total_seconds() / 3600)
                time_diff = min(prev_day_diff, next_day_diff)
            
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                best_match = sim_event
        
        # 如果找到匹配且时间差在1小时内
        if best_match and min_time_diff <= 1:
            matched_sim_events.add((best_match['date'], best_match['max_time']))
            results['matches'].append({
                'date': nasa_event['date'],
                'type': nasa_event['type'],
                'simulated_time': best_match['max_time'],
                'nasa_time': nasa_event['max_time'],
                'time_diff': min_time_diff
            })
        else:
            results['missed'].append({
                'date': nasa_event['date'],
                'type': nasa_event['type'],
                'max_time': nasa_event['max_time']
            })
    
    # 检查未匹配的模拟事件（多余事件）
    for sim_event in simulated_events:
        if (sim_event['date'], sim_event['max_time']) not in matched_sim_events:
            results['extra'].append({
                'date': sim_event['date'],
                'type': sim_event['type'],
                'max_time': sim_event['max_time']
            })
    
    return results

def evaluate(log_path, nasa_path):
    """评估函数主入口"""
    # 解析日志文件
    simulated_data = parse_log_file(log_path)
    
    # 加载NASA数据
    nasa_data = load_nasa_data(nasa_path)
    
    # 比较日食数据
    solar_results = compare_events(
        simulated_data['solar_eclipses'],
        nasa_data['solar_eclipses'],
        'solar'
    )
    
    # 比较月食数据
    lunar_results = compare_events(
        simulated_data['lunar_eclipses'],
        nasa_data['lunar_eclipses'],
        'lunar'
    )
    
    # 计算总体准确率
    total_matches = len(solar_results['matches']) + len(lunar_results['matches'])
    total_events = solar_results['total_nasa'] + lunar_results['total_nasa']
    accuracy = total_matches / total_events if total_events > 0 else 0
    
    # 输出详细统计信息到文件
    with open('evaluation_results.txt', 'w', encoding='utf-8') as f:
        # 写入总体准确率
        f.write(f"总体准确率: {accuracy:.2%}\n\n")
        
        # 写入日食结果统计
        f.write("日食结果:\n")
        f.write(f"模拟数量: {solar_results['total_simulated']}\n")
        f.write(f"NASA数量: {solar_results['total_nasa']}\n")
        f.write(f"匹配数量: {len(solar_results['matches'])}\n")
        f.write(f"遗漏数量: {len(solar_results['missed'])}\n")
        f.write(f"多余数量: {len(solar_results['extra'])}\n\n")
        
        # 写入月食结果统计
        f.write("月食结果:\n")
        f.write(f"模拟数量: {lunar_results['total_simulated']}\n")
        f.write(f"NASA数量: {lunar_results['total_nasa']}\n")
        f.write(f"匹配数量: {len(lunar_results['matches'])}\n")
        f.write(f"遗漏数量: {len(lunar_results['missed'])}\n")
        f.write(f"多余数量: {len(lunar_results['extra'])}\n\n")
        
        # 写入日食匹配详情
        f.write("日食匹配详情:\n")
        for match in solar_results['matches']:
            f.write(f"日期: {match['date']}, 类型: {match['type']}\n")
            f.write(f"模拟时间: {match['simulated_time']}, NASA时间: {match['nasa_time']}\n")
            f.write(f"时间差: {match['time_diff']:.2f}小时\n\n")
        
        # 写入月食匹配详情
        f.write("月食匹配详情:\n")
        for match in lunar_results['matches']:
            f.write(f"日期: {match['date']}, 类型: {match['type']}\n")
            f.write(f"模拟时间: {match['simulated_time']}, NASA时间: {match['nasa_time']}\n")
            f.write(f"时间差: {match['time_diff']:.2f}小时\n\n")
            
        # 写入日食遗漏事件详情
        f.write("日食遗漏事件详情:\n")
        for missed in solar_results['missed']:
            f.write(f"日期: {missed['date']}, 类型: {missed['type']}\n")
            if 'nasa_time' in missed:  # 对于时间差过大的事件
                f.write(f"NASA时间: {missed['nasa_time']}, 模拟时间: {missed['simulated_time']}\n")
                f.write(f"时间差: {missed['time_diff']:.2f}小时\n")
            else:  # 对于完全未预测到的事件
                f.write(f"NASA时间: {missed['max_time']}\n")
            f.write("---\n")
        f.write("\n")
        
        # 写入日食多余事件详情
        f.write("日食多余事件详情:\n")
        for extra in solar_results['extra']:
            f.write(f"日期: {extra['date']}, 类型: {extra['type']}\n")
            f.write(f"模拟的max时间: {extra['max_time']}\n")
            f.write("---\n")
        f.write("\n")

        # 写入月食遗漏事件详情
        f.write("月食遗漏事件详情:\n")
        for missed in lunar_results['missed']:
            f.write(f"日期: {missed['date']}, 类型: {missed['type']}\n")
            if 'nasa_time' in missed:  # 对于时间差过大的事件
                f.write(f"NASA时间: {missed['nasa_time']}, 模拟时间: {missed['simulated_time']}\n")
                f.write(f"时间差: {missed['time_diff']:.2f}小时\n")
            else:  # 对于完全未预测到的事件
                f.write(f"NASA时间: {missed['max_time']}\n")
            f.write("---\n")
        f.write("\n")
        
        # 写入月食多余事件详情
        f.write("月食多余事件详情:\n")
        for extra in lunar_results['extra']:
            f.write(f"日期: {extra['date']}, 类型: {extra['type']}\n")
            f.write(f"模拟的max时间: {extra['max_time']}\n")
            f.write("---\n")
        f.write("\n")
if __name__ == '__main__':
    evaluate('record.log', 'nasa_eclipse_data.json')