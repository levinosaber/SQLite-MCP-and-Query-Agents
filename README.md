# 垃圾监管系统 MCP Server

基于SQLite数据库的垃圾监管系统，提供生活垃圾和装修垃圾监管功能，使用MCP (Model Context Protocol) 协议实现。

## 系统功能

### 生活垃圾监管
1. **展示全区清运实时数据** - 查看指定日期的清运概览和明细
2. **筛选查询各街道清运数量** - 按时间段和街道统计清运数据
3. **整治逾期混运等问题** - 监控小包垃圾超时和垃圾桶满溢问题

### 装修垃圾监管
4. **接入新旧模式预约数据** - 整合新旧预约模式的数据
5. **查看各状态工单详情** - 查询和统计不同状态的工单

### 辅助功能
- 数据质量检查
- 获取可用数据日期范围

## 项目结构

```
shanghaichengdi/
├── mcp_server.py              # MCP Server主程序
├── sqlite_operations.py       # SQLite数据库操作逻辑
├── test_garbage_monitoring.py # 完整测试套件
├── config.py                  # 系统配置
├── requirements.txt           # Python依赖
├── README.md                  # 项目说明
└── data/                      # 数据文件目录
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 运行测试

```bash
python test_garbage_monitoring.py
```

测试将自动：
- 创建测试数据库
- 插入模拟数据
- 测试所有5个核心功能
- 验证数据一致性
- 测试MCP Server功能

### 2. 启动MCP Server

```bash
python mcp_server.py [数据库路径]
```

如果不指定数据库路径，默认使用 `garbage_monitoring.db`

### 3. 可用的MCP工具

#### 生活垃圾监管工具

- `get_realtime_clearance_data`: 获取实时清运数据
  ```json
  {
    "date": "2024-01-15"  // 可选，默认今天
  }
  ```

- `get_street_clearance_statistics`: 获取街道清运统计
  ```json
  {
    "start_date": "2024-01-15",
    "end_date": "2024-01-16",
    "street_name": "陆家嘴街道"  // 可选
  }
  ```

- `get_overdue_issues`: 获取逾期问题
  ```json
  {}
  ```

#### 装修垃圾监管工具

- `get_decoration_appointments_data`: 获取预约数据
  ```json
  {
    "days_back": 30  // 可选，默认30天
  }
  ```

- `get_order_status_details`: 获取工单状态详情
  ```json
  {
    "status": "已完成",     // 可选，筛选状态
    "mode": "老模式"       // 可选，筛选模式
  }
  ```

#### 辅助工具

- `check_data_quality`: 检查数据质量
- `get_available_date_range`: 获取数据日期范围

## 数据库表结构

系统使用以下SQLite表：

1. **garbage_data** - 干湿垃圾数据
2. **small_package_garbage** - 小包垃圾落地详情
3. **garbage_bin_overflow** - 垃圾桶满溢详情
4. **decoration_garbage_old** - 装修垃圾预约（老模式）
5. **decoration_garbage_new** - 装修垃圾预约（新模式）

详细字段定义请参考原始数据描述文档。

## 开发说明

### 添加新功能

1. 在 `sqlite_operations.py` 中添加新的查询方法
2. 在 `mcp_server.py` 中注册新工具
3. 在 `test_garbage_monitoring.py` 中添加测试用例
4. 更新 `config.py` 中的功能描述

### 测试覆盖

- 数据库连接测试
- 5个核心功能测试
- 数据一致性验证
- MCP Server集成测试
- 端到端工作流程测试

## 依赖说明

- **mcp**: Model Context Protocol实现
- **pandas**: 数据处理（可选，用于扩展功能）
- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持
- **sqlite3**: Python内置，无需安装

## 日志

系统日志配置在 `config.py` 中，支持：
- 控制台输出（INFO级别）
- 文件记录（DEBUG级别）
- 详细的调用追踪

## 后续扩展

这个MCP Server为后续的AI Agent系统提供基础：
- 可以被LangChain/LangGraph调用
- 支持复杂的垃圾监管分析
- 可扩展更多数据源和功能

## 技术特点

- 🚀 **高性能**: SQLite内存操作，快速响应
- 🔒 **可靠性**: 完整的错误处理和日志记录  
- 🧪 **可测试**: 全面的测试覆盖和模拟数据
- 🔌 **可扩展**: MCP协议支持，易于集成
- 📊 **数据完整**: 支持5个核心监管场景

---

💡 **提示**: 如需帮助或发现问题，请查看测试输出或日志文件 `garbage_monitoring.log` 