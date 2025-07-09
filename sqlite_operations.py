"""
SQLite数据库操作模块
实现垃圾监管系统的核心数据库查询功能
"""
import sqlite3
import logging
import os
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class GarbageMonitoringDB:
    """垃圾监管数据库操作类"""
    
    # 文件名到表名的映射
    FILE_TABLE_MAPPING = {
        "单位详情.csv": "unit_details",
        "合同详情.csv": "contract_details",  
        "商铺详情.csv": "shop_details",
        "干湿垃圾数据2025-06-16.csv": "garbage_data",
        "小包垃圾落地详情2025-06-16.csv": "small_package_garbage",
        "垃圾桶满溢详情2025-06-16.csv": "garbage_bin_overflow",
        "装修垃圾预约-新模式.csv": "decoration_garbage_new",
        "装修垃圾预约-老模式.csv": "decoration_garbage_old",
        "巡检详情近一周2025-06-16.csv": "inspection_details",
        "居住区巡检数据近一周2025-06-16.csv": "residential_inspection",
        "清运单位对应.csv": "clearance_unit_mapping",
        "清运小区对应.csv": "clearance_community_mapping"
    }
    
    # 中文表名到英文表名的映射
    TABLE_NAME_MAPPING = {
        "单位详情": "unit_details",
        "合同详情": "contract_details",
        "商铺详情": "shop_details", 
        "干湿垃圾数据": "garbage_data",
        "小包垃圾落地详情": "small_package_garbage",
        "垃圾桶满溢详情": "garbage_bin_overflow",
        "装修垃圾预约（新模式）": "decoration_garbage_new",
        "装修垃圾预约（老模式）": "decoration_garbage_old",
        "巡检详情": "inspection_details",
        "居民区巡检": "residential_inspection",
        "清运单位对应": "clearance_unit_mapping",
        "清运小区对应": "clearance_community_mapping"
    }
    
    def __init__(self, db_path: str = "garbage_monitoring.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self.connection = None
        self.data_dir = "./data/"
        
        # 检查数据库是否需要初始化
        db_exists = os.path.exists(db_path)
        
        self.connect()
        
        if not db_exists:
            logger.info("数据库文件不存在，开始初始化数据库...")
            self.initialize_database()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # 返回字典格式结果
            logger.info(f"成功连接到数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def initialize_database(self):
        """初始化数据库，从CSV文件创建表格并填充数据"""
        try:
            logger.info("开始初始化数据库...")
            
            # 检查数据目录是否存在
            if not os.path.exists(self.data_dir):
                logger.warning(f"数据目录不存在: {self.data_dir}")
                return
            
            # 遍历文件映射，创建表格并导入数据
            for filename, table_name in self.FILE_TABLE_MAPPING.items():
                file_path = os.path.join(self.data_dir, filename)
                
                if os.path.exists(file_path):
                    logger.info(f"正在处理文件: {filename} -> 表: {table_name}")
                    self.create_table_from_csv(file_path, table_name)
                else:
                    logger.warning(f"文件不存在: {file_path}")
            
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def create_table_from_csv(self, csv_path: str, table_name: str):
        """
        从CSV文件创建表格并插入数据
        CSV文件结构：
        - 第一行：中文注释（字段含义）
        - 第二行：字段数据类型（SQL认可的数据类型）
        - 第三行：字段名称
        - 第四行开始：实际数据
        
        Args:
            csv_path: CSV文件路径
            table_name: 表格名称
        """
        try:
            # 尝试不同编码读取CSV文件
            df = None
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding, header=None)
                    logger.info(f"成功使用 {encoding} 编码读取文件: {csv_path}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"使用 {encoding} 编码读取文件失败: {e}")
                    continue
            
            if df is None or df.empty:
                logger.warning(f"无法读取CSV文件或文件为空: {csv_path}")
                return
            
            if len(df) < 4:
                logger.warning(f"CSV文件行数不足，至少需要4行（注释、类型、字段名、数据）: {csv_path}")
                return
            
            # 解析CSV结构
            comments_row = df.iloc[0].values  # 第一行：中文注释
            types_row = df.iloc[1].values     # 第二行：字段数据类型
            column_names_row = df.iloc[2].values  # 第三行：字段名称
            data_rows = df.iloc[3:]           # 第四行开始：实际数据
            
            # 清理字段名称
            clean_column_names = []
            for col_name in column_names_row:
                clean_name = self.clean_column_name(str(col_name))
                clean_column_names.append(clean_name)
            
            # 映射SQL数据类型
            sql_types = []
            for sql_type in types_row:
                mapped_type = self.map_sql_type(str(sql_type))
                sql_types.append(mapped_type)
            
            # 删除表如果存在
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # 创建表结构
            column_definitions = []
            for i, (col_name, col_type, comment) in enumerate(zip(clean_column_names, sql_types, comments_row)):
                # 添加列定义，包含注释信息
                column_def = f"{col_name} {col_type}"
                column_definitions.append(column_def)
                logger.debug(f"列 {i+1}: {col_name} ({col_type}) - {comment}")
            
            # 创建表
            create_sql = f"CREATE TABLE {table_name} ({', '.join(column_definitions)})"
            cursor.execute(create_sql)
            logger.info(f"成功创建表 {table_name}，共 {len(column_definitions)} 个字段")
            
            # 准备数据并插入
            if not data_rows.empty:
                # 设置正确的列名
                data_rows.columns = clean_column_names
                
                # 处理缺失值
                data_rows = data_rows.fillna('')
                
                # 生成插入语句
                placeholders = ', '.join(['?' for _ in clean_column_names])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(clean_column_names)}) VALUES ({placeholders})"
                
                # 批量插入数据
                data_to_insert = data_rows.values.tolist()
                cursor.executemany(insert_sql, data_to_insert)
                
                self.connection.commit()
                logger.info(f"成功向表 {table_name} 插入 {len(data_to_insert)} 条记录")
            else:
                logger.warning(f"表 {table_name} 没有数据行可插入")
            
        except Exception as e:
            logger.error(f"创建表 {table_name} 失败: {e}")
            if self.connection:
                self.connection.rollback()
    
    def map_sql_type(self, sql_type: str) -> str:
        """
        映射SQL数据类型到SQLite支持的类型
        
        Args:
            sql_type: 原始SQL数据类型
            
        Returns:
            SQLite支持的数据类型
        """
        sql_type = str(sql_type).upper().strip()
        
        # 处理常见的SQL类型映射
        type_mapping = {
            'VARCHAR': 'TEXT',
            'CHAR': 'TEXT',
            'TEXT': 'TEXT',
            'STRING': 'TEXT',
            'INT': 'INTEGER',
            'INTEGER': 'INTEGER',
            'BIGINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'TINYINT': 'INTEGER',
            'FLOAT': 'REAL',
            'DOUBLE': 'REAL',
            'DECIMAL': 'REAL',
            'NUMERIC': 'REAL',
            'REAL': 'REAL',
            'BOOLEAN': 'INTEGER',
            'BOOL': 'INTEGER',
            'DATE': 'TEXT',
            'DATETIME': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'TIME': 'TEXT'
        }
        
        # 处理带长度的类型（如VARCHAR(255)）
        base_type = sql_type.split('(')[0].strip()
        
        mapped_type = type_mapping.get(base_type, 'TEXT')
        logger.debug(f"映射数据类型: {sql_type} -> {mapped_type}")
        
        return mapped_type
    
    def clean_column_name(self, column_name: str) -> str:
        """
        清理列名，使其适合作为SQL列名
        
        Args:
            column_name: 原始列名
            
        Returns:
            清理后的列名
        """
        # 移除特殊字符，保留中文、英文、数字和下划线
        import re
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '_', str(column_name))
        cleaned = cleaned.strip('_')
        return cleaned if cleaned else 'column'
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            logger.error(f"SQL: {query}")
            logger.error(f"参数: {params}")
            raise
    
    # ========== 生活垃圾监管功能 ==========
    
    def get_realtime_clearance_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        功能1: 展示全区清运实时数据
        
        Args:
            date: 查询日期，默认为今天 (YYYY-MM-DD格式)
            
        Returns:
            包含清运概览和明细的数据
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 查询清运概览
        overview_query = """
        SELECT 
            street_name AS 街道,
            type_name AS 垃圾类型,
            COUNT(*) AS 清运次数,
            SUM(CAST(garbage_weight AS FLOAT)) AS 总清运量,
            COUNT(DISTINCT vehicle_license_num) AS 参与车辆数,
            MAX(load_time_str) AS 最新清运时间
        FROM garbage_data 
        WHERE DATE(load_time_str) = ?
        GROUP BY street_name, type_name
        ORDER BY 总清运量 DESC
        """
        
        # 查询清运明细
        detail_query = """
        SELECT 
            load_time_str AS 清运时间,
            street_name AS 街道,
            community_name AS 小区,
            type_name AS 垃圾类型,
            garbage_weight AS 清运量,
            vehicle_license_num AS 车牌号,
            car_group_name AS 车队
        FROM garbage_data 
        WHERE DATE(load_time_str) = ?
        ORDER BY load_time_str DESC
        LIMIT 100
        """
        
        overview = self.execute_query(overview_query, (date,))
        details = self.execute_query(detail_query, (date,))
        
        return {
            "查询日期": date,
            "清运概览": overview,
            "清运明细": details,
            "统计时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_street_clearance_statistics(self, start_date: str, end_date: str, 
                                      street_name: Optional[str] = None) -> Dict[str, Any]:
        """
        功能2: 筛选查询各街道清运数量
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            street_name: 指定街道名称，为None时查询所有街道
            
        Returns:
            街道清运统计数据
        """
        # 基础查询语句
        base_query = """
        SELECT 
            street_name AS 街道,
            type_name AS 垃圾类型,
            COUNT(*) AS 清运次数,
            SUM(CAST(garbage_weight AS FLOAT)) AS 总清运量,
            AVG(CAST(garbage_weight AS FLOAT)) AS 平均清运量,
            COUNT(DISTINCT community_name) AS 涉及小区数
        FROM garbage_data 
        WHERE load_time_str BETWEEN ? AND ?
        """
        
        params = [start_date, end_date]
        
        # 如果指定了街道，添加过滤条件
        if street_name:
            base_query += " AND street_name = ?"
            params.append(street_name)
        
        base_query += """
        GROUP BY street_name, type_name
        ORDER BY street_name, 总清运量 DESC
        """
        
        # 查询趋势数据
        trend_query = """
        SELECT 
            street_name AS 街道,
            DATE(load_time_str) AS 日期,
            SUM(CAST(garbage_weight AS FLOAT)) AS 日清运量
        FROM garbage_data 
        WHERE load_time_str BETWEEN ? AND ?
        """
        
        trend_params = [start_date, end_date]
        if street_name:
            trend_query += " AND street_name = ?"
            trend_params.append(street_name)
        
        trend_query += """
        GROUP BY street_name, DATE(load_time_str)
        ORDER BY 街道, 日期
        """
        
        statistics = self.execute_query(base_query, tuple(params))
        trends = self.execute_query(trend_query, tuple(trend_params))
        
        return {
            "查询时间段": f"{start_date} 至 {end_date}",
            "指定街道": street_name or "全部街道",
            "清运统计": statistics,
            "清运趋势": trends
        }
    
    def get_overdue_issues(self) -> Dict[str, Any]:
        """
        功能3: 整治逾期混运等问题
        
        Returns:
            包含小包垃圾超时和垃圾桶满溢超时问题的数据
        """
        # 小包垃圾超时未处置问题
        small_package_query = """
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
        ORDER BY drop_time DESC
        """
        
        # 垃圾桶满溢超时问题
        overflow_query = """
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
        ORDER BY full_time DESC
        """
        
        small_package_issues = self.execute_query(small_package_query)
        overflow_issues = self.execute_query(overflow_query)
        
        return {
            "小包垃圾超时问题": {
                "问题数量": len(small_package_issues),
                "问题详情": small_package_issues
            },
            "垃圾桶满溢问题": {
                "问题数量": len(overflow_issues),
                "问题详情": overflow_issues
            },
            "查询时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # ========== 装修垃圾监管功能 ==========
    
    def get_decoration_appointments_data(self, days_back: int = 30) -> Dict[str, Any]:
        """
        功能4: 接入新旧模式预约数据
        
        Args:
            days_back: 查询最近多少天的数据
            
        Returns:
            整合的新旧模式预约数据
        """
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # 整合新旧模式数据的查询
        integrated_query = """
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
        WHERE DATE(create_time_str) >= ?
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
        WHERE DATE(create_order_time) >= ?
        ORDER BY 创建时间 DESC
        """
        
        # 统计查询
        stats_query = """
        SELECT 
            '老模式' AS 模式,
            COUNT(*) AS 总订单数,
            COUNT(CASE WHEN order_state = '7' THEN 1 END) AS 已完成,
            COUNT(CASE WHEN is_over_time = '是' THEN 1 END) AS 超时订单
        FROM decoration_garbage_old
        WHERE DATE(create_time_str) >= ?
        UNION ALL
        SELECT 
            '新模式' AS 模式,
            COUNT(*) AS 总订单数,
            COUNT(CASE WHEN order_state = '已完成' THEN 1 END) AS 已完成,
            NULL AS 超时订单
        FROM decoration_garbage_new
        WHERE DATE(create_order_time) >= ?
        """
        
        appointments = self.execute_query(integrated_query, (cutoff_date, cutoff_date))
        statistics = self.execute_query(stats_query, (cutoff_date, cutoff_date))
        
        return {
            "查询天数": days_back,
            "预约数据": appointments,
            "统计信息": statistics,
            "数据总数": len(appointments)
        }
    
    def get_order_status_details(self, status: Optional[str] = None, 
                               mode: Optional[str] = None) -> Dict[str, Any]:
        """
        功能5: 查看各状态工单详情
        
        Args:
            status: 筛选特定状态的工单
            mode: 筛选模式 ('老模式' 或 '新模式')
            
        Returns:
            工单状态统计和详情
        """
        # 工单状态统计
        status_stats_query = """
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
        ORDER BY 模式, 工单数量 DESC
        """
        
        # 工单详情查询
        detail_query = """
        SELECT 
            '老模式' AS 模式,
            CAST(bg_order_id AS TEXT) AS 订单号,
            street_name AS 街道,
            community_name AS 小区,
            order_state_desc AS 状态,
            create_time_str AS 创建时间,
            estimate_clear_time_str AS 预约时间,
            finish_time_str AS 完成时间,
            CASE WHEN is_over_time = '是' THEN '是' ELSE '否' END AS 是否超时
        FROM decoration_garbage_old
        WHERE 1=1
        """
        
        detail_params = []
        
        # 添加筛选条件
        if status:
            detail_query += " AND order_state_desc = ?"
            detail_params.append(status)
        
        if mode == '老模式':
            pass  # 已经只查询老模式
        elif mode == '新模式':
            detail_query = """
            SELECT 
                '新模式' AS 模式,
                appointment_order_id AS 订单号,
                street_name AS 街道,
                community_name AS 小区,
                order_state AS 状态,
                create_order_time AS 创建时间,
                resident_appointment_time AS 预约时间,
                NULL AS 完成时间,
                NULL AS 是否超时
            FROM decoration_garbage_new
            WHERE 1=1
            """
            detail_params = []
            if status:
                detail_query += " AND order_state = ?"
                detail_params.append(status)
        elif mode is None:
            # 查询两种模式
            new_mode_query = """
            UNION ALL
            SELECT 
                '新模式' AS 模式,
                appointment_order_id AS 订单号,
                street_name AS 街道,
                community_name AS 小区,
                order_state AS 状态,
                create_order_time AS 创建时间,
                resident_appointment_time AS 预约时间,
                NULL AS 完成时间,
                NULL AS 是否超时
            FROM decoration_garbage_new
            WHERE 1=1
            """
            if status:
                new_mode_query += " AND order_state = ?"
                detail_params.append(status)
            
            detail_query += new_mode_query
        
        detail_query += " ORDER BY 创建时间 DESC"
        
        status_stats = self.execute_query(status_stats_query)
        order_details = self.execute_query(detail_query, tuple(detail_params))
        
        return {
            "筛选条件": {
                "状态": status or "全部状态",
                "模式": mode or "全部模式"
            },
            "状态统计": [e for e in status_stats if e['模式'] == mode],
            "工单详情": order_details,
            "查询结果数": len(order_details)
        }
    
    # ========== 辅助功能 ==========
    
    def check_data_quality(self) -> Dict[str, Any]:
        """
        检查数据质量
        
        Returns:
            数据质量报告
        """
        quality_checks = []
        
        # 检查各表的数据完整性
        tables_to_check = [
            ("garbage_data", "干湿垃圾数据", ["street_name", "garbage_weight"]),
            ("small_package_garbage", "小包垃圾落地", ["division_name", "drop_time"]),
            ("garbage_bin_overflow", "垃圾桶满溢", ["station_name", "full_time"]),
            ("decoration_garbage_old", "装修垃圾老模式", ["street_name", "create_time_str"]),
            ("decoration_garbage_new", "装修垃圾新模式", ["street_name", "create_order_time"])
        ]
        
        for table_name, display_name, key_fields in tables_to_check:
            try:
                # 总行数
                count_query = f"SELECT COUNT(*) as total FROM {table_name}"
                total_result = self.execute_query(count_query)
                total_count = total_result[0]['total'] if total_result else 0
                
                # 检查关键字段缺失
                missing_data = {}
                for field in key_fields:
                    missing_query = f"""
                    SELECT COUNT(*) as missing 
                    FROM {table_name} 
                    WHERE {field} IS NULL OR {field} = ''
                    """
                    missing_result = self.execute_query(missing_query)
                    missing_count = missing_result[0]['missing'] if missing_result else 0
                    missing_data[field] = {
                        "缺失数量": missing_count,
                        "缺失率": f"{(missing_count/total_count*100):.2f}%" if total_count > 0 else "0%"
                    }
                
                quality_checks.append({
                    "表名": display_name,
                    "总行数": total_count,
                    "字段缺失情况": missing_data
                })
                
            except Exception as e:
                quality_checks.append({
                    "表名": display_name,
                    "错误": str(e)
                })
        
        return {
            "数据质量检查": quality_checks,
            "检查时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_available_date_range(self) -> Dict[str, Any]:
        """
        获取可用的数据日期范围
        
        Returns:
            各表的数据日期范围
        """
        date_ranges = {}
        
        # 检查干湿垃圾数据日期范围
        garbage_query = """
        SELECT 
            MIN(DATE(load_time_str)) as min_date,
            MAX(DATE(load_time_str)) as max_date,
            COUNT(DISTINCT DATE(load_time_str)) as date_count
        FROM garbage_data
        WHERE load_time_str IS NOT NULL
        """
        
        # 检查装修垃圾老模式日期范围
        old_decoration_query = """
        SELECT 
            MIN(DATE(create_time_str)) as min_date,
            MAX(DATE(create_time_str)) as max_date,
            COUNT(DISTINCT DATE(create_time_str)) as date_count
        FROM decoration_garbage_old
        WHERE create_time_str IS NOT NULL
        """
        
        # 检查装修垃圾新模式日期范围
        new_decoration_query = """
        SELECT 
            MIN(DATE(create_order_time)) as min_date,
            MAX(DATE(create_order_time)) as max_date,
            COUNT(DISTINCT DATE(create_order_time)) as date_count
        FROM decoration_garbage_new
        WHERE create_order_time IS NOT NULL
        """
        
        try:
            garbage_range = self.execute_query(garbage_query)
            date_ranges["干湿垃圾数据"] = garbage_range[0] if garbage_range else {}
            
            old_decoration_range = self.execute_query(old_decoration_query)
            date_ranges["装修垃圾老模式"] = old_decoration_range[0] if old_decoration_range else {}
            
            new_decoration_range = self.execute_query(new_decoration_query)
            date_ranges["装修垃圾新模式"] = new_decoration_range[0] if new_decoration_range else {}
            
        except Exception as e:
            logger.error(f"获取日期范围失败: {e}")
        
        return {
            "数据日期范围": date_ranges,
            "查询时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        } 