#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单元3：比例分析 - 负责生成数据的比例和分布分析
"""

import logging
from .base_analysis_unit import BaseAnalysisUnit, NumpyEncoder
import json

logger = logging.getLogger(__name__)

class PieChartAnalysisUnit(BaseAnalysisUnit):
    """
    比例分析单元，负责生成数据的比例和分布分析数据
    """
    
    def __init__(self, model, config):
        """
        初始化比例分析单元
        
        Args:
            model: 模型连接器对象
            config (dict): 配置信息
        """
        super().__init__(model, config)
        self.unit_name = "比例分析单元"
    
    def get_prompt(self, structure_analysis, column_names, csv_path):
        """
        获取提示词
        
        Args:
            structure_analysis (dict): 数据结构分析结果
            column_names (list): 列名列表
            csv_path (str): CSV文件路径
            
        Returns:
            str: 提示词
        """
        return f"""
分析CSV文件中的数据，并生成比例分析。

CSV文件路径: {csv_path}
列名: {', '.join(column_names)}

数据结构分析:
{json.dumps(structure_analysis, ensure_ascii=False, indent=2, cls=NumpyEncoder)}

请编写Python代码，完成以下任务:
1. 读取CSV文件
2. 分析分类列的分布情况
3. 计算各类别的占比
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
1. 分析结果应包含各类别的数量和占比
2. 结果应保存到"pngs/category_distribution_results.txt"
3. 结果格式应清晰易读，包含适当的章节标题和分隔符

请生成完整的Python代码。
"""
