#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown转HTML渲染器 - 将Markdown格式的报告转换为HTML格式
支持基本Markdown语法以及Mermaid图表
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import markdown
except ImportError:
    logger.error("缺少markdown模块，请使用以下命令安装：pip install markdown")
    print("缺少markdown模块，请使用以下命令安装：pip install markdown")
    sys.exit(1)
import re
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarkdownToHtmlRenderer:
    """
    Markdown转HTML渲染器类
    """
    
    def __init__(self, theme="light"):
        """
        初始化渲染器
        
        Args:
            theme (str): 主题样式，可选 "light" 或 "dark"
        """
        self.theme = theme
        
        # 设置Markdown扩展
        self.markdown_extensions = [
            'tables',              # 表格支持
            'fenced_code',         # 代码块支持
            'codehilite',          # 代码高亮
            'attr_list',           # 属性列表
            'def_list',            # 定义列表
            'footnotes',           # 脚注
            'md_in_html',          # HTML中的Markdown
            'toc'                  # 目录
        ]
        
        # 设置Markdown扩展配置
        self.extension_configs = {
            'codehilite': {
                'linenums': False,
                'use_pygments': True,
                'pygments_style': 'github-dark' if theme == 'dark' else 'github'
            }
        }
    
    def _get_css_style(self):
        """
        获取CSS样式
        
        Returns:
            str: CSS样式代码
        """
        if self.theme == "dark":
            return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #e0e0e0;
                background-color: #121212;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #ffffff;
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
            }
            h1 { font-size: 2em; border-bottom: 1px solid #333; padding-bottom: 0.3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #333; padding-bottom: 0.3em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            a { color: #58a6ff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            code {
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                background-color: #2a2a2a;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-size: 85%;
                color: #e0e0e0;
            }
            pre {
                background-color: #2a2a2a;
                border-radius: 6px;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                border-radius: 0;
            }
            blockquote {
                border-left: 4px solid #444;
                padding-left: 16px;
                color: #aaa;
                margin: 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }
            table th, table td {
                border: 1px solid #444;
                padding: 8px 12px;
                text-align: left;
            }
            table th {
                background-color: #2a2a2a;
                font-weight: 600;
            }
            table tr:nth-child(even) {
                background-color: #1e1e1e;
            }
            img {
                max-width: 100%;
                height: auto;
            }
            hr {
                height: 1px;
                background-color: #444;
                border: none;
                margin: 24px 0;
            }
            .mermaid {
                background-color: #1e1e1e;
                padding: 16px;
                border-radius: 6px;
                text-align: center;
            }
            """
        else:
            return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #24292e;
                background-color: #ffffff;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #24292e;
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
            }
            h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            a { color: #0366d6; text-decoration: none; }
            a:hover { text-decoration: underline; }
            code {
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
                background-color: #f6f8fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-size: 85%;
                color: #24292e;
            }
            pre {
                background-color: #f6f8fa;
                border-radius: 6px;
                padding: 16px;
                overflow: auto;
                font-size: 85%;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                border-radius: 0;
            }
            blockquote {
                border-left: 4px solid #dfe2e5;
                padding-left: 16px;
                color: #6a737d;
                margin: 0;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }
            table th, table td {
                border: 1px solid #dfe2e5;
                padding: 8px 12px;
                text-align: left;
            }
            table th {
                background-color: #f6f8fa;
                font-weight: 600;
            }
            table tr:nth-child(even) {
                background-color: #f8f8f8;
            }
            img {
                max-width: 100%;
                height: auto;
            }
            hr {
                height: 1px;
                background-color: #dfe2e5;
                border: none;
                margin: 24px 0;
            }
            .mermaid {
                background-color: #f8f8f8;
                padding: 16px;
                border-radius: 6px;
                text-align: center;
            }
            """
    
    def _process_mermaid_blocks(self, markdown_text):
        """
        处理Markdown中的Mermaid图表块
        
        Args:
            markdown_text (str): Markdown文本
        
        Returns:
            str: 处理后的Markdown文本
        """
        # 查找所有的Mermaid代码块
        pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        
        # 替换为带有mermaid类的div
        for match in matches:
            original = f'```mermaid\n{match}\n```'
            replacement = f'<div class="mermaid">\n{match}\n</div>'
            markdown_text = markdown_text.replace(original, replacement)
        
        return markdown_text
    
    def render(self, markdown_text, title="数据分析报告"):
        """
        将Markdown文本渲染为HTML
        
        Args:
            markdown_text (str): Markdown文本
            title (str): HTML页面标题
        
        Returns:
            str: 渲染后的HTML
        """
        # 处理Mermaid图表
        processed_markdown = self._process_mermaid_blocks(markdown_text)
        
        # 使用Python-Markdown库渲染Markdown
        html_content = markdown.markdown(
            processed_markdown,
            extensions=self.markdown_extensions,
            extension_configs=self.extension_configs
        )
        
        # 构建完整的HTML文档
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{self._get_css_style()}
    </style>
    <!-- 引入Mermaid.js -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            mermaid.initialize({{
                startOnLoad: true,
                theme: '{self.theme == "dark" and "dark" or "default"}',
                securityLevel: 'loose'
            }});
        }});
    </script>
</head>
<body>
    <article class="markdown-body">
{html_content}
    </article>
    <footer style="margin-top: 40px; text-align: center; color: #6a737d; font-size: 0.8em;">
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>"""
        
        return html_template
    
    def render_file(self, markdown_file, output_file=None, title=None):
        """
        渲染Markdown文件为HTML文件
        
        Args:
            markdown_file (str): Markdown文件路径
            output_file (str): 输出HTML文件路径，如果为None则自动生成
            title (str): HTML页面标题，如果为None则使用文件名
        
        Returns:
            str: 输出的HTML文件路径
        """
        try:
            # 读取Markdown文件
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            
            # 如果未指定标题，使用文件名
            if title is None:
                title = Path(markdown_file).stem
            
            # 渲染为HTML
            html_content = self.render(markdown_text, title)
            
            # 如果未指定输出文件，自动生成
            if output_file is None:
                output_dir = 'reports'
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                output_file = f"{output_dir}/{Path(markdown_file).stem}_{timestamp}.html"
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 写入HTML文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"已将Markdown渲染为HTML并保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"渲染Markdown文件时出错: {str(e)}")
            return None

def main():
    """
    主函数，处理命令行参数并执行渲染
    """
    parser = argparse.ArgumentParser(description='将Markdown文件渲染为HTML')
    parser.add_argument('markdown_file', help='输入的Markdown文件路径')
    parser.add_argument('-o', '--output', help='输出的HTML文件路径')
    parser.add_argument('-t', '--title', help='HTML页面标题')
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help='主题样式')
    
    args = parser.parse_args()
    
    renderer = MarkdownToHtmlRenderer(theme=args.theme)
    output_file = renderer.render_file(args.markdown_file, args.output, args.title)
    
    if output_file:
        print(f"已将Markdown渲染为HTML并保存到: {output_file}")
        
        # 尝试自动打开HTML文件
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
            print("已自动打开HTML报告")
        except Exception as e:
            print(f"无法自动打开HTML报告: {str(e)}")
    else:
        print("渲染失败，请检查错误日志")
        sys.exit(1)

if __name__ == "__main__":
    main()
