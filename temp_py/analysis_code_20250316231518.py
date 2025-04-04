#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
零售销售数据分析脚本
该脚本分析零售业务的销售数据，特别是服装产品的销售情况。
分析内容包括基础统计分析、趋势分析、对比分析和分类统计。
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

def load_data(file_path):
    """
    加载CSV文件数据并进行初步处理
    
    参数:
        file_path (str): CSV文件的路径
    
    返回:
        pandas.DataFrame: 处理后的数据框
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查必要的列是否存在
        required_columns = ['Category', 'Item', 'Price', 'Date', 'Week', 'Month', 'Sales', 'Revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"CSV文件缺少以下必要列: {', '.join(missing_columns)}")
        
        # 转换数据类型
        df['Date'] = pd.to_datetime(df['Date'])
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
        
        # 检查并处理缺失值
        if df.isnull().sum().sum() > 0:
            print(f"警告: 数据中存在缺失值，进行处理中...")
            # 对于数值型列，用中位数填充缺失值
            df['Price'].fillna(df['Price'].median(), inplace=True)
            df['Sales'].fillna(df['Sales'].median(), inplace=True)
            df['Revenue'].fillna(df['Revenue'].median(), inplace=True)
            # 对于分类列，用众数填充缺失值
            df['Category'].fillna(df['Category'].mode()[0], inplace=True)
            df['Item'].fillna(df['Item'].mode()[0], inplace=True)
            df['Week'].fillna(df['Week'].mode()[0], inplace=True)
            df['Month'].fillna(df['Month'].mode()[0], inplace=True)
        
        # 检查Revenue是否等于Price乘以Sales，如果不等则修正
        calculated_revenue = df['Price'] * df['Sales']
        revenue_diff = np.abs(df['Revenue'] - calculated_revenue)
        inconsistent_rows = revenue_diff > 0.01  # 允许小的浮点数误差
        
        if inconsistent_rows.any():
            print(f"警告: 发现{inconsistent_rows.sum()}行的Revenue不等于Price乘以Sales，进行修正...")
            df.loc[inconsistent_rows, 'Revenue'] = calculated_revenue[inconsistent_rows]
        
        # 提取年份和季度信息，方便后续分析
        df['Year'] = df['Date'].dt.year
        df['Quarter'] = df['Date'].dt.quarter
        
        # 将月份名称转换为月份数字，便于排序
        month_order = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        df['Month_Num'] = df['Month'].map(month_order)
        
        return df
        
    except Exception as e:
        print(f"加载数据时出错: {str(e)}")
        sys.exit(1)

def basic_statistics(df):
    """
    计算基础统计指标
    
    参数:
        df (pandas.DataFrame): 数据框
    
    返回:
        str: 基础统计结果的文本描述
    """
    result = "1. 基础统计分析\n" + "="*50 + "\n\n"
    
    # 数值型列的统计分析
    numeric_cols = ['Price', 'Sales', 'Revenue']
    result += "1.1 数值型数据统计\n" + "-"*50 + "\n"
    
    for col in numeric_cols:
        result += f"\n{col} 统计:\n"
        result += f"  最小值: {df[col].min():.2f}\n"
        result += f"  最大值: {df[col].max():.2f}\n"
        result += f"  平均值: {df[col].mean():.2f}\n"
        result += f"  中位数: {df[col].median():.2f}\n"
        result += f"  标准差: {df[col].std():.2f}\n"
        result += f"  四分位数: {df[col].quantile([0.25, 0.5, 0.75]).to_dict()}\n"
    
    # 检测异常值
    result += "\n1.2 异常值检测\n" + "-"*50 + "\n"
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        
        result += f"\n{col} 异常值:\n"
        result += f"  异常值范围: < {lower_bound:.2f} 或 > {upper_bound:.2f}\n"
        result += f"  异常值数量: {len(outliers)}\n"
        
        if len(outliers) > 0:
            result += f"  异常值示例(前5个):\n"
            sample_outliers = outliers.head(5)
            for idx, row in sample_outliers.iterrows():
                result += f"    行 {idx}: {col} = {row[col]:.2f}, Date = {row['Date'].strftime('%Y-%m-%d')}, Item = {row['Item']}\n"
    
    # 分类数据统计
    result += "\n1.3 分类数据统计\n" + "-"*50 + "\n"
    
    # 产品类别统计
    category_counts = df['Category'].value_counts()
    result += f"\n产品类别分布:\n"
    for category, count in category_counts.items():
        result += f"  {category}: {count} 条记录 ({count/len(df)*100:.2f}%)\n"
    
    # 商品统计
    item_counts = df['Item'].value_counts()
    result += f"\n商品分布 (前10个):\n"
    for item, count in item_counts.head(10).items():
        result += f"  {item}: {count} 条记录 ({count/len(df)*100:.2f}%)\n"
    
    # 周统计
    week_counts = df['Week'].value_counts().sort_index()
    result += f"\n周分布:\n"
    for week, count in week_counts.items():
        result += f"  {week}: {count} 条记录\n"
    
    # 月份统计
    month_counts = df.groupby('Month_Num')['Month'].first().reset_index()
    month_counts = month_counts.set_index('Month_Num').loc[range(1, 13), 'Month']
    month_data = df.groupby('Month_Num').size()
    
    result += f"\n月份分布:\n"
    for month_num in range(1, 13):
        if month_num in month_data.index:
            month_name = month_counts.get(month_num, f"Month {month_num}")
            count = month_data.get(month_num, 0)
            result += f"  {month_name}: {count} 条记录\n"
    
    return result

def trend_analysis(df):
    """
    进行销售趋势分析
    
    参数:
        df (pandas.DataFrame): 数据框
    
    返回:
        str: 趋势分析结果的文本描述
    """
    result = "\n2. 销售趋势分析\n" + "="*50 + "\n\n"
    
    # 按月份分析销售趋势
    result += "2.1 月度销售趋势\n" + "-"*50 + "\n"
    monthly_sales = df.groupby('Month_Num').agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    # 添加月份名称
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    monthly_sales['Month'] = monthly_sales['Month_Num'].map(month_names)
    
    result += "\n月度销售数量和收入:\n"
    for _, row in monthly_sales.sort_values('Month_Num').iterrows():
        result += f"  {row['Month']}: 销售量 = {row['Sales']}, 收入 = ${row['Revenue']:.2f}\n"
    
    # 计算月度增长率
    monthly_sales['Sales_Growth'] = monthly_sales['Sales'].pct_change() * 100
    monthly_sales['Revenue_Growth'] = monthly_sales['Revenue'].pct_change() * 100
    
    result += "\n月度增长率:\n"
    for i, row in monthly_sales.sort_values('Month_Num').iterrows():
        if i > 0:  # 跳过第一个月，因为没有前一个月的数据
            result += f"  {row['Month']}: 销售量增长率 = {row['Sales_Growth']:.2f}%, 收入增长率 = {row['Revenue_Growth']:.2f}%\n"
    
    # 按季度分析销售趋势
    result += "\n2.2 季度销售趋势\n" + "-"*50 + "\n"
    quarterly_sales = df.groupby('Quarter').agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    result += "\n季度销售数量和收入:\n"
    for _, row in quarterly_sales.sort_values('Quarter').iterrows():
        result += f"  Q{int(row['Quarter'])}: 销售量 = {row['Sales']}, 收入 = ${row['Revenue']:.2f}\n"
    
    # 按周分析销售趋势
    result += "\n2.3 周销售趋势\n" + "-"*50 + "\n"
    
    # 提取周数字部分，便于排序
    df['Week_Num'] = df['Week'].str.extract(r'Week (\d+)').astype(int)
    weekly_sales = df.groupby('Week_Num').agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    result += "\n周销售趋势 (前10周):\n"
    for _, row in weekly_sales.sort_values('Week_Num').head(10).iterrows():
        result += f"  Week {int(row['Week_Num'])}: 销售量 = {row['Sales']}, 收入 = ${row['Revenue']:.2f}\n"
    
    # 分析销售高峰期
    peak_sales_week = weekly_sales.loc[weekly_sales['Sales'].idxmax()]
    peak_revenue_week = weekly_sales.loc[weekly_sales['Revenue'].idxmax()]
    
    result += f"\n销售高峰期:\n"
    result += f"  销售量最高的周: Week {int(peak_sales_week['Week_Num'])}, 销售量 = {peak_sales_week['Sales']}\n"
    result += f"  收入最高的周: Week {int(peak_revenue_week['Week_Num'])}, 收入 = ${peak_revenue_week['Revenue']:.2f}\n"
    
    # 分析销售淡季
    low_sales_week = weekly_sales.loc[weekly_sales['Sales'].idxmin()]
    low_revenue_week = weekly_sales.loc[weekly_sales['Revenue'].idxmin()]
    
    result += f"\n销售淡季:\n"
    result += f"  销售量最低的周: Week {int(low_sales_week['Week_Num'])}, 销售量 = {low_sales_week['Sales']}\n"
    result += f"  收入最低的周: Week {int(low_revenue_week['Week_Num'])}, 收入 = ${low_revenue_week['Revenue']:.2f}\n"
    
    return result

def comparative_analysis(df):
    """
    进行对比分析
    
    参数:
        df (pandas.DataFrame): 数据框
    
    返回:
        str: 对比分析结果的文本描述
    """
    result = "\n3. 对比分析\n" + "="*50 + "\n\n"
    
    # 按产品类别对比分析
    result += "3.1 产品类别对比\n" + "-"*50 + "\n"
    category_analysis = df.groupby('Category').agg({
        'Sales': 'sum',
        'Revenue': 'sum',
        'Price': 'mean'
    }).reset_index()
    
    result += "\n各产品类别销售情况:\n"
    for _, row in category_analysis.iterrows():
        result += f"  {row['Category']}:\n"
        result += f"    总销售量: {row['Sales']}\n"
        result += f"    总收入: ${row['Revenue']:.2f}\n"
        result += f"    平均价格: ${row['Price']:.2f}\n"
    
    # 按商品对比分析
    result += "\n3.2 商品对比\n" + "-"*50 + "\n"
    item_analysis = df.groupby('Item').agg({
        'Sales': 'sum',
        'Revenue': 'sum',
        'Price': 'mean'
    }).reset_index().sort_values('Revenue', ascending=False)
    
    result += "\n销售收入最高的商品 (前5个):\n"
    for _, row in item_analysis.head(5).iterrows():
        result += f"  {row['Item']}:\n"
        result += f"    总销售量: {row['Sales']}\n"
        result += f"    总收入: ${row['Revenue']:.2f}\n"
        result += f"    平均价格: ${row['Price']:.2f}\n"
    
    # 计算每个商品的销售占比
    total_revenue = df['Revenue'].sum()
    item_analysis['Revenue_Percentage'] = (item_analysis['Revenue'] / total_revenue) * 100
    
    result += "\n收入贡献占比最高的商品 (前5个):\n"
    for _, row in item_analysis.sort_values('Revenue_Percentage', ascending=False).head(5).iterrows():
        result += f"  {row['Item']}: {row['Revenue_Percentage']:.2f}% 的总收入\n"
    
    # 季节性对比分析
    result += "\n3.3 季节性对比\n" + "-"*50 + "\n"
    
    # 定义季节
    winter_months = [12, 1, 2]
    spring_months = [3, 4, 5]
    summer_months = [6, 7, 8]
    fall_months = [9, 10, 11]
    
    df['Season'] = 'Unknown'
    df.loc[df['Month_Num'].isin(winter_months), 'Season'] = 'Winter'
    df.loc[df['Month_Num'].isin(spring_months), 'Season'] = 'Spring'
    df.loc[df['Month_Num'].isin(summer_months), 'Season'] = 'Summer'
    df.loc[df['Month_Num'].isin(fall_months), 'Season'] = 'Fall'
    
    season_analysis = df.groupby('Season').agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    # 确保季节按自然顺序排列
    season_order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3, 'Unknown': 4}
    season_analysis['Season_Order'] = season_analysis['Season'].map(season_order)
    season_analysis = season_analysis.sort_values('Season_Order').drop('Season_Order', axis=1)
    
    result += "\n各季节销售情况:\n"
    for _, row in season_analysis.iterrows():
        result += f"  {row['Season']}:\n"
        result += f"    总销售量: {row['Sales']}\n"
        result += f"    总收入: ${row['Revenue']:.2f}\n"
    
    # 计算季节占比
    season_analysis['Sales_Percentage'] = (season_analysis['Sales'] / season_analysis['Sales'].sum()) * 100
    season_analysis['Revenue_Percentage'] = (season_analysis['Revenue'] / season_analysis['Revenue'].sum()) * 100
    
    result += "\n各季节销售占比:\n"
    for _, row in season_analysis.iterrows():
        result += f"  {row['Season']}: 销售量占比 = {row['Sales_Percentage']:.2f}%, 收入占比 = {row['Revenue_Percentage']:.2f}%\n"
    
    return result

def category_statistics(df):
    """
    进行分类统计分析
    
    参数:
        df (pandas.DataFrame): 数据框
    
    返回:
        str: 分类统计结果的文本描述
    """
    result = "\n4. 分类统计分析\n" + "="*50 + "\n\n"
    
    # 按产品类别和月份的交叉分析
    result += "4.1 产品类别与月份交叉分析\n" + "-"*50 + "\n"
    
    category_month_sales = df.groupby(['Category', 'Month_Num']).agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    # 添加月份名称
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August',
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    category_month_sales['Month'] = category_month_sales['Month_Num'].map(month_names)
    
    # 获取所有唯一的产品类别
    categories = df['Category'].unique()
    
    for category in categories:
        result += f"\n{category}的月度销售情况:\n"
        category_data = category_month_sales[category_month_sales['Category'] == category].sort_values('Month_Num')
        
        for _, row in category_data.iterrows():
            result += f"  {row['Month']}: 销售量 = {row['Sales']}, 收入 = ${row['Revenue']:.2f}\n"
    
    # 计算每个类别的最佳销售月份
    best_months = category_month_sales.sort_values('Revenue', ascending=False).groupby('Category').first().reset_index()
    
    result += "\n各产品类别的最佳销售月份:\n"
    for _, row in best_months.iterrows():
        result += f"  {row['Category']}: {row['Month']} (销售量 = {row['Sales']}, 收入 = ${row['Revenue']:.2f})\n"间分析
    result += "\n4.2 价格区间分析\n" + "-"*50 + "\n"
    
    # 创建价格区间
    price_bins = [0, 50, 100, 150, 200, float('inf')]
    price_labels = ['0-50', '51-100', '101-150', '151-200', '200+']
    
    df['Price_Range'] = pd.cut(df['Price'], bins=price_bins, labels=price_labels, right=False)
    
    price_range_analysis = df.groupby('Price_Range').agg({
        'Sales': 'sum',
        'Revenue': 'sum',
        'Item': 'nunique'
    }).reset_index()
    
    result += "\n各价格区间销售情况:\n"
    for _, row in price_range_analysis.iterrows():
        result += f"  价格区间 ${row['Price_Range']}:\n"
        result += f"    商品数量: {row['Item']}\n"
        result += f"    总销售量: {row['Sales']}\n"
        result += f"    总收入: ${row['Revenue']:.2f}\n"
    
    # 计算价格区间占比
    price_range_analysis['Sales_Percentage'] = (price_range_analysis['Sales'] / price_range_analysis['Sales'].sum()) * 100
    price_range_analysis['Revenue_Percentage'] = (price_range_analysis['Revenue'] / price_range_analysis['Revenue'].sum()) * 100
    
    result += "\n各价格区间销售占比:\n"
    for _, row in price_range_analysis.iterrows():
        result += f"  价格区间 ${row['Price_Range']}: 销售量占比 = {row['Sales_Percentage']:.2f}%, 收入占比 = {row['Revenue_Percentage']:.2f}%\n"
    
    return result

def business_insights(df):
    """
    提取业务洞察
    
    参数:
        df (pandas.DataFrame): 数据框
    
    返回:的文本描述
    """
    result = "\n5. 业务洞察\n" + "="*50 + "\n\n"
    
    # 计算总体销售和收入
    total_sales = df['Sales'].sum()
    total_revenue = df['Revenue'].sum()
    
    result += f"5.1 总体业务表现\n" + "-"*50 + "\n"
    result += f"\n总销售量: {total_sales}\n"
    result += f"总收入: ${total_revenue:.2f}\n"
    
    # 计算平均单价和客单价
    avg_price = df['Price'].mean()
    avg_revenue_per_sale = total_revenue / total_sales if total_sales > 0 else 0
    
    result += f"\n平均商品单价: ${avg_price:.2f}\n"
    result += f"平均客单价: ${avg_revenue_per_sale:.2f}\n"
    
    # 季节性分析洞察
    result += f"\n5.2 季节性洞察\n" + "-"*50 + "\n"
    
    # 定义季节
    winter_months = [12, 1, 2]
    spring_months = [3, 4, 5]
    summer_months = [6, 7, 8]
    fall_months = [9, 10, 11]
    
    df['Season'] = 'Unknown'
    df.loc[df['Month_Num'].isin(winter_months), 'Season'] = 'Winter'
    df.loc[df['Month_Num'].isin(spring_months), 'Season'] = 'Spring'
    df.loc[df['Month_Num'].isin(summer_months), 'Season'] = 'Summer'
    df.loc[df['Month_Num'].isin(fall_months), 'Season'] = 'Fall'
    
    season_analysis = df.groupby('Season').agg({
        'Sales': 'sum',
        'Revenue': 'sum'
    }).reset_index()
    
    # 确保季节season_order = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3, 'Unknown': 4}
    season_analysis['Season_Order'] = season_analysis['Season'].map(season_order)
    season_analysis = season_analysis.sort_values('Season_Order').drop('Season_Order', axis=1)
    
    # 找出销售最高和最低的季节
    best_season = season_analysis.loc[season_analysis['Sales'].idxmax()]
    worst_season = season_analysis.loc[season_analysis['Sales'].idxmin()]
    
    result += f"\n销售高峰季节: {best_season['Season']} (销售量 = {best_season['Sales']}, 收入 = ${best_season['Revenue']:.2f})\n"
    result += f"销售淡季: {worst_season['Season']} (销售量 = {worst_season['Sales']}, 收入 = ${worst_season['Revenue']:.2f})\n"
    
    # 计算季节性波动
    season_variation = (best_season['Sales'] - worst_season['Sales']) / worst_season['Sales'] * 100 if worst_season['Sales'] > 0 else 0
    result += f"季节性销售波动: {season_variation:.2f}%\n"
    
    # 产品组合洞察
    result += f"\n5.3 产品组合洞察\n" + "-"*50 + "\n"
    
    # 计算每个商品的收入贡献
    item_revenue = df.groupby('Item').agg({
        'Revenue': 'sum'
    }).reset_index()
    
    item_revenue['Revenue_Percentage'] = (item_revenue['Revenue'] / total_revenue) * 100
    item_revenue = item_revenue.sort_values('Revenue_Percentage', ascending=False)
    
    # 应用80/20法则 (帕累托原则)
    item_revenue['Cumulative_Percentage'] = item_revenue['Revenue_Percentage'].cumsum()
    key_items = item_revenue[item_revenue['Cumulative_Percentage'] <= 80]
    
    result += f"\n关键产品 (贡献了80%收入的商品):\n"
    for _, row in key_items.iterrows():
        }: ${row['Revenue']:.2f} ({row['Revenue_Percentage']:.2f}% 的总收入)\n"
    
    result += f"\n关键产品数量: {len(key_items)} (占总商品数的 {len(key_items)/len(item_revenue)*100:.2f}%)\n"
    
    # 价格策略洞察
    result += f"\n5.4 价格策略洞察\n" + "-"*50 + "\n"
    
    # 计算不同价格区间的销售效率
    price_bins = [0, 50, 100, 150, 200, float('inf')]
    price_labels = ['0-50', '51-100', '101-150', '151-200', '200+']
    
    if 'Price_Range' not in df.columns:
        df['Price_Range'] = pd.cut(df['Price'], bins=price_bins, labels=price_labels, right=False)
    
    price_efficiency = df.groupby('Price_Range').agg({
        'Sales': 'sum',
        'Revenue': 'sum',
        'Item': 'nunique'
    }).reset_index()
    
    price_efficiency['Sales_per_Item'] = price_efficiency['Sales'] / price_efficiency['Item']
    price_efficiency['Revenue_per_Item'] = price_efficiency['Revenue'] / price_efficiency['Item']
    
    result += "\n各价格区间的销售效率:\n"
    for _, row in price_efficiency.iterrows():
        result += f"  价格区间 ${row['Price_Range']}:\n"
        result += f"    平均每个商品销售量: {row['Sales_per_Item']:.2f}\n"
        result += f"    平均每个商品收入: ${row['Revenue_per_Item']:.2f}\n"
    
    # 找出最有效的价格区间
    most_efficient_price = price_efficiency.loc[price_efficiency['Sales_per_Item'].idxmaxefficiency.loc[price_efficiency['Revenue_per_Item'].idxmax()]
    
    result += f"\n销售量最高的价格区间: ${most_efficient_price['Price_Range']} (平均每个商品销售量: {most_efficient_price['Sales_per_Item']:.2f})\n"
    result += f"收入最高的价格区间Range']} (平均每个商品收入: ${most_profitable_price['Revenue_per_Item']:.2f})\n"
    
    return result

def main():
    """
    主函数，处理命令行参数并执行数据分析
    """
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python script.py <csv_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        sys.exit(1)
    
    print(f"正在分析文件: {file_path}")
    
    try:
        #