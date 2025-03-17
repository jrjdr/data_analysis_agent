#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试增强型Markdown报告生成器
"""

import os
import sys
import json
import logging
import argparse
import webbrowser
from pathlib import Path
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.model_connector import ModelConnector
from modules.enhanced_markdown_report_generator import EnhancedMarkdownReportGenerator
from modules.excel_analyzer import ExcelAnalyzer
from modules.config_loader import load_config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试增强型Markdown报告生成器')
    parser.add_argument('--file', type=str, default='sample_data/5g_station_data_2025_03_01.xlsx',
                      help='要分析的Excel文件路径')
    parser.add_argument('--theme', type=str, choices=['light', 'dark'], default='light',
                      help='HTML报告主题')
    args = parser.parse_args()
    
    # 加载配置
    config_file = 'config.yaml'
    logger.info(f"加载配置文件: {config_file}")
    config = load_config(config_file)
    
    if not config:
        logger.error("加载配置失败")
        return
    
    # 更新配置
    config['theme'] = args.theme
    
    # 获取模型配置
    model_config = config.get('models', {}).get('conversational', {})
    
    # 初始化模型连接器
    logger.info(f"初始化模型连接器 (模型: {model_config.get('model_id', 'unknown')})")
    model = ModelConnector(config)
    
    # 初始化增强型Markdown报告生成器
    logger.info("初始化增强型Markdown报告生成器")
    report_generator = EnhancedMarkdownReportGenerator(model, config)
    
    # 初始化Excel分析器
    logger.info("初始化Excel分析器")
    excel_analyzer = ExcelAnalyzer(model, config)
    
    # 分析Excel文件
    logger.info(f"分析Excel文件: {args.file}")
    html_report = excel_analyzer.analyze_excel(args.file)
    
    if html_report:
        logger.info("HTML报告生成完成")
        
        # 使用增强型Markdown报告生成器
        logger.info("使用增强型Markdown报告生成器生成报告")
        markdown_report = report_generator.generate_markdown_report(html_report)
        
        if markdown_report:
            logger.info("Markdown报告生成完成")
            
            # 将Markdown转换为HTML
            logger.info("将Markdown转换为HTML")
            from modules.markdown_to_html import markdown_to_html
            
            html_content = markdown_to_html(markdown_report, theme=args.theme)
            
            # 保存HTML报告
            html_file = f"reports/enhanced_report_{time.strftime('%Y%m%d%H%M%S')}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已将增强型HTML报告保存到: {html_file}")
            
            # 自动打开HTML报告
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(html_file)}")
            logger.info("已自动打开HTML报告")
        else:
            logger.error("Markdown报告生成失败")
    else:
        logger.error("HTML报告生成失败")

if __name__ == "__main__":
    main()
