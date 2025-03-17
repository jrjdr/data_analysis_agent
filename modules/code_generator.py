#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码生成器 - 负责生成数据分析代码并执行
现在使用分析调度器来协调多个分析单元
"""

import os
import logging
import time
import re
import subprocess
from datetime import datetime

from .analysis_dispatcher import AnalysisDispatcher

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    代码生成器类，负责生成数据分析代码并执行
    现在作为分析调度器的包装器
    """
    
    def __init__(self, model, config):
        """
        初始化代码生成器
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        
        # 创建分析调度器
        self.dispatcher = AnalysisDispatcher(model, config)
        
        # 确保临时目录存在
        os.makedirs('temp_py', exist_ok=True)
    
    def generate_analysis_code(self, structure_analysis, column_names):
        """
        生成数据分析代码
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
        
        Returns:
            str: 生成的Python代码，如果生成失败则返回None
        """
        logger.info("正在生成数据分析代码（通过调度器）...")
        
        # 这个方法现在只是为了向后兼容
        # 实际的代码生成将由调度器中的各个分析单元完成
        
        # 创建一个简单的包装代码，它将调用所有分析单元
        code = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

\"\"\"
数据分析代码 - 由分析调度器生成
这个代码文件是一个包装器，实际分析由各个分析单元完成
\"\"\"

import sys
import os
import json

def main():
    \"\"\"
    主函数，调用各个分析单元
    \"\"\"
    if len(sys.argv) < 2:
        print("使用方法: python script.py <数据文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print(f"正在分析数据文件: {file_path}")
    
    # 实际分析由分析调度器中的各个分析单元完成
    # 这个脚本只是一个占位符
    print("分析完成，请查看生成的JSON结果文件")

if __name__ == "__main__":
    main()
"""
        
        # 保存生成的代码
        code_file = f"temp_py/analysis_code_{time.strftime('%Y%m%d%H%M%S')}.py"
        os.makedirs(os.path.dirname(code_file), exist_ok=True)
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        logger.info(f"已将生成的代码保存到: {code_file}")
        
        return code
    
    def execute_and_fix_code(self, code, file_path):
        """
        执行代码并在出错时尝试修复，最多尝试三次
        现在使用分析调度器来执行所有分析单元
        
        Args:
            code (str): 要执行的Python代码（现在主要是占位符）
            file_path (str): 数据文件路径
        
        Returns:
            tuple: (成功标志, 最终代码, 执行结果)
        """
        logger.info("开始执行分析（通过调度器）...")
        
        try:
            # 从文件路径中提取结构分析和列名
            # 这里假设这些信息已经在之前的步骤中被确定
            # 在实际使用中，这些应该从调用方传入
            structure_analysis = self._get_structure_analysis_from_file(file_path)
            column_names = self._get_column_names_from_file(file_path)
            
            if not structure_analysis or not column_names:
                logger.error("无法获取数据结构分析或列名信息")
                return False, code, "无法获取数据结构分析或列名信息"
            
            # 使用调度器运行所有分析单元
            results = self.dispatcher.run_analysis(structure_analysis, column_names, file_path)
            
            # 检查是否至少有一个分析单元成功执行
            success = any(result["status"] == "success" for result in results.values())
            
            if not success:
                logger.error("所有分析单元执行失败")
                return False, code, "所有分析单元执行失败"
            
            # 获取组合结果
            combined_results = self.dispatcher.get_combined_results(results)
            
            # 保存组合结果
            result_file = f"temp_py/analysis_results_{time.strftime('%Y%m%d%H%M%S')}.txt"
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(combined_results)
            logger.info(f"已将分析结果保存到: {result_file}")
            
            return True, code, combined_results
            
        except Exception as e:
            logger.error(f"执行分析时出错: {str(e)}")
            return False, code, str(e)
    
    def _get_structure_analysis_from_file(self, file_path):
        """
        从文件中获取数据结构分析信息
        
        Args:
            file_path (str): 数据文件路径
            
        Returns:
            dict: 数据结构分析结果
        """
        # 这个方法应该根据实际情况实现
        # 在这个示例中，我们返回一个简单的结构分析
        import pandas as pd
        
        try:
            # 尝试读取数据文件
            df = pd.read_csv(file_path)
            
            # 创建一个简单的结构分析
            structure_analysis = {
                "file_path": file_path,
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
            
            return structure_analysis
            
        except Exception as e:
            logger.error(f"从文件获取数据结构分析时出错: {str(e)}")
            return None
    
    def _get_column_names_from_file(self, file_path):
        """
        从文件中获取列名
        
        Args:
            file_path (str): 数据文件路径
            
        Returns:
            list: 列名列表
        """
        # 这个方法应该根据实际情况实现
        import pandas as pd
        
        try:
            # 尝试读取数据文件
            df = pd.read_csv(file_path)
            
            # 返回列名列表
            return df.columns.tolist()
            
        except Exception as e:
            logger.error(f"从文件获取列名时出错: {str(e)}")
            return None
    
    def fix_analysis_code(self, code, error_message):
        """
        修复数据分析代码
        
        Args:
            code (str): 原始代码
            error_message (str): 错误信息
        
        Returns:
            str: 修复后的代码，如果修复失败则返回None
        """
        logger.info("正在修复数据分析代码...")
        
        try:
            # 构建提示词
            prompt = f"""
请修复以下Python数据分析代码中的错误。

原始代码:
```python
{code}
```

执行时出现的错误:
```
{error_message}
```

请提供修复后的完整代码，确保它能够正确执行并处理上述错误。
修复后的代码应该保持原有的功能和结构，只修改导致错误的部分。
请确保代码是高质量的、可执行的，并且能够处理各种边缘情况。
"""
            
            # 调用模型（使用流式API调用）
            logger.info("尝试调用API修复代码（流式输出）...")
            print("\n开始修复代码...\n")
            
            response = ""
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    print(chunk, end='', flush=True)
                    response += chunk
            
            print("\n\n代码修复完成\n")
            
            if not response:
                logger.error("修复数据分析代码失败: 模型未返回有效响应")
                return None
            
            # 提取Python代码
            fixed_code = self._extract_python_code(response)
            if not fixed_code:
                logger.error("修复数据分析代码失败: 无法从响应中提取Python代码")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return None
            
            logger.info("成功修复数据分析代码")
            
            # 保存修复后的代码
            code_file = f"temp_py/fixed_analysis_code_{time.strftime('%Y%m%d%H%M%S')}.py"
            os.makedirs(os.path.dirname(code_file), exist_ok=True)
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            logger.info(f"已将修复后的代码保存到: {code_file}")
            
            return fixed_code
            
        except Exception as e:
            logger.error(f"修复数据分析代码时出错: {str(e)}")
            return None
    
    def _extract_python_code(self, response):
        """
        从模型响应中提取Python代码
        
        Args:
            response (str): 模型响应
        
        Returns:
            str: 提取的Python代码，如果提取失败则返回None
        """
        if not response:
            logger.warning("响应为空，无法提取Python代码")
            return None
        
        # 尝试从Python代码块中提取代码
        code_match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            logger.info("成功从Python代码块中提取代码")
            return code
        
        # 如果没有找到Python代码块，尝试查找普通代码块
        code_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            logger.info("成功从普通代码块中提取代码")
            return code
        
        # 检查是否有不完整的代码块开始标记
        if '```python' in response or '``` python' in response:
            # 尝试提取不完整的Python代码块
            code_parts = re.split(r'```python|``` python', response, 1)
            if len(code_parts) > 1:
                code = code_parts[1].strip()
                if code:
                    logger.info("从不完整的Python代码块中提取代码")
                    return code
        
        # 检查是否有不完整的普通代码块开始标记
        if '```' in response:
            # 尝试提取不完整的普通代码块
            code_parts = re.split(r'```', response, 1)
            if len(code_parts) > 1:
                code = code_parts[1].strip()
                if code:
                    logger.info("从不完整的普通代码块中提取代码")
                    return code
        
        # 如果仍然没有找到代码块，检查是否整个响应就是代码
        if (response.strip().startswith('import') or 
            response.strip().startswith('def') or
            response.strip().startswith('#') or
            response.strip().startswith('#!/usr/bin/env python') or
            response.strip().startswith('"""') or
            'import pandas as pd' in response or
            'import numpy as np' in response):
            logger.info("将整个响应作为代码返回")
            return response.strip()
        
        # 如果响应很长并且包含多行，可能是代码
        lines = response.strip().split('\n')
        if len(lines) > 10:  # 假设超过10行的内容可能是代码
            code_like_lines = 0
            for line in lines:
                line = line.strip()
                if (line.startswith('def ') or
                    line.startswith('class ') or
                    line.startswith('import ') or
                    line.startswith('from ') or
                    line.startswith('if ') or
                    line.startswith('for ') or
                    line.startswith('while ') or
                    line.startswith('with ') or
                    line.startswith('try:') or
                    line.startswith('except ') or
                    line.startswith('return ') or
                    line.startswith('# ') or
                    ' = ' in line):
                    code_like_lines += 1
            
            # 如果有超过30%的行看起来像代码
            if code_like_lines / len(lines) > 0.3:
                logger.info(f"基于内容特征判断响应为代码 (代码特征行占比: {code_like_lines/len(lines):.2f})")
                return response.strip()
        
        # 如果以上方法都失败，则返回None
        logger.warning("无法从响应中提取Python代码")
        return None
    
    def _execute_code(self, code, file_path):
        """
        在沙箱环境中执行Python代码
        
        Args:
            code (str): 要执行的Python代码
            file_path (str): 数据文件路径
        
        Returns:
            tuple: (执行结果, 错误信息)
        """
        logger.info("在沙箱环境中执行代码...")
        
        # 创建临时文件
        temp_file = f"temp_py/temp_code_{time.strftime('%Y%m%d%H%M%S')}.py"
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 构建执行命令
        cmd = f"python {temp_file} {file_path}"
        
        try:
            # 执行代码
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=60)  # 设置超时时间为60秒
            
            # 检查执行结果
            if process.returncode == 0:
                logger.info("代码执行成功")
                return stdout, None
            else:
                logger.warning(f"代码执行失败，错误码: {process.returncode}")
                return None, stderr
                
        except subprocess.TimeoutExpired:
            logger.error("代码执行超时")
            return None, "代码执行超时（超过60秒）"
        except Exception as e:
            logger.error(f"执行代码时发生异常: {str(e)}")
            return None, str(e)

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试代码生成器
    print("请在主程序中测试代码生成器")
