#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown报告生成器 - 负责生成Markdown格式的数据分析报告
支持使用Mermaid.js语法生成图表
"""

import os
import logging
import json
import time
from datetime import datetime
import re
import mistune  # 用于验证Markdown格式
import numpy as np

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

class MarkdownReportGenerator:
    """
    Markdown报告生成器类，负责生成Markdown格式的数据分析报告
    """
    
    def __init__(self, model, config):
        """
        初始化Markdown报告生成器
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        
        # 确保临时目录存在
        os.makedirs('temp_txts', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # 初始化Markdown解析器（用于验证）
        self.markdown_parser = mistune.create_markdown()
    
    def generate_markdown_report(self, analysis_results):
        """
        生成Markdown格式的数据分析报告
        
        Args:
            analysis_results (dict): 分析结果
            
        Returns:
            tuple: (markdown_content, file_path)
        """
        logger.info("开始生成Markdown报告...")
        
        try:
            # 提取结构分析和单元结果
            structure_analysis = analysis_results.get("structure_analysis", {})
            unit_results = analysis_results.get("unit_results", {})
            
            # 准备提示信息
            prompt = self._prepare_report_prompt(structure_analysis, unit_results)
            
            # 调用模型生成Markdown报告（流式输出）
            logger.info("调用模型生成Markdown报告（流式输出）...")
            print("\n开始生成Markdown报告...\n")
            print("\n正在生成Markdown报告（流式输出）...\n")
            
            markdown_content = ""
            
            # 使用流式API调用
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    print(chunk, end="", flush=True)
                    markdown_content += chunk
            
            print("\n\n报告内容接收完成，正在处理...\n\n")
            
            # 提取和验证Markdown内容
            markdown_content = self._extract_and_validate_markdown(markdown_content)
            
            if not markdown_content:
                logger.error("无法提取有效的Markdown内容")
                return None, None
            
            # 保存Markdown报告
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            report_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(report_dir, exist_ok=True)
            
            file_path = os.path.join(report_dir, f"markdown_report_{timestamp}.md")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            logger.info(f"已将Markdown报告保存到: {file_path}")
            print("\n\nMarkdown报告生成完成\n")
            
            return markdown_content, file_path
            
        except Exception as e:
            logger.error(f"生成Markdown报告时出错: {str(e)}")
            return None, None

    def _prepare_report_prompt(self, structure_analysis, unit_results):
        """
        准备生成报告的提示信息
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            unit_results (dict): 分析单元结果
            
        Returns:
            str: 提示信息
        """
        # 提取文件路径和列信息
        file_path = structure_analysis.get("file_path", "未知文件")
        columns_info = structure_analysis.get("columns", {})
        
        # 将分析单元结果转换为简化格式
        simplified_results = {}
        for unit_name, result in unit_results.items():
            if result.get("status") == "success":
                simplified_results[unit_name] = result.get("results", "")
        
        # 构建提示信息
        prompt = f"""
你是一位专业的数据分析师，请根据以下分析结果生成一份详细的Markdown格式数据分析报告。

# 分析数据信息
- 文件: {os.path.basename(file_path)}
- 行数: {structure_analysis.get('row_count', '未知')}
- 列数: {structure_analysis.get('column_count', '未知')}

## 列信息
{json.dumps(columns_info, indent=2, ensure_ascii=False, cls=NumpyEncoder)}

## 分析单元结果
{json.dumps(simplified_results, indent=2, ensure_ascii=False, cls=NumpyEncoder)}

请生成一份包含以下部分的Markdown格式报告:

1. 概览：简要介绍数据集，包括数据量、主要字段等基本信息。
2. 数据洞察：展示关键的数据统计和发现，包括均值、中位数、最大/最小值等。
3. 关键发现：列出分析过程中发现的重要模式、异常和趋势。
4. 总结：总结主要发现并提供建议。

要求：
1. 使用标准Markdown格式，包括标题、列表、表格等。
2. 可以使用Mermaid.js语法创建图表（如柱状图、饼图、折线图等）。
3. 报告应该专业、简洁、易于理解。
4. 确保所有数据分析结果都有明确的解释。
5. 使用中文编写报告。

请直接输出Markdown内容，不要添加额外的解释或前言。
"""
        return prompt
    
    def _extract_and_validate_markdown(self, content):
        """
        从模型响应中提取Markdown内容并验证格式
        
        Args:
            content (str): 模型响应内容
            
        Returns:
            str: 提取的Markdown内容，如果提取失败则返回None
        """
        if not content:
            logger.error("模型返回的内容为空")
            return None
        
        # 尝试直接使用内容（如果已经是Markdown格式）
        try:
            # 使用mistune验证Markdown格式
            mistune.create_markdown()(content)
            return content
        except Exception as e:
            logger.warning(f"直接验证Markdown失败: {str(e)}")
        
        # 尝试从内容中提取Markdown代码块
        markdown_blocks = re.findall(r'```markdown\s*([\s\S]*?)\s*```', content)
        if markdown_blocks:
            markdown_content = markdown_blocks[0].strip()
            try:
                # 验证提取的Markdown内容
                mistune.create_markdown()(markdown_content)
                return markdown_content
            except Exception as e:
                logger.warning(f"验证提取的Markdown代码块失败: {str(e)}")
        
        # 如果没有找到Markdown代码块，尝试查找其他代码块
        code_blocks = re.findall(r'```(?:md)?\s*([\s\S]*?)\s*```', content)
        if code_blocks:
            markdown_content = code_blocks[0].strip()
            try:
                # 验证提取的代码块内容
                mistune.create_markdown()(markdown_content)
                return markdown_content
            except Exception as e:
                logger.warning(f"验证提取的代码块失败: {str(e)}")
        
        # 如果以上方法都失败，尝试直接使用整个内容
        logger.warning("无法找到Markdown代码块，尝试使用整个内容")
        return content
    
    def _validate_markdown(self, content):
        """
        验证Markdown内容是否有效
        
        Args:
            content (str): 要验证的Markdown内容
        
        Returns:
            bool: 是否有效
        """
        try:
            # 使用mistune解析Markdown内容
            self.markdown_parser(content)
            
            # 检查是否包含基本的Markdown元素
            has_headers = bool(re.search(r'^#{1,6}\s+.+', content, re.MULTILINE))
            
            # 如果没有标题，可能不是有效的Markdown报告
            if not has_headers:
                logger.warning("Markdown内容缺少标题元素")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证Markdown内容时出错: {str(e)}")
            return False
