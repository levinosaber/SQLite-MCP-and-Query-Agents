#!/usr/bin/env python3
"""
垃圾监管系统AI智能体
基于LangGraph官方MCP适配器实现智能查询工作流
"""
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import asyncio

# LangGraph和LangChain相关导入
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# MCP适配器导入
from langchain_mcp_adapters.client import MultiServerMCPClient

# === VS Code 调试桥 ===
# import debugpy
# debugpy.listen(("0.0.0.0", 5678))    # 端口随意
# print("Waiting for debugger attach on 5678...")
# debugpy.wait_for_client()            # 先挂起，连上后才继续
# =======================

# 定义结构化输出模型
class AgentResponse(BaseModel):
    """Agent的结构化响应"""
    if_continue: bool = Field(description="是否需要用户继续提供信息")
    returned_content: str = Field(description="返回的内容，如果if_continue为True则为空")


def get_project_root():
    """获取项目根目录"""
    # 从当前脚本文件的位置开始查找项目根目录
    current_path = Path(__file__).parent
    
    # 如果当前在agents目录，则向上一级
    if current_path.name == "agents":
        return current_path.parent
    
    # 否则查找包含标识文件的目录
    markers = ['pyproject.toml', 'setup.py', 'requirements.txt', '.git']
    while current_path != current_path.parent:
        for marker in markers:
            if (current_path / marker).exists():
                return current_path
        current_path = current_path.parent
    
    # 如果找不到，返回当前脚本所在目录的父目录
    return Path(__file__).parent.parent

PROJECT_ROOT = get_project_root()
MCP_SERVER_PATH = str(PROJECT_ROOT / "mcp_server_fast.py")
OUTPUT_DIR = PROJECT_ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

class GarbageMonitoringAgent:
    """垃圾监管AI智能体"""
    
    def __init__(self):
        """初始化智能体"""
        self.mcp_client = None
        self.agent = None
        self.tools = None
        
    async def initialize(self):
        """初始化MCP客户端和工具"""
        print("🔧 正在初始化MCP客户端...")
        
        # 配置MCP服务器
        self.mcp_client = MultiServerMCPClient({
            "garbage_monitoring": {
                "command": "python",
                "args": [MCP_SERVER_PATH],
                "transport": "stdio",
            }
        })
        
        # 获取工具
        self.tools = await self.mcp_client.get_tools()
        print(f"✅ 成功加载 {len(self.tools)} 个MCP工具")
        
        # 初始化LLM
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
            temperature=0.1
        )
        
        # 系统提示词
        system_prompt = """
你是一个垃圾监管系统的AI助手，专门帮助用户查询和分析垃圾管理相关数据。

## 系统背景
你有权访问一个完整的垃圾监管SQLite数据库，包含以下数据表的详细结构：

### 1. garbage_data (干湿垃圾数据)
- 主要字段：
  * id (TEXT): 主键
  * area_name (TEXT): 区
  * street_name (TEXT): 街道
  * community_name (TEXT): 小区名称
  * car_group_name (TEXT): 车队
  * load_time_str (TEXT): 清运时间，格式为YYYY-MM-DD HH:MM:SS
  * vehicle_license_num (TEXT): 车牌
  * garbage_weight (TEXT): 清运量，注意是TEXT类型，需要CAST转换
  * type_name (TEXT): 垃圾类型
  * community_type_name (TEXT): 小区类型名称

### 2. small_package_garbage (小包垃圾落地详情)
- 主要字段：
  * event_id (TEXT): 事件ID，主键
  * station_name (TEXT): 垃圾房名称
  * division_name (TEXT): 区划名称
  * community_name (TEXT): 小区名称
  * drop_time (TEXT): 落地时间
  * handle_time (TEXT): 处置时间
  * is_handle (TEXT): 但实际存在数据库中的是TRUE或者FALSE，字符串类型
  * is_timeout (TEXT): 但实际存在数据库中的是TRUE或者FALSE，字符串类型
  * take_minutes (REAL): 处置耗时分钟

### 3. garbage_bin_overflow (垃圾桶满溢详情)
- 主要字段：
  * event_id (TEXT): 事件ID，主键
  * station_name (TEXT): 垃圾房名称
  * division_name (TEXT): 区划名称
  * community_name (TEXT): 小区名称
  * full_time (TEXT): 第一次满溢时间
  * handle_time (TEXT): 处置时间
  * is_handle (TEXT): 但实际存在数据库中的是TRUE或者FALSE，字符串类型

### 4. decoration_garbage_old (装修垃圾预约-老模式)
- 主要字段：
  * bg_order_id (INTEGER): 预约单id，主键
  * street_name (TEXT): 街道
  * community_name (TEXT): 小区名
  * order_state (TEXT): 状态码（重要：7=已完成）
  * order_state_desc (TEXT): 状态描述（已完成/已超时）
  * create_time_str (TEXT): 上报时间
  * estimate_clear_time_str (TEXT): 预约清运时间
  * finish_time_str (TEXT): 完成时间
  * is_over_time (TEXT): 超时完成，值为'是'或其他
  * garbage_weight (REAL): 预约量（袋）
  * vehicle_license_num (TEXT): 车牌号

### 5. decoration_garbage_new (装修垃圾预约-新模式)
- 主要字段：
  * appointment_order_id (TEXT): 预约单号，主键
  * street_name (TEXT): 街道
  * community_name (TEXT): 小区
  * address (TEXT): 详细地址
  * decoration_stage (TEXT): 装修阶段
  * resident_appointment_time (TEXT): 居民预约时间
  * appointment_bags_number (INTEGER): 预约投放袋数
  * create_order_time (TEXT): 建单时间
  * order_state (TEXT): 预约单状态（已完成/已超时）

### 6. unit_details (单位详情)
- 主要字段：
  * id (INTEGER): 主键
  * street (TEXT): 街道
  * unit_name (TEXT): 单位名称
  * unit_address (TEXT): 单位地址

### 7. shop_details (商铺详情)
- 主要字段：
  * id (TEXT): 主键
  * company_name (TEXT): 商铺名称
  * company_town_string (TEXT): 街道
  * company_addr (TEXT): 地址

### 8. contract_details (合同详情)
- 主要字段：
  * guid (TEXT): 主键
  * code (TEXT): 合同编号
  * company_name (TEXT): 产生单位名称
  * company_town_string (TEXT): 产生单位街道

### 9. inspection_details (巡检详情)
- 主要字段：
  * id (TEXT): 主键
  * createtime (TEXT): 巡查时间
  * total (REAL): 扣分
  * town (TEXT): 街道
  * village (TEXT): 居委

### 10. residential_inspection (居民区巡检)
- 主要字段：
  * 居住区名称 (TEXT)
  * 巡查数 (INTEGER)
  * 问题数 (INTEGER)
  * 整改数 (INTEGER)

### 11. clearance_unit_mapping (清运单位对应)
- 主要字段：
  * unit_name (TEXT): 单位名称
  * street_name (TEXT): 街道名称

### 12. clearance_community_mapping (清运小区对应)
- 主要字段：
  * base_community_name (TEXT): 基础小区名称
  * vehicle_community_name (TEXT): 车辆小区名称
  * street_name (TEXT): 街道名称

## SQLite特性重要说明
1. **数据类型限制**: SQLite主要支持TEXT、INTEGER、REAL、BLOB四种存储类型
2. **类型转换**: 数值数据存储为TEXT时需要CAST转换，如：CAST(garbage_weight AS FLOAT)
3. **布尔值处理**: 布尔值存储为TEXT('TRUE'/'FALSE')或INTEGER(1/0)
4. **日期处理**: 日期存储为TEXT，使用DATE()函数提取日期部分
5. **状态码映射**: decoration_garbage_old表中order_state=7对应order_state_desc='已完成'

## SQL查询示例（从实际代码中提取）

### 清运数据查询示例
```sql
-- 查询指定日期清运概览
SELECT 
    street_name AS 街道,
    type_name AS 垃圾类型,
    COUNT(*) AS 清运次数,
    SUM(CAST(garbage_weight AS FLOAT)) AS 总清运量,
    COUNT(DISTINCT vehicle_license_num) AS 参与车辆数,
    MAX(load_time_str) AS 最新清运时间
FROM garbage_data 
WHERE DATE(load_time_str) = '2025-06-16'
GROUP BY street_name, type_name
ORDER BY 总清运量 DESC;

-- 街道清运统计（时间段查询）
SELECT 
    street_name AS 街道,
    type_name AS 垃圾类型,
    COUNT(*) AS 清运次数,
    SUM(CAST(garbage_weight AS FLOAT)) AS 总清运量,
    AVG(CAST(garbage_weight AS FLOAT)) AS 平均清运量,
    COUNT(DISTINCT community_name) AS 涉及小区数
FROM garbage_data 
WHERE load_time_str BETWEEN '2025-06-10' AND '2025-06-16'
GROUP BY street_name, type_name
ORDER BY street_name, 总清运量 DESC;
```

### 问题监管查询示例
```sql
-- 小包垃圾超时问题
SELECT 
    station_name AS 垃圾房名称,
    division_name AS 区划名称,
    community_name AS 小区名称,
    drop_time AS 落地时间,
    handle_time AS 处置时间,
    CASE WHEN is_timeout = 'TRUE' THEN '超时' ELSE '正常' END AS 处置状态,
    CASE WHEN is_handle = 'TRUE' THEN '已处置' ELSE '未处置' END AS 处置情况,
    take_minutes AS 处置耗时分钟
FROM small_package_garbage 
WHERE is_timeout = 'TRUE' OR is_handle = 'FALSE'
ORDER BY drop_time DESC;

-- 垃圾桶满溢问题
SELECT 
    station_name AS 垃圾房名称,
    division_name AS 区划名称,
    community_name AS 小区名称,
    full_time AS 满溢时间,
    handle_time AS 处置时间,
    CASE WHEN is_handle = 'TRUE' THEN '已处置' ELSE '未处置' END AS 处置状态,
    ROUND((JULIANDAY(COALESCE(handle_time, datetime('now'))) - JULIANDAY(full_time)) * 24, 2) AS 处置耗时小时
FROM garbage_bin_overflow 
WHERE is_handle = 'FALSE' OR handle_time IS NULL
ORDER BY full_time DESC;
```

### 装修垃圾查询示例
```sql
-- 整合新旧模式预约数据
SELECT 
    '老模式' AS 模式类型,
    CAST(bg_order_id AS TEXT) AS 订单号,
    street_name AS 街道,
    community_name AS 小区名称,
    community_addr AS 地址,
    order_state_desc AS 订单状态,
    create_time_str AS 创建时间,
    estimate_clear_time_str AS 预约清运时间,
    finish_time_str AS 完成时间,
    CAST(garbage_weight AS TEXT) AS 预约量,
    vehicle_license_num AS 清运车牌,
    CASE WHEN is_over_time = '是' THEN '是' ELSE '否' END AS 是否超时
FROM decoration_garbage_old
WHERE DATE(create_time_str) >= '2025-05-17'
UNION ALL
SELECT 
    '新模式' AS 模式类型,
    appointment_order_id AS 订单号,
    street_name AS 街道,
    community_name AS 小区名称,
    address AS 地址,
    order_state AS 订单状态,
    create_order_time AS 创建时间,
    resident_appointment_time AS 预约清运时间,
    NULL AS 完成时间,
    CAST(appointment_bags_number AS TEXT) || '袋' AS 预约量,
    NULL AS 清运车牌,
    NULL AS 是否超时
FROM decoration_garbage_new
WHERE DATE(create_order_time) >= '2025-05-17'
ORDER BY 创建时间 DESC;

-- 工单状态统计
SELECT 
    '老模式' AS 模式,
    order_state_desc AS 状态,
    COUNT(*) AS 工单数量,
    COUNT(CASE WHEN is_over_time = '是' THEN 1 END) AS 超时数量
FROM decoration_garbage_old
GROUP BY order_state_desc
UNION ALL
SELECT 
    '新模式' AS 模式,
    order_state AS 状态,
    COUNT(*) AS 工单数量,
    NULL AS 超时数量
FROM decoration_garbage_new
GROUP BY order_state
ORDER BY 模式, 工单数量 DESC;
```

### 数据质量检查示例
```sql
-- 检查数据完整性
SELECT COUNT(*) as total FROM garbage_data;

SELECT COUNT(*) as missing 
FROM garbage_data 
WHERE street_name IS NULL OR street_name = '';

-- 日期范围查询
SELECT 
    MIN(DATE(load_time_str)) as min_date,
    MAX(DATE(load_time_str)) as max_date,
    COUNT(DISTINCT DATE(load_time_str)) as date_count
FROM garbage_data
WHERE load_time_str IS NOT NULL;
```

## 可用工具
你可以调用以下工具来查询数据：
1. get_realtime_clearance_data - 查询指定日期的全区清运实时数据
2. get_street_clearance_statistics - 查询街道清运统计
3. get_overdue_issues - 查询逾期混运等问题
4. get_decoration_appointments_data - 查询装修垃圾预约数据
5. get_order_status_details - 查询工单状态详情
6. check_data_quality - 检查数据质量
7. get_available_date_range - 获取可用数据日期范围
8. execute_any_sql_query - 执行自定义SQL查询

## 响应策略
- **优先使用预定义工具**: 对于常见查询，优先使用1-7号工具
- **自定义SQL场景**: 只有在预定义工具无法满足需求时才使用execute_any_sql_query
- **提供清晰分析**: 突出重要发现和趋势，用结构化方式展示结果
- **数据洞察**: 提供有价值的业务建议和数据解读

## 重要约定
- 日期格式：YYYY-MM-DD
- 数值转换：使用CAST(field AS FLOAT)或CAST(field AS INTEGER)
- 布尔值：'TRUE'/'FALSE'（TEXT）
- 状态映射：老模式order_state=7表示'已完成'
- 超时标识：is_over_time='是'表示超时
- NULL处理：使用COALESCE()或IS NULL/IS NOT NULL判断
"""
        
        # 创建带结构化输出的LLM
        self.structured_llm = llm.with_structured_output(AgentResponse)
        
        # 创建ReAct Agent
        self.agent = create_react_agent(llm, self.tools, prompt=system_prompt)
        print("✅ Agent初始化完成")
    
    async def close(self):
        """关闭客户端连接"""
        # MultiServerMCPClient 不需要显式关闭
        if self.mcp_client:
            self.mcp_client = None
            print("✅ MCP客户端已清理")

# 定义状态结构
class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str
    agent_response: str
    output_files: List[str]
    current_step: str
    agent_instance: GarbageMonitoringAgent
    structured_response: Optional[AgentResponse]
    session_count: int

# 工作流节点定义
def welcome_node(state: AgentState) -> AgentState:
    """节点1：欢迎用户并展示功能"""
    session_num = state.get("session_count", 0) + 1
    state["session_count"] = session_num
    
    if session_num == 1:
        welcome_message = """
🏢 欢迎使用垃圾监管系统AI智能体！

本系统可以帮您查询以下内容：

📊 生活垃圾监管功能：
   1. 全区清运实时数据查询
   2. 各街道清运数量统计分析
   3. 逾期混运等问题整治信息

🔧 装修垃圾监管功能：
   4. 新旧模式预约数据查询
   5. 各状态工单详情分析

🛠️ 辅助功能：
   6. 数据质量检查报告
   7. 可用数据日期范围查询
   8. 自定义SQL查询执行

💡 使用示例：
   - "查询2025年6月16日的全区清运数据"
   - "分析龙华街道最近一周的清运统计"
   - "检查小包垃圾超时处理问题"
   - "查看装修垃圾预约工单状态"
   - "执行自定义数据分析查询"

请输入您的查询需求：
        """.strip()
        print(welcome_message)
    else:
        print(f"\n🔄 开始第 {session_num} 轮查询")
        print("请输入您的新查询需求：")
    
    user_input = input("\n>>> ")
    
    # 更新状态
    state["user_query"] = user_input
    state["current_step"] = "processing"
    state["messages"] = [HumanMessage(content=user_input)]  # 重置消息历史
    state["agent_response"] = ""
    state["structured_response"] = None
    
    return state

async def process_query_node(state: AgentState) -> AgentState:
    """节点2：处理查询并调用MCP工具，支持多轮交互"""
    print(f"\n🔄 开始处理查询: {state['user_query']}")
    
    try:
        # 获取全局智能体实例
        agent_instance = state.get("agent_instance")
        if not agent_instance:
            raise ValueError("Agent实例未初始化")
        
        # 使用agent处理查询
        result = await agent_instance.agent.ainvoke({
            "messages": state["messages"]
        })
        # 记录本次用户messages元素的长度
        user_messages_length = len(state["messages"])
        
        # 提取最终回复
        agent_response_content = ""
        if result["messages"]:
            final_message = result["messages"][-1]
            if hasattr(final_message, 'content'):
                agent_response_content = final_message.content
                print(f"✅ 获得LLM回复: {len(final_message.content)} 字符")
            else:
                agent_response_content = "未获得来自LLM的文本回复"
        else:
            agent_response_content = "未获得来自LLM的回复"
        
        # 使用结构化输出来分析回复
        structured_prompt = f"""
请分析以下AI助手的回复，判断是否需要用户提供更多信息：

用户查询: {state['user_query']}
AI回复: {agent_response_content}

请根据以下标准判断：
1. 如果回复中明确表示需要用户提供更多参数、日期、具体条件等信息，则if_continue为true
2. 如果回复中包含具体的查询结果、数据分析或完整的答案，则if_continue为false
3. 如果if_continue为true，returned_content应该为空字符串
4. 如果if_continue为false，returned_content应该是完整的AI回复内容

请返回结构化的响应。
"""
        
        structured_result = await agent_instance.structured_llm.ainvoke([
            HumanMessage(content=structured_prompt)
        ])
        
        state["structured_response"] = structured_result
        
        # 如果需要继续，清空返回内容
        if structured_result.if_continue:
            state["agent_response"] = ""
            state["current_step"] = "continue_asking"
            print("🤔 需要用户提供更多信息...")
        else:
            state["agent_response"] = structured_result.returned_content
            state["current_step"] = "saving"
            print("✅ 查询已完成，准备保存结果")
        
        # 保存所有消息
        state["messages"].extend(result["messages"][user_messages_length:])
        
    except Exception as e:
        error_msg = f"查询处理失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["agent_response"] = error_msg
        state["structured_response"] = AgentResponse(if_continue=False, returned_content=error_msg)
        state["messages"].append(AIMessage(content=error_msg))
        state["current_step"] = "saving"
    
    return state

async def continue_asking_node(state: AgentState) -> AgentState:
    """节点：需要用户提供更多信息时的处理"""
    print(f"\n💬 AI助手回复: {state['messages'][-1].content}")
    print("\n请提供更多信息：")
    
    user_input = input("\n>>> ")
    
    # 添加用户的新输入到消息历史
    state["messages"].append(HumanMessage(content=user_input))
    state["user_query"] = user_input  # 更新当前查询
    state["current_step"] = "processing"
    
    return state

def save_results_node(state: AgentState) -> AgentState:
    """节点3：保存结果为CSV和JSON文件"""
    print(f"\n💾 开始保存结果...")
    
    if not state["agent_response"]:
        print("⚠️ 没有查询结果需要保存")
        return state
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []
    
    try:
        # 保存完整对话记录
        conversation_file = f"conversation_{timestamp}.json"
        conversation_path = OUTPUT_DIR / conversation_file
        
        conversation_data = {
            "查询时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "用户查询": state["user_query"],
            "AI回复": state["agent_response"],
            "消息历史": [
                {
                    "类型": type(msg).__name__,
                    "内容": msg.content if hasattr(msg, 'content') else str(msg)
                }
                for msg in state["messages"]
            ]
        }
        
        with open(conversation_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        saved_files.append(str(conversation_path))
        print(f"📄 已保存对话记录: {conversation_file}")
        
        # 尝试从消息中提取工具调用结果并保存为CSV
        extract_and_save_tool_results(state["messages"], timestamp, saved_files)
        
        # 保存简化的查询结果文本
        result_file = f"query_result_{timestamp}.txt"
        result_path = OUTPUT_DIR / result_file
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"用户查询: {state['user_query']}\n")
            f.write(f"AI回复:\n{state['agent_response']}\n")
        saved_files.append(str(result_path))
        print(f"📝 已保存查询结果: {result_file}")
        
        state["output_files"] = saved_files
        print(f"\n🎉 所有结果已保存到 {OUTPUT_DIR} 目录")
        print(f"共保存 {len(saved_files)} 个文件")
        
    except Exception as e:
        error_msg = f"结果保存失败: {str(e)}"
        print(f"❌ {error_msg}")
        state["messages"].append(AIMessage(content=error_msg))
    
    # 询问用户是否继续
    print(f"\n🤖 查询结果已展示并保存完成。")
    continue_choice = input("是否需要进行新的查询？(y/n): ").lower().strip()
    
    if continue_choice in ['y', 'yes', '是', '需要']:
        state["current_step"] = "continue_new_query"
        print("🔄 准备开始新的查询...")
    else:
        state["current_step"] = "completed"
        print("👋 感谢使用垃圾监管系统AI智能体！")
    
    return state

def extract_and_save_tool_results(messages: List[BaseMessage], timestamp: str, saved_files: list):
    """从消息中提取工具调用结果并保存为CSV"""
    try:
        tool_result_count = 0
        
        for i, message in enumerate(messages):
            # 查找包含JSON数据的消息
            if hasattr(message, 'content') and isinstance(message.content, str):
                content = message.content.strip()
                
                # 检查是否是JSON格式的工具结果
                if content.startswith('{') and content.endswith('}'):
                    try:
                        result_data = json.loads(content)
                        
                        # 检查是否是有效的工具结果
                        if isinstance(result_data, dict) and any(
                            key in result_data for key in [
                                "查询日期", "查询时间段", "小包垃圾超时问题", 
                                "预约数据", "状态统计", "数据质量检查", 
                                "数据日期范围", "查询结果"
                            ]
                        ):
                            tool_result_count += 1
                            save_tool_result_as_csv(result_data, f"tool_result_{tool_result_count}", timestamp, saved_files)
                    
                    except json.JSONDecodeError:
                        continue
    
    except Exception as e:
        print(f"⚠️ 工具结果提取失败: {e}")

def save_tool_result_as_csv(result_data: dict, tool_name: str, timestamp: str, saved_files: list):
    """保存单个工具结果为CSV格式"""
    try:
        # 保存完整JSON结果
        json_filename = f"{tool_name}_complete_{timestamp}.json"
        json_filepath = OUTPUT_DIR / json_filename
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        saved_files.append(str(json_filepath))
        print(f"📄 已保存: {json_filename}")
        
        # 遍历结果数据，查找可以转换为CSV的列表数据
        for key, value in result_data.items():
            if isinstance(value, list) and value:
                # 检查列表中是否包含字典（可以转为表格）
                if isinstance(value[0], dict):
                    filename = f"{tool_name}_{key}_{timestamp}.csv"
                    filepath = OUTPUT_DIR / filename
                    
                    df = pd.DataFrame(value)
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    saved_files.append(str(filepath))
                    print(f"📊 已保存: {filename} ({len(value)} 条记录)")
            
            elif isinstance(value, dict):
                # 递归处理嵌套字典
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, list) and sub_value and isinstance(sub_value[0], dict):
                        filename = f"{tool_name}_{key}_{sub_key}_{timestamp}.csv"
                        filepath = OUTPUT_DIR / filename
                        
                        df = pd.DataFrame(sub_value)
                        df.to_csv(filepath, index=False, encoding='utf-8-sig')
                        saved_files.append(str(filepath))
                        print(f"📊 已保存: {filename} ({len(sub_value)} 条记录)")
    
    except Exception as e:
        print(f"⚠️ CSV保存失败: {e}")

# 构建工作流
def create_workflow():
    """创建LangGraph工作流"""
    # 创建状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("welcome", welcome_node)
    workflow.add_node("process_query", process_query_node)
    workflow.add_node("continue_asking", continue_asking_node)
    workflow.add_node("save_results", save_results_node)
    
    # 定义条件函数
    def should_continue_asking(state: AgentState) -> str:
        """判断是否需要继续询问用户"""
        current_step = state.get("current_step", "")
        if current_step == "continue_asking":
            return "continue_asking"
        elif current_step == "saving":
            return "save_results"
        else:
            return "save_results"
    
    def should_continue_new_query(state: AgentState) -> str:
        """判断是否开始新查询"""
        current_step = state.get("current_step", "")
        if current_step == "continue_new_query":
            return "welcome"
        else:
            return END
    
    # 添加边
    workflow.add_edge(START, "welcome")
    workflow.add_edge("welcome", "process_query")
    
    # 添加条件边：从process_query到continue_asking或save_results
    workflow.add_conditional_edges(
        "process_query",
        should_continue_asking,
        {
            "continue_asking": "continue_asking",
            "save_results": "save_results"
        }
    )
    
    # 从continue_asking回到process_query
    workflow.add_edge("continue_asking", "process_query")
    
    # 添加条件边：从save_results到welcome或END
    workflow.add_conditional_edges(
        "save_results",
        should_continue_new_query,
        {
            "welcome": "welcome",
            END: END
        }
    )
    
    # 编译工作流
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

async def main():
    """主函数"""
    print("启动垃圾监管AI智能体")
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 检查MCP服务器文件
    if not os.path.exists(MCP_SERVER_PATH):
        print(f"❌ MCP服务器文件不存在: {MCP_SERVER_PATH}")
        return
    
    # 初始化智能体
    agent_instance = GarbageMonitoringAgent()
    
    try:
        await agent_instance.initialize()
        
        # 创建工作流
        app = create_workflow()
        
        # 初始状态
        initial_state = {
            "messages": [],
            "user_query": "",
            "agent_response": "",
            "output_files": [],
            "current_step": "welcome",
            "agent_instance": agent_instance,  # 传递agent实例
            "structured_response": None,
            "session_count": 0
        }
        
        # 执行工作流
        config = {"configurable": {"thread_id": "main"}}
        
        final_state = None
        async for state in app.astream(initial_state, config):
            final_state = state
            # 只在调试模式下显示步骤信息
            # current_step = state.get("current_step", "unknown")
            # print(f"🔄 当前步骤: {current_step}")
        
        if final_state and final_state.get("output_files"):
            print(f"\n📂 输出文件列表:")
            for file_path in final_state["output_files"]:
                print(f"   - {file_path}")
        
        print(f"\n程序已结束")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭MCP客户端
        await agent_instance.close()

if __name__ == "__main__":
    asyncio.run(main()) 