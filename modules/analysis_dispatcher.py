#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分析调度器 - 负责协调和执行所有分析单元
"""

import os
import logging
import json
import time
import numpy as np
from datetime import datetime

from .analysis_units import (
    GeneralStatisticsUnit,
    BarChartAnalysisUnit,
    PieChartAnalysisUnit,
    TimeTrendAnalysisUnit,
    CorrelationAnalysisUnit
)

logger = logging.getLogger(__name__)

# 自定义JSON编码器，处理NumPy类型
class NumpyEncoder(json.JSONEncoder):
    """处理NumPy类型的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

class AnalysisDispatcher:
    """
    分析调度器类，负责协调和执行所有分析单元
    """
    
    def __init__(self, model, config):
        """
        初始化分析调度器
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        self.analysis_units = []
        self.results_dir = os.path.join(os.getcwd(), 'analysis_results')
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 创建临时文本文件目录
        self.temp_txts_dir = os.path.join(os.getcwd(), 'temp_txts')
        os.makedirs(self.temp_txts_dir, exist_ok=True)
        
        # 初始化所有分析单元
        self._initialize_analysis_units()
        
        # 初始化大模型报告生成器
        from modules.enhanced_markdown_report_generator import EnhancedMarkdownReportGenerator
        self.report_generator = EnhancedMarkdownReportGenerator(model, config)
    
    def _initialize_analysis_units(self):
        """
        初始化所有分析单元
        """
        logger.info("初始化分析单元...")
        
        # 获取分析单元配置
        analysis_units_config = self.config.get('analysis', {}).get('analysis_units', {})
        
        # 创建分析单元实例，根据配置决定是否添加
        self.analysis_units = []
        
        # 通用统计分析单元
        if analysis_units_config.get('general_statistics', True):
            self.analysis_units.append(GeneralStatisticsUnit(self.model, self.config))
            logger.info("已启用通用统计分析单元")
        
        # 柱状图分析单元
        if analysis_units_config.get('bar_chart', True):
            self.analysis_units.append(BarChartAnalysisUnit(self.model, self.config))
            logger.info("已启用柱状图分析单元")
        
        # 饼图分析单元
        if analysis_units_config.get('pie_chart', True):
            self.analysis_units.append(PieChartAnalysisUnit(self.model, self.config))
            logger.info("已启用饼图分析单元")
        
        # 时间趋势分析单元
        if analysis_units_config.get('time_trend', True):
            self.analysis_units.append(TimeTrendAnalysisUnit(self.model, self.config))
            logger.info("已启用时间趋势分析单元")
        
        # 相关性分析单元
        if analysis_units_config.get('correlation', True):
            self.analysis_units.append(CorrelationAnalysisUnit(self.model, self.config))
            logger.info("已启用相关性分析单元")
        
        logger.info(f"成功初始化 {len(self.analysis_units)} 个分析单元")
    
    def run_analysis(self, structure_analysis, column_names, file_path):
        """
        运行所有分析单元
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            file_path (str): 数据文件路径
            
        Returns:
            dict: 所有分析单元的结果
        """
        logger.info("开始运行分析调度器...")
        
        # 创建结果目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_session_dir = os.path.join(self.results_dir, f"analysis_session_{timestamp}")
        os.makedirs(analysis_session_dir, exist_ok=True)
        
        # 创建图表目录
        pngs_dir = os.path.join(analysis_session_dir, "pngs")
        os.makedirs(pngs_dir, exist_ok=True)
        
        # 保存结构分析和列名信息
        with open(os.path.join(analysis_session_dir, "structure_analysis.json"), "w", encoding="utf-8") as f:
            json.dump(structure_analysis, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        with open(os.path.join(analysis_session_dir, "column_names.json"), "w", encoding="utf-8") as f:
            json.dump(column_names, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        # 初始化结果字典和上下文字典
        results = {}
        data_context = {}
        
        # 记录成功执行的分析单元数量
        successful_units = 0
        
        # 依次执行每个分析单元
        for i, unit in enumerate(self.analysis_units):
            unit_name = unit.unit_name
            logger.info(f"执行分析单元 {i+1}/{len(self.analysis_units)}: {unit_name}")
            
            try:
                # 生成分析代码
                analysis_code = unit.generate_analysis_code(structure_analysis, column_names, file_path, data_context)
                
                if not analysis_code:
                    logger.error(f"分析单元 {unit_name} 生成代码失败，跳过此单元")
                    results[unit_name] = {
                        "status": "failed",
                        "error": "生成代码失败",
                        "code": None,
                        "results": None
                    }
                    continue
                
                # 执行分析代码
                success, final_code, execution_result = unit.execute_code(analysis_code, file_path)
                
                if not success:
                    logger.error(f"分析单元 {unit_name} 执行代码失败: {execution_result}")
                    results[unit_name] = {
                        "status": "failed",
                        "error": execution_result,
                        "code": final_code,
                        "results": None
                    }
                    continue
                
                # 保存成功执行的代码
                code_file = os.path.join(analysis_session_dir, f"{i+1}_{unit_name.replace(' ', '_')}_code.py")
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(final_code)
                
                # 保存执行结果
                result_file = os.path.join(analysis_session_dir, f"{i+1}_{unit_name.replace(' ', '_')}_result.txt")
                with open(result_file, "w", encoding="utf-8") as f:
                    f.write(execution_result)
                
                # 保存分析结论到临时文本文件
                temp_txt_file = os.path.join(self.temp_txts_dir, f"{i+1}_{unit_name.replace(' ', '_')}_conclusion.txt")
                with open(temp_txt_file, "w", encoding="utf-8") as f:
                    f.write(f"# {unit_name} 分析结论\n\n")
                    f.write(execution_result)
                logger.info(f"已将分析结论保存到临时文件: {temp_txt_file}")
                
                # 为每个分析单元生成独立的Markdown报告
                # 构建提示词
                unit_prompt = f"""请基于以下分析结果，生成一份详细的Markdown格式分析报告。

## 分析单元
{unit_name}

## 分析结论
{execution_result}
"""
                
                # 添加文本结果（如果有）
                txt_results = None
                expected_txt_files = [
                    "analysis_results.txt",
                    "group_comparison_results.txt",
                    "category_distribution_results.txt",
                    "time_trend_results.txt",
                    "correlation_results.txt"
                ]
                
                if i < len(expected_txt_files):
                    txt_file = expected_txt_files[i]
                    txt_file_path = os.path.join("pngs", txt_file)
                    if os.path.exists(txt_file_path):
                        try:
                            with open(txt_file_path, "r", encoding="utf-8") as f:
                                txt_results = f.read()
                            
                            # 将文本结果复制到会话目录
                            with open(os.path.join(analysis_session_dir, txt_file), "w", encoding="utf-8") as f:
                                f.write(txt_results)
                                
                            # 添加到提示词中
                            unit_prompt += f"\n\n## 详细分析\n{txt_results}"
                        except Exception as e:
                            logger.warning(f"无法加载文本结果文件 {txt_file}: {str(e)}")
                
                # 添加报告要求
                unit_prompt += """

## 报告要求
请生成一份专业的Markdown格式分析报告，包含以下部分：
1. 数据概览（包含数据表格）
2. 数据洞察（包含数据表格）
3. 关键发现（包含数据表格）
4. 总结

请确保报告内容全面、准确，并且格式规范。"""
                
                # 使用大模型生成Markdown报告
                logger.info(f"开始使用大模型为分析单元 {unit_name} 生成Markdown报告...")
                try:
                    # 调用enhanced_markdown_report_generator生成报告
                    unit_report_content = self.report_generator._generate_report_with_model(unit_prompt)
                    
                    if not unit_report_content:
                        logger.warning(f"大模型未能生成分析单元 {unit_name} 的报告，将使用默认格式")
                        # 使用默认格式
                        unit_report_content = f"# {unit_name} 分析报告\n\n"
                        unit_report_content += f"## 分析结论\n\n{execution_result}\n\n"
                        if txt_results:
                            unit_report_content += f"## 详细分析\n\n{txt_results}\n\n"
                except Exception as e:
                    logger.error(f"使用大模型生成分析单元 {unit_name} 的报告时出错: {str(e)}")
                    # 使用默认格式
                    unit_report_content = f"# {unit_name} 分析报告\n\n"
                    unit_report_content += f"## 分析结论\n\n{execution_result}\n\n"
                    if txt_results:
                        unit_report_content += f"## 详细分析\n\n{txt_results}\n\n"
                
                # 保存单元报告到文件
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unit_type_name = unit_name.replace("单元", "").strip().replace(" ", "_").lower()
                unit_report_file = os.path.join("reports", f"{unit_type_name}_{timestamp}.md")
                os.makedirs(os.path.dirname(unit_report_file), exist_ok=True)
                with open(unit_report_file, "w", encoding="utf-8") as f:
                    f.write(unit_report_content)
                logger.info(f"已为分析单元 {unit_name} 生成独立的Markdown报告: {unit_report_file}")
                
                # 更新结果和上下文
                results[unit_name] = {
                    "status": "success",
                    "error": None,
                    "code": final_code,
                    "results": execution_result,
                    "txt_results": txt_results,
                    "report_file": unit_report_file
                }
                
                # 更新数据上下文，用于后续分析单元
                unit_key = unit_name.replace("单元", "").strip()
                data_context[unit_key] = txt_results if txt_results else execution_result
                
                logger.info(f"分析单元 {unit_name} 执行成功")
                successful_units += 1
                
            except Exception as e:
                logger.error(f"分析单元 {unit_name} 执行过程中出错: {str(e)}")
                results[unit_name] = {
                    "status": "error",
                    "error": str(e),
                    "code": None,
                    "results": None
                }
        
        # 保存所有结果到一个汇总文件
        summary_file = os.path.join(analysis_session_dir, "analysis_summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "structure_analysis": structure_analysis,
                "column_names": column_names,
                "results": results
            }, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        
        # 检查是否有成功执行的分析单元
        if successful_units == 0:
            logger.error("所有分析单元执行失败，无法继续流程")
            return results
        
        logger.info(f"分析调度器执行完成，结果已保存到: {analysis_session_dir}")
        logger.info(f"成功执行的分析单元: {successful_units}/{len(self.analysis_units)}")
        
        return results
    
    def get_combined_results(self, results):
        """
        获取所有分析单元的组合结果，用于生成报告
        
        Args:
            results (dict): 所有分析单元的结果
            
        Returns:
            str: 组合结果的文本表示
        """
        combined_results = []
        
        for unit_name, result in results.items():
            combined_results.append(f"## {unit_name} 分析结果")
            
            if result["status"] == "success":
                if result["txt_results"]:
                    combined_results.append(result["txt_results"])
                else:
                    combined_results.append(result["results"])
            else:
                combined_results.append(f"分析失败: {result['error']}")
            
            combined_results.append("\n")
        
        return "\n".join(combined_results)
