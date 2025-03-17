# 智能数据分析助手

一个基于大型语言模型的智能数据分析工具，能够自动分析Excel文件并生成详细的Markdown和HTML报告。系统支持多种数据分析单元，并能通过大模型生成丰富的分析内容。

## 项目结构

项目采用模块化设计，主要组件包括：

```
smolagent/
├── main.py                    # 主程序入口
├── config.yaml                # 配置文件
├── markdown_to_html.py        # Markdown转HTML渲染器
├── modules/                   # 模块目录
│   ├── __init__.py            # 模块初始化文件
│   ├── model_connector.py     # 模型连接器，负责与API通信
│   ├── excel_analyzer.py      # Excel分析器，负责处理Excel文件
│   ├── code_generator.py      # 代码生成器，负责生成分析代码
│   ├── report_generator.py    # 基础报告生成器
│   ├── markdown_report_generator.py   # Markdown报告生成器
│   ├── enhanced_markdown_report_generator.py # 增强型Markdown报告生成器
│   ├── chart_generator.py     # 图表生成器
│   ├── analysis_dispatcher.py # 分析调度器，协调各分析单元
│   └── analysis_units/        # 分析单元目录
│       ├── __init__.py        # 分析单元包初始化
│       ├── base_analysis_unit.py       # 基础分析单元类
│       ├── unit1_general_statistics.py # 通用统计分析单元
│       ├── unit2_bar_chart_analysis.py # 条形图分析单元
│       ├── unit3_pie_chart_analysis.py # 饼图分析单元
│       ├── unit4_time_trend_analysis.py # 时间趋势分析单元
│       └── unit5_correlation_analysis.py # 相关性分析单元
├── sample_data/               # 示例数据目录
├── reports/                   # 生成的报告目录
├── temp_csv/                  # 临时CSV文件目录
├── temp_py/                   # 临时Python代码目录
└── temp_txts/                 # 临时文本文件目录
```

## 功能特点

1. **模块化设计**：将数据分析过程分解为多个功能单元，便于维护和扩展
2. **自动分析**：自动识别数据类型和结构，生成相应的分析代码
3. **错误处理**：内置错误检测和修复机制，提高分析成功率
4. **大模型增强**：利用大型语言模型生成丰富的分析报告内容
5. **Markdown报告**：生成基于Markdown格式的详细报告，支持文本、表格和图表
6. **HTML渲染**：将Markdown报告转换为美观的HTML页面，支持Mermaid.js图表
7. **流式输出**：所有与大模型的交互采用流式输出，方便用户观察分析过程
8. **综合报告**：汇总所有分析单元的结果，生成全面的综合分析报告

## 分析单元

系统包含以下五个专门的分析单元：

1. **通用统计分析单元**：提供数据的基本统计信息，如均值、中位数、标准差等
2. **条形图分析单元**：进行类别比较分析，适合用条形图展示的数据
3. **饼图分析单元**：进行占比分析，适合用饼图展示的数据
4. **时间趋势分析单元**：分析时间序列数据，识别趋势和模式
5. **相关性分析单元**：分析变量间的相关性，找出潜在的关联关系

## 报告生成流程

1. **数据分析**：各分析单元执行数据分析，生成分析结果
2. **单元报告**：为每个分析单元生成独立的Markdown报告
   - 使用大模型生成丰富的分析内容
   - 支持文本、表格和图表（包括Mermaid.js图表）
3. **综合报告**：汇总所有分析单元的结果，生成综合分析报告
4. **HTML渲染**：将Markdown报告转换为HTML格式
   - 使用markdown_to_html.py程序渲染
   - 支持代码高亮和Mermaid.js图表
5. **自动打开**：自动在浏览器中打开生成的HTML报告

## 使用方法

### 安装依赖

```bash
pip install -r requirements.txt
```

### 设置API密钥

设置环境变量：

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

或者在配置文件中设置：

```yaml
# config.yaml
model:
  api_key: your_api_key_here
```

### 配置分析参数

编辑config.yaml文件：

```yaml
# 分析配置
analysis:
  # 要分析的Excel文件（相对于当前目录）
  excel_file: 'sample_data/network_traffic_data_2025_02.xlsx'
  
  # 默认生成的图表类型
  default_charts:
    - bar
    - pie
    - line
```

### 运行分析

```bash
python main.py
```

或者指定配置文件：

```bash
python main.py --config custom_config.yaml
```

## 开发说明

### 添加新的分析单元

1. 在 `modules/analysis_units/` 目录下创建新的分析单元文件
2. 继承 `BaseAnalysisUnit` 类并实现必要的方法
3. 在 `modules/analysis_units/__init__.py` 中导入新单元
4. 在 `analysis_dispatcher.py` 中注册新单元

### 调试

系统会在以下目录生成临时文件和日志，便于调试：

- `logs/`: 应用日志
- `temp_csv/`: 临时CSV文件
- `temp_py/`: 临时Python代码
- `temp_txts/`: 临时文本文件
- `reports/`: 生成的Markdown和HTML报告

## 示例数据

项目包含多个示例数据文件，位于sample_data目录：

1. **network_performance_data_2025_Q1.xlsx**: 网络性能数据
2. **customer_complaints_data_2025_Q1.xlsx**: 客户投诉数据
3. **network_equipment_inventory_2025.xlsx**: 网络设备库存数据
4. **network_traffic_data_2025_02.xlsx**: 网络流量数据
5. **telecom_subscriber_data_2025.xlsx**: 电信用户数据

## 许可证

MIT
