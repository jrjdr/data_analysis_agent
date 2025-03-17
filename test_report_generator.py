#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试报表生成器功能
"""

import os
import sys
import logging
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

def main():
    """主函数，测试报表生成器"""
    logger.info("开始测试报表生成器...")
    
    # 创建配置
    config = {
        "model": {
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.2,
            "max_tokens": 4000
        }
    }
    
    # 检查API密钥
    if not config["model"]["api_key"]:
        logger.error("未设置API密钥，请设置OPENAI_API_KEY环境变量")
        return
    
    # 创建模型连接器
    model = ModelConnector(config["model"])
    
    # 创建报表生成器
    report_generator = ReportGenerator(model, config)
    
    # 创建模拟分析结果
    analysis_results = """
# 数据分析结果摘要

## 数据集概述
- 数据集包含10个字段，共有1000条记录
- 数据完整性良好，缺失值比例低于2%
- 主要数据类型包括数值型、日期型和分类型数据

## 主要统计指标
- 销售额平均值：5,234元，中位数：4,890元
- 客户年龄分布：18-65岁，平均年龄：34.5岁
- 地区分布：华东区占比最高(42%)，其次是华南区(28%)和华北区(18%)
"""
    
    # 生成HTML报告
    logger.info("开始生成HTML报告...")
    html_report = report_generator.generate_html_report(analysis_results)
    
    if html_report:
        # 保存报告
        report_file = f"reports/test_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
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
