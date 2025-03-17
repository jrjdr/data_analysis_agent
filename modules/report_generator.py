#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
报告生成器 - 负责生成HTML分析报告
"""

import os
import logging
import re
import time
import glob
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    报告生成器类，负责生成HTML分析报告
    """
    
    def __init__(self, model, config):
        """
        初始化报告生成器
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        
        # 确保报告目录存在
        os.makedirs('reports', exist_ok=True)
    
    def generate_html_report(self, analysis_results, structure_analysis=None):
        """
        生成HTML分析报告
        
        Args:
            analysis_results (str): 分析结果文本
            structure_analysis (dict, optional): 数据结构分析结果
        
        Returns:
            str: 生成的HTML报告
        """
        logger.info("正在生成HTML报告...")
        
        if not analysis_results:
            logger.error("分析结果为空，无法生成报告")
            return self._generate_error_report("分析结果为空，无法生成报告")
        
        try:
            # 读取临时文本文件中的分析结论
            conclusions = self._read_temp_txt_conclusions()
            
            # 构建提示词
            prompt = f"""
请根据以下数据分析结果和结论生成一个结构化的HTML报告。

初始数据分析:
```
{analysis_results}
```

各分析单元结论:
```
{conclusions}
```

要求:
1. 生成一个结构良好的HTML报告，专注于数据洞察而非复杂的可视化
2. 报告必须包含以下部分：
   - 概览（Overview）：提供数据集的基本信息和主要特点，包含数据表格
   - 数据洞察（Data Insights）：展示从数据中发现的主要模式和趋势，包含数据表格
   - 关键发现（Key Findings）：突出显示最重要的分析结果和发现，包含数据表格
   - 总结（Summary）：总结整体分析结果和建议
3. 使用简洁的HTML格式，确保良好的排版
4. 不要包含图表，但可以使用表格展示数据
5. 确保报告内容简洁明了，突出最重要的发现

请直接返回完整的HTML代码，不要包含任何解释或其他内容。
"""
            
            # 调用模型（使用流式API调用）
            logger.info("尝试调用API生成HTML报告（流式输出）...")
            print("\n开始生成HTML报告...\n")
            
            response = ""
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    print(chunk, end='', flush=True)
                    response += chunk
            
            print("\n\nHTML报告生成完成\n")
            
            if not response:
                logger.error("生成HTML报告失败: 模型未返回有效响应")
                return self._generate_error_report("生成HTML报告失败: 模型未返回有效响应")
            
            # 提取HTML代码
            html = self.extract_html(response)
            if not html:
                logger.error("生成HTML报告失败: 无法从响应中提取HTML代码")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return self._generate_error_report("生成HTML报告失败: 无法从响应中提取HTML代码")
            
            logger.info("成功生成HTML报告")
            
            # 保存报告
            report_file = f"reports/analysis_report_{time.strftime('%Y%m%d%H%M%S')}.html"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"已将HTML报告保存到: {report_file}")
            
            return html
            
        except Exception as e:
            logger.error(f"生成HTML报告时出错: {str(e)}")
            return self._generate_error_report(f"生成HTML报告时出错: {str(e)}")
    
    def _read_temp_txt_conclusions(self):
        """
        读取临时文本文件中的分析结论
        
        Returns:
            str: 合并后的分析结论文本
        """
        logger.info("读取临时文本文件中的分析结论...")
        
        # 检查temp_txts目录是否存在
        temp_txts_dir = os.path.join(os.getcwd(), 'temp_txts')
        if not os.path.exists(temp_txts_dir):
            logger.warning("临时文本文件目录不存在，将返回空结论")
            return ""
        
        # 获取所有结论文件
        conclusion_files = glob.glob(os.path.join(temp_txts_dir, '*_conclusion.txt'))
        if not conclusion_files:
            logger.warning("未找到任何结论文件，将返回空结论")
            return ""
        
        # 按文件名排序（确保按分析单元顺序）
        conclusion_files.sort()
        
        # 读取并合并所有结论
        conclusions = []
        for file_path in conclusion_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        conclusions.append(content)
            except Exception as e:
                logger.error(f"读取结论文件 {file_path} 时出错: {str(e)}")
        
        return "\n\n".join(conclusions)
    
    def extract_html(self, response):
        """
        从模型响应中提取HTML代码
        
        Args:
            response (str): 模型响应
        
        Returns:
            str: 提取的HTML代码，如果提取失败则返回None
        """
        if not response:
            logger.warning("响应为空，无法提取HTML代码")
            return None
        
        # 尝试从HTML代码块中提取代码
        html_match = re.search(r'```html\s*(.*?)\s*```', response, re.DOTALL)
        if html_match:
            html = html_match.group(1).strip()
            logger.info("成功从HTML代码块中提取代码")
            return html
        
        # 如果没有找到HTML代码块，尝试查找普通代码块
        code_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            html = code_match.group(1).strip()
            logger.info("成功从普通代码块中提取代码")
            return html
        
        # 检查是否有不完整的代码块开始标记
        if '```html' in response or '``` html' in response:
            # 尝试提取不完整的HTML代码块
            html_parts = re.split(r'```html|``` html', response, 1)
            if len(html_parts) > 1:
                html = html_parts[1].strip()
                if html:
                    logger.info("从不完整的HTML代码块中提取代码")
                    return html
        
        # 检查是否有不完整的普通代码块开始标记
        if '```' in response:
            # 尝试提取不完整的普通代码块
            html_parts = re.split(r'```', response, 1)
            if len(html_parts) > 1:
                html = html_parts[1].strip()
                if html:
                    logger.info("从不完整的普通代码块中提取代码")
                    return html
        
        # 检查是否整个响应就是HTML
        if response.strip().startswith('<!DOCTYPE html>') or response.strip().startswith('<html') or '<body>' in response:
            logger.info("将整个响应作为HTML返回")
            return response.strip()
        
        # 如果响应包含HTML标签，可能是HTML
        if '<div' in response or '<h1' in response or '<p>' in response or '<table' in response:
            logger.info("检测到HTML标签，将响应作为HTML返回")
            return response.strip()
        
        # 如果以上方法都失败，则返回None
        logger.warning("无法从响应中提取HTML代码")
        return None
    
    def _generate_error_report(self, error_message):
        """
        生成错误报告
        
        Args:
            error_message (str): 错误信息
        
        Returns:
            str: 生成的错误HTML报告
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>分析报告 - 错误</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ color: red; padding: 20px; border: 1px solid red; background-color: #ffeeee; }}
    </style>
</head>
<body>
    <h1>数据分析报告 - 错误</h1>
    <div class="error">
        <h2>生成报告时出错</h2>
        <p>{error_message}</p>
    </div>
    <p>请检查数据文件和日志，然后重试。</p>
    <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
        
        return html

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试报告生成器
    print("请在主程序中测试报告生成器")