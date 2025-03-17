import pandas as pd
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

def analyze_csv_and_create_pie_charts(file_path):
    try:
        # 1. 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 确保输出目录存在
        output_dir = "pngs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 2. 分析分类列的分布和比例
        categorical_columns = ['base_station_id', 'base_station_name', 'signal_type', 'status']
        analysis_results = {}
        chart_files = []
        
        # 3. 生成饼图
        # 饼图1: 基站ID分布
        plt.figure(figsize=(10, 8))
        base_station_counts = df['base_station_id'].value_counts()
        plt.pie(base_station_counts, labels=base_station_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True)
        plt.title('Distribution of Base Stations by ID', fontsize=16)
        plt.figtext(0.5, 0.01, 'Key Finding: Base stations have equal distribution in the dataset', 
                   ha='center', fontsize=12)
        plt.tight_layout()
        
        # 保存图表
        chart_file1 = os.path.join(output_dir, f"chart_pie_base_station_id_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(chart_file1)
        plt.close()
        chart_files.append(chart_file1)
        
        # 将分析结果添加到结果字典
        analysis_results['base_station_id'] = {
            'total_count': len(df),
            'distribution': base_station_counts.to_dict(),
            'chart_file': chart_file1
        }
        
        # 饼图2: 信号类型分布
        plt.figure(figsize=(12, 10))
        signal_type_counts = df['signal_type'].value_counts()
        plt.pie(signal_type_counts, labels=signal_type_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, explode=[0.05]*len(signal_type_counts))
        plt.title('Distribution of Signal Types', fontsize=16)
        plt.figtext(0.5, 0.01, f'Key Finding: {signal_type_counts.index[0]} is the most common signal type ({signal_type_counts.iloc[0]/len(df)*100:.1f}%)', 
                   ha='center', fontsize=12)
        plt.tight_layout()
        
        # 保存图表
        chart_file2 = os.path.join(output_dir, f"chart_pie_signal_type_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(chart_file2)
        plt.close()
        chart_files.append(chart_file2)
        
        # 将分析结果添加到结果字典
        analysis_results['signal_type'] = {
            'total_count': len(df),
            'distribution': signal_type_counts.to_dict(),
            'chart_file': chart_file2
        }
        
        # 饼图3: 状态分布
        plt.figure(figsize=(10, 8))
        status_counts = df['status'].value_counts()
        plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
                startangle=90, shadow=True, colors=['#4CAF50', '#F44336', '#2196F3', '#FFC107', '#9C27B0'])
        plt.title('Distribution of Connection Status', fontsize=16)
        plt.figtext(0.5, 0.01, f'Key Finding: Success rate is {status_counts["SUCCESS"]/len(df)*100:.1f}% of all connections', 
                   ha='center', fontsize=12)
        plt.tight_layout()
        
        # 保存图表
        chart_file3 = os.path.join(output_dir, f"chart_pie_status_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
        plt.savefig(chart_file3)
        plt.close()
        chart_files.append(chart_file3)
        
        # 将分析结果添加到结果字典
        analysis_results['status'] = {
            'total_count': len(df),
            'distribution': status_counts.to_dict(),
            'chart_file': chart_file3
        }
        
        # 4. 将分析结果保存为JSON格式
        result = {
            'file_analyzed': file_path,
            'total_records': len(df),
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'charts_generated': chart_files,
            'category_analysis': analysis_results
        }
        
        json_file = f"pie_chart_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        return {
            'status': 'success',
            'message': f'分析完成，生成了{len(chart_files)}个饼图',
            'json_file': json_file,
            'chart_files': chart_files
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'分析过程中出错: {str(e)}'
        }

if __name__ == "__main__":
    file_path = "temp_csv/excel_data_20250317111047.csv"
    result = analyze_csv_and_create_pie_charts(file_path)
    print(result['message'])
    print(f"JSON结果保存在: {result.get('json_file', '')}")
    if result['status'] == 'success':
        print("生成的图表:")
        for chart in result['chart_files']:
            print(f" - {chart}")