import pandas as pd
import numpy as np
import json
import sys
from typing import Dict, List

def analyze_pie_chart_data(df: pd.DataFrame) -> Dict[str, List[Dict[str, float]]]:
    """
    分析适合饼图展示的数据比例
    """
    results = {}

    # 分析信号类型分布
    signal_type_counts = df['signal_type'].value_counts(normalize=True)
    results['signal_type_distribution'] = [
        {'name': name, 'value': value} 
        for name, value in signal_type_counts.items()
    ]

    # 分析基站状态分布
    status_counts = df['status'].value_counts(normalize=True)
    results['status_distribution'] = [
        {'name': name, 'value': value} 
        for name, value in status_counts.items()
    ]

    # 分析基站使用情况
    base_station_usage = df.groupby('base_station_name')['active_users'].mean()
    total_users = base_station_usage.sum()
    results['base_station_usage'] = [
        {'name': name, 'value': users / total_users} 
        for name, users in base_station_usage.items()
    ]

    # 分析资源块使用率分布
    resource_block_bins = pd.cut(df['resource_block_usage_percent'], bins=5)
    resource_block_distribution = resource_block_bins.value_counts(normalize=True)
    results['resource_block_usage_distribution'] = [
        {'name': str(interval), 'value': value} 
        for interval, value in resource_block_distribution.items()
    ]

    # 分析CPU使用率分布
    cpu_usage_bins = pd.cut(df['cpu_usage_percent'], bins=5)
    cpu_usage_distribution = cpu_usage_bins.value_counts(normalize=True)
    results['cpu_usage_distribution'] = [
        {'name': str(interval), 'value': value} 
        for interval, value in cpu_usage_distribution.items()
    ]

    return results

def main(file_path: str):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 分析数据
        analysis_results = analyze_pie_chart_data(df)

        # 保存结果到JSON文件
        with open('pie_chart_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)

        print("分析完成，结果已保存到 pie_chart_analysis_results.json")

    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except pd.errors.EmptyDataError:
        print(f"错误：文件 {file_path} 是空的")
    except pd.errors.ParserError:
        print(f"错误：无法解析文件 {file_path}，请确保它是有效的CSV格式")
    except KeyError as e:
        print(f"错误：找不到所需的列 {e}")
    except Exception as e:
        print(f"发生未知错误：{e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
    else:
        main(sys.argv[1])