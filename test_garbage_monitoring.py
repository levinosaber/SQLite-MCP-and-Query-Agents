#!/usr/bin/env python3
"""
垃圾监管系统数据库操作测试文件
专门测试sqlite_operations.py中GarbageMonitoringDB类的功能
"""
import sqlite3
import pytest
import tempfile
import os
import logging
# 删除csv依赖
from unittest.mock import patch
from datetime import datetime

from sqlite_operations import GarbageMonitoringDB

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestGarbageMonitoringDB:
    """测试GarbageMonitoringDB类的功能"""
    use_temp_dir = False
    clear_db_file_after_test = False

    def setup_method(self, method):
        """设置测试环境"""
        if self.use_temp_dir:
            self.temp_dir = tempfile.mkdtemp()
        else:
            self.temp_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.temp_dir, "garbage_monitoring.db")
        
        # 直接实例化GarbageMonitoringDB。
        # 当数据库文件不存在时，GarbageMonitoringDB 会自动
        # 读取项目根目录下 ./data/ 目录里的 CSV 文件并初始化表结构。
        self.db = GarbageMonitoringDB(self.db_path)
    
    def teardown_method(self):
        """清理测试环境"""
        self.db.close()
        if self.clear_db_file_after_test and os.path.exists(self.db_path):
            os.remove(self.db_path)
        import shutil
        if self.use_temp_dir:
            shutil.rmtree(self.temp_dir)
    
    def test_database_auto_initialization(self):
        """测试数据库自动初始化功能"""
        # 验证数据库文件已创建
        assert os.path.exists(self.db_path)
        
        # 验证预期的表格已创建
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = [
            "garbage_data",
            "small_package_garbage", 
            "garbage_bin_overflow",
            "decoration_garbage_old",
            "decoration_garbage_new"
        ]
        
        for expected_table in expected_tables:
            assert expected_table in table_names, f"缺少表: {expected_table}"
        
        # 验证表格结构和数据
        # 检查garbage_data表
        cursor.execute("PRAGMA table_info(garbage_data)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "street_name" in column_names
        assert "community_name" in column_names
        assert "load_time_str" in column_names
        assert "garbage_weight" in column_names
        assert "type_name" in column_names
        
        # 检查数据是否正确插入
        garbage_result = self.db.execute_query("SELECT COUNT(*) as count FROM garbage_data")
        assert garbage_result[0]['count'] >= 4
        
        # 检查small_package_garbage表
        cursor.execute("PRAGMA table_info(small_package_garbage)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "event_id" in column_names
        assert "station_name" in column_names
        assert "division_name" in column_names
        assert "is_handle" in column_names
        assert "is_timeout" in column_names
        
        package_result = self.db.execute_query("SELECT COUNT(*) as count FROM small_package_garbage")
        assert package_result[0]['count'] >= 4
        
        # 检查garbage_bin_overflow表
        cursor.execute("PRAGMA table_info(garbage_bin_overflow)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "event_id" in column_names
        assert "station_name" in column_names
        assert "full_time" in column_names
        assert "is_handle" in column_names
        
        overflow_result = self.db.execute_query("SELECT COUNT(*) as count FROM garbage_bin_overflow")
        assert overflow_result[0]['count'] >= 4
        
        # 检查decoration_garbage_old表
        cursor.execute("PRAGMA table_info(decoration_garbage_old)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "bg_order_id" in column_names
        assert "street_name" in column_names
        assert "order_state" in column_names
        assert "order_state_desc" in column_names
        
        old_result = self.db.execute_query("SELECT COUNT(*) as count FROM decoration_garbage_old")
        assert old_result[0]['count'] >= 4
        
        # 检查decoration_garbage_new表
        cursor.execute("PRAGMA table_info(decoration_garbage_new)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        assert "appointment_order_id" in column_names
        assert "street_name" in column_names
        assert "order_state" in column_names
        assert "appointment_bags_number" in column_names
        
        new_result = self.db.execute_query("SELECT COUNT(*) as count FROM decoration_garbage_new")
        assert new_result[0]['count'] >= 4
    
    def test_get_realtime_clearance_data(self):
        """测试get_realtime_clearance_data函数"""
        # 测试指定日期查询
        result = self.db.get_realtime_clearance_data("2025-06-16")
        
        # 验证返回结构
        assert isinstance(result, dict)
        assert "查询日期" in result
        assert "清运概览" in result
        assert "清运明细" in result
        assert "统计时间" in result
        
        # 验证数据内容
        assert result["查询日期"] == "2025-06-16"
        assert isinstance(result["清运概览"], list)
        assert isinstance(result["清运明细"], list)
        # 即使没有数据，也要保证返回的是列表类型
        
        # 验证清运概览数据结构
        if result["清运概览"]:
            overview = result["清运概览"][0]
            assert "街道" in overview
            assert "垃圾类型" in overview
            assert "清运次数" in overview
            assert "总清运量" in overview
        
        # 验证清运明细数据结构
        if result["清运明细"]:
            detail = result["清运明细"][0]
            assert "清运时间" in detail
            assert "街道" in detail
            assert "垃圾类型" in detail
            assert "清运量" in detail
        
        # 测试默认日期（当天）
        result_default = self.db.get_realtime_clearance_data()
        if result_default:
            assert "查询日期" in result_default
            assert result_default["查询日期"] == datetime.now().strftime('%Y-%m-%d')
        else:
            logger.info("get_realtime_clearance_data默认日期返回空值")
        
    def test_get_street_clearance_statistics(self):
        """测试get_street_clearance_statistics函数"""
        # 测试指定街道查询
        result = self.db.get_street_clearance_statistics("2025-06-16", "2025-06-17", "龙华街道")
        
        # 验证返回结构
        assert isinstance(result, dict)
        assert "查询时间段" in result
        assert "指定街道" in result
        assert "清运统计" in result
        assert "清运趋势" in result
        
        # 验证数据内容
        assert result["查询时间段"] == "2025-06-16 至 2025-06-17"
        assert result["指定街道"] == "龙华街道"
        assert isinstance(result["清运统计"], list)
        assert isinstance(result["清运趋势"], list)
        
        # 验证清运统计数据结构
        if result["清运统计"]:
            stats = result["清运统计"][0]
            assert "街道" in stats
            assert "垃圾类型" in stats
            assert "清运次数" in stats
            assert "总清运量" in stats
        
        # 测试查询所有街道
        result_all = self.db.get_street_clearance_statistics("2025-06-16", "2025-06-17")
        assert result_all["指定街道"] == "全部街道"
        
        logger.info("✓ get_street_clearance_statistics函数测试通过")
    
    def test_get_overdue_issues(self):
        """测试get_overdue_issues函数"""
        result = self.db.get_overdue_issues()
        
        # 验证返回结构
        assert isinstance(result, dict)
        assert "小包垃圾超时问题" in result
        assert "垃圾桶满溢问题" in result
        assert "查询时间" in result
        
        # 验证小包垃圾超时问题结构
        small_package = result["小包垃圾超时问题"]
        assert isinstance(small_package, dict)
        assert "问题数量" in small_package
        assert "问题详情" in small_package
        assert isinstance(small_package["问题详情"], list)
        
        # 验证垃圾桶满溢问题结构
        overflow = result["垃圾桶满溢问题"]
        assert isinstance(overflow, dict)
        assert "问题数量" in overflow
        assert "问题详情" in overflow
        assert isinstance(overflow["问题详情"], list)
        
        # 验证问题详情数据结构
        if len(small_package["问题详情"]) > 0:
            issue = small_package["问题详情"][0]
            assert "垃圾房名称" in issue
            assert "区划名称" in issue
            assert "落地时间" in issue
            assert "处置状态" in issue
        
        if len(overflow["问题详情"]) > 0:
            issue = overflow["问题详情"][0]
            assert "垃圾房名称" in issue
            assert "区划名称" in issue
            assert "满溢时间" in issue
            assert "处置状态" in issue
        
        logger.info("✓ get_overdue_issues函数测试通过")
    
    def test_get_decoration_appointments_data(self):
        """测试get_decoration_appointments_data函数"""
        # 测试指定天数查询
        result = self.db.get_decoration_appointments_data(30)
        
        # 验证返回结构
        assert isinstance(result, dict)
        assert "查询天数" in result
        assert "预约数据" in result
        assert "统计信息" in result
        assert "数据总数" in result
        
        # 验证数据内容
        assert result["查询天数"] == 30
        assert isinstance(result["预约数据"], list)
        assert isinstance(result["统计信息"], list)
        assert isinstance(result["数据总数"], int)
        
        # 验证预约数据结构
        if result["预约数据"]:
            appointment = result["预约数据"][0]
            assert "模式类型" in appointment
            assert "订单号" in appointment
            assert "街道" in appointment
            assert "订单状态" in appointment
            assert "创建时间" in appointment
        
        # 验证统计信息结构
        if result["统计信息"]:
            stats = result["统计信息"][0]
            assert "模式" in stats
            assert "总订单数" in stats
            assert "已完成" in stats
        
        # 测试默认天数（30天）
        result_default = self.db.get_decoration_appointments_data()
        assert result_default["查询天数"] == 30
        
        logger.info("✓ get_decoration_appointments_data函数测试通过")
    
    def test_get_order_status_details(self):
        """测试get_order_status_details函数"""
        # 测试无筛选条件查询
        result = self.db.get_order_status_details()
        
        # 验证返回结构
        assert isinstance(result, dict)
        assert "筛选条件" in result
        assert "状态统计" in result
        assert "工单详情" in result
        assert "查询结果数" in result
        
        # 验证筛选条件
        filter_conditions = result["筛选条件"]
        assert "状态" in filter_conditions
        assert "模式" in filter_conditions
        assert filter_conditions["状态"] == "全部状态"
        assert filter_conditions["模式"] == "全部模式"
        
        # 验证数据结构
        assert isinstance(result["状态统计"], list)
        assert isinstance(result["工单详情"], list)
        assert isinstance(result["查询结果数"], int)
        
        # 验证状态统计数据结构
        if result["状态统计"]:
            stats = result["状态统计"][0]
            assert "模式" in stats
            assert "状态" in stats
            assert "工单数量" in stats
        
        # 验证工单详情数据结构
        if result["工单详情"]:
            order = result["工单详情"][0]
            assert "模式" in order
            assert "订单号" in order
            assert "街道" in order
            assert "状态" in order
            assert "创建时间" in order
        
        # 测试带筛选条件查询
        result_filtered = self.db.get_order_status_details(status="已完成", mode="老模式")
        assert result_filtered["筛选条件"]["状态"] == "已完成"
        assert result_filtered["筛选条件"]["模式"] == "老模式"
        
        logger.info("✓ get_order_status_details函数测试通过")
    
    def test_additional_methods(self):
        """测试其他辅助方法"""
        # 测试数据质量检查
        quality_result = self.db.check_data_quality()
        assert isinstance(quality_result, dict)
        assert "数据质量检查" in quality_result
        assert "检查时间" in quality_result
        
        # 测试获取可用日期范围
        date_range_result = self.db.get_available_date_range()
        assert isinstance(date_range_result, dict)
        assert "数据日期范围" in date_range_result
        assert "查询时间" in date_range_result
        
        logger.info("✓ 辅助方法测试通过")

def run_tests():
    """运行测试"""
    logger.info("开始运行GarbageMonitoringDB类功能测试...")
    
    # 运行pytest
    pytest_args = [
        __file__,
        "-v",  # 详细输出
        "-s",  # 显示print语句
        "--tb=short"  # 简短的错误回溯
    ]
    
    exit_code = pytest.main(pytest_args)
    
    # if exit_code == 0:
    #     logger.info("🎉 所有测试通过！")
    #     print("\n" + "="*60)
    #     print("🎉 GarbageMonitoringDB类功能测试完成 - 所有功能正常！")
    #     print("="*60)
    #     print("\n✅ 测试通过的功能:")
    #     print("  • GarbageMonitoringDB类实例化")
    #     print("  • 数据库自动初始化（从CSV文件创建表格）")
    #     print("  • get_realtime_clearance_data - 实时清运数据查询")
    #     print("  • get_street_clearance_statistics - 街道清运统计查询")
    #     print("  • get_overdue_issues - 逾期问题查询")
    #     print("  • get_decoration_appointments_data - 装修垃圾预约数据查询")
    #     print("  • get_order_status_details - 工单状态详情查询")
    #     print("  • 辅助方法（数据质量检查、日期范围查询）")
    #     print("\n🚀 GarbageMonitoringDB类已准备就绪，自动初始化和业务功能完整！")
    # else:
    #     logger.error("❌ 部分测试失败")
    #     print("\n" + "="*60)
    #     print("❌ 测试过程中发现问题，请检查上述错误信息")
    #     print("="*60)
    
    return exit_code

if __name__ == "__main__":
    run_tests() 