#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能数据分析助手 - 主程序
集成了所有模块，提供完整的Excel文件分析功能
"""

import os
import sys
import logging
import argparse
import yaml
from datetime import datetime

from modules.model_connector import ModelConnector
from modules.excel_analyzer import ExcelAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/app_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_path='config.yaml'):
    """
    加载配置文件
    
    Args:
        config_path (str): 配置文件路径
    
    Returns:
        dict: 配置信息
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"成功加载配置文件: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return None

def main():
    """主程序入口"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='智能数据分析助手')
    parser.add_argument('--file', help='要分析的Excel文件路径 (覆盖配置文件中的设置)')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--api-key', help='API密钥（覆盖配置文件中的设置）')
    parser.add_argument('--model', help='要使用的模型名称（覆盖配置文件中的设置）')
    parser.add_argument('--output', help='输出报告的文件路径（覆盖配置文件中的设置）')
    parser.add_argument('--no-charts', action='store_true', help='不生成图表HTML报告')
    args = parser.parse_args()
    
    # 确保目录存在
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp_csv', exist_ok=True)
    os.makedirs('temp_py', exist_ok=True)
    
    try:
        # 加载配置文件
        config = load_config(args.config)
        if not config:
            logger.error(f"无法加载配置文件: {args.config}")
            print(f"错误: 无法加载配置文件: {args.config}")
            return 1
        
        # 确定Excel文件路径
        file_path = args.file or config.get('analysis', {}).get('excel_file')
        if not file_path:
            logger.error("未指定Excel文件路径")
            print("错误: 未指定Excel文件路径，请在配置文件中设置或使用--file参数")
            return 1
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            print(f"错误: 文件不存在: {file_path}")
            return 1
        
        # 检查是否为Excel文件
        if not file_path.endswith(('.xlsx', '.xls')):
            logger.error(f"不是Excel文件: {file_path}")
            print(f"错误: 不是Excel文件: {file_path}")
            return 1
        
        # 获取模型配置
        model_config = config.get('models', {}).get('conversational', {})
        if not model_config:
            logger.error("配置文件中缺少模型配置")
            print("错误: 配置文件中缺少模型配置")
            return 1
        
        # 获取API密钥
        api_key = args.api_key or model_config.get('api_key') or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("未提供API密钥")
            print("错误: 未提供API密钥，请在配置文件中设置、使用--api-key参数或设置OPENAI_API_KEY环境变量")
            return 1
        
        # 更新模型配置
        model_config['api_key'] = api_key
        if args.model:
            model_config['model_id'] = args.model
        
        # 获取分析配置
        analysis_config = config.get('analysis', {})
        
        # 获取报告配置
        report_config = config.get('report', {})
        
        # 如果命令行参数指定了不生成图表报告，则覆盖配置
        if args.no_charts:
            report_config['generate_chart_subreport'] = False
        
        # 合并配置
        app_config = {
            'model': model_config.get('model_id', 'gpt-4'),
            'api_key': api_key,
            'api_base': model_config.get('api_base'),
            'temperature': model_config.get('parameters', {}).get('temperature', 0.2),
            'max_tokens': model_config.get('parameters', {}).get('max_tokens', 4000),
            'retry_count': config.get('api', {}).get('max_retries', 3),
            'retry_delay': config.get('api', {}).get('retry_delay', 5),
            'analysis': analysis_config,
            'report': report_config
        }
        
        # 初始化模型连接器
        logger.info(f"初始化模型连接器 (模型: {app_config['model']})")
        model = ModelConnector(app_config)
        
        # 初始化Excel分析器
        logger.info("初始化Excel分析器")
        analyzer = ExcelAnalyzer(model, app_config)
        
        # 分析Excel文件
        logger.info(f"开始分析Excel文件: {file_path}")
        print(f"正在分析Excel文件: {file_path}...")
        markdown_report, html_report = analyzer.analyze_excel(file_path)
        
        # 确定Markdown输出路径
        if args.output:
            output_base = args.output
            if output_base.endswith('.html'):
                output_base = output_base[:-5]  # 移除.html后缀
            elif output_base.endswith('.md'):
                output_base = output_base[:-3]  # 移除.md后缀
            
            markdown_path = f"{output_base}.md"
            html_path = f"{output_base}.html"
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_output = report_config.get('default_output_file', 'excel_analysis_report')
            if default_output.endswith('.html') or default_output.endswith('.md'):
                default_output = default_output.rsplit('.', 1)[0]  # 移除任何文件扩展名
            
            markdown_path = f"reports/{default_output}_{timestamp}.md"
            html_path = f"reports/{default_output}_{timestamp}.html"
        
        # 保存Markdown报告
        os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"分析完成，Markdown报告已保存到: {markdown_path}")
        print(f"分析完成，Markdown报告已保存到: {markdown_path}")
        
        # 如果生成了HTML报告，则保存
        if html_report:
            logger.info(f"HTML图表报告已保存到: {html_report}")
            print(f"HTML图表报告已保存到: {html_report}")
        else:
            logger.info(f"分析完成，没有生成HTML报告")
            print(f"分析完成，没有生成HTML报告")
        
        return 0
        
    except Exception as e:
        logger.exception("程序执行过程中发生错误")
        print(f"错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
