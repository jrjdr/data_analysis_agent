
import pandas as pd
import sys

# 这段代码包含一个错误：缺少参数
def analyze_data():
    # 读取CSV文件
    file_path = sys.argv[1]
    df = pd.read_csv(file_path)
    
    # 基本统计
    print(f"数据行数: {len(df)}")
    print(f"数据列数: {len(df.columns)}")
    
    # 计算平均年龄和薪资（这里有一个错误：拼写错误）
    avg_age = df['age'].maen()  # 正确应该是 mean()
    avg_salary = df['salary'].mean()
    
    print(f"平均年龄: {avg_age}")
    print(f"平均薪资: {avg_salary}")
    
    # 保存结果
    with open('analysis_results.txt', 'w') as f:
        f.write(f"数据行数: {len(df)}\n")
        f.write(f"数据列数: {len(df.columns)}\n")
        f.write(f"平均年龄: {avg_age}\n")
        f.write(f"平均薪资: {avg_salary}\n")
    
    print("分析完成，结果已保存到 analysis_results.txt")

if __name__ == "__main__":
    analyze_data()
