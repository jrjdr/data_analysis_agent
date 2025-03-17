#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础分析单元 - 所有分析单元的父类
"""

import os
import logging
import time
import re
import subprocess
import json
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
        elif isinstance(obj, np.int64):
            return int(obj)
        elif isinstance(obj, np.float64):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.datetime64, np.timedelta64)):
            return str(obj)
        return super(NumpyEncoder, self).default(obj)

class BaseAnalysisUnit:
    """
    基础分析单元类，定义了所有分析单元共有的方法和属性
    """
    
    def __init__(self, model, config):
        """
        初始化基础分析单元
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        self.model = model
        self.config = config
        self.unit_name = "基础分析单元"
        self.max_attempts = 3
    
    def generate_analysis_code(self, structure_analysis, column_names, csv_path, data_context=None):
        """
        生成数据分析代码
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            csv_path (str): CSV文件路径
            data_context (dict, optional): 之前分析单元的结果和上下文
            
        Returns:
            str: 生成的Python代码，如果生成失败则返回None
        """
        logger.info(f"[{self.unit_name}] 正在生成数据分析代码...")
        
        # 构建提示词
        prompt = self.get_prompt(structure_analysis, column_names, csv_path)
        
        try:
            # 调用模型（使用流式API调用）
            logger.info(f"[{self.unit_name}] 尝试调用API生成代码（流式输出）...")
            print(f"\n开始为 {self.unit_name} 生成分析代码...\n")
            
            response = ""
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    print(chunk, end='', flush=True)
                    response += chunk
            
            print(f"\n\n{self.unit_name} 代码生成完成\n")
            
            if not response:
                logger.error(f"[{self.unit_name}] 生成数据分析代码失败: 模型未返回有效响应")
                return None
            
            # 提取Python代码
            code = self._extract_python_code(response)
            if not code:
                logger.error(f"[{self.unit_name}] 生成数据分析代码失败: 无法从响应中提取Python代码")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_prompt_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                logger.info(f"已将完整提示词保存到: {debug_file}")
                
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return None
            
            logger.info(f"[{self.unit_name}] 成功生成数据分析代码")
            return code
            
        except Exception as e:
            logger.error(f"[{self.unit_name}] 生成数据分析代码时出错: {str(e)}")
            return None
    
    def get_prompt(self, structure_analysis, column_names, csv_path):
        """
        获取提示词（子类需要重写此方法）
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            csv_path (str): CSV文件路径
            
        Returns:
            str: 提示词
        """
        raise NotImplementedError("子类必须实现get_prompt方法")
    
    def fix_analysis_code(self, code, error_message):
        """
        修复数据分析代码
        
        Args:
            code (str): 原始代码
            error_message (str): 错误信息
        
        Returns:
            str: 修复后的代码，如果修复失败则返回None
        """
        logger.info(f"[{self.unit_name}] 正在修复数据分析代码...")
        
        try:
            # 构建提示词
            prompt = f"""
请修复以下Python数据分析代码中的错误。这段代码是{self.unit_name}的一部分。

原始代码:
```python
{code}
```

执行时出现的错误:
```
{error_message}
```

请提供修复后的完整代码，确保它能够正确执行并处理上述错误。
请确保代码是高质量的、可执行的，并且能够处理各种边缘情况。
"""
            
            # 调用模型（使用流式API调用）
            logger.info(f"[{self.unit_name}] 尝试调用API修复代码（流式输出）...")
            print(f"\n开始修复 {self.unit_name} 的代码...\n")
            
            response = ""
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    print(chunk, end='', flush=True)
                    response += chunk
            
            print(f"\n\n{self.unit_name} 代码修复完成\n")
            
            if not response:
                logger.error(f"[{self.unit_name}] 修复数据分析代码失败: 模型未返回有效响应")
                return None
            
            # 提取Python代码
            fixed_code = self._extract_python_code(response)
            if not fixed_code:
                logger.error(f"[{self.unit_name}] 修复数据分析代码失败: 无法从响应中提取Python代码")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return None
            
            logger.info(f"[{self.unit_name}] 成功修复数据分析代码")
            return fixed_code
            
        except Exception as e:
            logger.error(f"[{self.unit_name}] 修复数据分析代码时出错: {str(e)}")
            return None
    
    def _build_prompt(self, structure_analysis, column_names, data_context=None):
        """
        构建提示词（已废弃，保留向后兼容）
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            data_context (dict, optional): 之前分析单元的结果和上下文
            
        Returns:
            str: 构建的提示词
        """
        # 将结构分析转换为字符串表示
        structure_str = str(structure_analysis)
        
        prompt = f"""
请根据以下Excel数据结构信息，生成一段Python数据分析代码。

数据结构分析:
{structure_str}

列名:
{', '.join(column_names)}

要求:
1. 代码应该读取CSV文件并进行数据分析
2. 代码应该将分析结果以纯文本格式保存到文件中，不要使用JSON格式
3. 代码应该简洁精炼，不超过2000行
4. 代码应该使用pandas和numpy库进行数据分析
5. 代码应该包含必要的注释，解释主要分析步骤
6. 代码应该处理可能的错误和异常情况

请生成一个可执行的Python脚本，包含必要的导入语句和异常处理。代码应该假设CSV文件路径作为命令行参数传入，并将分析结果保存到文本文件中。
"""
        return prompt
    
    def _extract_python_code(self, response):
        """
        从模型响应中提取Python代码
        
        Args:
            response (str): 模型响应
        
        Returns:
            str: 提取的Python代码，如果提取失败则返回None
        """
        if not response:
            logger.warning(f"[{self.unit_name}] 响应为空，无法提取Python代码")
            return None
        
        # 尝试从Python代码块中提取代码
        code_match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            logger.info(f"[{self.unit_name}] 成功从Python代码块中提取代码")
            return code
        
        # 如果没有找到Python代码块，尝试查找普通代码块
        code_match = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            logger.info(f"[{self.unit_name}] 成功从普通代码块中提取代码")
            return code
        
        # 检查是否有不完整的代码块开始标记
        if '```python' in response or '``` python' in response:
            # 尝试提取不完整的Python代码块
            code_parts = re.split(r'```python|``` python', response, 1)
            if len(code_parts) > 1:
                code = code_parts[1].strip()
                if code:
                    logger.info(f"[{self.unit_name}] 从不完整的Python代码块中提取代码")
                    return code
        
        # 检查是否有不完整的普通代码块开始标记
        if '```' in response:
            # 尝试提取不完整的普通代码块
            code_parts = re.split(r'```', response, 1)
            if len(code_parts) > 1:
                code = code_parts[1].strip()
                if code:
                    logger.info(f"[{self.unit_name}] 从不完整的普通代码块中提取代码")
                    return code
        
        # 如果仍然没有找到代码块，检查是否整个响应就是代码
        if (response.strip().startswith('import') or 
            response.strip().startswith('def') or
            response.strip().startswith('#') or
            response.strip().startswith('#!/usr/bin/env python') or
            response.strip().startswith('"""') or
            'import pandas as pd' in response or
            'import numpy as np' in response):
            logger.info(f"[{self.unit_name}] 将整个响应作为代码返回")
            return response.strip()
        
        # 如果以上方法都失败，则返回None
        logger.warning(f"[{self.unit_name}] 无法从响应中提取Python代码")
        return None
    
    def execute_code(self, code, file_path):
        """
        执行代码并在出错时尝试修复，最多尝试三次
        
        Args:
            code (str): 要执行的Python代码
            file_path (str): 数据文件路径
        
        Returns:
            tuple: (成功标志, 最终代码, 执行结果)
        """
        logger.info(f"[{self.unit_name}] 开始执行并尝试修复代码...")
        
        # 保存原始代码
        code_file = f"temp_py/{self.unit_name}_code_to_execute_{time.strftime('%Y%m%d%H%M%S')}.py"
        os.makedirs(os.path.dirname(code_file), exist_ok=True)
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        current_attempt = 1
        current_code = code
        
        while current_attempt <= self.max_attempts:
            logger.info(f"[{self.unit_name}] 执行代码尝试 {current_attempt}/{self.max_attempts}")
            
            # 执行代码
            result, error = self._execute_code_in_sandbox(current_code, file_path)
            
            # 如果执行成功，返回结果
            if result and not error:
                logger.info(f"[{self.unit_name}] 代码执行成功（尝试 {current_attempt}/{self.max_attempts}）")
                return True, current_code, result
            
            # 如果是最后一次尝试且失败，则返回失败结果
            if current_attempt == self.max_attempts:
                logger.warning(f"[{self.unit_name}] 达到最大尝试次数 ({self.max_attempts})，终止修复流程")
                return False, current_code, error
            
            # 尝试修复代码
            logger.info(f"[{self.unit_name}] 代码执行失败，尝试修复（尝试 {current_attempt}/{self.max_attempts}）")
            fixed_code = self.fix_analysis_code(current_code, error)
            
            # 如果修复失败，返回失败结果
            if not fixed_code:
                logger.error(f"[{self.unit_name}] 代码修复失败（尝试 {current_attempt}/{self.max_attempts}）")
                return False, current_code, error
            
            # 更新当前代码和尝试次数
            current_code = fixed_code
            current_attempt += 1
        
        # 理论上不会执行到这里，但为了代码完整性，添加一个默认返回值
        return False, current_code, f"[{self.unit_name}] 达到最大尝试次数，终止修复流程"
    
    def _execute_code_in_sandbox(self, code, file_path):
        """
        在沙箱环境中执行Python代码
        
        Args:
            code (str): 要执行的Python代码
            file_path (str): 数据文件路径
        
        Returns:
            tuple: (执行结果, 错误信息)
        """
        logger.info(f"[{self.unit_name}] 在沙箱环境中执行代码...")
        
        # 创建临时文件
        temp_file = f"temp_py/{self.unit_name}_temp_code_{time.strftime('%Y%m%d%H%M%S')}.py"
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
                logger.info(f"[{self.unit_name}] 代码执行成功")
                return stdout, None
            else:
                logger.warning(f"[{self.unit_name}] 代码执行失败，错误码: {process.returncode}")
                return None, stderr
                
        except subprocess.TimeoutExpired:
            logger.error(f"[{self.unit_name}] 代码执行超时")
            return None, "代码执行超时（超过60秒）"
        except Exception as e:
            logger.error(f"[{self.unit_name}] 执行代码时发生异常: {str(e)}")
            return None, str(e)
