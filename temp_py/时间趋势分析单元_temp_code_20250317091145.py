import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def time_trend_analysis(csv_path):
    """
    对CSV文件进行时间趋势分析
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_path)
        
        # 检查必要的列是否存在
        required_columns = ['Date', 'Sales', 'Revenue']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV文件缺少必要的列: {', '.join(required_columns)}")
        
        # 转换日期列为datetime类型
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        
        # 创建结果字典
        results = {
            "file_path": csv_path,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time_trend_analysis": {}
        }
        
        # 1. 按日期聚合销售和收入数据
        daily_data = df.groupby('Date')[['Sales', 'Revenue']].sum().reset_index()
        
        # 2. 计算月度数据
        monthly_data = df.groupby(df['Date'].dt.strftime('%Y-%m'))[['Sales', 'Revenue']].sum().reset_index()
        monthly_data.columns = ['Month', 'Sales', 'Revenue']
        
        # 3. 计算季度数据
        df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
        quarterly_data = df.groupby('Quarter')[['Sales', 'Revenue']].sum().reset_index()
        
        # 4. 计算移动平均
        daily_data['Sales_7D_MA'] = daily_data['Sales'].rolling(window=7, min_periods=1).mean()
        daily_data['Revenue_7D_MA'] = daily_data['Revenue'].rolling(window=7, min_periods=1).mean()
        daily_data['Sales_30D_MA'] = daily_data['Sales'].rolling(window=30, min_periods=1).mean()
        daily_data['Revenue_30D_MA'] = daily_data['Revenue'].rolling(window=30, min_periods=1).mean()
        
        # 5. 计算环比增长率（日环比）
        daily_data['Sales_DoD_Growth'] = daily_data['Sales'].pct_change() * 100
        daily_data['Revenue_DoD_Growth'] = daily_data['Revenue'].pct_change() * 100
        
        # 6. 计算月度环比增长率
        monthly_data['Sales_MoM_Growth'] = monthly_data['Sales'].pct_change() * 100
        monthly_data['Revenue_MoM_Growth'] = monthly_data['Revenue'].pct_change() * 100
        
        # 7. 季节性分析（使用月度数据）
        # 创建月度时间序列
        monthly_ts = df.groupby(df['Date'].dt.to_period('M'))[['Sales', 'Revenue']].sum()
        monthly_ts.index = pd.DatetimeIndex(monthly_ts.index.astype(str))
        
        # 如果有足够的数据点进行季节性分析（至少2个完整周期）
        if len(monthly_ts) >= 24:
            try:
                # 销售量的季节性分解
                sales_decomposition = seasonal_decompose(monthly_ts['Sales'], model='additive', period=12)
                revenue_decomposition = seasonal_decompose(monthly_ts['Revenue'], model='additive', period=12)
                
                # 提取季节性成分
                seasonality = {
                    "sales_seasonality": sales_decomposition.seasonal.tolist(),
                    "revenue_seasonality": revenue_decomposition.seasonal.tolist(),
                    "months": [str(idx) for idx in sales_decomposition.seasonal.index]
                }
                results["time_trend_analysis"]["seasonality"] = seasonality
            except Exception as e:
                results["time_trend_analysis"]["seasonality_error"] = str(e)
        
        # 8. 简单预测（使用指数平滑）
        if len(monthly_ts) >= 12:
            try:
                # 销售量预测
                sales_model = ExponentialSmoothing(
                    monthly_ts['Sales'], 
                    trend='add', 
                    seasonal='add', 
                    seasonal_periods=12
                ).fit()
                
                # 收入预测
                revenue_model = ExponentialSmoothing(
                    monthly_ts['Revenue'], 
                    trend='add', 
                    seasonal='add', 
                    seasonal_periods=12
                ).fit()
                
                # 预测未来3个月
                forecast_periods = 3
                sales_forecast = sales_model.forecast(forecast_periods).tolist()
                revenue_forecast = revenue_model.forecast(forecast_periods).tolist()
                
                # 获取预测的日期
                last_date = monthly_ts.index[-1]
                forecast_dates = pd.date_range(start=last_date, periods=forecast_periods+1, freq='M')[1:]
                forecast_dates_str = [date.strftime('%Y-%m') for date in forecast_dates]
                
                # 保存预测结果
                forecast_data = {
                    "forecast_dates": forecast_dates_str,
                    "sales_forecast": sales_forecast,
                    "revenue_forecast": revenue_forecast
                }
                results["time_trend_analysis"]["forecast"] = forecast_data
            except Exception as e:
                results["time_trend_analysis"]["forecast_error"] = str(e)
        
        # 9. 保存时间序列数据用于绘图
        results["time_trend_analysis"]["daily_data"] = {
            "dates": [d.strftime('%Y-%m-%d') for d in daily_data['Date']],
            "sales": daily_data['Sales'].tolist(),
            "revenue": daily_data['Revenue'].tolist(),
            "sales_7d_ma": daily_data['Sales_7D_MA'].tolist(),
            "revenue_7d_ma": daily_data['Revenue_7D_MA'].tolist(),
            "sales_30d_ma": daily_data['Sales_30D_MA'].tolist(),
            "revenue_30d_ma": daily_data['Revenue_30D_MA'].tolist()
        }
        
        results["time_trend_analysis"]["monthly_data"] = {
            "months": monthly_data['Month'].tolist(),
            "sales": monthly_data['Sales'].tolist(),
            "revenue": monthly_data['Revenue'].tolist(),
            "sales_mom_growth": monthly_data['Sales_MoM_Growth'].tolist(),
            "revenue_mom_growth": monthly_data['Revenue_MoM_Growth'].tolist()
        }
        
        results["time_trend_analysis"]["quarterly_data"] = {
            "quarters": quarterly_data['Quarter'].tolist(),
            "sales": quarterly_data['Sales'].tolist(),
            "revenue": quarterly_data['Revenue'].tolist()
        }
        
        # 10. 计算总体趋势指标
        results["time_trend_analysis"]["trend_indicators"] = {
            "total_sales": int(df['Sales'].sum()),
            "total_revenue": float(df['Revenue'].sum()),
            "avg_daily_sales": float(daily_data['Sales'].mean()),
            "avg_daily_revenue": float(daily_data['Revenue'].mean()),
            "sales_growth_first_last": float((daily_data['Sales'].iloc[-1] / daily_data['Sales'].iloc[0] - 1) * 100) if daily_data['Sales'].iloc[0] != 0 else None,
            "revenue_growth_first_last": float((daily_data['Revenue'].iloc[-1] / daily_data['Revenue'].iloc[0] - 1) * 100) if daily_data['Revenue'].iloc[0] != 0 else None
        }
        
        # 保存结果到JSON文件
        with open('time_trend_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return "分析完成，结果已保存到 time_trend_analysis_results.json"
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "file_path": csv_path,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open('time_trend_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        
        return f"分析过程中出错: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv文件路径>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f"错误: 文件 '{csv_path}' 不存在")
        sys.exit(1)
    
    result = time_trend_analysis(csv_path)
    print(result)