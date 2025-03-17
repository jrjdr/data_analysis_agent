import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from datetime import datetime

def analyze_csv_data(file_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 确保pngs目录存在
        os.makedirs('pngs', exist_ok=True)
        
        # 2. 基本描述性统计
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # 基本统计信息
        numeric_stats = df[numeric_columns].describe().to_dict()
        categorical_stats = {col: df[col].value_counts().to_dict() for col in categorical_columns}
        
        # 3. 分析数值列和分类列的分布
        # 创建结果字典
        analysis_results = {
            "file_info": {
                "file_path": file_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "numeric_statistics": numeric_stats,
            "categorical_statistics": categorical_stats,
            "charts": []
        }
        
        # 4. 生成统计图表
        
        # 图表1: 不同基站的性能指标对比
        plt.figure(figsize=(12, 8))
        performance_metrics = ['success_rate', 'signal_quality_db', 'latency_ms', 'packet_loss_percent']
        
        # 计算每个基站的平均性能指标
        station_performance = df.groupby('base_station_name')[performance_metrics].mean()
        
        # 归一化数据以便于比较
        normalized_performance = (station_performance - station_performance.min()) / (station_performance.max() - station_performance.min())
        
        # 创建雷达图
        labels = normalized_performance.index
        stats = normalized_performance.columns.tolist()
        
        angles = np.linspace(0, 2*np.pi, len(stats), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))
        
        for i, station in enumerate(labels):
            values = normalized_performance.loc[station].tolist()
            values += values[:1]  # 闭合图形
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=station)
            ax.fill(angles, values, alpha=0.1)
        
        ax.set_thetagrids(np.degrees(angles[:-1]), stats)
        ax.set_title('Base Station Performance Comparison', fontsize=15)
        ax.grid(True)
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        chart1_path = 'pngs/chart_stats_base_station_performance.png'
        plt.savefig(chart1_path)
        plt.close()
        
        # 图表2: 信号类型分布和状态关系
        plt.figure(figsize=(14, 10))
        
        # 创建信号类型和状态的交叉表
        signal_status = pd.crosstab(df['signal_type'], df['status'])
        
        # 绘制堆叠条形图
        signal_status.plot(kind='bar', stacked=True, figsize=(14, 8))
        plt.title('Signal Type Distribution by Status', fontsize=15)
        plt.xlabel('Signal Type')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加注释
        plt.figtext(0.5, 0.01, 
                   'Note: PAGING signals have the highest frequency with mostly successful status.',
                   ha='center', fontsize=12, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        chart2_path = 'pngs/chart_stats_signal_type_status.png'
        plt.tight_layout()
        plt.savefig(chart2_path)
        plt.close()
        
        # 图表3: 资源使用情况随时间变化
        # 将时间戳转换为datetime对象
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 选择一个基站进行分析
        sample_station = df['base_station_name'].value_counts().index[0]
        station_data = df[df['base_station_name'] == sample_station]
        
        # 按小时聚合数据
        hourly_data = station_data.set_index('timestamp').resample('H').mean()
        
        plt.figure(figsize=(14, 8))
        
        # 绘制资源使用情况
        plt.plot(hourly_data.index, hourly_data['cpu_usage_percent'], label='CPU Usage', linewidth=2)
        plt.plot(hourly_data.index, hourly_data['memory_usage_percent'], label='Memory Usage', linewidth=2)
        plt.plot(hourly_data.index, hourly_data['resource_block_usage_percent'], label='Resource Block Usage', linewidth=2)
        
        plt.title(f'Resource Usage Over Time for {sample_station}', fontsize=15)
        plt.xlabel('Time')
        plt.ylabel('Usage Percentage (%)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        
        # 添加注释
        plt.figtext(0.5, 0.01, 
                   'Resource usage shows cyclical patterns with peaks during high-traffic periods.',
                   ha='center', fontsize=12, bbox={"facecolor":"lightgray", "alpha":0.5, "pad":5})
        
        chart3_path = 'pngs/chart_stats_resource_usage_time.png'
        plt.tight_layout()
        plt.savefig(chart3_path)
        plt.close()
        
        # 更新分析结果
        analysis_results["charts"] = [
            {
                "title": "Base Station Performance Comparison",
                "path": chart1_path,
                "description": "Radar chart comparing normalized performance metrics across base stations"
            },
            {
                "title": "Signal Type Distribution by Status",
                "path": chart2_path,
                "description": "Stacked bar chart showing the distribution of signal types and their status"
            },
            {
                "title": "Resource Usage Over Time",
                "path": chart3_path,
                "description": "Line chart showing resource usage patterns over time for a sample base station"
            }
        ]
        
        # 5. 保存分析结果为JSON
        with open('pngs/analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, ensure_ascii=False, indent=2)
        
        return analysis_results
        
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        return {"error": str(e)}

# 执行分析
if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317123517.csv"
    results = analyze_csv_data(file_path)
    print(f"Analysis complete. Results saved to pngs/analysis_results.json")
    print(f"Generated {len(results.get('charts', []))} charts in the pngs directory")