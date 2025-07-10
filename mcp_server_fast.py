#!/usr/bin/env python3
"""
垃圾监管系统 FastMCP Server
使用FastMCP框架简化MCP Server实现，提供生活垃圾和装修垃圾监管功能
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from sqlite_operations import GarbageMonitoringDB

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastMCP应用实例
mcp = FastMCP("garbage-monitoring")

# 全局数据库实例
db = None

def initialize_database_instance(db_path: str = "garbage_monitoring.db"):
    """初始化数据库连接"""
    global db
    if db is None:
        db = GarbageMonitoringDB(db_path)
        logger.info(f"数据库初始化完成: {db_path}")

@mcp.tool()
def get_realtime_clearance_data(date: Optional[str] = None) -> dict:
    """
    展示全区清运实时数据
    
    Args:
        date: 查询日期 (YYYY-MM-DD格式)，默认为今天
        
    Returns:
        包含清运概览和明细的数据
    """
    if db is None:
        initialize_database_instance()
    
    logger.info(f"查询实时清运数据，日期: {date or '今天'}")
    return db.get_realtime_clearance_data(date)

@mcp.tool()
def get_street_clearance_statistics(
    start_date: str, 
    end_date: str, 
    street_name: Optional[str] = None
) -> dict:
    """
    筛选查询各街道清运数量
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        street_name: 指定街道名称，可选
        
    Returns:
        街道清运统计数据
    """
    if db is None:
        initialize_database_instance()
    
    logger.info(f"查询街道清运统计，时间段: {start_date} 至 {end_date}，街道: {street_name or '全部'}")
    return db.get_street_clearance_statistics(start_date, end_date, street_name)

@mcp.tool()
def get_overdue_issues() -> dict:
    """
    整治逾期混运等问题
    
    Returns:
        包含小包垃圾超时和垃圾桶满溢超时问题的数据
    """
    if db is None:
        initialize_database_instance()
    
    logger.info("查询逾期混运问题")
    return db.get_overdue_issues()

@mcp.tool()
def get_decoration_appointments_data(days_back: int = 30) -> dict:
    """
    接入新旧模式预约数据
    
    Args:
        days_back: 查询最近多少天的数据，默认30天
        
    Returns:
        整合的新旧模式预约数据
    """
    if db is None:
        initialize_database_instance()
    
    logger.info(f"查询装修垃圾预约数据，最近 {days_back} 天")
    return db.get_decoration_appointments_data(days_back)

@mcp.tool()
def get_order_status_details(
    status: Optional[str] = None, 
    mode: Optional[str] = None
) -> dict:
    """
    查看各状态工单详情
    
    Args:
        status: 筛选特定状态的工单，可选
        mode: 筛选模式 ('老模式' 或 '新模式')，可选
        
    Returns:
        工单状态统计和详情
    """
    if db is None:
        initialize_database_instance()
    
    logger.info(f"查询工单状态详情，状态: {status or '全部'}，模式: {mode or '全部'}")
    return db.get_order_status_details(status, mode)

@mcp.tool()
def check_data_quality() -> dict:
    """
    检查数据质量
    
    Returns:
        数据质量报告
    """
    if db is None:
        initialize_database_instance()
    
    logger.info("执行数据质量检查")
    return db.check_data_quality()

@mcp.tool()
def get_available_date_range() -> dict:
    """
    获取可用的数据日期范围
    
    Returns:
        各表的数据日期范围
    """
    if db is None:
        initialize_database_instance()
    
    logger.info("查询可用数据日期范围")
    return db.get_available_date_range()

@mcp.tool()
def execute_any_sql_query(query: str, params: Optional[list] = None) -> dict:
    """
    执行任意SQL查询语句
    
    当用户的需求不属于预定义的五种功能，或需求比较模糊时，
    大模型可以根据具体需求生成SQL查询语句和参数，通过此工具执行查询。
    
    Args:
        query: SQL查询语句，可以使用?作为占位符
        params: 占位符对应的参数列表，可选
        
    Returns:
        包含查询结果和执行信息的字典，结构如下：
        - 查询语句: SQL查询语句
        - 查询参数: 查询参数列表
        - 结果数量: 查询结果数量
        - 查询结果: 查询结果列表
        - 执行状态: 执行状态，成功或失败
        - 错误信息: 错误信息，如果执行失败
    """
    if db is None:
        initialize_database_instance()
    
    # 确保params是列表或元组格式
    if params is None:
        params = []
    elif not isinstance(params, (list, tuple)):
        params = [params]
    
    logger.info(f"执行自定义SQL查询: {query}")
    logger.info(f"查询参数: {params}")
    
    try:
        # 调用数据库操作类的execute_query方法
        result = db.execute_query(query, tuple(params))
        
        return {
            "查询语句": query,
            "查询参数": params,
            "结果数量": len(result),
            "查询结果": result,
            "执行状态": "成功",
        }
        
    except Exception as e:
        error_msg = f"SQL查询执行失败: {str(e)}"
        logger.error(error_msg)
        
        return {
            "查询语句": query,
            "查询参数": params,
            "结果数量": 0,
            "查询结果": [],
            "执行状态": "失败",
            "错误信息": str(e)
        }

def create_app(db_path: str = "garbage_monitoring.db"):
    """
    创建FastMCP应用
    
    Args:
        db_path: SQLite数据库文件路径
        
    Returns:
        FastMCP应用实例
    """
    # 初始化数据库路径
    initialize_database_instance(db_path)
    return mcp

def main():
    """主函数"""
    import sys
    
    # 从命令行参数获取数据库路径
    db_path = sys.argv[1] if len(sys.argv) > 1 else "garbage_monitoring.db"
    
    logger.info(f"启动垃圾监管FastMCP服务器，数据库路径: {db_path}")
    
    # 初始化数据库
    initialize_database_instance(db_path)
    
    try:
        logger.info("✅ FastMCP服务器启动完成，等待连接...")
        # 运行FastMCP服务器（同步版本）
        mcp.run()
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"❌ 服务器运行出错: {e}")
        raise
    finally:
        # 清理资源
        global db
        if db:
            db.close()
            logger.info("数据库连接已关闭")

if __name__ == "__main__":
    main() 