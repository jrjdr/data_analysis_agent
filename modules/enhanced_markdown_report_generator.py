#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强型Markdown报告生成器 - 支持文本、表格和图表
"""

import os
import re
import json
import logging
import mistune
from pathlib import Path
from datetime import datetime
import numpy as np
from .chart_generator import ChartGenerator

logger = logging.getLogger(__name__)

class NumpyEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，处理NumPy数据类型
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

class EnhancedMarkdownReportGenerator:
    """
    增强型Markdown报告生成器，支持文本、表格和图表
    """
    
    def __init__(self, model_connector, config):
        """
        初始化增强型Markdown报告生成器
        
        Args:
            model_connector: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model_connector
        self.config = config
        self.reports_dir = Path(config.get('reports_dir', 'reports'))
        
        # 确保报告目录存在
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 初始化图表生成器
        self.chart_generator = ChartGenerator(model_connector, config)
        
        # 初始化Markdown解析器
        self.markdown_parser = mistune.create_markdown()
    
    def generate_report(self, analysis_results, file_info, structure_analysis):
        """
        生成增强型Markdown报告
        
        Args:
            analysis_results (dict): 分析结果
            file_info (dict): 文件信息
            structure_analysis (dict): 结构分析结果
            
        Returns:
            tuple: (markdown_path, html_path) 生成的Markdown和HTML文件路径
        """
        logger.info("开始生成增强型Markdown报告...")
        
        try:
            # 准备报告生成的提示词
            prompt = self._build_report_prompt(analysis_results, file_info, structure_analysis)
            
            # 流式生成Markdown报告
            markdown_content = self._generate_markdown_with_stream(prompt)
            
            # 验证并提取Markdown内容
            valid_markdown = self._extract_and_validate_markdown(markdown_content)
            
            if not valid_markdown:
                logger.error("无法提取有效的Markdown内容")
                return None, None
            
            # 增强Markdown内容，添加图表
            enhanced_markdown = self._enhance_with_charts(valid_markdown, analysis_results)
            
            # 保存Markdown文件
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            markdown_filename = f"markdown_report_{timestamp}.md"
            markdown_path = self.reports_dir / markdown_filename
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_markdown)
            
            logger.info(f"已将Markdown报告保存到: {markdown_path}")
            
            # 将Markdown渲染为HTML
            html_path = self._render_to_html(markdown_path)
            
            return str(markdown_path), str(html_path)
            
        except Exception as e:
            logger.error(f"生成增强型Markdown报告时出错: {str(e)}")
            return None, None
    
    def _build_report_prompt(self, analysis_results, file_info, structure_analysis):
        """
        构建报告生成的提示词
        
        Args:
            analysis_results (dict): 分析结果
            file_info (dict): 文件信息
            structure_analysis (dict): 结构分析结果
            
        Returns:
            str: 构建的提示词
        """
        # 将分析结果转换为JSON字符串
        try:
            results_json = json.dumps(analysis_results, ensure_ascii=False, indent=2, cls=NumpyEncoder)
        except Exception as e:
            logger.error(f"序列化分析结果时出错: {str(e)}")
            results_json = str(analysis_results)
        
        # 文件信息
        file_name = file_info.get('file_name', 'unknown')
        
        prompt = f"""
请根据以下数据分析结果，生成一份详细的Markdown格式报告。

文件信息:
- 文件名: {file_name}

分析结果:
```json
{results_json}
```

报告要求:
1. 使用Markdown格式，包含标题、子标题、列表、表格等元素
2. 报告应包含以下部分：
   - 概览：简要介绍数据集和分析目标
   - 数据洞察：展示主要的数据发现和统计信息
   - 关键发现：突出显示重要的分析结果和模式
   - 总结与建议：基于分析结果提供的建议和下一步行动
3. 对于数值数据，使用Markdown表格展示
4. 对于分类数据，使用列表或表格展示
5. 使用Mermaid.js语法创建简单的图表（如饼图、柱状图等）
6. 报告应该专业、简洁，并突出关键信息
7. 使用适当的格式化（如粗体、斜体、引用等）增强可读性

请生成一份完整的Markdown报告，确保内容丰富、格式正确，并且可以直接转换为HTML。
"""
        return prompt
    
    def _generate_markdown_with_stream(self, prompt):
        """
        使用流式输出生成Markdown内容
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 生成的Markdown内容
        """
        logger.info("开始流式生成Markdown报告...")
        
        # 使用流式API调用模型
        full_response = ""
        print("\n开始生成Markdown报告...")
        
        try:
            for content in self.model.call_model_stream(prompt):
                # 直接使用返回的内容字符串
                if content:
                    print(content, end='', flush=True)
                    full_response += content
            
            print("\n\n报告内容接收完成，正在处理...")
            return full_response
            
        except Exception as e:
            logger.error(f"生成Markdown内容时出错: {str(e)}")
            return ""
    
    def _extract_and_validate_markdown(self, content):
        """
        提取并验证Markdown内容
        
        Args:
            content (str): 模型返回的内容
            
        Returns:
            str: 有效的Markdown内容
        """
        if not content:
            logger.warning("输入内容为空")
            return ""
            
        # 尝试多种提取方式
        extraction_methods = [
            # 方法1: 提取```markdown```代码块
            lambda text: re.search(r'```markdown\s*([\s\S]*?)\s*```', text),
            
            # 方法2: 提取任意```代码块
            lambda text: re.search(r'```\s*([\s\S]*?)\s*```', text),
            
            # 方法3: 假设整个内容都是Markdown
            lambda text: text
        ]
        
        for method in extraction_methods:
            try:
                result = method(content)
                
                # 如果是正则表达式匹配结果，提取匹配组
                if hasattr(result, 'group') and callable(getattr(result, 'group')):
                    markdown_content = result.group(1)
                else:
                    markdown_content = result
                
                # 验证Markdown内容
                if markdown_content and self._is_valid_markdown(markdown_content):
                    return markdown_content
            except Exception as e:
                logger.warning(f"Markdown提取方法失败: {str(e)}")
                continue
        
        # 如果所有方法都失败，返回原始内容（如果不为空）
        logger.warning("无法提取有效的Markdown，返回原始内容")
        return content if content else ""
    
    def _is_valid_markdown(self, content):
        """
        验证内容是否为有效的Markdown
        
        Args:
            content (str): 要验证的内容
            
        Returns:
            bool: 是否为有效的Markdown
        """
        if not content or not isinstance(content, str):
            return False
            
        try:
            # 尝试解析Markdown
            self.markdown_parser(content)
            
            # 检查是否包含基本的Markdown元素
            has_headers = bool(re.search(r'^#{1,6}\s+.+', content, re.MULTILINE))
            has_content = len(content.strip()) > 10  # 降低内容长度要求
            
            return has_content  # 只要有内容就认为有效，不强制要求标题
        except Exception as e:
            logger.warning(f"Markdown验证失败: {str(e)}")
            return False
    
    def _enhance_with_charts(self, markdown_content, analysis_results, pngs_dir=None):
        """
        使用图表增强Markdown内容
        
        Args:
            markdown_content (str): 原始Markdown内容
            analysis_results (dict): 分析结果
            pngs_dir (str, optional): 图表目录路径
            
        Returns:
            str: 增强后的Markdown内容
        """
        # 查找Markdown中的Mermaid图表定义
        mermaid_blocks = re.findall(r'```mermaid\s*([\s\S]*?)\s*```', markdown_content)
        
        enhanced_content = markdown_content
        
        # 为每个Mermaid图表生成静态图片
        for i, mermaid_code in enumerate(mermaid_blocks):
            try:
                # 提取图表类型和标题
                chart_type = re.search(r'(pie|bar|line|graph|flowchart)\s+title\s+(.*?)$', 
                                      mermaid_code, re.MULTILINE | re.IGNORECASE)
                
                if chart_type:
                    chart_type_str = chart_type.group(1).lower()
                    chart_title = chart_type.group(2).strip()
                else:
                    chart_type_str = None
                    chart_title = f"图表 {i+1}"
                
                # 准备相关数据
                chart_data = self._extract_data_for_chart(mermaid_code, analysis_results)
                
                # 生成静态图表
                chart_path = self.chart_generator.generate_chart(
                    chart_data, 
                    chart_type=chart_type_str,
                    title=chart_title,
                    pngs_dir=pngs_dir
                )
                
                if chart_path:
                    # 将相对路径转换为相对于报告的路径
                    rel_path = os.path.relpath(chart_path, self.reports_dir)
                    
                    # 在Mermaid代码块后添加图片引用
                    mermaid_pattern = f"```mermaid\\s*{re.escape(mermaid_code)}\\s*```"
                    replacement = f"```mermaid\n{mermaid_code}\n```\n\n![{chart_title}]({rel_path})\n"
                    
                    enhanced_content = re.sub(mermaid_pattern, replacement, enhanced_content)
            
            except Exception as e:
                logger.error(f"为Mermaid图表 {i+1} 生成静态图片时出错: {str(e)}")
        
        return enhanced_content
    
    def _extract_data_for_chart(self, mermaid_code, analysis_results):
        """
        从Mermaid代码和分析结果中提取图表数据
        
        Args:
            mermaid_code (str): Mermaid图表代码
            analysis_results (dict): 分析结果
            
        Returns:
            dict: 图表数据
        """
        # 提取图表类型
        chart_type_match = re.search(r'^(pie|bar|line|graph|flowchart)\s+', 
                                    mermaid_code, re.MULTILINE | re.IGNORECASE)
        chart_type = chart_type_match.group(1).lower() if chart_type_match else "unknown"
        
        # 根据图表类型提取数据
        if chart_type == "pie":
            # 提取饼图数据
            data_points = re.findall(r'"([^"]+)"\s*:\s*(\d+)', mermaid_code)
            data = {
                "type": "pie",
                "labels": [label for label, _ in data_points],
                "values": [int(value) for _, value in data_points]
            }
        
        elif chart_type == "bar":
            # 提取柱状图数据
            data_points = re.findall(r'"([^"]+)"\s*:\s*(\d+)', mermaid_code)
            data = {
                "type": "bar",
                "labels": [label for label, _ in data_points],
                "values": [int(value) for _, value in data_points]
            }
        
        else:
            # 对于其他类型，提供原始分析结果
            data = {
                "type": chart_type,
                "mermaid_code": mermaid_code,
                "analysis_results": analysis_results
            }
        
        return data
    
    def _render_to_html(self, markdown_path):
        """
        将Markdown文件渲染为HTML
        
        Args:
            markdown_path (Path): Markdown文件路径
            
        Returns:
            Path: 生成的HTML文件路径
        """
        logger.info(f"开始将Markdown文件 {markdown_path} 渲染为HTML...")
        
        try:
            import os
            
            # 如果没有指定输出文件，则使用时间戳生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"reports/html_report_{timestamp}.html"
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 简单的Markdown到HTML转换函数
            def simple_markdown_to_html(md_text):
                # 基本HTML头部
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel数据分析报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        p, ul, ol, table {{ margin-bottom: 16px; }}
        code {{
            font-family: Consolas, Monaco, 'Andale Mono', monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
            margin: 0 0 16px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        table tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
"""
                # 处理标题
                lines = md_text.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # 处理标题 (h1-h6)
                    if line.startswith('#'):
                        count = 0
                        for char in line:
                            if char == '#':
                                count += 1
                            else:
                                break
                        if count <= 6 and (len(line) <= count or line[count] == ' '):
                            title_text = line[count:].strip()
                            html += f"<h{count}>{title_text}</h{count}>\n"
                        else:
                            html += f"<p>{line}</p>\n"
                    
                    # 处理代码块
                    elif line.startswith('```'):
                        code_block = []
                        i += 1
                        while i < len(lines) and not lines[i].startswith('```'):
                            code_block.append(lines[i])
                            i += 1
                        code_content = '\n'.join(code_block)
                        html += f"<pre><code>{code_content}</code></pre>\n"
                    
                    # 处理列表
                    elif line.strip().startswith('- ') or line.strip().startswith('* '):
                        list_items = []
                        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                            item_text = lines[i].strip()[2:].strip()
                            list_items.append(f"<li>{item_text}</li>")
                            i += 1
                        i -= 1  # 回退一行，因为下一行不是列表项
                        html += "<ul>\n" + '\n'.join(list_items) + "\n</ul>\n"
                    
                    # 处理有序列表
                    elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
                        list_items = []
                        while i < len(lines) and lines[i].strip() and lines[i].strip()[0].isdigit() and '. ' in lines[i]:
                            item_text = lines[i].strip().split('. ', 1)[1].strip()
                            list_items.append(f"<li>{item_text}</li>")
                            i += 1
                        i -= 1  # 回退一行，因为下一行不是列表项
                        html += "<ol>\n" + '\n'.join(list_items) + "\n</ol>\n"
                    
                    # 处理表格
                    elif '|' in line:
                        table_rows = []
                        header_row = line
                        i += 1
                        if i < len(lines) and '---' in lines[i] and '|' in lines[i]:
                            # 这是表格的分隔行，跳过
                            i += 1
                            table_rows = []
                            # 处理表头
                            header_cells = [cell.strip() for cell in header_row.split('|')]
                            header_cells = [cell for cell in header_cells if cell]  # 移除空单元格
                            header_html = '<tr>' + ''.join([f'<th>{cell}</th>' for cell in header_cells]) + '</tr>'
                            table_rows.append(header_html)
                            
                            # 处理数据行
                            while i < len(lines) and '|' in lines[i]:
                                cells = [cell.strip() for cell in lines[i].split('|')]
                                cells = [cell for cell in cells if cell]  # 移除空单元格
                                row_html = '<tr>' + ''.join([f'<td>{cell}</td>' for cell in cells]) + '</tr>'
                                table_rows.append(row_html)
                                i += 1
                            i -= 1  # 回退一行，因为下一行不是表格行
                            html += "<table>\n" + '\n'.join(table_rows) + "\n</table>\n"
                        else:
                            # 不是表格，当作普通段落处理
                            html += f"<p>{line}</p>\n"
                    
                    # 处理普通段落
                    elif line.strip():
                        html += f"<p>{line}</p>\n"
                    
                    # 处理空行
                    else:
                        html += "<br>\n"
                    
                    i += 1
                
                # 添加HTML尾部
                html += """
</body>
</html>
"""
                return html
            
            # 读取Markdown内容
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 转换Markdown为HTML
            html_content = simple_markdown_to_html(markdown_content)
            
            # 保存HTML文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已将Markdown渲染为HTML并保存到: {output_file}")
            
            # 尝试自动打开HTML文件
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_file)}")
                logger.info(f"已自动打开HTML报告: {output_file}")
            except Exception as e:
                logger.warning(f"无法自动打开HTML报告: {str(e)}")
            
            return output_file
                
        except Exception as e:
            logger.error(f"渲染Markdown为HTML时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def generate_markdown_report(self, analysis_results, pngs_dir=None):
        """
        从分析结果生成Markdown报告
        
        Args:
            analysis_results (dict): 分析结果
            pngs_dir (str, optional): 图表目录路径
            
        Returns:
            str: 生成的Markdown内容
        """
        logger.info("从分析结果生成Markdown报告...")
        
        try:
            # 构建提示词，包含所有分析结果
            prompt = """请基于以下分析结果生成一份详细的Markdown格式分析报告。

## 分析结果数据
"""
            # 检查分析结果中是否有错误
            has_errors = self._has_analysis_errors(analysis_results)
            
            # 处理分析结果
            if isinstance(analysis_results, dict):
                # 如果是字典，按照单元处理
                for unit_name, result in analysis_results.items():
                    prompt += f"\n### {unit_name} 分析结果\n"
                    
                    if result["status"] == "success":
                        # 优先使用txt_results，如果存在
                        if result.get("txt_results"):
                            prompt += f"```\n{result['txt_results']}\n```\n"
                        # 其次使用普通结果
                        else:
                            prompt += f"```\n{result['results']}\n```\n"
                    else:
                        prompt += f"分析失败: {result['error']}\n"
            else:
                # 如果不是字典，直接使用整个结果
                prompt += f"\n### 分析结果\n```\n{analysis_results}\n```\n"
            
            prompt += """
## 报告要求
请生成一份专业的Markdown格式分析报告，包含以下部分：

1. 数据概览（包含数据表格）
2. 数据洞察（包含数据表格）
3. 关键发现（包含数据表格）
4. 总结

请确保报告内容全面、准确，并且格式规范。
"""
            
            # 如果有错误，添加错误处理指导
            if has_errors:
                prompt += "\n注意：部分分析单元执行失败，请在报告中注明哪些分析无法完成，并重点关注成功的分析结果。\n"
            
            logger.info("开始流式生成Markdown报告...")
            # 调用模型生成报告
            report_content = self._generate_report_with_model(prompt)
            
            # 如果有错误，添加错误信息
            if has_errors:
                report_content = self._add_error_information(report_content, analysis_results)
            
            return report_content
            
        except Exception as e:
            logger.error(f"生成Markdown报告时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"# 报告生成失败\n\n生成报告时发生错误: {str(e)}"
    
    def render_markdown_to_html(self, markdown_content, output_file=None, title=None):
        """
        将Markdown内容渲染为HTML并保存
        
        Args:
            markdown_content (str): Markdown内容
            output_file (str, optional): 输出HTML文件路径
            title (str, optional): HTML页面标题
            
        Returns:
            str: 生成的HTML文件路径
        """
        try:
            import os
            
            # 如果没有指定输出文件，则使用时间戳生成文件名
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = f"reports/html_report_{timestamp}.html"
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 如果没有指定标题，使用默认标题
            if not title:
                title = "Excel数据分析报告"
                
            # 简单的Markdown到HTML转换函数
            def simple_markdown_to_html(md_text):
                # 基本HTML头部
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        p, ul, ol, table {{ margin-bottom: 16px; }}
        code {{
            font-family: Consolas, Monaco, 'Andale Mono', monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 3px;
            padding: 16px;
            overflow: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
            margin: 0 0 16px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}
        table tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
"""
                # 处理标题
                lines = md_text.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i]
                    
                    # 处理标题 (h1-h6)
                    if line.startswith('#'):
                        count = 0
                        for char in line:
                            if char == '#':
                                count += 1
                            else:
                                break
                        if count <= 6 and (len(line) <= count or line[count] == ' '):
                            title_text = line[count:].strip()
                            html += f"<h{count}>{title_text}</h{count}>\n"
                        else:
                            html += f"<p>{line}</p>\n"
                    
                    # 处理代码块
                    elif line.startswith('```'):
                        code_block = []
                        i += 1
                        while i < len(lines) and not lines[i].startswith('```'):
                            code_block.append(lines[i])
                            i += 1
                        code_content = '\n'.join(code_block)
                        html += f"<pre><code>{code_content}</code></pre>\n"
                    
                    # 处理列表
                    elif line.strip().startswith('- ') or line.strip().startswith('* '):
                        list_items = []
                        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                            item_text = lines[i].strip()[2:].strip()
                            list_items.append(f"<li>{item_text}</li>")
                            i += 1
                        i -= 1  # 回退一行，因为下一行不是列表项
                        html += "<ul>\n" + '\n'.join(list_items) + "\n</ul>\n"
                    
                    # 处理有序列表
                    elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
                        list_items = []
                        while i < len(lines) and lines[i].strip() and lines[i].strip()[0].isdigit() and '. ' in lines[i]:
                            item_text = lines[i].strip().split('. ', 1)[1].strip()
                            list_items.append(f"<li>{item_text}</li>")
                            i += 1
                        i -= 1  # 回退一行，因为下一行不是列表项
                        html += "<ol>\n" + '\n'.join(list_items) + "\n</ol>\n"
                    
                    # 处理表格
                    elif '|' in line:
                        table_rows = []
                        header_row = line
                        i += 1
                        if i < len(lines) and '---' in lines[i] and '|' in lines[i]:
                            # 这是表格的分隔行，跳过
                            i += 1
                            table_rows = []
                            # 处理表头
                            header_cells = [cell.strip() for cell in header_row.split('|')]
                            header_cells = [cell for cell in header_cells if cell]  # 移除空单元格
                            header_html = '<tr>' + ''.join([f'<th>{cell}</th>' for cell in header_cells]) + '</tr>'
                            table_rows.append(header_html)
                            
                            # 处理数据行
                            while i < len(lines) and '|' in lines[i]:
                                cells = [cell.strip() for cell in lines[i].split('|')]
                                cells = [cell for cell in cells if cell]  # 移除空单元格
                                row_html = '<tr>' + ''.join([f'<td>{cell}</td>' for cell in cells]) + '</tr>'
                                table_rows.append(row_html)
                                i += 1
                            i -= 1  # 回退一行，因为下一行不是表格行
                            html += "<table>\n" + '\n'.join(table_rows) + "\n</table>\n"
                        else:
                            # 不是表格，当作普通段落处理
                            html += f"<p>{line}</p>\n"
                    
                    # 处理普通段落
                    elif line.strip():
                        html += f"<p>{line}</p>\n"
                    
                    # 处理空行
                    else:
                        html += "<br>\n"
                    
                    i += 1
                
                # 添加HTML尾部
                html += """
</body>
</html>
"""
                return html
            
            # 转换Markdown为HTML
            html_content = simple_markdown_to_html(markdown_content)
            
            # 保存HTML文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已将Markdown渲染为HTML并保存到: {output_file}")
            
            # 尝试自动打开HTML文件
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_file)}")
                logger.info(f"已自动打开HTML报告: {output_file}")
            except Exception as e:
                logger.warning(f"无法自动打开HTML报告: {str(e)}")
            
            return output_file
                
        except Exception as e:
            logger.error(f"渲染Markdown为HTML时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _has_analysis_errors(self, analysis_results):
        """
        检查分析结果中是否有错误
        
        Args:
            analysis_results (dict): 分析结果
            
        Returns:
            bool: 是否有错误
        """
        # 如果分析结果是字符串，无法检查错误
        if isinstance(analysis_results, str):
            return False
            
        # 如果分析结果为空或没有结论，认为没有错误
        if not analysis_results:
            return False
            
        # 检查是否有单元执行失败
        if isinstance(analysis_results, dict):
            for unit_name, result in analysis_results.items():
                if result.get("status") == "error":
                    return True
                    
            # 检查结论中是否包含错误关键词
            if 'conclusions' in analysis_results:
                for conclusion in analysis_results.get('conclusions', []):
                    if '错误' in conclusion or 'error' in conclusion.lower():
                        return True
                        
        return False
        
    def _add_error_information(self, report_content, analysis_results):
        """
        向报告中添加错误信息
        
        Args:
            report_content (str): 原始报告内容
            analysis_results (dict): 分析结果
            
        Returns:
            str: 添加了错误信息的报告内容
        """
        # 如果分析结果是字符串，无法添加错误信息
        if isinstance(analysis_results, str):
            return report_content
            
        # 如果分析结果为空，无法添加错误信息
        if not analysis_results:
            return report_content
            
        error_section = "\n\n## 分析过程中的错误\n\n"
        has_errors = False
        
        # 检查每个分析单元的状态
        if isinstance(analysis_results, dict):
            for unit_name, result in analysis_results.items():
                if result.get("status") == "error":
                    has_errors = True
                    error_section += f"- **{unit_name}**: {result.get('error', '未知错误')}\n"
        
        # 如果有错误，添加错误部分
        if has_errors:
            return report_content + error_section
        else:
            return report_content
    
    def _generate_report_with_model(self, prompt):
        """
        使用模型生成报告
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 生成的报告内容
        """
        logger.info("开始生成报告...")
        
        try:
            # 流式生成报告
            report_content = self._generate_markdown_with_stream(prompt)
            
            # 验证并提取报告内容
            valid_report = self._extract_and_validate_markdown(report_content)
            
            if not valid_report:
                logger.error("无法提取有效的报告内容")
                return None
            
            return valid_report
            
        except Exception as e:
            logger.error(f"生成报告时出错: {str(e)}")
            return f"# 报告生成失败\n\n生成报告时发生错误: {str(e)}"
    
    def _convert_markdown_to_html(self, markdown_content):
        """
        将Markdown内容转换为HTML
        
        Args:
            markdown_content (str): Markdown内容
            
        Returns:
            str: HTML内容
        """
        try:
            # 直接使用备用方法，避免调用外部脚本
            return self._fallback_markdown_to_html(markdown_content)
            
        except Exception as e:
            logger.error(f"将Markdown转换为HTML时出错: {str(e)}")
            # 返回一个最基本的HTML
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>数据分析报告</title>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>
"""
    
    def _fallback_markdown_to_html(self, markdown_content):
        """
        当markdown_to_html.py不可用或出错时的备用方法
        
        Args:
            markdown_content (str): Markdown内容
            
        Returns:
            str: HTML内容
        """
        try:
            # 尝试使用Python的markdown库
            try:
                import markdown
                html_body = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
            except ImportError:
                # 如果markdown库不可用，使用简单的文本替换
                logger.warning("Python markdown库不可用，使用简单的文本替换")
                html_body = self._simple_markdown_to_html(markdown_content)
            
            # 创建完整的HTML文档
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
        body {{
            font-family: 'Arial', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        h1 {{
            text-align: center;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background-color: #f5f5f5;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        blockquote {{
            border-left: 5px solid #eee;
            padding-left: 15px;
            color: #666;
        }}
        .insight {{
            background-color: #f0f7fb;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
        .key-finding {{
            background-color: #fdf7f7;
            border-left: 5px solid #e74c3c;
            padding: 15px;
            margin: 20px 0;
        }}
        .summary {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
"""
            return html_content
            
        except Exception as e:
            logger.error(f"备用HTML转换失败: {str(e)}")
            # 返回一个最基本的HTML
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>数据分析报告</title>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>
"""
    
    def _simple_markdown_to_html(self, markdown_content):
        """
        简单的Markdown到HTML转换
        
        Args:
            markdown_content (str): Markdown内容
            
        Returns:
            str: HTML内容
        """
        import re
        
        # 替换标题
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown_content, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        
        # 替换列表
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\g<0></ul>', html, flags=re.DOTALL)
        
        # 替换粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 替换代码块
        html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # 替换段落
        html = re.sub(r'^(?!<[hlu])(.*?)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        
        return html
    
    def generate_html_report(self, analysis_results):
        """
        从分析结果生成HTML报告
        
        Args:
            analysis_results (dict): 分析结果
            
        Returns:
            str: 生成的HTML内容
        """
        logger.info("从分析结果生成HTML报告...")
        
        try:
            # 构建HTML报告
            html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
        body {
            font-family: 'Arial', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4 {
            color: #2c3e50;
        }
        h1 {
            text-align: center;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px 15px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .insight {
            background-color: #f0f7fb;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }
        .key-finding {
            background-color: #fdf7f7;
            border-left: 5px solid #e74c3c;
            padding: 15px;
            margin: 20px 0;
        }
        .summary {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-top: 30px;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
        }
    </style>
</head>
<body>
    <h1>数据分析报告</h1>
"""
            
            # 添加概览部分
            html_content += """
    <div class="section">
        <h2>数据概览</h2>
"""
            
            # 添加通用统计分析结果
            if 'general_statistics' in analysis_results and analysis_results['general_statistics']['status'] == 'success':
                stats = analysis_results['general_statistics']['results']
                if 'conclusion' in stats:
                    html_content += f"""
        <div class="insight">
            <p>{stats['conclusion']}</p>
        </div>
"""
                
                if 'data_summary' in stats:
                    html_content += """
        <h3>数据摘要</h3>
        <table>
            <tr>
                <th>指标</th>
                <th>值</th>
            </tr>
"""
                    for key, value in stats['data_summary'].items():
                        html_content += f"""
            <tr>
                <td>{key}</td>
                <td>{value}</td>
            </tr>
"""
                    html_content += """
        </table>
"""
            
            html_content += """
    </div>
"""
            
            # 添加数据洞察部分
            html_content += """
    <div class="section">
        <h2>数据洞察</h2>
"""
            
            # 添加柱状图分析结果
            if 'bar_chart' in analysis_results and analysis_results['bar_chart']['status'] == 'success':
                bar_results = analysis_results['bar_chart']['results']
                if 'conclusion' in bar_results:
                    html_content += f"""
        <div class="insight">
            <p>{bar_results['conclusion']}</p>
        </div>
"""
            
            # 添加饼图分析结果
            if 'pie_chart' in analysis_results and analysis_results['pie_chart']['status'] == 'success':
                pie_results = analysis_results['pie_chart']['results']
                if 'conclusion' in pie_results:
                    html_content += f"""
        <div class="insight">
            <p>{pie_results['conclusion']}</p>
        </div>
"""
            
            # 添加时间趋势分析结果
            if 'time_trend' in analysis_results and analysis_results['time_trend']['status'] == 'success':
                trend_results = analysis_results['time_trend']['results']
                if 'conclusion' in trend_results:
                    html_content += f"""
        <div class="insight">
            <p>{trend_results['conclusion']}</p>
        </div>
"""
            
            html_content += """
    </div>
"""
            
            # 添加关键发现部分
            html_content += """
    <div class="section">
        <h2>关键发现</h2>
"""
            
            # 添加相关性分析结果
            if 'correlation' in analysis_results and analysis_results['correlation']['status'] == 'success':
                corr_results = analysis_results['correlation']['results']
                if 'conclusion' in corr_results:
                    html_content += f"""
        <div class="key-finding">
            <p>{corr_results['conclusion']}</p>
        </div>
"""
            
            html_content += """
    </div>
"""
            
            # 添加总结部分
            html_content += """
    <div class="summary">
        <h2>总结</h2>
        <p>本报告通过多角度分析了数据集，提供了数据的统计特征、分布情况、时间趋势和相关性分析。以上发现可以帮助决策者更好地理解数据并做出数据驱动的决策。</p>
    </div>
"""
            
            # 结束HTML文档
            html_content += """
</body>
</html>
"""
            
            # 保存HTML文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"html_report_{timestamp}.html"
            html_path = self.reports_dir / html_filename
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已将HTML报告保存到: {html_path}")
            
            return html_content
            
        except Exception as e:
            logger.error(f"从分析结果生成HTML报告时出错: {str(e)}")
            return None


    def create_enhanced_report(self, analysis_results, file_info, structure_analysis=None, pngs_dir=None):
        """
        创建增强型Markdown报告
        
        Args:
            analysis_results (dict): 分析结果
            file_info (dict): 文件信息
            structure_analysis (dict, optional): 结构分析结果
            pngs_dir (str, optional): 图表目录路径
            
        Returns:
            tuple: (markdown_path, html_path) 生成的Markdown和HTML文件路径
        """
        logger.info("开始创建增强型Markdown报告...")
        
        try:
            # 生成Markdown报告内容
            report_content = self.generate_markdown_report(analysis_results, pngs_dir)
            
            if not report_content:
                logger.error("无法生成报告内容")
                return None, None
            
            # 保存Markdown文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            markdown_filename = f"excel_analysis_report_{timestamp}.md"
            markdown_path = self.reports_dir / markdown_filename
            
            # 确保报告目录存在
            os.makedirs(self.reports_dir, exist_ok=True)
            
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"已将Markdown报告保存到: {markdown_path}")
            
            # 将Markdown渲染为HTML
            html_path = self._render_to_html(markdown_path)
            
            return str(markdown_path), str(html_path)
            
        except Exception as e:
            logger.error(f"生成增强型Markdown报告时出错: {str(e)}")
            return None, None


# 如果直接运行此脚本，执行测试
if __name__ == "__main__":
    import sys
    from model_connector import ModelConnector
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试配置
    config = {
        'reports_dir': 'test_reports',
        'charts_dir': 'test_reports/charts'
    }
    
    # 初始化模型连接器
    model = ModelConnector('openai', 'gpt-4')
    
    # 初始化增强型Markdown报告生成器
    report_generator = EnhancedMarkdownReportGenerator(model, config)
    
    # 测试数据
    test_results = {
        "general_statistics": {
            "total_records": 1000,
            "categories": {
                "A": 250,
                "B": 300,
                "C": 180,
                "D": 270
            }
        }
    }
    
    test_file_info = {
        "file_name": "test_data.csv"
    }
    
    test_structure = {
        "columns": {
            "category": {"type": "string"},
            "value": {"type": "number"}
        }
    }
    
    # 生成报告
    markdown_path, html_path = report_generator.generate_report(
        test_results, test_file_info, test_structure
    )
    
    if markdown_path and html_path:
        print(f"报告生成成功:\nMarkdown: {markdown_path}\nHTML: {html_path}")
    else:
        print("报告生成失败")
