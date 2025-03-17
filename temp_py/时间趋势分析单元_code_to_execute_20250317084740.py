import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import argparse

def load_data(file_path):
    """加载CSV数据文件"""
    try:
        df = pd.read_csv(file_path)
        print(f"成功加载数据，共{len(df)}行")
        return df
    except Exception as e:
        print(f"加载数据失败: {e}")
        sys.exit(1)

def prepare_time_data(df):
    """准备时间序列数据"""
    # 检查是否存在Date列
    if 'Date' not in df.columns:
        print("警告: 数据中没有Date列，尝试使用Week或Month列")
        if 'Week' in df.columns:
            print("使用Week列作为时间索引")
            return df, 'Week'
        elif 'Month' in df.columns:
            print("使用Month列作为时间索引")
            return df, 'Month'
        else:
            print("错误: 数据中没有可用的时间列")
            sys.exit(1)
    
    # 转换Date列为datetime类型
    try:
        df['Date'] = pd.to_datetime(df['Date'])
        return df, 'Date'
    except Exception as e:
        print(f"转换Date列失败: {e}")
        if 'Week' in df.columns:
            print("使用Week列作为替代")
            return df, 'Week'
        elif 'Month' in df.columns:
            print("使用Month列作为替代")
            return df, 'Month'
        else:
            print("错误: 无法处理时间数据")
            sys.exit(1)

def analyze_time_trends(df, time_col):
    """分析时间趋势"""
    results = {}
    
    # 1. 按时间聚合销售和收入数据
    if time_col == 'Date':
        # 日期级别分析
        daily_sales = df.groupby(time_col)[['Sales', 'Revenue']].sum().reset_index()
        daily_sales['Date'] = daily_sales['Date'].dt.strftime('%Y-%m-%d')
        
        # 计算7天和30天移动平均
        daily_sales['Sales_7D_MA'] = daily_sales['Sales'].rolling(window=7, min_periods=1).mean()
        daily_sales['Revenue_7D_MA'] = daily_sales['Revenue'].rolling(window=7, min_periods=1).mean()
        daily_sales['Sales_30D_MA'] = daily_sales['Sales'].rolling(window=30, min_periods=1).mean()
        daily_sales['Revenue_30D_MA'] = daily_sales['Revenue'].rolling(window=30, min_periods=1).mean()
        
        results['daily_trends'] = daily_sales.to_dict(orient='records')
        
        # 计算环比增长率
        daily_sales['Sales_DoD_Growth'] = daily_sales['Sales'].pct_change() * 100
        daily_sales['Revenue_DoD_Growth'] = daily_sales['Revenue'].pct_change() * 100
        results['daily_growth'] = daily_sales[['Date', 'Sales_DoD_Growth', 'Revenue_DoD_Growth']].dropna().to_dict(orient='records')
    
    # 2. 月度分析
    monthly_sales = df.groupby('Month')[['Sales', 'Revenue']].sum().reset_index()
    
    # 确保月份按时间顺序排列
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    monthly_sales['Month'] = pd.Categorical(monthly_sales['Month'], categories=month_order, ordered=True)
    monthly_sales = monthly_sales.sort_values('Month')
    
    results['monthly_trends'] = monthly_sales.to_dict(orient='records')
    
    # 3. 周度分析
    weekly_sales = df.groupby('Week')[['Sales', 'Revenue']].sum().reset_index()
    # 尝试从Week列提取周数以便排序
    try:
        weekly_sales['Week_Num'] = weekly_sales['Week'].str.extract(r'Week (\d+)').astype(int)
        weekly_sales = weekly_sales.sort_values('Week_Num')
        weekly_sales = weekly_sales.drop('Week_Num', axis=1)
    except:
        pass  # 如果提取失败，保持原样
    
    results['weekly_trends'] = weekly_sales.to_dict(orient='records')
    
    # 4. 类别随时间的趋势
    category_time_trends = df.groupby([time_col, 'Category'])[['Sales', 'Revenue']].sum().reset_index()
    if time_col == 'Date':
        category_time_trends['Date'] = category_time_trends['Date'].dt.strftime('%Y-%m-%d')
    results['category_time_trends'] = category_time_trends.to_dict(orient='records')
    
    # 5. 季节性分析 (如果有足够的数据)
    if time_col == 'Date' and len(daily_sales) >= 14:  # 需要足够的数据点
        try:
            # 设置日期索引用于时间序列分析
            ts_data = daily_sales.set_index('Date')['Revenue']
            # 执行季节性分解
            decomposition = seasonal_decompose(ts_data, model='additive', period=7)  # 假设周期为7天
            
            seasonal_data = decomposition.seasonal.reset_index()
            seasonal_data['Date'] = seasonal_data['Date'].dt.strftime('%Y-%m-%d')
            trend_data = decomposition.trend.reset_index()
            trend_data['Date'] = trend_data['Date'].dt.strftime('%Y-%m-%d')
            
            results['seasonal_components'] = {
                'seasonal': seasonal_data.dropna().to_dict(orient='records'),
                'trend': trend_data.dropna().to_dict(orient='records')
            }
        except Exception as e:
            print(f"季节性分解失败: {e}")
    
    # 6. 简单预测 (如果有足够的数据)
    if time_col == 'Date' and len(daily_sales) >= 14:
        try:
            # 使用指数平滑进行简单预测
            ts_data = daily_sales.set_index('Date')['Revenue']
            model = ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        seasonal='add', 
                                        seasonal_periods=7).fit()
            
            # 预测未来7天
            forecast = model.forecast(7)
            forecast_df = pd.DataFrame({
                'Date': pd.date_range(start=ts_data.index[-1] + pd.Timedelta(days=1), periods=7),
                'Forecasted_Revenue': forecast.values
            })
            forecast_df['Date'] = forecast_df['Date'].dt.strftime('%Y-%m-%d')
            
            results['forecast'] = forecast_df.to_dict(orient='records')
        except Exception as e:
            print(f"预测失败: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='分析CSV文件中的时间趋势')
    parser.add_argument('file_path', help='CSV文件路径')
    parser.add_argument('--output', default='time_trend_analysis_results.json', help='输出JSON文件路径')
    
    args = parser.parse_args()
    
    # 加载数据
    df = load_data(args.file_path)
    
    # 准备时间数据
    df, time_col = prepare_time_data(df)
    
    # 分析时间趋势
    results = analyze_time_trends(df, time_col)
    
    # 保存结果到JSON文件
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到 {args.output}")
    except Exception as e:
        print(f"保存结果失败: {e}")

if __name__ == "__main__":
    main()