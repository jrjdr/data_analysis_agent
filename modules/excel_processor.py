#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel处理器模块 - 负责读取和处理Excel文件
"""

import os
import pandas as pd
import logging
import csv
from io import StringIO

logger = logging.getLogger(__name__)

class ExcelProcessor:
    """
    Excel处理器类，负责读取和处理Excel文件
    """
    
    def __init__(self, config):
        """
        初始化Excel处理器
        
        Args:
            config (dict): 配置信息
        """
        self.config = config
        self.excel_file = config['analysis']['excel_file']
        self.excel_path = os.path.join(os.getcwd(), self.excel_file)
        self.df = None
        self.column_names = []
        
        logger.info(f"初始化Excel处理器: 文件={self.excel_file}")
    
    def load_sample_data(self, max_rows=50):
        """
        加载Excel文件的样本数据（前N行）
        
        Args:
            max_rows (int): 最大加载行数，默认为50
        
        Returns:
            dict: 包含样本数据和列名的字典，如果加载失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.excel_path):
                logger.error(f"Excel文件不存在: {self.excel_path}")
                return None
            
            # 读取Excel文件
            self.df = pd.read_excel(self.excel_path, nrows=max_rows)
            rows_count, cols_count = self.df.shape
            self.column_names = self.df.columns.tolist()
            
            logger.info(f"成功加载Excel文件: {self.excel_path}, 读取了 {rows_count} 行和 {cols_count} 列")
            logger.info(f"列名: {self.column_names}")
            
            # 将数据转换为CSV格式的字符串
            csv_buffer = StringIO()
            self.df.to_csv(csv_buffer, index=False)
            sample_csv = csv_buffer.getvalue()
            
            return {
                'sample_csv': sample_csv,
                'column_names': self.column_names,
                'rows_count': rows_count,
                'cols_count': cols_count
            }
            
        except Exception as e:
            logger.error(f"加载Excel样本数据时出错: {str(e)}")
            return None
    
    def load_full_data(self):
        """
        加载Excel文件的完整数据
        
        Returns:
            pandas.DataFrame: 完整的数据框，如果加载失败则返回None
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.excel_path):
                logger.error(f"Excel文件不存在: {self.excel_path}")
                return None
            
            # 读取Excel文件
            self.df = pd.read_excel(self.excel_path)
            rows_count, cols_count = self.df.shape
            self.column_names = self.df.columns.tolist()
            
            logger.info(f"成功加载完整Excel数据: {self.excel_path}, 读取了 {rows_count} 行和 {cols_count} 列")
            
            return self.df
            
        except Exception as e:
            logger.error(f"加载完整Excel数据时出错: {str(e)}")
            return None
    
    def get_column_names(self):
        """
        获取Excel文件的列名
        
        Returns:
            list: 列名列表
        """
        return self.column_names
    
    def save_to_csv(self, df=None, output_path=None):
        """
        将数据保存为CSV文件
        
        Args:
            df (pandas.DataFrame, optional): 要保存的数据框，如果为None则使用当前加载的数据
            output_path (str, optional): 输出文件路径，如果为None则使用默认路径
        
        Returns:
            str: 保存的文件路径，如果保存失败则返回None
        """
        try:
            # 如果未指定数据框，使用当前加载的数据
            if df is None:
                df = self.df
            
            # 如果数据框为空，返回错误
            if df is None or df.empty:
                logger.error("没有数据可保存")
                return None
            
            # 如果未指定输出路径，使用默认路径
            if output_path is None:
                output_path = os.path.join(os.getcwd(), 'temp_py', f'temp_data_{pd.Timestamp.now().strftime("%Y%m%d%H%M%S")}.csv')
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存数据
            df.to_csv(output_path, index=False)
            logger.info(f"成功将数据保存到: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"保存数据到CSV时出错: {str(e)}")
            return None

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试Excel处理器
    from config_loader import load_config
    
    config = load_config()
    if config:
        processor = ExcelProcessor(config)
        sample_data = processor.load_sample_data()
        if sample_data:
            print(f"样本数据加载成功: {sample_data['rows_count']} 行, {sample_data['cols_count']} 列")
            print(f"列名: {sample_data['column_names']}")
            print("样本CSV数据:")
            print(sample_data['sample_csv'][:500] + "...")
