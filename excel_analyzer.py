#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel Analyzer - 基于大模型的Excel数据分析工具

这个程序会:
1. 从config.yaml读取配置信息
2. 通过OpenAI的接口连接大模型并确认连通性
3. 读取Excel文件并让大模型分析数据结构
4. 让大模型生成Python数据分析代码
5. 在沙箱环境中执行代码，获取结果
6. 将结果再次传给大模型，生成HTML报告
7. 保存HTML报告
"""

import os
import sys
import logging
from datetime import datetime
import traceback

# 导入自定义模块
from modules.config_loader import load_config
from modules.model_connector import ModelConnector
from modules.excel_processor import ExcelProcessor
from modules.code_generator import CodeGenerator
from modules.code_executor import CodeExecutor
from modules.report_generator import ReportGenerator

# 创建目录（如果不存在）
for directory in ['debug', 'logs', 'reports', 'htmls', 'temp_py']:
    os.makedirs(os.path.join(os.getcwd(), directory), exist_ok=True)

# 配置日志
log_file = os.path.join(os.getcwd(), 'logs', f'excel_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    主函数，运行整个Excel分析流程
    """
    try:
        logger.info("开始Excel分析流程")
        
        # 1. 加载配置
        logger.info("正在加载配置...")
        config = load_config()
        if not config:
            logger.error("加载配置失败，程序终止")
            return
        
        # 2. 初始化模型连接器并测试连接
        logger.info("正在初始化模型连接...")
        model = ModelConnector(config)
        if not model.test_connection():
            logger.error("模型连接测试失败，程序终止")
            return
        
        # 3. 处理Excel文件并分析数据结构
        logger.info("正在处理Excel文件...")
        excel_processor = ExcelProcessor(config)
        excel_data = excel_processor.load_sample_data()
        if not excel_data:
            logger.error("加载Excel样本数据失败，程序终止")
            return
        
        # 4. 分析数据结构
        logger.info("正在分析数据结构...")
        structure_analysis = model.analyze_data_structure(excel_data)
        if not structure_analysis:
            logger.error("分析数据结构失败，程序终止")
            return
        
        # 5. 生成分析代码
        logger.info("正在生成分析代码...")
        code_generator = CodeGenerator(model, config)
        analysis_code = code_generator.generate_analysis_code(structure_analysis, excel_processor.get_column_names())
        if not analysis_code:
            logger.error("生成分析代码失败，程序终止")
            return
        
        # 6. 执行分析代码
        logger.info("正在执行分析代码...")
        full_data = excel_processor.load_full_data()
        
        # 使用新的execute_and_fix_code方法执行和修复代码
        success, final_code, result = code_generator.execute_and_fix_code(analysis_code, full_data)
        
        if not success:
            logger.error("执行代码失败，即使经过多次修复尝试")
            logger.error(f"错误信息: {result}")
            return
        
        # 更新分析代码为最终成功执行的代码
        analysis_code = final_code
        
        # 假设结果已经保存到文件，从结果中提取输出文件路径
        # 如果结果中没有明确的输出文件路径，可以创建一个临时文件
        output_file = os.path.join(os.getcwd(), 'temp_py', f'analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        logger.info(f"分析代码执行成功，结果已保存到: {output_file}")
        
        # 7. 生成HTML报告
        logger.info("正在生成HTML报告...")
        report_generator = ReportGenerator(model, config)
        html_report = report_generator.generate_report(structure_analysis, output_file)
        if not html_report:
            logger.error("生成HTML报告失败，程序终止")
            return
        
        # 8. 保存HTML报告
        report_path = os.path.join(os.getcwd(), 'htmls', f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"分析完成，HTML报告已保存到: {report_path}")
        
    except Exception as e:
        logger.error(f"程序执行过程中出错: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
