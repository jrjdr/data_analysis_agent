import pandas as pd
import numpy as np
import json
import sys
from typing import Dict, List

def analyze_pie_chart_data(df: pd.DataFrame) -> Dict[str, List[Dict[str, float]]]:
    """
    分析数据并生成适合饼图展示的比例数据
    """
    results = {}

    # 分析基站分布
    base_station_counts = df['base_station_name'].value_counts(normalize=True)
    results['base_station_distribution'] = [
        {'name': name, 'value': value} 
        for name, value in base_station_counts.items()
    ]

    # 分析信号类型分布
    signal_type_counts = df['signal_type'].value_counts(normalize=True)
    results['signal_type_distribution'] = [
        {'name': name, 'value': value} 
        for name, value in signal_type_counts.items()
    ]

    # 分析状态分布
    status_counts = df['status'].value_counts(normalize=True)
    results['status_distribution'] = [
        {'name': name, 'value': value} 
        for name, value in status_counts.items()
    ]

    # 分析资源块使用率分布
    resource_block_bins = pd.cut(df['resource_block_usage_percent'], bins=5)
    resource_block_counts = resource_block_bins.value_counts(normalize=True)
    results['resource_block_usage_distribution'] = [
        {'name': str(name), 'value': value} 
        for name, value in resource_block_counts.items()
    ]

    # 分析CPU使用率分布
    cpu_usage_bins = pd.cut(df['cpu_usage_percent'], bins=5)
    cpu_usage_counts = cpu_usage_bins.value_counts(normalize=True)
    results['cpu_usage_distribution'] = [
        {'name': str(name), 'value': value} 
        for name, value in cpu_usage_counts.items()
    ]

    # 分析内存使用率分布
    memory_usage_bins = pd.cut(df['memory_usage_percent'], bins=5)
    memory_usage_counts = memory_usage_bins.value_counts(normalize=True)
    results['memory_usage_distribution'] = [
        {'name': str(name), 'value': value} 
        for name, value in memory_usage_counts.items()
    ]

    return results

def main(csv_file_path: str):
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file_path)

        # 分析数据
        analysis_results = analyze_pie_chart_data(df)

        # 保存结果到JSON文件
        with open('pie_chart_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)

        print("分析完成，结果已保存到 pie_chart_analysis_results.json")

    except FileNotFoundError:
        print(f"错误：找不到文件 {csv_file_path}")
    except pd.errors.EmptyDataError:
        print(f"错误：文件 {csv_file_path} 是空的")
    except pd.errors.ParserError:
        print(f"错误：无法解析文件 {csv_file_path}，请确保它是有效的CSV格式")
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
    else:
        main(sys.argv[1])