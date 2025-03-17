#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试代码生成器的执行和修复功能
"""

import os
import sys
import logging
import yaml
from modules.model_connector import ModelConnector
from modules.code_generator import CodeGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 创建模型连接器
    model = ModelConnector(config)
    
    # 创建代码生成器
    code_generator = CodeGenerator(model, config)
    
    # 创建测试数据文件路径
    test_file = "test_data.csv"
    if not os.path.exists(test_file):
        # 如果测试文件不存在，创建一个简单的测试CSV文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("id,name,age,salary\n")
            f.write("1,Alice,30,5000\n")
            f.write("2,Bob,25,4500\n")
            f.write("3,Charlie,35,6000\n")
            f.write("4,David,28,5200\n")
            f.write("5,Eve,32,5800\n")
    
    # 创建一个包含错误的测试代码
    test_code = """
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
        f.write(f"数据行数: {len(df)}\\n")
        f.write(f"数据列数: {len(df.columns)}\\n")
        f.write(f"平均年龄: {avg_age}\\n")
        f.write(f"平均薪资: {avg_salary}\\n")
    
    print("分析完成，结果已保存到 analysis_results.txt")

if __name__ == "__main__":
    analyze_data()
"""
    
    # 执行并尝试修复代码
    print("=" * 80)
    print("开始测试代码执行和修复功能")
    print("=" * 80)
    
    success, final_code, result = code_generator.execute_and_fix_code(test_code, test_file)
    
    print("\n" + "=" * 80)
    print("测试结果:")
    print(f"成功执行: {'是' if success else '否'}")
    print("-" * 80)
    print("最终代码:")
    print("-" * 80)
    print(final_code)
    print("-" * 80)
    print("执行结果或错误信息:")
    print("-" * 80)
    print(result)
    print("=" * 80)

if __name__ == "__main__":
    main()
