#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单元4：时间趋势分析 - 负责生成时间序列和趋势分析
"""

import logging
from .base_analysis_unit import BaseAnalysisUnit, NumpyEncoder
import json

logger = logging.getLogger(__name__)

class TimeTrendAnalysisUnit(BaseAnalysisUnit):
    """
    时间趋势分析单元，负责生成时间序列和趋势分析数据
    """
    
    def __init__(self, model, config):
        """
        初始化时间趋势分析单元
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        super().__init__(model, config)
        self.unit_name = "时间趋势分析单元"
    
    def _build_prompt(self, structure_analysis, column_names, data_context=None):
        """
        构建提示词
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            data_context (dict, optional): 之前分析单元的结果和上下文
            
        Returns:
            str: 构建的提示词
        """
        # 将结构分析转换为字符串表示
        structure_str = str(structure_analysis)
        
        # 如果有前一个单元的上下文，则包含在提示中
        context_str = ""
        if data_context:
            context_parts = []
            if "general_statistics" in data_context:
                context_parts.append(f"总体统计分析结果: {data_context['general_statistics']}")
            
            if context_parts:
                context_str = "\n前一个分析单元的结果:\n" + "\n".join(context_parts) + "\n\n请基于上述分析结果，进行更深入的时间趋势分析。"
        
        prompt = f"""
分析CSV文件中的数据，并生成时间趋势分析。

列名: {', '.join(column_names)}

数据结构分析:
{json.dumps(structure_analysis, ensure_ascii=False, indent=2, cls=NumpyEncoder)}

请编写Python代码，完成以下任务:
1. 读取CSV文件
2. 识别时间列并将其转换为适当的日期时间格式
3. 分析时间序列数据的趋势和模式
4. 将分析结果保存为纯文本格式

代码要求:
1. 使用pandas库进行数据分析
2. 确保代码健壮，包含错误处理
3. 代码简洁，不超过100行（不包括注释）
4. 不需要生成图表或可视化内容
5. 不要使用JSON格式保存结果，而是使用纯文本格式，避免NumPy数据类型序列化问题
   - 将所有分析结果格式化为可读的文本内容
   - 使用适当的标题、分隔符和缩进使结果易于阅读

输出要求:
1. 分析结果应包含时间趋势、周期性模式和异常点
2. 结果应保存到"pngs/time_trend_results.txt"
3. 结果格式应清晰易读，包含适当的章节标题和分隔符

请生成完整的Python代码。
"""
        return prompt
        
    def get_prompt(self, structure_analysis, column_names, csv_file_path, data_context=None):
        """
        获取用于生成分析代码的提示词
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            csv_file_path (str): CSV文件路径
            data_context (dict, optional): 之前分析单元的结果和上下文
            
        Returns:
            str: 构建的提示词
        """
        # 添加文件路径到提示词中
        prompt = self._build_prompt(structure_analysis, column_names, data_context)
        prompt = prompt.replace("请编写Python代码", f"CSV文件路径: {csv_file_path}\n\n请编写Python代码")
        return prompt
