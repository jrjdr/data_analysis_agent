#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图表生成模块 - 负责基于分析结果生成可视化图表
"""

import os
import sys
import json
import uuid
import logging
import tempfile
import subprocess
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)

class ChartGenerator:
    """
    图表生成器，负责将分析结果转换为可视化图表
    """
    
    def __init__(self, model_connector, config):
        """
        初始化图表生成器
        
        Args:
            model_connector: 模型连接器对象，用于与大模型交互
            config (dict): 配置信息
        """
        self.model = model_connector
        self.config = config
        self.charts_dir = Path(config.get('charts_dir', 'reports/charts'))
        self.max_attempts = config.get('chart_generation_max_attempts', 3)
        
        # 确保图表目录存在
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # 沙箱环境的Python库白名单
        self.allowed_modules = [
            'matplotlib', 'numpy', 'pandas', 'seaborn', 
            'plotly', 'json', 'os', 'sys', 'math', 
            'datetime', 'collections', 're'
        ]
    
    def generate_chart(self, analysis_result, chart_type=None, title=None, pngs_dir=None):
        """
        基于分析结果生成图表
        
        Args:
            analysis_result (dict): 分析结果数据
            chart_type (str, optional): 期望的图表类型，如'bar', 'line', 'scatter', 'pie'等
            title (str, optional): 图表标题
            pngs_dir (str, optional): 图表保存目录，如果指定则优先使用此目录
            
        Returns:
            str: 生成的图表文件路径
        """
        logger.info(f"开始生成图表: {title or '未命名图表'}")
        
        # 为图表生成唯一ID
        chart_id = str(uuid.uuid4())[:8]
        chart_filename = f"chart_{chart_id}.png"
        
        # 确定图表保存路径
        if pngs_dir and os.path.isdir(pngs_dir):
            chart_dir = Path(pngs_dir)
        else:
            chart_dir = self.charts_dir
            
        # 确保目录存在
        os.makedirs(chart_dir, exist_ok=True)
        
        chart_path = chart_dir / chart_filename
        
        # 准备提示词
        prompt = self._build_chart_prompt(analysis_result, chart_type, title)
        
        # 尝试生成并执行代码
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"图表生成尝试 {attempt}/{self.max_attempts}")
            
            # 流式调用模型生成代码
            code = self._generate_code_with_stream(prompt)
            
            # 执行代码生成图表
            success, error_message = self._execute_code_in_sandbox(
                code, chart_path, analysis_result
            )
            
            if success:
                logger.info(f"图表生成成功: {chart_path}")
                return str(chart_path)
            
            # 如果失败且还有尝试次数，则修改提示词并重试
            if attempt < self.max_attempts:
                logger.warning(f"图表生成失败，错误: {error_message}")
                prompt = self._build_correction_prompt(code, error_message)
        
        # 所有尝试都失败
        logger.error(f"图表生成失败，达到最大尝试次数 ({self.max_attempts})")
        return None
    
    def _build_chart_prompt(self, analysis_result, chart_type=None, title=None):
        """
        构建生成图表代码的提示词
        
        Args:
            analysis_result (dict): 分析结果数据
            chart_type (str, optional): 期望的图表类型
            title (str, optional): 图表标题
            
        Returns:
            str: 构建的提示词
        """
        # 将分析结果转换为字符串表示
        result_str = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        chart_type_str = f"图表类型: {chart_type}" if chart_type else "请根据数据特点选择合适的图表类型"
        title_str = f"图表标题: {title}" if title else "请为图表生成一个合适的标题"
        
        prompt = f"""
请根据以下分析结果数据，生成一段Python代码来创建一个高质量的可视化图表。

分析结果数据:
```json
{result_str}
```

{chart_type_str}
{title_str}

要求:
1. 使用matplotlib、seaborn或plotly库创建图表
2. 图表应该美观、专业，包含适当的标题、标签和图例
3. 使用合适的颜色方案，确保视觉效果良好
4. 代码应该将图表保存为PNG文件，文件路径将通过变量'output_path'提供
5. 数据将通过变量'data'提供，格式为Python字典
6. 不要显示图表，只需保存为文件
7. 代码应该处理可能的错误和边缘情况
8. 不要使用plt.show()，只使用plt.savefig(output_path, dpi=300, bbox_inches='tight')
9. 确保代码完整可执行，包含所有必要的导入语句

请生成一个可执行的Python脚本，不超过50行。
"""
        return prompt
    
    def _build_correction_prompt(self, code, error_message):
        """
        构建修正代码的提示词
        
        Args:
            code (str): 原始代码
            error_message (str): 错误信息
            
        Returns:
            str: 构建的提示词
        """
        prompt = f"""
以下是生成图表的Python代码，但执行时遇到了错误。请修正代码使其能够正确执行。

原始代码:
```python
{code}
```

错误信息:
```
{error_message}
```

请修正上述代码中的错误，并确保:
1. 代码能够正确执行并生成图表
2. 图表保存为PNG文件，使用变量'output_path'作为文件路径
3. 不要使用plt.show()，只使用plt.savefig()
4. 处理所有可能的错误情况
5. 代码应该简洁明了，不超过50行

请提供完整的修正后代码。
"""
        return prompt
    
    def _generate_code_with_stream(self, prompt):
        """
        使用流式输出生成Python代码
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 生成的Python代码
        """
        logger.info("开始流式生成图表代码...")
        
        # 使用流式API调用模型
        full_response = ""
        print("\n开始生成图表代码...")
        
        try:
            for chunk in self.model.call_model_stream(prompt):
                # 提取内容
                content = chunk.get('content', '')
                if content:
                    print(content, end='', flush=True)
                    full_response += content
            
            print("\n代码生成完成")
            
            # 从响应中提取Python代码
            code = self._extract_python_code(full_response)
            return code
            
        except Exception as e:
            logger.error(f"生成代码时出错: {str(e)}")
            return ""
    
    def _extract_python_code(self, text):
        """
        从文本中提取Python代码
        
        Args:
            text (str): 包含代码的文本
            
        Returns:
            str: 提取的Python代码
        """
        # 查找Python代码块
        import re
        code_block_patterns = [
            r'```python\s*([\s\S]*?)\s*```',  # Markdown风格
            r'```\s*([\s\S]*?)\s*```',         # 无语言标记的代码块
            r'(?:^|\n)(\s*import[\s\S]*)'      # 直接以import开头的代码
        ]
        
        for pattern in code_block_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        # 如果没有找到代码块，返回原始文本
        return text.strip()
    
    def _execute_code_in_sandbox(self, code, output_path, data):
        """
        在沙箱环境中执行Python代码
        
        Args:
            code (str): 要执行的Python代码
            output_path (Path): 图表输出路径
            data (dict): 分析结果数据
            
        Returns:
            tuple: (成功标志, 错误信息)
        """
        # 创建临时Python文件
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
            temp_file = f.name
            
            # 添加安全检查和导入限制
            sandbox_code = f"""
# 导入限制
import sys
import importlib

# 允许的模块列表
ALLOWED_MODULES = {self.allowed_modules}

# 重写__import__函数以限制导入
original_import = __import__

def secure_import(name, *args, **kwargs):
    if name not in ALLOWED_MODULES and not any(name.startswith(prefix + '.') for prefix in ALLOWED_MODULES):
        raise ImportError(f"导入模块 '{{name}}' 不在允许列表中")
    return original_import(name, *args, **kwargs)

sys.modules['builtins'].__import__ = secure_import

# 设置输出路径和数据
output_path = r"{output_path}"
data = {json.dumps(data, ensure_ascii=False)}

# 用户代码开始
try:
{self._indent_code(code)}
    print("图表生成成功，已保存到:", output_path)
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    print(traceback.format_exc())
    sys.exit(1)
"""
            f.write(sandbox_code)
        
        try:
            # 执行代码
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 设置超时时间
            )
            
            # 检查执行结果
            if result.returncode == 0:
                logger.info(f"代码执行成功，输出: {result.stdout.strip()}")
                return True, ""
            else:
                error = f"代码执行失败 (返回码: {result.returncode}):\n{result.stderr}"
                logger.error(error)
                return False, error
                
        except subprocess.TimeoutExpired:
            return False, "代码执行超时"
        except Exception as e:
            return False, f"执行代码时出错: {str(e)}\n{traceback.format_exc()}"
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def _indent_code(self, code, spaces=4):
        """
        缩进代码
        
        Args:
            code (str): 要缩进的代码
            spaces (int): 缩进空格数
            
        Returns:
            str: 缩进后的代码
        """
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in code.split('\n'))


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
        'charts_dir': 'test_charts',
        'chart_generation_max_attempts': 3
    }
    
    # 初始化模型连接器
    model = ModelConnector('openai', 'gpt-4')
    
    # 初始化图表生成器
    chart_generator = ChartGenerator(model, config)
    
    # 测试数据
    test_data = {
        "summary": {
            "total_records": 1000,
            "categories": {
                "A": 250,
                "B": 300,
                "C": 180,
                "D": 270
            },
            "numeric_values": [10, 25, 15, 30, 20]
        }
    }
    
    # 生成图表
    chart_path = chart_generator.generate_chart(
        test_data, 
        chart_type="pie", 
        title="Category Distribution",
        pngs_dir="custom_charts"
    )
    
    if chart_path:
        print(f"图表生成成功: {chart_path}")
    else:
        print("图表生成失败")
