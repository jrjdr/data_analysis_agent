#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代码执行器模块 - 负责执行生成的Python数据分析代码
"""

import os
import sys
import logging
import tempfile
import traceback
import subprocess
import pandas as pd
from io import StringIO
import time

logger = logging.getLogger(__name__)

class CodeExecutor:
    """
    代码执行器类，负责执行生成的Python数据分析代码
    """
    
    def __init__(self):
        """
        初始化代码执行器
        """
        self.error_message = None
        logger.info("初始化代码执行器")
    
    def execute_code(self, code, data_df):
        """
        执行生成的Python代码
        
        Args:
            code (str): 要执行的Python代码
            data_df (pandas.DataFrame): 数据框
        
        Returns:
            tuple: (执行结果, 输出文件路径)，如果执行失败则返回(False, None)
        """
        logger.info("正在执行生成的Python代码...")
        
        try:
            # 清除之前的错误信息
            self.error_message = None
            
            # 保存数据框到临时CSV文件
            temp_dir = os.path.join(os.getcwd(), 'temp_py')
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = time.strftime('%Y%m%d%H%M%S')
            temp_csv = os.path.join(temp_dir, f'temp_data_{timestamp}.csv')
            data_df.to_csv(temp_csv, index=False)
            logger.info(f"已将数据保存到临时CSV文件: {temp_csv}")
            
            # 创建临时Python脚本文件
            temp_py = os.path.join(temp_dir, f'temp_script_{timestamp}.py')
            with open(temp_py, 'w', encoding='utf-8') as f:
                f.write(code)
            logger.info(f"已将代码保存到临时Python脚本文件: {temp_py}")
            
            # 创建输出文件路径
            output_file = os.path.join(os.getcwd(), 'reports', f'analysis_results_{timestamp}.txt')
            
            # 使用subprocess执行代码
            logger.info("开始执行Python脚本...")
            result = subprocess.run(
                [sys.executable, temp_py, temp_csv],
                capture_output=True,
                text=True,
                timeout=300  # 设置超时时间为5分钟
            )
            
            # 检查执行结果
            if result.returncode == 0:
                logger.info("Python脚本执行成功")
                
                # 检查是否生成了分析结果文件
                if os.path.exists('analysis_results.txt'):
                    # 如果文件在当前目录，移动到指定位置
                    os.rename('analysis_results.txt', output_file)
                    logger.info(f"已将分析结果文件移动到: {output_file}")
                elif os.path.exists(os.path.join(temp_dir, 'analysis_results.txt')):
                    # 如果文件在临时目录，移动到指定位置
                    os.rename(os.path.join(temp_dir, 'analysis_results.txt'), output_file)
                    logger.info(f"已将分析结果文件移动到: {output_file}")
                else:
                    # 如果找不到分析结果文件，创建一个包含脚本输出的文件
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write("脚本执行成功，但未生成分析结果文件。以下是脚本的输出：\n\n")
                        f.write(result.stdout)
                    logger.warning("未找到分析结果文件，已创建包含脚本输出的文件")
                
                return True, output_file
            else:
                logger.error(f"Python脚本执行失败，返回码: {result.returncode}")
                logger.error(f"标准输出: {result.stdout}")
                logger.error(f"标准错误: {result.stderr}")
                
                # 保存错误信息
                self.error_message = result.stderr
                
                # 创建错误报告
                error_file = os.path.join(os.getcwd(), 'debug', f'execution_error_{timestamp}.txt')
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"执行时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"返回码: {result.returncode}\n\n")
                    f.write("标准输出:\n")
                    f.write(result.stdout)
                    f.write("\n\n标准错误:\n")
                    f.write(result.stderr)
                    f.write("\n\n执行的代码:\n")
                    f.write(code)
                logger.info(f"已将错误信息保存到: {error_file}")
                
                return False, None
            
        except subprocess.TimeoutExpired:
            logger.error("Python脚本执行超时")
            self.error_message = "执行超时（超过5分钟）"
            return False, None
            
        except Exception as e:
            logger.error(f"执行Python代码时出错: {str(e)}")
            logger.error(traceback.format_exc())
            self.error_message = str(e)
            return False, None
    
    def get_error_message(self):
        """
        获取执行过程中的错误信息
        
        Returns:
            str: 错误信息，如果没有错误则返回None
        """
        return self.error_message

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试代码执行器
    print("请在主程序中测试代码执行器")
