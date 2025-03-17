#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel分析器 - 负责分析Excel文件并生成报告
使用分析调度器来协调多个分析单元
"""

import os
import logging
import pandas as pd
import time
from datetime import datetime

from .code_generator import CodeGenerator
from .enhanced_markdown_report_generator import EnhancedMarkdownReportGenerator
from .analysis_dispatcher import AnalysisDispatcher

logger = logging.getLogger(__name__)

class ExcelAnalyzer:
    """
    Excel分析器类，负责分析Excel文件并生成报告
    现在使用分析调度器来协调多个分析单元
    """
    
    def __init__(self, model, config):
        """
        初始化Excel分析器
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        
        # 创建代码生成器和增强的Markdown报告生成器
        self.code_generator = CodeGenerator(model, config)
        self.report_generator = EnhancedMarkdownReportGenerator(model, config)
        
        # 直接创建分析调度器
        self.dispatcher = AnalysisDispatcher(model, config)
        
        # 确保临时目录存在
        os.makedirs('temp_csv', exist_ok=True)
    
    def analyze_excel(self, file_path):
        """
        分析Excel文件并生成报告
        
        Args:
            file_path (str): Excel文件路径
        
        Returns:
            tuple: (Markdown报告内容, HTML报告内容)
        """
        logger.info(f"开始分析Excel文件: {file_path}")
        
        try:
            # 将Excel转换为CSV以便处理
            csv_path = self._convert_excel_to_csv(file_path)
            if not csv_path:
                logger.error("转换Excel为CSV失败")
                return "转换Excel为CSV失败，请检查文件格式是否正确", None
            
            # 获取数据结构分析和列名
            structure_analysis, column_names = self._analyze_structure(csv_path)
            if not structure_analysis or not column_names:
                logger.error("分析数据结构失败")
                return "分析数据结构失败，请检查文件内容是否有效", None
            
            # 使用分析调度器直接运行所有分析单元
            logger.info("使用分析调度器运行所有分析单元...")
            analysis_results = self.dispatcher.run_analysis(structure_analysis, column_names, csv_path)
            
            # 检查是否至少有一个分析单元成功执行
            success = any(result["status"] == "success" for result in analysis_results.values())
            
            if not success:
                logger.error("所有分析单元执行失败")
                return "分析过程中出错，所有分析单元执行失败", None
            
            # 获取组合结果
            combined_results = self.dispatcher.get_combined_results(analysis_results)
            
            # 获取最新的分析会话目录
            analysis_dirs = [d for d in os.listdir(os.path.join(os.getcwd(), 'analysis_results')) 
                            if d.startswith('analysis_session_')]
            if analysis_dirs:
                latest_dir = sorted(analysis_dirs)[-1]
                analysis_session_dir = os.path.join(os.getcwd(), 'analysis_results', latest_dir)
                pngs_dir = os.path.join(analysis_session_dir, 'pngs')
            else:
                analysis_session_dir = None
                pngs_dir = None
            
            # 生成Markdown报告
            logger.info("生成Markdown报告...")
            markdown_report = self.report_generator.generate_markdown_report(combined_results, pngs_dir)
            
            if markdown_report is None:
                logger.error("生成Markdown报告失败")
                return "生成Markdown报告失败，请检查分析结果是否有效", None
            
            # 保存Markdown报告
            report_timestamp = time.strftime('%Y%m%d_%H%M%S')
            markdown_file = f"reports/excel_analysis_report_{report_timestamp}.md"
            os.makedirs(os.path.dirname(markdown_file), exist_ok=True)
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            # 将Markdown转换为HTML
            html_file = f"reports/html_report_{report_timestamp}.html"
            html_report = self.report_generator.render_markdown_to_html(
                markdown_report, 
                output_file=html_file, 
                title="Excel数据分析报告"
            )
            
            # 处理每个分析单元的独立报告
            unit_html_reports = []
            unit_md_files = []
            for unit_name, unit_result in analysis_results.items():
                if unit_result.get("status") == "success" and unit_result.get("report_file"):
                    unit_md_file = unit_result["report_file"]
                    if os.path.exists(unit_md_file):
                        # 保存Markdown文件路径
                        unit_md_files.append(unit_md_file)
                        
                        # 生成HTML文件名
                        unit_html_file = unit_md_file.replace(".md", ".html")
                        
                        # 读取Markdown内容
                        with open(unit_md_file, 'r', encoding='utf-8') as f:
                            unit_md_content = f.read()
                        
                        # 转换为HTML
                        unit_title = unit_name.replace("单元", "").strip() + "分析报告"
                        unit_html_report = self.report_generator.render_markdown_to_html(
                            unit_md_content,
                            output_file=unit_html_file,
                            title=unit_title
                        )
                        
                        if unit_html_report:
                            unit_html_reports.append(unit_html_file)
                            logger.info(f"已将分析单元 {unit_name} 的Markdown报告转换为HTML: {unit_html_file}")
            
            # 尝试自动打开HTML报告
            if html_report:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(html_file)}")
                    logger.info(f"已自动打开HTML报告: {html_file}")
                    # 添加输出信息
                    print(f"HTML图表报告已保存到: {html_file}")
                except Exception as e:
                    logger.warning(f"无法自动打开HTML报告: {str(e)}")
            
            # 尝试自动打开每个分析单元的HTML报告
            for unit_html_file in unit_html_reports:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(unit_html_file)}")
                    logger.info(f"已自动打开分析单元HTML报告: {unit_html_file}")
                    print(f"分析单元HTML报告已保存到: {unit_html_file}")
                except Exception as e:
                    logger.warning(f"无法自动打开分析单元HTML报告: {str(e)}")
            
            # 如果有多个分析单元报告，生成综合报告
            if len(unit_md_files) > 1:
                logger.info("开始生成综合分析报告...")
                comprehensive_md, comprehensive_html = self.generate_comprehensive_report(unit_md_files)
                if comprehensive_html:
                    logger.info(f"综合分析报告已生成: {comprehensive_html}")
                    print(f"综合分析报告已生成: {comprehensive_html}")
            
            return markdown_report, html_report
            
        except Exception as e:
            logger.error(f"分析Excel文件时出错: {str(e)}")
            return f"分析Excel文件时出错: {str(e)}", None
    
    def _convert_excel_to_csv(self, excel_path):
        """
        将Excel文件转换为CSV文件
        
        Args:
            excel_path (str): Excel文件路径
        
        Returns:
            str: CSV文件路径，如果转换失败则返回None
        """
        logger.info(f"将Excel文件转换为CSV: {excel_path}")
        
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            
            # 保存为CSV
            csv_path = f"temp_csv/excel_data_{time.strftime('%Y%m%d%H%M%S')}.csv"
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"已将Excel转换为CSV: {csv_path}")
            
            return csv_path
            
        except Exception as e:
            logger.error(f"转换Excel为CSV时出错: {str(e)}")
            return None
            
    def generate_comprehensive_report(self, unit_reports):
        """
        将每个分析单元的独立结果输入到大模型，生成一份总体分析的Markdown报告
        
        Args:
            unit_reports (list): 分析单元报告文件路径列表
            
        Returns:
            tuple: (markdown_report, html_report)
        """
        logger.info("开始生成综合分析报告...")
        
        try:
            # 构建提示词，包含所有分析单元的结果
            prompt = """请基于以下各个分析单元的独立结果，生成一份全面的综合分析报告。
            
## 各分析单元结果
"""
            # 读取每个分析单元的报告内容
            for unit_report in unit_reports:
                if os.path.exists(unit_report):
                    # 从文件名提取单元名称
                    unit_name = os.path.basename(unit_report).split('_')[0]
                    unit_name = unit_name.replace('_', ' ').title()
                    
                    # 读取报告内容
                    with open(unit_report, 'r', encoding='utf-8') as f:
                        unit_content = f.read()
                    
                    # 添加到提示词中
                    prompt += f"\n### {unit_name} 分析结果\n"
                    prompt += f"{unit_content}\n\n"
            
            prompt += """
## 报告要求
请生成一份综合性的Markdown格式分析报告，将各个分析单元的结果整合为一个连贯的整体。报告应包含以下部分：

1. 数据概览（包含数据表格）
2. 数据洞察（包含数据表格）
3. 关键发现（包含数据表格）
4. 总结与建议

请确保报告内容全面、准确，并且格式规范。重点关注不同分析单元之间的关联性和整体趋势。
"""
            
            # 生成综合报告
            logger.info("开始流式生成综合Markdown报告...")
            comprehensive_report = self.report_generator._generate_report_with_model(prompt)
            
            if comprehensive_report is None:
                logger.error("生成综合Markdown报告失败")
                return "生成综合Markdown报告失败，请检查分析结果是否有效", None
            
            # 保存综合Markdown报告
            report_timestamp = time.strftime('%Y%m%d_%H%M%S')
            markdown_file = f"reports/comprehensive_report_{report_timestamp}.md"
            os.makedirs(os.path.dirname(markdown_file), exist_ok=True)
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(comprehensive_report)
            
            # 将Markdown转换为HTML
            html_file = f"reports/comprehensive_html_report_{report_timestamp}.html"
            html_report = self.report_generator.render_markdown_to_html(
                comprehensive_report, 
                output_file=html_file, 
                title="综合数据分析报告"
            )
            
            # 尝试自动打开HTML报告
            if html_report:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(html_file)}")
                    logger.info(f"已自动打开综合HTML报告: {html_file}")
                    # 添加输出信息
                    print(f"综合HTML报告已保存到: {html_file}")
                except Exception as e:
                    logger.warning(f"无法自动打开综合HTML报告: {str(e)}")
            
            return comprehensive_report, html_report
            
        except Exception as e:
            logger.error(f"生成综合报告时出错: {str(e)}")
            return f"生成综合报告时出错: {str(e)}", None
    
    def _analyze_structure(self, csv_path):
        """
        分析CSV文件的数据结构
        
        Args:
            csv_path (str): CSV文件路径
        
        Returns:
            tuple: (数据结构分析结果, 列名列表)，如果分析失败则返回(None, None)
        """
        logger.info(f"分析CSV文件结构: {csv_path}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            
            # 获取列名
            column_names = df.columns.tolist()
            
            # 创建结构分析
            structure_analysis = {
                "file_path": csv_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": {}
            }
            
            # 分析每一列
            for col in df.columns:
                col_type = str(df[col].dtype)
                structure_analysis["columns"][col] = {
                    "type": col_type,
                    "missing_values": df[col].isna().sum(),
                    "unique_values": df[col].nunique()
                }
                
                # 对于数值型列，计算基本统计信息
                if df[col].dtype.kind in 'ifc':  # 整数、浮点数或复数
                    structure_analysis["columns"][col].update({
                        "min": df[col].min() if not df[col].isna().all() else None,
                        "max": df[col].max() if not df[col].isna().all() else None,
                        "mean": df[col].mean() if not df[col].isna().all() else None,
                        "median": df[col].median() if not df[col].isna().all() else None
                    })
                
                # 对于分类型或字符串列，计算最常见的值
                elif df[col].dtype == 'object' or df[col].dtype.name == 'category':
                    if not df[col].isna().all():
                        value_counts = df[col].value_counts(dropna=True)
                        if not value_counts.empty:
                            structure_analysis["columns"][col]["most_common"] = {
                                "value": value_counts.index[0],
                                "count": int(value_counts.iloc[0])
                            }
            
            logger.info("成功分析CSV文件结构")
            
            return structure_analysis, column_names
            
        except Exception as e:
            logger.error(f"分析CSV文件结构时出错: {str(e)}")
            return None, None

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试Excel分析器
    print("请在主程序中测试Excel分析器")
