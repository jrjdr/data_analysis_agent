#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码生成器模块 - 负责生成Python数据分析代码
"""

import os
import logging
import json
import re
import time

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    代码生成器类，负责生成Python数据分析代码
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
        logger.info("初始化代码生成器")

    def generate_analysis_code(self, structure_analysis, column_names):
        """
        生成数据分析代码

        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表

        Returns:
            str: 生成的Python代码，如果生成失败则返回None
        """
        logger.info("正在生成数据分析代码...")

        try:
            # 将结构分析转换为字符串
            structure_json = json.dumps(structure_analysis, ensure_ascii=False, indent=2)

            # 构建提示词
            prompt = f"""
请根据以下Excel数据结构信息，生成一段简短的Python数据分析代码。

数据结构分析:
{structure_json}

列名:
{', '.join(column_names)}

要求:
1. 生成的代码应该简洁精点，不超过100行
2. 代码应该能够读取CSV文件并进行基础数据分析
3. 只包含最核心的数据统计（如均值、中位数等）和简单的分组分析
4. 代码应该处理可能的缺失值
5. 代码应该将分析结果以简单格式输出到文本文件
6. 代码应该使用pandas库进行数据分析
7. 包含简洁的注释，解释主要分析步骤
8. 不要包含可视化相关代码
     
请生成一个简短的、可执行的Python脚本，包含必要的导入语句和异常处理。代码应该假设CSV文件路径作为命令行参数传入，并将分析结果保存到'analysis_results.txt'文件中。
"""

            # 调用模型（使用流式API调用）
            response = ""
            for chunk in self.model.call_model_stream(prompt):
                if chunk:
                    response += chunk
            
            if not response:
                logger.error("生成数据分析代码失败: 模型未返回有效响应")
                return None
            
            # 提取Python代码
            code = self.extract_python_code(response)
            if not code:
                logger.error("生成数据分析代码失败: 无法从响应中提取Python代码")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return None
            
            logger.info("成功生成数据分析代码")
            
            # 保存生成的代码
            code_file = f"temp_py/analysis_code_{time.strftime('%Y%m%d%H%M%S')}.py"
            os.makedirs(os.path.dirname(code_file), exist_ok=True)
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)
            logger.info(f"已将生成的代码保存到: {code_file}")
            
            return code
            
        except Exception as e:
            logger.error(f"生成数据分析代码时出错: {str(e)}")
            return None

    def generate_default_code(self, file_path, column_info):
        """
        生成默认的数据分析代码（当模型生成失败时使用）
        
        Args:
            file_path (str): 数据文件路径
            column_info (dict): 列信息
        
        Returns:
            str: 默认的Python代码
        """
        logger.info("正在生成默认数据分析代码...")
        
        # 获取数值列和分类列
        numeric_cols = []
        categorical_cols = []
        
        for col, info in column_info.items():
            if info.get('type') in ['int', 'float', 'number']:
                numeric_cols.append(col)
            else:
                categorical_cols.append(col)
        
        # 限制列数，避免代码过长
        numeric_cols = numeric_cols[:3]
        categorical_cols = categorical_cols[:2]
        
        # 构建默认代码
        code = """
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

def analyze_data(file_path):
    \"\"\"
    对CSV文件进行基本数据分析
    
    Args:
        file_path (str): CSV文件路径
    \"\"\"
    print(f"正在分析文件: {file_path}")
    
    # 创建输出文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"analysis_results_{timestamp}.txt"
    
    try:
        # 读取数据
        df = pd.read_csv(file_path)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\\n")
            f.write(f"数据分析报告 - {os.path.basename(file_path)}\\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write("=" * 80 + "\\n\\n")
            
            # 1. 基本信息
            f.write("1. 基本信息\\n")
            f.write("-" * 80 + "\\n")
            f.write(f"行数: {len(df)}\\n")
            f.write(f"列数: {len(df.columns)}\\n")
            f.write(f"列名: {', '.join(df.columns)}\\n\\n")
            
            # 2. 缺失值统计
            f.write("2. 缺失值统计\\n")
            f.write("-" * 80 + "\\n")
            missing_data = df.isnull().sum()
            for col, count in missing_data.items():
                if count > 0:
                    f.write(f"{col}: {count} ({count/len(df):.2%})\\n")
            if missing_data.sum() == 0:
                f.write("无缺失值\\n")
            f.write("\\n")
            
            # 3. 数据类型
            f.write("3. 数据类型\\n")
            f.write("-" * 80 + "\\n")
            for col, dtype in df.dtypes.items():
                f.write(f"{col}: {dtype}\\n")
            f.write("\\n")
"""
        
        # 添加数值列分析
        if numeric_cols:
            code += """
            # 4. 数值列统计
            f.write("4. 数值列统计\\n")
            f.write("-" * 80 + "\\n")
"""
            
            for col in numeric_cols:
                code += f"""
            try:
                f.write(f"{col}:\\n")
                stats = df['{col}'].describe()
                f.write(f"  计数: {{stats['count']}}\\n")
                f.write(f"  均值: {{stats['mean']:.2f}}\\n")
                f.write(f"  标准差: {{stats['std']:.2f}}\\n")
                f.write(f"  最小值: {{stats['min']:.2f}}\\n")
                f.write(f"  25%分位数: {{stats['25%']:.2f}}\\n")
                f.write(f"  中位数: {{stats['50%']:.2f}}\\n")
                f.write(f"  75%分位数: {{stats['75%']:.2f}}\\n")
                f.write(f"  最大值: {{stats['max']:.2f}}\\n\\n")
            except Exception as e:
                f.write(f"分析 {col} 时出错: {{str(e)}}\\n\\n")
"""
        
        # 添加分类列分析
        if categorical_cols:
            code += """
            # 5. 分类列统计
            f.write("5. 分类列统计\\n")
            f.write("-" * 80 + "\\n")
"""
            
            for col in categorical_cols:
                code += f"""
            try:
                f.write(f"{col}:\\n")
                value_counts = df['{col}'].value_counts().head(10)
                for value, count in value_counts.items():
                    f.write(f"  {{value}}: {{count}} ({{count/len(df):.2%}})\\n")
                f.write("\\n")
            except Exception as e:
                f.write(f"分析 {col} 时出错: {{str(e)}}\\n\\n")
"""
        
        # 添加简单的相关性分析
        if len(numeric_cols) >= 2:
            code += """
            # 6. 相关性分析
            f.write("6. 相关性分析\\n")
            f.write("-" * 80 + "\\n")
            try:
                numeric_df = df.select_dtypes(include=['number'])
                if len(numeric_df.columns) >= 2:
                    corr = numeric_df.corr()
                    f.write("数值列相关性 (Pearson):\\n")
                    for i, col1 in enumerate(corr.columns):
                        for col2 in corr.columns[i+1:]:
                            f.write(f"  {col1} 与 {col2}: {corr.loc[col1, col2]:.4f}\\n")
                else:
                    f.write("数值列不足，无法计算相关性\\n")
            except Exception as e:
                f.write(f"计算相关性时出错: {str(e)}\\n")
            f.write("\\n")
"""
        
        # 添加简单的分组分析
        if categorical_cols and numeric_cols:
            code += """
            # 7. 简单分组分析
            f.write("7. 简单分组分析\\n")
            f.write("-" * 80 + "\\n")
"""
            
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            code += f"""
            try:
                # 按分类列分组，计算数值列的统计量
                group_stats = df.groupby('{cat_col}')['{num_col}'].agg(['mean', 'median', 'std', 'min', 'max']).reset_index()
                f.write(f"分组统计 (前10项):\\n")
                for idx, row in group_stats.head(10).iterrows():
                    f.write(f"- {{row['{cat_col}']}}:\\n")
                    f.write(f"  平均值: {{row['mean']:.2f}}, 中位数: {{row['median']:.2f}}, ")
                    f.write(f"标准差: {{row['std']:.2f}}, 最小值: {{row['min']:.2f}}, 最大值: {{row['max']:.2f}}\\n")
                f.write("\\n")
            except Exception as e:
                f.write(f"分析 {cat_col} 和 {num_col} 时出错: {{str(e)}}\\n\\n")
"""
        
        # 添加结论
        code += """
            # 结论
            f.write("8. 分析结论\\n")
            f.write("-" * 80 + "\\n")
            f.write("这是一个自动生成的数据分析报告，包含了基本的统计分析。\\n")
            f.write("请根据以上分析结果，结合业务场景进行进一步解读。\\n\\n")
            
            f.write("=" * 80 + "\\n")
            f.write("分析完成\\n")
        
        print(f"分析完成，结果已保存到: {output_file}")
    
    except Exception as e:
        print(f"分析过程中出错: {str(e)}")
        return None
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python script.py <csv文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_data(file_path)
"""
        
        return code

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
            
            # 调用模型
            response = self.model.call_model(prompt)
            if not response:
                logger.error("修复数据分析代码失败: 模型未返回有效响应")
                return None
            
            # 提取Python代码
            fixed_code = self.extract_python_code(response)
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

    def extract_python_code(self, response):
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

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试代码生成器
    print("请在主程序中测试代码生成器")
