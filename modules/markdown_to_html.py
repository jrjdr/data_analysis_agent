#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown转HTML模块 - 将Markdown内容转换为HTML
"""

import re
import os
import logging
from pathlib import Path
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

logger = logging.getLogger(__name__)

# 自定义代码高亮渲染器
class HighlightRenderer(mistune.HTMLRenderer):
    def __init__(self, escape=True, allow_harmful_protocols=None):
        super().__init__(escape=escape, allow_harmful_protocols=allow_harmful_protocols)
        self.formatter = HtmlFormatter(style='github', linenos=False)
    
    def block_code(self, code, info=None):
        """
        渲染代码块
        """
        if info:
            info = info.strip()
            if info == 'mermaid':
                # 对于Mermaid图表，使用特殊的处理
                return f'<div class="mermaid">{code}</div>'
            else:
                try:
                    lexer = get_lexer_by_name(info)
                    return highlight(code, lexer, self.formatter)
                except:
                    pass
        return f'<pre><code>{mistune.markdown.escape_html(code)}</code></pre>'

def convert_markdown_to_html(markdown_content, theme='light'):
    """
    将Markdown内容转换为HTML
    
    Args:
        markdown_content (str): Markdown内容
        theme (str): 主题，'light'或'dark'
        
    Returns:
        str: HTML内容
    """
    # 创建Markdown解析器
    renderer = HighlightRenderer(escape=False)
    markdown_parser = mistune.create_markdown(renderer=renderer)
    
    # 解析Markdown
    html_content = markdown_parser(markdown_content)
    
    # 添加Mermaid.js支持
    html_content = _add_mermaid_support(html_content)
    
    # 添加样式和主题
    html_content = _add_html_template(html_content, theme)
    
    return html_content

def _add_mermaid_support(html_content):
    """
    添加Mermaid.js支持
    
    Args:
        html_content (str): HTML内容
        
    Returns:
        str: 添加Mermaid.js支持后的HTML内容
    """
    # 检查是否包含Mermaid图表
    if '<div class="mermaid">' in html_content:
        # 添加Mermaid.js脚本
        mermaid_script = """
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    flowchart: { useMaxWidth: false, htmlLabels: true }
                });
            });
        </script>
        """
        # 在</body>标签前插入脚本
        html_content = html_content.replace('</body>', f'{mermaid_script}</body>')
    
    return html_content

def _add_html_template(html_content, theme='light'):
    """
    添加HTML模板
    
    Args:
        html_content (str): HTML内容
        theme (str): 主题，'light'或'dark'
        
    Returns:
        str: 添加模板后的HTML内容
    """
    # 定义CSS样式
    if theme == 'dark':
        css = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #eee;
            background-color: #222;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #fff;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        h1 { font-size: 2em; border-bottom: 1px solid #444; padding-bottom: 0.3em; }
        h2 { font-size: 1.5em; border-bottom: 1px solid #444; padding-bottom: 0.3em; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        code {
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            background-color: #333;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            color: #ddd;
        }
        pre {
            background-color: #333;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #444;
            margin-left: 0;
            padding-left: 16px;
            color: #aaa;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        table th, table td {
            border: 1px solid #444;
            padding: 8px 12px;
        }
        table th {
            background-color: #333;
        }
        table tr:nth-child(even) {
            background-color: #2a2a2a;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 16px 0;
        }
        .mermaid {
            background-color: #333;
            padding: 16px;
            border-radius: 6px;
            margin: 16px 0;
        }
        """
    else:  # light theme
        css = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #24292e;
            background-color: #fff;
            max-width: 900px;
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
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        code {
            font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            color: #24292e;
        }
        pre {
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            margin-left: 0;
            padding-left: 16px;
            color: #6a737d;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        table th, table td {
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
        }
        table th {
            background-color: #f6f8fa;
        }
        table tr:nth-child(even) {
            background-color: #f8f8f8;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 16px 0;
        }
        .mermaid {
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            margin: 16px 0;
        }
        """
    
    # 构建完整的HTML
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
{css}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    
    return html_template

# 如果直接运行此脚本，执行测试
if __name__ == "__main__":
    import sys
    import argparse
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='将Markdown文件转换为HTML')
    parser.add_argument('markdown_file', help='Markdown文件路径')
    parser.add_argument('--theme', choices=['light', 'dark'], default='light',
                      help='HTML主题')
    args = parser.parse_args()
    
    # 读取Markdown文件
    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 转换为HTML
        html_content = convert_markdown_to_html(markdown_content, args.theme)
        
        # 保存HTML文件
        html_file = Path(args.markdown_file).with_suffix('.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"已将Markdown转换为HTML: {html_file}")
        print(f"已将Markdown转换为HTML: {html_file}")
        
    except Exception as e:
        logger.error(f"转换Markdown为HTML时出错: {str(e)}")
        sys.exit(1)
