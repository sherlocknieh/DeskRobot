
"""日志分析器
找出相邻两行时间间隔超过一定秒数的行，并根据间隔秒数插入对应数量的空行。
"""


from datetime import datetime


def parse_time(line):
    try:
        timestamp_str = line.split(' ')[0] + ' ' + line.split(' ')[1].split(',')[0]
        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return None

def insert_blank_lines_by_gap(lines):
    result = []
    prev_time = None

    for line in lines:
        curr_time = parse_time(line)
        if curr_time and prev_time:
            gap = (curr_time - prev_time).total_seconds()
            if gap > 1:
                result.extend(['\n'] * int(gap))  # 插入 gap 秒对应的空行
        result.append(line)
        prev_time = curr_time if curr_time else prev_time

    return result


log_file = 'localfiles/logs/desk_robot.log'
output_file = 'localfiles/logs/desk_robot_processed.log'


# 读取日志文件
with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 处理间隔
new_lines = insert_blank_lines_by_gap(lines)

# 保存新日志
with open(log_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
