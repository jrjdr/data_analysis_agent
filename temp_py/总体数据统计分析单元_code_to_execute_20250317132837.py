import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

def read_csv_file(file_path):
    """读取CSV文件并返回DataFrame"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"读取CSV文件出错: {e}")
        return None

def get_basic_stats(df):
    """获取基本统计信息"""
    result = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": {}
    }
    
    for column in df.columns:
        col_data = df[column]
        col_info = {
            "type": str(col_data.dtype),
            "missing_values": col_data.isna().sum()
        }
        
        if col_data.dtype == 'object':
            # 分类列
            col_info["unique_values"] = col_data.nunique()
            if col_data.nunique() < len(df) * 0.1:  # 如果唯一值较少
                most_common = col_data.value_counts().iloc[0]
                col_info["most_common"] = {
                    "value": col_data.value_counts().index[0],
                    "count": int(most_common)
                }
        else:
            # 数值列
            non_null_data = col_data.dropna()
            if len(non_null_data) > 0:
                col_info["unique_values"] = non_null_data.nunique()
                col_info["min"] = float(non_null_data.min())
                col_info["max"] = float(non_null_data.max())
                col_info["mean"] = float(non_null_data.mean())
                col_info["median"] = float(non_null_data.median())
                
                # 检测异常值
                q1 = non_null_data.quantile(0.25)
                q3 = non_null_data.quantile(0.75)
                iqr = q3 - q1
                outliers = ((non_null_data < (q1 - 1.5 * iqr)) | (non_null_data > (q3 + 1.5 * iqr))).sum()
                if outliers > 0:
                    col_info["outliers_count"] = int(outliers)
                    
        result["columns"][column] = col_info
    
    return result

def analyze_distributions(df):
    """分析数据分布"""
    result = {}
    
    # 分析时间分布
    if 'timestamp' in df.columns:
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            result["time_distribution"] = {
                "start_time": df['timestamp'].min().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": df['timestamp'].max().strftime("%Y-%m-%d %H:%M:%S"),
                "time_span_hours": (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
            }
        except Exception as e:
            print(f"分析时间分布出错: {e}")
    
    # 分析事件类型分布
    if 'event_type' in df.columns:
        event_counts = df['event_type'].value_counts().to_dict()
        result["event_distribution"] = {k: int(v) for k, v in event_counts.items()}
    
    # 分析服务器分布
    if 'server_id' in df.columns:
        server_counts = df['server_id'].value_counts().to_dict()
        result["server_distribution"] = {k: int(v) for k, v in server_counts.items()}
    
    return result

def analyze_correlations(df):
    """分析相关性"""
    try:
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        # 找出高相关性的列对
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= 0.7:  # 高相关性阈值
                    high_corr_pairs.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": float(corr_value)
                    })
        
        return {
            "high_correlations": high_corr_pairs
        }
    except Exception as e:
        print(f"分析相关性出错: {e}")
        return {}

def save_json(data, file_path):
    """保存结果为JSON文件"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到 {file_path}")
    except Exception as e:
        print(f"保存JSON文件出错: {e}")

def main():
    file_path = "temp_csv/excel_data_20250317132811.csv"
    output_path = "pngs/analysis_results.json"
    
    # 读取CSV文件
    df = read_csv_file(file_path)
    if df is None:
        return
    
    # 分析数据
    analysis = {
        "file_path": file_path,
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "basic_stats": get_basic_stats(df),
        "distributions": analyze_distributions(df),
        "correlations": analyze_correlations(df)
    }
    
    # 保存结果
    save_json(analysis, output_path)

if __name__ == "__main__":
    main()