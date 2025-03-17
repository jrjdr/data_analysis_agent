#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用真实配置和大模型测试报表生成功能
"""

import os
import sys
import logging
import yaml
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.report_generator import ReportGenerator
from modules.model_connector import ModelConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_config(config_file='config.yaml'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return None

def main():
    """主函数，测试报表生成器"""
    logger.info("开始测试报表生成器...")
    
    # 加载配置
    config = load_config()
    if not config:
        logger.error("无法加载配置文件")
        return
    
    # 使用配置文件中的模型设置
    model_config = config['models']['conversational']
    
    # 创建模型连接器
    model = ModelConnector(model_config)
    
    # 创建报表生成器
    report_generator = ReportGenerator(model, config)
    
    # 读取临时文本文件中的分析结论
    conclusions = []
    temp_txts_dir = os.path.join(os.getcwd(), 'temp_txts')
    if os.path.exists(temp_txts_dir):
        conclusion_files = [f for f in os.listdir(temp_txts_dir) if f.endswith('_conclusion.txt')]
        conclusion_files.sort()
        
        for file_name in conclusion_files:
            file_path = os.path.join(temp_txts_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        conclusions.append(content)
                        logger.info(f"已读取结论文件: {file_name}")
            except Exception as e:
                logger.error(f"读取结论文件 {file_path} 时出错: {str(e)}")
    
    # 合并所有结论
    combined_conclusions = "\n\n".join(conclusions)
    logger.info(f"共读取到 {len(conclusions)} 个分析结论")
    
    # 创建模拟数据结构分析结果
    structure_analysis = {
        "file_name": "clothing_sales_data.xlsx",
        "sheet_count": 1,
        "active_sheet": "Sheet1",
        "row_count": 1000,
        "column_count": 10,
        "columns": [
            {"name": "日期", "type": "date", "missing_values": 0},
            {"name": "产品类别", "type": "category", "missing_values": 0},
            {"name": "产品名称", "type": "string", "missing_values": 0},
            {"name": "单价", "type": "numeric", "missing_values": 0},
            {"name": "销售数量", "type": "numeric", "missing_values": 0},
            {"name": "销售额", "type": "numeric", "missing_values": 0},
            {"name": "客户年龄", "type": "numeric", "missing_values": 0},
            {"name": "客户性别", "type": "category", "missing_values": 0},
            {"name": "地区", "type": "category", "missing_values": 0},
            {"name": "渠道", "type": "category", "missing_values": 0}
        ]
    }
    
    # 生成HTML报告
    logger.info("开始生成HTML报告...")
    html_report = report_generator.generate_html_report(combined_conclusions, structure_analysis)
    
    if html_report:
        # 保存报告
        report_file = f"reports/real_model_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        logger.info(f"测试报告已保存到: {report_file}")
        
        # 尝试自动打开报告
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_file)}")
            logger.info("已自动打开报告")
        except Exception as e:
            logger.warning(f"无法自动打开报告: {str(e)}")
    else:
        logger.error("生成HTML报告失败")
    
    logger.info("报表生成器测试完成")

if __name__ == "__main__":
    main()
