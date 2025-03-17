#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型连接器模块 - 负责与大模型API的连接和交互
"""

import json
import logging
import requests
import time
import re
import os

logger = logging.getLogger(__name__)

class ModelConnector:
    """
    模型连接器类，负责与大模型API的连接和交互
    """
    
    def __init__(self, config):
        """
        初始化模型连接器
        
        Args:
            config (dict): 配置信息，可以是完整配置或直接的模型配置
        """
        self.config = config
        
        # 检查配置结构，支持两种格式：
        # 1. 完整配置: {'models': {'conversational': {...}}}
        # 2. 直接模型配置: {'model': '...', 'api_key': '...', ...}
        if 'models' in config and 'conversational' in config['models']:
            # 完整配置格式
            self.model_config = config['models']['conversational']
            self.model_type = self.model_config.get('type', 'openai')
            self.model_id = self.model_config.get('model_id', 'gpt-4')
            self.api_base = self.model_config.get('api_base')
            self.api_key = self.model_config.get('api_key')
            
            # 设置API调用参数
            self.params = self.model_config.get('parameters', {})
            self.timeout = config.get('api', {}).get('timeout_ms', 60000) / 1000  # 转换为秒
            self.max_retries = config.get('api', {}).get('max_retries', 3)
            self.retry_delay = config.get('api', {}).get('retry_delay', 2)
        else:
            # 直接模型配置格式
            self.model_type = config.get('type', 'openai')
            self.model_id = config.get('model', 'gpt-4')
            self.api_base = config.get('api_base')
            self.api_key = config.get('api_key')
            
            # 设置API调用参数
            self.params = {
                'temperature': config.get('temperature', 0.7),
                'max_tokens': config.get('max_tokens', 4000),
                'top_p': config.get('top_p', 0.95)
            }
            self.timeout = config.get('timeout', 60)
            self.max_retries = config.get('retry_count', 3)
            self.retry_delay = config.get('retry_delay', 2)
        
        logger.info(f"初始化模型连接器: 类型={self.model_type}, 模型={self.model_id}")
        logger.info(f"API调用参数: 超时={self.timeout}秒, 最大重试次数={self.max_retries}, 重试间隔={self.retry_delay}秒")
    
    def test_connection(self):
        """
        测试与大模型的连接
        
        Returns:
            bool: 连接测试是否成功
        """
        logger.info("正在测试与大模型的连接...")
        
        try:
            # 简单的测试提示
            prompt = "你好，这是一个测试消息。请回复'连接测试成功'。"
            
            # 调用模型
            response = self.call_model(prompt)
            
            # 检查响应
            if response and "连接测试成功" in response:
                logger.info("连接测试成功")
                return True
            else:
                logger.warning(f"连接测试返回了意外的响应: {response}")
                return False
            
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return False
    
    def call_model(self, prompt, json_mode=False, temperature=None):
        """
        调用大模型API
        
        Args:
            prompt (str): 提示词
            json_mode (bool): 是否使用JSON模式
            temperature (float): 温度参数，如果为None则使用配置中的值
        
        Returns:
            str: 模型响应，如果调用失败则返回None
        """
        # 如果未指定温度参数，使用配置中的值
        if temperature is None:
            temperature = self.params.get('temperature', 0.7)
        
        # 设置代理配置
        proxy = self.params.get('proxy', None)
        proxies = None
        if proxy:
            proxies = {"http": proxy, "https": proxy}
        
        # 添加重试机制
        for retry in range(self.max_retries):
            try:
                logger.info(f"尝试调用API (尝试 {retry+1}/{self.max_retries})...")
                
                # 准备请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # 准备请求体
                payload = {
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.params.get('max_tokens', 4000),
                    "temperature": temperature,
                    "top_p": self.params.get('top_p', 0.95)
                }
                
                # 如果是JSON模式，添加响应格式
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                
                try:
                    # 先尝试使用代理
                    if proxies:
                        logger.info(f"使用代理尝试连接: {proxy}")
                        response = requests.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=self.timeout,
                            proxies=proxies
                        )
                    else:
                        # 如果没有配置代理，直接连接
                        logger.info("直接连接API（无代理）")
                        response = requests.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=self.timeout
                        )
                except requests.exceptions.ProxyError as pe:
                    # 如果代理连接失败，尝试直接连接
                    logger.warning(f"代理连接失败: {str(pe)}，尝试直接连接...")
                    response = requests.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                
                # 检查响应状态
                if response.status_code == 200:
                    response_json = response.json()
                    logger.info(f"API响应状态: {response.status_code} OK")
                    
                    # 尝试从响应中提取内容
                    if "choices" in response_json and response_json["choices"]:
                        if "message" in response_json["choices"][0] and "content" in response_json["choices"][0]["message"]:
                            content = response_json["choices"][0]["message"]["content"]
                            return content
                    
                    # 如果无法提取内容，记录响应并返回适当的错误信息
                    logger.warning(f"API响应格式异常: {response_json}")
                    return None
                else:
                    logger.error(f"API请求失败: 状态码 {response.status_code}, 响应: {response.text}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求异常 (尝试 {retry+1}/{self.max_retries}): {str(e)}")
            
            # 如果不是最后一次重试，等待一段时间后重试
            if retry < self.max_retries - 1:
                retry_wait = self.retry_delay * (retry + 1)  # 指数退避
                logger.info(f"{retry_wait}秒后重试...")
                time.sleep(retry_wait)
        
        logger.error(f"达到最大重试次数 ({self.max_retries})，API调用失败")
        return None
    
    def call_model_stream(self, prompt, json_mode=False, temperature=None):
        """
        流式调用大模型API，实时返回结果
        
        Args:
            prompt (str): 提示词
            json_mode (bool): 是否使用JSON模式
            temperature (float): 温度参数，如果为None则使用配置中的值
        
        Returns:
            generator: 返回一个生成器，可以逐步获取模型响应的片段
        """
        # 如果未指定温度参数，使用配置中的值
        if temperature is None:
            temperature = self.params.get('temperature', 0.7)
        
        # 设置代理配置
        proxy = self.params.get('proxy', None)
        proxies = None
        if proxy:
            proxies = {"http": proxy, "https": proxy}
        
        # 添加重试机制
        for retry in range(self.max_retries):
            try:
                logger.info(f"尝试流式调用API (尝试 {retry+1}/{self.max_retries})...")
                
                # 准备请求头
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # 准备请求体
                payload = {
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.params.get('max_tokens', 65536),  # 增加到64K，确保HTML报告不会被截断
                    "temperature": temperature,
                    "top_p": self.params.get('top_p', 0.95),
                    "stream": True  # 启用流式输出
                }
                
                # 如果是JSON模式，添加响应格式
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                
                try:
                    # 先尝试使用代理
                    if proxies:
                        logger.info(f"使用代理尝试流式连接: {proxy}")
                        response = requests.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=self.timeout,
                            proxies=proxies,
                            stream=True
                        )
                    else:
                        # 如果没有配置代理，直接连接
                        logger.info("直接流式连接API（无代理）")
                        response = requests.post(
                            f"{self.api_base}/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=self.timeout,
                            stream=True
                        )
                except requests.exceptions.ProxyError as pe:
                    # 如果代理连接失败，尝试直接连接
                    logger.warning(f"代理流式连接失败: {str(pe)}，尝试直接连接...")
                    response = requests.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout,
                        stream=True
                    )
                
                # 检查响应状态
                if response.status_code == 200:
                    logger.info(f"API流式响应状态: {response.status_code} OK")
                    
                    print("\n开始接收流式响应...\n")
                    logger.info("开始接收流式响应...")
                    
                    # 处理每个数据块并实时返回内容
                    for chunk in response.iter_lines():
                        if chunk:
                            chunk_str = chunk.decode('utf-8')
                            # 跳过保持连接的行
                            if chunk_str.startswith('data: [DONE]'):
                                continue
                            if chunk_str.startswith('data: '):
                                # 提取JSON部分
                                json_str = chunk_str[6:]  # 去掉 'data: ' 前缀
                                try:
                                    chunk_data = json.loads(json_str)
                                    
                                    # 提取内容
                                    if 'choices' in chunk_data and chunk_data['choices']:
                                        choice = chunk_data['choices'][0]
                                        if 'delta' in choice and 'content' in choice['delta']:
                                            content = choice['delta']['content']
                                            if content:
                                                # 实时打印内容
                                                print(content, end='', flush=True)
                                                logger.debug(f"收到内容片段: {content}")
                                                # 返回内容片段给调用者
                                                yield content
                                except json.JSONDecodeError:
                                    logger.warning(f"无法解析JSON: {json_str}")
                    
                    print("\n\n流式响应接收完成\n")
                    logger.info("流式响应接收完成")
                    return
                else:
                    logger.error(f"API流式请求失败: 状态码 {response.status_code}, 响应: {response.text}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"API流式请求异常 (尝试 {retry+1}/{self.max_retries}): {str(e)}")
            
            # 如果不是最后一次重试，等待一段时间后重试
            if retry < self.max_retries - 1:
                retry_wait = self.retry_delay * (retry + 1)  # 指数退避
                logger.info(f"{retry_wait}秒后重试...")
                time.sleep(retry_wait)
        
        logger.error(f"达到最大重试次数 ({self.max_retries})，API流式调用失败")
        return None

    def analyze_data_structure(self, excel_data):
        """
        分析Excel数据结构
        
        Args:
            excel_data (dict): Excel数据，包含样本数据和列名
        
        Returns:
            dict: 数据结构分析结果，如果分析失败则返回None
        """
        logger.info("正在分析Excel数据结构...")
        
        try:
            # 提取样本数据和列名
            sample_data = excel_data.get('sample_data', [])
            column_names = excel_data.get('column_names', [])
            
            if not sample_data or not column_names:
                logger.error("Excel数据格式错误: 缺少样本数据或列名")
                return None
            
            # 构建提示词
            prompt = f"""
请分析以下Excel数据的结构，并返回JSON格式的分析结果。

列名:
{', '.join(column_names)}

样本数据 (前{len(sample_data)}行):
{sample_data}

请分析每一列的数据类型、可能的值域、是否包含缺失值等信息，并以JSON格式返回分析结果。
JSON结构应该包含以下字段:
1. 每列的名称
2. 每列的推断数据类型 (如数值型、字符串、日期等)
3. 每列的可能值域 (如数值范围、唯一值列表等)
4. 每列是否可能包含缺失值
5. 每列可能适合的图表类型 (如柱状图、折线图、饼图等)
6. 整体数据的结构特点和可能的分析方向

请确保返回的JSON格式正确，可以被Python的json.loads()函数直接解析。
"""
            
            # 调用模型（使用流式API调用）
            logger.info("尝试调用API分析数据结构（流式输出）...")
            print("\n开始分析数据结构...\n")
            
            response = ""
            for chunk in self.call_model_stream(prompt, json_mode=True):
                if chunk:
                    print(chunk, end='', flush=True)
                    response += chunk
            
            print("\n\n数据结构分析完成\n")
            
            if not response:
                logger.error("分析Excel数据结构失败: 模型未返回有效响应")
                return None
            
            # 尝试解析JSON响应
            try:
                structure_analysis = json.loads(response)
                logger.info("成功解析数据结构分析结果")
                return structure_analysis
            except json.JSONDecodeError as e:
                logger.error(f"解析数据结构分析结果失败: {str(e)}")
                
                # 尝试提取JSON部分
                json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    try:
                        structure_analysis = json.loads(json_str)
                        logger.info("成功从代码块中提取并解析数据结构分析结果")
                        return structure_analysis
                    except json.JSONDecodeError:
                        logger.error("从代码块中提取的JSON格式错误")
                
                # 保存完整响应以便调试
                debug_file = f"debug/model_response_debug_{time.strftime('%Y%m%d%H%M%S')}.txt"
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response)
                logger.info(f"已将完整响应内容保存到: {debug_file}")
                
                return None
                
        except Exception as e:
            logger.error(f"分析Excel数据结构时出错: {str(e)}")
            return None

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 测试模型连接器
    from config_loader import load_config
    
    config = load_config()
    if config:
        model = ModelConnector(config)
        model.test_connection()
