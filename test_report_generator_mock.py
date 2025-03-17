#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试报表生成器功能（使用模拟模型连接器）
"""

import os
import sys
import logging
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.report_generator import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 模拟模型连接器
class MockModelConnector:
    """模拟模型连接器，用于测试"""
    
    def __init__(self, config):
        self.config = config
    
    def call_model(self, prompt, json_mode=False, temperature=None):
        """模拟调用模型"""
        logger.info("模拟调用模型...")
        return self._generate_mock_response(prompt, json_mode)
    
    def call_model_stream(self, prompt, json_mode=False, temperature=None):
        """模拟流式调用模型"""
        logger.info("模拟流式调用模型...")
        response = self._generate_mock_response(prompt, json_mode)
        
        # 将响应分成小块返回
        chunk_size = max(len(response) // 10, 1)
        for i in range(0, len(response), chunk_size):
            chunk = response[i:i+chunk_size]
            yield chunk
    
    def _generate_mock_response(self, prompt, json_mode):
        """生成模拟响应"""
        # 根据提示词中的关键字生成不同的响应
        if "HTML报告" in prompt:
            return self._generate_mock_html_report()
        elif json_mode:
            return json.dumps({"result": "模拟JSON响应"})
        else:
            return "模拟文本响应"
    
    def _generate_mock_html_report(self):
        """生成模拟HTML报告"""
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
                except Exception as e:
                    logger.error(f"读取结论文件 {file_path} 时出错: {str(e)}")
        
        # 生成HTML报告
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>数据分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .section {{ margin-bottom: 30px; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
    </style>
</head>
<body>
    <h1>数据分析报告</h1>
    
    <div class="section">
        <h2>概览 (Overview)</h2>
        <p>本报告基于对数据集的全面分析，提供了关键洞察和发现。数据集包含销售、客户和产品相关信息。</p>
        
        <table>
            <tr>
                <th>指标</th>
                <th>值</th>
            </tr>
            <tr>
                <td>记录数量</td>
                <td>1,000</td>
            </tr>
            <tr>
                <td>字段数量</td>
                <td>10</td>
            </tr>
            <tr>
                <td>数据完整性</td>
                <td>98%（缺失值比例低于2%）</td>
            </tr>
            <tr>
                <td>销售额平均值</td>
                <td>5,234元</td>
            </tr>
            <tr>
                <td>销售额中位数</td>
                <td>4,890元</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>数据洞察 (Data Insights)</h2>
        <p>通过深入分析，我们发现了以下关键数据洞察：</p>
        
        <table>
            <tr>
                <th>类别</th>
                <th>洞察</th>
                <th>数值</th>
            </tr>
            <tr>
                <td>客户分布</td>
                <td>年龄范围</td>
                <td>18-65岁</td>
            </tr>
            <tr>
                <td>客户分布</td>
                <td>平均年龄</td>
                <td>34.5岁</td>
            </tr>
            <tr>
                <td>地区分布</td>
                <td>华东区占比</td>
                <td>42%</td>
            </tr>
            <tr>
                <td>地区分布</td>
                <td>华南区占比</td>
                <td>28%</td>
            </tr>
            <tr>
                <td>地区分布</td>
                <td>华北区占比</td>
                <td>18%</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>关键发现 (Key Findings)</h2>
        <p>基于数据分析，我们总结出以下关键发现：</p>
        
        <table>
            <tr>
                <th>领域</th>
                <th>发现</th>
                <th>影响</th>
            </tr>
            <tr>
                <td>销售趋势</td>
                <td>季节性波动明显</td>
                <td>第四季度销售额高于其他季度35%</td>
            </tr>
            <tr>
                <td>客户价值</td>
                <td>高价值客户贡献显著</td>
                <td>8%的客户贡献了35%的销售额</td>
            </tr>
            <tr>
                <td>产品表现</td>
                <td>产品类别差异</td>
                <td>类别A销售额最高，类别B增长最快</td>
            </tr>
            <tr>
                <td>相关性</td>
                <td>促销与销售量强相关</td>
                <td>相关系数r=0.78</td>
            </tr>
            <tr>
                <td>客户行为</td>
                <td>客户满意度影响复购</td>
                <td>相关系数r=0.65</td>
            </tr>
        </table>
    </div>
    
    <div class="section summary">
        <h2>总结 (Summary)</h2>
        <p>数据分析揭示了几个关键业务洞察：</p>
        <ol>
            <li>销售表现呈现明显的季节性模式，第四季度表现最佳，建议针对性调整营销策略。</li>
            <li>高价值客户对业务贡献显著，应加强客户关系管理和忠诚度计划。</li>
            <li>产品类别B虽然当前销售额不及A，但增长更快，值得增加投资。</li>
            <li>促销活动对销售量有显著影响，每增加10%的广告投入可带来约7.5%的销售增长。</li>
            <li>客户满意度是驱动复购的关键因素，提高服务质量将直接提升业务表现。</li>
        </ol>
        <p>建议下一步行动：优化第四季度营销策略、开发高价值客户留存计划、增加产品类别B的投资，并持续监测客户满意度指标。</p>
    </div>
    
    <footer>
        <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>分析结论数量: {len(conclusions)}</p>
    </footer>
</body>
</html>"""
        return html

def main():
    """主函数，测试报表生成器"""
    logger.info("开始测试报表生成器...")
    
    # 创建配置
    config = {
        "model": {
            "model_name": "mock-model",
            "temperature": 0.2,
            "max_tokens": 4000
        }
    }
    
    # 创建模拟模型连接器
    model = MockModelConnector(config["model"])
    
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
