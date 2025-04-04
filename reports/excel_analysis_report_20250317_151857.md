# 服务器性能数据分析报告

## 1. 数据概览

本报告基于2025年2月28日00:00:00至23:59:00的服务器性能数据进行分析。数据包含10台服务器的详细性能指标，总计14,400条记录。

### 1.1 基本信息

| 项目 | 数值 |
|------|------|
| 记录总数 | 14,400 |
| 数据时间范围 | 2025-02-28 00:00:00 至 2025-02-28 23:59:00 |
| 服务器数量 | 10 |
| 资源类型 | server, database |

### 1.2 服务器分布

| 服务器ID | 服务器名称 | 类型 | 记录数 |
|----------|------------|------|--------|
| SRV001 | 主应用服务器 | server | 1,440 |
| SRV002 | 备份应用服务器 | server | 1,440 |
| SRV003 | 数据处理服务器 | server | 1,440 |
| SRV004 | 缓存服务器 | server | 1,440 |
| SRV005 | 负载均衡服务器 | server | 1,440 |
| DB001 | MySQL主数据库 | database | 1,440 |
| DB002 | MySQL从数据库 | database | 1,440 |
| DB003 | Redis缓存数据库 | database | 1,440 |
| DB004 | MongoDB文档数据库 | database | 1,440 |
| DB005 | Elasticsearch搜索数据库 | database | 1,440 |

### 1.3 事件类型分布

| 事件类型 | 次数 | 占比 |
|----------|------|------|
| normal | 14,103 | 97.94% |
| network_issue | 122 | 0.85% |
| high_load | 92 | 0.64% |
| db_slowdown | 62 | 0.43% |
| memory_leak | 21 | 0.15% |

## 2. 数据洞察

### 2.1 关键性能指标统计

| 指标 | 最小值 | 最大值 | 平均值 | 中位数 | 标准差 |
|------|--------|--------|--------|--------|--------|
| CPU使用率 | 5.58% | 100.00% | 37.58% | 31.62% | 20.65% |
| 内存使用率 | 27.41% | 100.00% | 53.57% | 51.70% | 15.33% |
| 磁盘使用率 | 50.00% | 89.16% | 52.84% | 50.00% | 5.81% |
| 网络流量 | 5.22% | 100.00% | 38.25% | 32.30% | 21.58% |
| 每秒查询率 | 51.60 | 1242.16 | 349.16 | 242.72 | 246.15 |
| 活跃连接数 | 5.09 | 196.48 | 40.83 | 31.25 | 28.10 |
| 缓存命中率 | 27.49% | 99.81% | 84.69% | 85.52% | 7.98% |
| 平均查询时间 | 8.22ms | 246.53ms | 18.01ms | 16.87ms | 12.64ms |

### 2.2 资源使用情况分析