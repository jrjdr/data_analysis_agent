import pandas as pd
import numpy as np
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

def read_and_process_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        # 检查必要的列是否存在
        required_columns = ['Date_Reported', 'Resolution_Date']
        for col in required_columns:
            if col not in df.columns:
                print(f"错误: CSV文件中缺少必要的列 '{col}'")
                return None
                
        # 转换日期列，处理错误格式
        df['Date_Reported'] = pd.to_datetime(df['Date_Reported'], errors='coerce')
        df['Resolution_Date'] = pd.to_datetime(df['Resolution_Date'], errors='coerce')
        
        # 删除日期无效的行
        invalid_dates = df['Date_Reported'].isna().sum()
        if invalid_dates > 0:
            print(f"警告: 删除了 {invalid_dates} 行含有无效报告日期的数据")
            df = df.dropna(subset=['Date_Reported'])
            
        if len(df) == 0:
            print("错误: 处理后数据为空")
            return None
            
        return df
    except Exception as e:
        print(f"读取CSV文件时出错: {e}")
        return None

def analyze_time_trends(df):
    # 确保数据框不为空
    if df is None or len(df) == 0:
        print("错误: 无法分析空数据")
        return None, None, None, None, None, None
    
    # 按日期分组并计数
    daily_complaints = df.groupby(df['Date_Reported'].dt.date).size()
    # 转换为时间序列
    daily_complaints.index = pd.DatetimeIndex(daily_complaints.index)
    
    # 确保数据有足够的长度进行重采样
    if len(daily_complaints) < 2:
        print("错误: 数据点不足，无法进行时间趋势分析")
        return daily_complaints, None, None, None, None, None
    
    # 重采样
    daily_complaints = daily_complaints.resample('D').sum().fillna(0)
    weekly_complaints = daily_complaints.resample('W').sum()
    monthly_complaints = daily_complaints.resample('M').sum()
    
    # 季节性分解需要足够的数据点
    if len(daily_complaints) >= 14:  # 至少需要两周的数据
        try:
            # 确保索引是有序的
            daily_complaints = daily_complaints.sort_index()
            # 执行季节性分解
            result = seasonal_decompose(daily_complaints, model='additive', period=7)
            trend = result.trend
            seasonal = result.seasonal
            residual = result.resid
            
            # 检测异常值
            std_residual = residual.dropna().std()
            if not pd.isna(std_residual) and std_residual > 0:
                anomalies = residual[abs(residual) > 2 * std_residual]
            else:
                anomalies = pd.Series(dtype='float64')
        except Exception as e:
            print(f"季节性分解时出错: {e}")
            trend = pd.Series(dtype='float64')
            seasonal = pd.Series(dtype='float64')
            residual = pd.Series(dtype='float64')
            anomalies = pd.Series(dtype='float64')
    else:
        print("警告: 数据点不足，无法进行季节性分解")
        trend = pd.Series(dtype='float64')
        seasonal = pd.Series(dtype='float64')
        residual = pd.Series(dtype='float64')
        anomalies = pd.Series(dtype='float64')

    return daily_complaints, weekly_complaints, monthly_complaints, trend, seasonal, anomalies

def format_results(daily, weekly, monthly, trend, seasonal, anomalies):
    # 检查输入是否有效
    if daily is None:
        return "无法生成分析结果: 数据无效"
    
    result = "时间趋势分析结果\n"
    result += "===========================\n\n"

    result += "1. 每日投诉趋势\n"
    result += "--------------------------\n"
    if len(daily) > 0:
        result += f"平均每日投诉: {daily.mean():.2f}\n"
        if not daily.empty:
            result += f"最大每日投诉: {daily.max()} 发生于 {daily.idxmax().strftime('%Y-%m-%d')}\n"
            result += f"最小每日投诉: {daily.min()} 发生于 {daily.idxmin().strftime('%Y-%m-%d')}\n\n"
    else:
        result += "没有足够的每日数据进行分析\n\n"

    result += "2. 每周投诉趋势\n"
    result += "---------------------------\n"
    if weekly is not None and len(weekly) > 0:
        result += f"平均每周投诉: {weekly.mean():.2f}\n"
        if not weekly.empty:
            result += f"最大每周投诉: {weekly.max()} 截止于 {weekly.idxmax().strftime('%Y-%m-%d')}\n"
            result += f"最小每周投诉: {weekly.min()} 截止于 {weekly.idxmin().strftime('%Y-%m-%d')}\n\n"
    else:
        result += "没有足够的每周数据进行分析\n\n"

    result += "3. 每月投诉趋势\n"
    result += "----------------------------\n"
    if monthly is not None and len(monthly) > 0:
        result += f"平均每月投诉: {monthly.mean():.2f}\n"
        if not monthly.empty:
            result += f"最大每月投诉: {monthly.max()} 发生于 {monthly.idxmax().strftime('%Y-%m')}\n"
            result += f"最小每月投诉: {monthly.min()} 发生于 {monthly.idxmin().strftime('%Y-%m')}\n\n"
    else:
        result += "没有足够的每月数据进行分析\n\n"

    result += "4. 趋势分析\n"
    result += "-------------------\n"
    if trend is not None and not trend.empty and len(trend.dropna()) > 1:
        result += f"趋势起始值: {trend.dropna().iloc[0]:.2f}\n"
        result += f"趋势结束值: {trend.dropna().iloc[-1]:.2f}\n"
        result += f"整体趋势: {'上升' if trend.dropna().iloc[-1] > trend.dropna().iloc[0] else '下降'}\n\n"
    else:
        result += "没有足够的数据进行趋势分析\n\n"

    result += "5. 季节性模式\n"
    result += "---------------------\n"
    if seasonal is not None and not seasonal.empty:
        try:
            max_day = seasonal.idxmax().dayofweek
            min_day = seasonal.idxmin().dayofweek
            days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            result += f"最高季节性因子: {seasonal.max():.2f} (星期几: {days[max_day]})\n"
            result += f"最低季节性因子: {seasonal.min():.2f} (星期几: {days[min_day]})\n\n"
        except:
            result += "无法确定季节性模式\n\n"
    else:
        result += "没有足够的数据进行季节性分析\n\n"

    result += "6. 异常值\n"
    result += "--------------\n"
    if anomalies is not None and not anomalies.empty:
        result += f"检测到的异常值数量: {len(anomalies)}\n"
        if len(anomalies) > 0:
            result += "异常日期:\n"
            for date, value in anomalies.items():
                result += f"  {date.strftime('%Y-%m-%d')}: {value:.2f}\n"
    else:
        result += "没有检测到异常值或数据不足以进行异常值分析\n"
        
    return result

def main(file_path):
    # 读取和处理数据
    df = read_and_process_csv(file_path)
    if df is None:
        return "无法读取或处理数据文件"
    
    # 分析时间趋势
    daily, weekly, monthly, trend, seasonal, anomalies = analyze_time_trends(df)
    
    # 格式化并返回结果
    return format_results(daily, weekly, monthly, trend, seasonal, anomalies)

# 使用示例
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(main(file_path))
    else:
        print("请提供CSV文件路径作为参数")