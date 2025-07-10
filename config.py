"""
垃圾监管系统配置文件
"""
import os
from typing import Dict, Any

# 数据库配置
DATABASE_CONFIG = {
    "default_db_path": "garbage_monitoring.db",
    "test_db_path": "test_garbage_monitoring.db",
    "connection_timeout": 30,
    "check_same_thread": False
}

# MCP Server配置
MCP_SERVER_CONFIG = {
    "server_name": "garbage-monitoring",
    "stdio_enabled": True,
    "log_level": "INFO"
}

# 数据表映射
TABLE_MAPPING = {
    "garbage_data": "干湿垃圾数据",
    "small_package_garbage": "小包垃圾落地详情",
    "garbage_bin_overflow": "垃圾桶满溢详情",
    "decoration_garbage_old": "装修垃圾预约（老模式）",
    "decoration_garbage_new": "装修垃圾预约（新模式）"
}

# 功能描述
FUNCTION_DESCRIPTIONS = {
    "生活垃圾监管": {
        "get_realtime_clearance_data": "展示全区清运实时数据",
        "get_street_clearance_statistics": "筛选查询各街道清运数量",
        "get_overdue_issues": "整治逾期混运等问题"
    },
    "装修垃圾监管": {
        "get_decoration_appointments_data": "接入新旧模式预约数据",
        "get_order_status_details": "查看各状态工单详情"
    },
    "辅助功能": {
        "check_data_quality": "检查数据质量",
        "get_available_date_range": "获取可用的数据日期范围"
    }
}

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "garbage_monitoring.log",
            "formatter": "detailed"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

def get_db_path(test_mode: bool = False) -> str:
    """
    获取数据库路径
    
    Args:
        test_mode: 是否为测试模式
        
    Returns:
        数据库文件路径
    """
    if test_mode:
        return DATABASE_CONFIG["test_db_path"]
    return DATABASE_CONFIG["default_db_path"]

def get_table_display_name(table_name: str) -> str:
    """
    获取表格的中文显示名称
    
    Args:
        table_name: 表格名称
        
    Returns:
        中文显示名称
    """
    return TABLE_MAPPING.get(table_name, table_name)

def get_function_description(category: str, function_name: str) -> str:
    """
    获取功能描述
    
    Args:
        category: 功能分类
        function_name: 功能名称
        
    Returns:
        功能描述
    """
    return FUNCTION_DESCRIPTIONS.get(category, {}).get(function_name, function_name) 