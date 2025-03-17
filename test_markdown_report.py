#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Markdown报告生成和渲染功能
"""

import os
import logging
import yaml
import argparse
import webbrowser
from pathlib import Path
import json
import time
import threading
import sys

from modules.model_connector import ModelConnector
from modules.excel_analyzer import ExcelAnalyzer
from modules.markdown_report_generator import MarkdownReportGenerator
from markdown_to_html import MarkdownToHtmlRenderer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置超时处理
class TimeoutError(Exception):
    pass

class Timeout:
    """Windows兼容的超时处理类"""
    def __init__(self, seconds):
        self.seconds = seconds
        self.timer = None
        self.is_timeout = False
    
    def timeout_handler(self):
        self.is_timeout = True
        # 在Windows上，我们不能直接终止线程，但可以设置标志
        logger.error(f"操作超时（{self.seconds}秒）")
    
    def __enter__(self):
        self.timer = threading.Timer(self.seconds, self.timeout_handler)
        self.timer.daemon = True
        self.timer.start()
        return self
    
    def __exit__(self, type, value, traceback):
        if self.timer:
            self.timer.cancel()
        if self.is_timeout:
            raise TimeoutError(f"操作超时（{self.seconds}秒）")

def main():
    """
    主函数，测试Markdown报告生成和渲染功能
    """
    parser = argparse.ArgumentParser(description='测试Markdown报告生成和渲染功能')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('--api_key', help='API密钥，如果不提供则使用环境变量或配置文件中的值')
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help='HTML报告主题')
    parser.add_argument('--timeout', type=int, default=300, help='分析操作超时时间（秒）')
    parser.add_argument('--skip_analysis', action='store_true', help='跳过分析步骤，直接使用已有的分析结果')
    parser.add_argument('--analysis_result', help='已有的分析结果文件路径')
    
    args = parser.parse_args()
    
    try:
        # 加载配置文件
        logger.info(f"加载配置文件: {args.config}")
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 如果提供了API密钥，覆盖配置中的值
        if args.api_key:
            config['models']['conversational']['api_key'] = args.api_key
        elif os.environ.get('OPENAI_API_KEY'):
            config['models']['conversational']['api_key'] = os.environ.get('OPENAI_API_KEY')
        
        # 初始化模型连接器
        logger.info(f"初始化模型连接器 (模型: {config['models']['conversational']['model_id']})")
        model = ModelConnector(config)
        
        # 初始化Markdown报告生成器
        logger.info("初始化Markdown报告生成器")
        md_report_generator = MarkdownReportGenerator(model, config)
        
        combined_results = None
        
        # 如果不跳过分析步骤，执行分析
        if not args.skip_analysis:
            # 初始化Excel分析器
            logger.info("初始化Excel分析器")
            analyzer = ExcelAnalyzer(model, config)
            
            # 分析Excel文件
            excel_file = config['analysis']['excel_file']
            logger.info(f"开始分析Excel文件: {excel_file}")
            print(f"正在分析Excel文件: {excel_file}...")
            
            # 使用Windows兼容的超时处理
            with Timeout(args.timeout) as timeout:
                try:
                    # 将Excel转换为CSV以便处理
                    csv_path = analyzer._convert_excel_to_csv(excel_file)
                    if not csv_path:
                        logger.error("转换Excel为CSV失败")
                        return
                    
                    # 获取数据结构分析和列名
                    structure_analysis, column_names = analyzer._analyze_structure(csv_path)
                    if not structure_analysis or not column_names:
                        logger.error("分析数据结构失败")
                        return
                    
                    # 使用分析调度器直接运行所有分析单元
                    logger.info("使用分析调度器运行所有分析单元...")
                    
                    # 创建一个简单的结果结构
                    combined_results = {
                        "structure_analysis": structure_analysis,
                        "unit_results": {}
                    }
                    
                    # 运行分析单元，但设置较短的超时时间
                    try:
                        results = analyzer.dispatcher.run_analysis(structure_analysis, column_names, csv_path)
                        
                        # 检查是否至少有一个分析单元成功执行
                        success = any(result["status"] == "success" for result in results.values())
                        
                        if not success:
                            logger.error("所有分析单元执行失败")
                            return
                        
                        # 获取组合结果
                        combined_results["unit_results"] = results
                        
                        # 保存分析结果以便后续使用
                        result_dir = "analysis_results"
                        os.makedirs(result_dir, exist_ok=True)
                        timestamp = time.strftime('%Y%m%d%H%M%S')
                        result_file = f"{result_dir}/analysis_result_{timestamp}.json"
                        
                        with open(result_file, 'w', encoding='utf-8') as f:
                            json.dump(combined_results, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"分析结果已保存到: {result_file}")
                        
                    except Exception as e:
                        logger.error(f"运行分析单元时出错: {str(e)}")
                        # 即使出错，也尝试继续生成报告
                    
                except TimeoutError:
                    logger.error(f"分析操作超时（{args.timeout}秒）")
                    return
                except Exception as e:
                    logger.error(f"分析过程中出错: {str(e)}")
                    return
        
        # 如果提供了已有的分析结果文件，加载它
        elif args.analysis_result:
            try:
                with open(args.analysis_result, 'r', encoding='utf-8') as f:
                    combined_results = json.load(f)
                logger.info(f"已加载分析结果: {args.analysis_result}")
            except Exception as e:
                logger.error(f"加载分析结果文件时出错: {str(e)}")
                return
        
        # 如果没有分析结果，使用示例数据
        if not combined_results:
            logger.warning("没有分析结果，使用示例数据")
            combined_results = {
                "structure_analysis": {
                    "file_path": config['analysis']['excel_file'],
                    "row_count": 1440,
                    "column_count": 10,
                    "columns": {
                        "时间戳": {"type": "datetime", "sample": "2025-03-01 00:00:00"},
                        "基站名称": {"type": "string", "sample": "城东-商业区基站"},
                        "信令类型": {"type": "string", "sample": "注册请求"},
                        "状态码": {"type": "integer", "sample": 200},
                        "延迟时间(ms)": {"type": "float", "sample": 45.2},
                        "吞吐量(Mbps)": {"type": "float", "sample": 120.5},
                        "资源块使用率(%)": {"type": "float", "sample": 56.3},
                        "CPU使用率(%)": {"type": "float", "sample": 55.8},
                        "内存使用率(%)": {"type": "float", "sample": 56.2},
                        "活跃用户数": {"type": "integer", "sample": 1250}
                    }
                },
                "unit_results": {
                    "总体数据统计分析单元": {
                        "status": "success",
                        "result": "基站数据总体统计分析完成，共分析1440条记录，5个基站的数据。"
                    },
                    "时间序列分析单元": {
                        "status": "success",
                        "result": "时间序列分析显示资源使用率在12:00-14:00达到峰值。"
                    },
                    "分类数据分析单元": {
                        "status": "success",
                        "result": "分类数据分析显示市中心商业区基站的错误率最高，达到25%。"
                    }
                }
            }
        
        # 生成Markdown报告
        logger.info("生成Markdown报告...")
        markdown_report, md_file_path = md_report_generator.generate_markdown_report(combined_results)
        
        if not markdown_report or not md_file_path:
            logger.error("生成Markdown报告失败")
            return
        
        # 渲染Markdown为HTML
        logger.info("渲染Markdown为HTML...")
        renderer = MarkdownToHtmlRenderer(theme=args.theme)
        
        # 生成HTML文件名
        timestamp = Path(md_file_path).stem.split('_')[-1]
        html_file = f"reports/markdown_report_{timestamp}.html"
        
        # 渲染为HTML
        html_file_path = renderer.render_file(
            md_file_path, 
            output_file=html_file,
            title=f"数据分析报告 - {Path(config['analysis']['excel_file']).stem}"
        )
        
        if html_file_path:
            logger.info(f"已将Markdown报告渲染为HTML: {html_file_path}")
            
            # 尝试自动打开HTML文件
            try:
                webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
                logger.info("已自动打开HTML报告")
                print("已自动打开HTML报告")
            except Exception as e:
                logger.error(f"无法自动打开HTML报告: {str(e)}")
        
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()
