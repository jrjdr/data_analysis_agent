#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置加载模块 - 负责从config.yaml加载配置信息
"""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

def load_config(config_path='config.yaml'):
    """
    从config.yaml加载配置信息
    
    Args:
        config_path (str): 配置文件路径，默认为'config.yaml'
    
    Returns:
        dict: 配置信息，如果加载失败则返回None
    """
    try:
        # 确保配置文件存在
        if not os.path.exists(config_path):
            logger.error(f"配置文件不存在: {config_path}")
            return None
        
        # 加载配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证配置文件中的必要字段
        required_fields = [
            'models.conversational.type',
            'models.conversational.api_base',
            'models.conversational.api_key',
            'models.conversational.model_id',
            'analysis.excel_file'
        ]
        
        for field in required_fields:
            parts = field.split('.')
            current = config
            for part in parts:
                if part not in current:
                    logger.error(f"配置文件缺少必要字段: {field}")
                    return None
                current = current[part]
        
        logger.info("成功加载配置文件")
        return config
    
    except Exception as e:
        logger.error(f"加载配置文件时出错: {str(e)}")
        return None

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试加载配置
    config = load_config()
    if config:
        print("配置加载成功:")
        print(f"- 模型类型: {config['models']['conversational']['type']}")
        print(f"- 模型ID: {config['models']['conversational']['model_id']}")
        print(f"- Excel文件: {config['analysis']['excel_file']}")
    else:
        print("配置加载失败")
