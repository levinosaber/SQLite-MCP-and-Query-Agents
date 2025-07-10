# shanghaichengdi

![image.png](image.png)

- 居住区详情
    
    
    | 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率（%） | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率 |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | id | int64 | 主键 | 0 | 0 | 1071 | 0 | 0 | 0 |
    | community_id | int64 | 小区ID | 89 | 8.31 | 962 | 2 | 22 | 2.05 |
    | community_name | object | 小区名称 | 0 | 0 | 1071 | 0 | 0 | 0 |
    | street | object | 街道 | 0 | 0 | 13 | 13 | 1071 | 100 |
    | committee | 0bject | 居委 | 46 | 4.3 | 374 | 236 | 887 | 82.82 |
    | committee_phone | object | 居委电话 | 816 | 76.19 | 108 | 57 | 204 | 19.05 |
    | address | object | 地址 | 0 | 0 | 1067 | 2 | 6 | 0.56 |
    | completion_date | object | 竣工时间 | 139 | 12.98 | 356 | 90 | 666 | 62.18 |
    | floor_area | object | 建筑面积 | 168 | 15.69 | 888 | 4 | 19 | 1.77 |
    | building_number | float64 | 楼栋数量 | 121 | 11.3 | 152 | 97 | 895 | 83.57 |
    | household_number | float64 | 房屋数量（户数） | 78 | 7.28 | 612 | 220 | 601 | 56.12 |
    | natong | float64 | 是否纳统 | 0 | 0 | 3 | 3 | 1071 | 100 |
    | household_property | float64 | 房屋性质 | 923 | 86.18 | 6 | 5 | 147 | 13.73 |
    | community_image | object | 小区照片 | 699 | 65.27 | 372 | 0 | 0 | 0 |
    | x | object | x坐标 | 1 | 0.09 | 1060 | 9 | 19 | 1.77 |
    | y | object | y坐标 | 1 | 0.09 | 1060 | 9 | 19 | 1.77 |
    | geometry | float64 | 小区范围 | 122 | 11.39 | 942 | 7 | 14 | 1.31 |
- 商铺详情
    
    
    | 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | id | object | 主键 | 0 | 0.00% | 60 | 0 | 0 | 0.00% |
    | company_name | object | 商铺名称 | 0 | 0.00% | 47 | 13 | 26 | 43.33% |
    | company_town_string | object | 街道 | 0 | 0.00% | 2 | 2 | 60 | 100.00% |
    | company_addr | object | 地址 | 0 | 0.00% | 48 | 12 | 24 | 40.00% |
    | x | object | x坐标 | 8 | 13.33% | 45 | 6 | 13 | 21.67% |
    | y | object | y坐标 | 8 | 13.33% | 45 | 6 | 13 | 21.67% |
    | fftt_lon | object | 经度 | 8 | 13.33% | 45 | 6 | 13 | 21.67% |
    | fftt_lat | object | 纬度 | 8 | 13.33% | 45 | 6 | 13 | 21.67% |
- 单位详情
    
    
    | 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | id | int64 | 主键 | 0 | 0 | 2280 | 0 | 0 | 0.00% |
    | street | object | 街道 | 0 | 0 | 14 | 14 | 2280 | 100.00% |
    | unit_name | object | 单位名称 | 0 | 0 | 1560 | 476 | 1196 | 52.46% |
    | unit_address | object | 单位地址 | 3 | 0.13 | 2069 | 135 | 343 | 15.04% |
    | property_contact | float64 | 物业联系人 | 2280 | 100 | 0 | 0 | 0 | 0.00% |
    | property_contact_phone | float64 | 物业联系电话 | 2280 | 100 | 0 | 0 | 0 | 0.00% |
    | remarks | float64 | 备注 | 2280 | 100 | 0 | 0 | 0 | 0.00% |
    | unit_nature | float64 | 单位性质 | 2280 | 100 | 0 | 0 | 0 | 0.00% |
    | property_company_name | float64 | 物业公司名称 | 2280 | 100 | 0 | 0 | 0 | 0.00% |
    | x | float64 | x坐标 | 1943 | 85.22 | 293 | 27 | 71 | 3.11% |
    | y | float64 | y坐标 | 1943 | 85.22 | 292 | 26 | 71 | 3.11% |
    | fftt_lon | float64 | 经度 | 1943 | 85.22 | 293 | 27 | 71 | 3.11% |
    | fftt_lat | float64 | 纬度 | 1943 | 85.22 | 293 | 27 | 71 | 3.11% |

- 干湿垃圾数据

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | object | 主键 | 0 | 0 | 6768 | 0 | 0 | 0 |
| area_name | object | 区 | 2837 | 41.92 | 1 | 1 | 3931 | 58.08 |
| street_name | object | 街道 | 4 | 0.06 | 20 | 20 | 6764 | 99.94 |
| community_name | object | 小区名称 | 9 | 0.13 | 3422 | 2254 | 5591 | 82.61 |
| operation_site_address | object | 作业点地址 | 6768 | 100 | 0 | 0 | 0 | 0 |
| car_group_name | object | 车队 | 2837 | 41.92 | 13 | 13 | 3931 | 58.08 |
| load_time_str | object | 清运时间 | 0 | 0 | 6345 | 398 | 821 | 12.13 |
| vehicle_license_num | object | 车牌 | 0 | 0 | 154 | 152 | 6766 | 99.97 |
| garbage_weight | object | 清运量 | 0 | 0 | 1130 | 665 | 6303 | 93.13 |
| type_name | object | 垃圾类型 | 0 | 0 | 4 | 4 | 6768 | 100 |
| trn_counts | object | 桶数 | 2837 | 41.92 | 102 | 65 | 3894 | 57.54 |
| trip_num | object | 趟次 | 6768 | 100 | 0 | 0 | 0 | 0 |
| converted_baidu_latitude | object | 百度纬度 | 2837 | 41.92 | 3866 | 58 | 123 | 1.82 |
| converted_baidu_longitude | object | 百度经度 | 2837 | 41.92 | 3866 | 58 | 123 | 1.82 |
| community_type_name | object | 小区类型名称 | 0 | 0 | 2 | 2 | 6768 | 100 |
- 小包垃圾落地详情

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率（%） |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event_id | object | 事件ID | 0 | 0 | 836 | 0 | 0 | 0.00% |
| station_id | int64 | 垃圾房 ID | 0 | 0 | 171 | 139 | 804 | 96.17% |
| station_name | object | 垃圾房名称 | 0 | 0 | 171 | 139 | 804 | 96.17% |
| division_id | int64 | 区划 ID | 0 | 0 | 99 | 89 | 826 | 98.80% |
| division_name | object | 区划名称 | 0 | 0 | 99 | 89 | 826 | 98.80% |
| grid_cell_id | float64 | 网格单元 ID | 836 | 100 | 0 | 0 | 0 | 0.00% |
| grid_cell_name | float64 | 网格单元名称 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| drop_time | object | 落地时间 | 0 | 0 | 715 | 90 | 211 | 25.24% |
| handle_time | object | 处置时间 | 1 | 0.12 | 679 | 119 | 275 | 32.89% |
| is_handle | bool | 小包垃圾滞留是否已处置 | 0 | 0 | 2 | 1 | 835 | 99.88% |
| is_timeout | bool | 是否超时 | 0 | 0 | 2 | 2 | 836 | 100.00% |
| drop_image_urls | object | 垃圾落地的图片 | 0 | 0 | 835 | 1 | 2 | 0.24% |
| handle_image_urls | object | 垃圾处置的图片 | 0 | 0 | 833 | 1 | 4 | 0.48% |
| timeout_image_urls | object | 超时未处置的图片 | 0 | 0 | 122 | 1 | 715 | 85.53% |
| processed | float64 | 处置人员是否已处置 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| processor_name | float64 | 处置人员名称 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| processor_id | float64 | 处置人员 ID | 836 | 100 | 0 | 0 | 0 | 0.00% |
| processor_mobile_no | float64 | 手机号码 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| process_time | float64 | 处置时间 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| process_description | float64 | 处置描述 | 836 | 100 | 0 | 0 | 0 | 0.00% |
| community_id | float64 | 小区ID | 836 | 100 | 0 | 0 | 0 | 0.00% |
| community_name | object | 小区名 | 0 | 0 | 168 | 136 | 804 | 96.17% |
| record_no | int64 | 记录ID | 0 | 0 | 836 | 0 | 0 | 0.00% |
| take_minutes | float64 | 花费分钟 | 2 | 0.24 | 750 | 51 | 135 | 16.15% |
- 合同详情

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guid | object | 主键 | 0 | 0 | 4425 | 0 | 0 | 0 |
| code | object | 合同编号 | 0 | 0 | 4425 | 0 | 0 | 0 |
| declare_date | object | 申报时间 | 0 | 0 | 1709 | 23 | 3202 | 61.38 |
| active_date | object | 起始-合同有效期 | 0 | 0 | 155 | 43 | 4345 | 96.5 |
| deactive_date | object | 结束-合同有效期 | 0 | 0 | 53 | 1 | 4345 | 98.8 |
| accept_date | object | 签约日期 | 0 | 0 | 726 | 1 | 4345 | 83.59 |
| company_name | object | 产生单位名称 | 0 | 0 | 2021 | 1220 | 2338 | 54.33 |
| company_town_string | object | 产生单位街道 | 0 | 0 | 14 | 14 | 4332 | 99.68 |
| company_address | object | 产生单位地址 | 1 | 0.02 | 2620 | 1060 | 1768 | 40.79 |
| transport_name | object | 运输单位名称 | 1146 | 25.9 | 1 | 1 | 4345 | 99.98 |
| clerk_name | object | 收费员名称 | 0 | 0 | 10 | 9 | 4336 | 99.77 |
| summary | float64 | 合同总金额 | 0 | 0 | 1374 | 513 | 2984 | 68.95 |
| g_summary | float64 | 干垃圾金额 | 0 | 0 | 871 | 363 | 3484 | 80.32 |
| c_summary | float64 | 餐厨垃圾金额 | 0 | 0 | 611 | 253 | 3744 | 86.19 |
| s_summary | int64 | 湿垃圾金额 | 0 | 0 | 156 | 59 | 4191 | 96.47 |
| g_amountm | float64 | 干垃圾申报量 | 0 | 0 | 170 | 110 | 4176 | 96.16 |
| c_amountm | float64 | 餐厨垃圾申报量 | 0 | 0 | 95 | 54 | 4251 | 97.85 |
| s_amountm | float64 | 湿垃圾申报量 | 0 | 0 | 38 | 19 | 4308 | 99.14 |
- 垃圾桶满溢详情

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event_id | object | 事件ID | 0 | 0.00% | 1920 | 0 | 0 | 0.00% |
| station_id | int64 | 垃圾房
  ID | 0 | 0.00% | 196 | 183 | 1907 | 99.32% |
| station_name | object | 垃圾房名称 | 0 | 0.00% | 196 | 183 | 1907 | 99.32% |
| division_id | int64 | 区划
  ID | 0 | 0.00% | 105 | 102 | 1917 | 99.84% |
| division_name | object | 区划名称 | 0 | 0.00% | 105 | 102 | 1917 | 99.84% |
| full_time | object | 第一次满溢时间 | 0 | 0.00% | 1847 | 70 | 143 | 7.45% |
| image_urls | object | 图片
  ID、图片地址列表 | 0 | 0.00% | 1 | 1 | 1920 | 100.00% |
| camera_image_urls | object | 图片
  ID、图片地址列表 | 0 | 0.00% | 1920 | 0 | 0 | 0.00% |
| grid_cell_id | float64 | 网格单元
  ID | 1920 | 100.00% | 0 | 0 | 0 | 0.00% |
| grid_cell_name | float64 | 网格单元名称 | 1920 | 100.00% | 0 | 0 | 0 | 0.00% |
| community_id | float64 | 小区
  ID | 1920 | 100.00% | 0 | 0 | 0 | 0.00% |
| community_name | object | 小区名称 | 0 | 0.00% | 192 | 180 | 1908 | 99.38% |
| handle_time | object | 处置时间 | 147 | 7.66% | 1694 | 76 | 155 | 8.07% |
| is_handle | bool | 是否已处置 | 0 | 0.00% | 2 | 2 | 1920 | 100.00% |
| handle_image_urls | object | 处置图片 | 0 | 0.00% | 1774 | 1 | 147 | 7.66% |
| processed | object | 处置人员是否已处置 | 1838 | 95.73% | 2 | 2 | 82 | 4.27% |
| processor_name | object | 处置人员名称 | 1915 | 99.74% | 1 | 1 | 5 | 0.26% |
| processor_id | object | 处置人员
  ID | 1915 | 99.74% | 1 | 1 | 5 | 0.26% |
| processor_mobile_no | float64 | 手机号码 | 1915 | 99.74% | 1 | 1 | 5 | 0.26% |
| process_time | object | 处置时间 | 1915 | 99.74% | 5 | 0 | 0 | 0.00% |
| process_description | float64 | 处置描述 | 1920 | 100.00% | 0 | 0 | 0 | 0.00% |
- 装修垃圾预约（老模式）

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bg_order_id | int64 | 预约单id | 0 | 0 | 1223 | 0 | 0 | 0 |
| property_person_mobile | int64 | 上报人电话 | 0 | 0 | 338 | 238 | 1123 | 91.82 |
| street_name | object | 街道 | 0 | 0 | 14 | 14 | 1223 | 100 |
| community_name | object | 小区名 | 0 | 0 | 420 | 274 | 1077 | 88.06 |
| is_resident | int64 | 小区类型 | 0 | 0 | 2 | 2 | 1223 | 100 |
| is_resident_desc | object | 小区类型描述 | 0 | 0 | 2 | 2 | 1223 | 100 |
| order_mode | float64 | 上报模式 | 1166 | 95.34 | 3 | 3 | 57 | 4.66 |
| order_mode_desc | object | 上报模式描述 | 1166 | 95.34 | 3 | 3 | 57 | 4.66 |
| community_addr | object | 小区地址 | 57 | 4.66 | 409 | 264 | 1021 | 83.48 |
| garbage_put_addr | object | 堆放点 | 708 | 57.89 | 225 | 76 | 366 | 29.93 |
| garbage_type_name | object | 垃圾类型 | 708 | 57.89 | 1 | 1 | 515 | 42.11 |
| garbage_weight | float64 | 预约量（袋） | 1217 | 99.51 | 4 | 2 | 4 | 0.33 |
| create_time_str | datetime64[ns] | 上报时间 | 0 | 0 | 1221 | 2 | 4 | 0.33 |
| estimate_clear_time_str | datetime64[ns] | 预约清运时间 | 708 | 57.89 | 180 | 86 | 421 | 34.42 |
| order_over_time_str | datetime64[ns] | 超时时间 | 0 | 0 | 897 | 81 | 407 | 33.28 |
| vehicle_fleet_company_name | object | 指派车队的人 | 0 | 0 | 2 | 2 | 1223 | 100 |
| vehicle_fleet_name | object | 车队名 | 14 | 1.14 | 15 | 15 | 1209 | 98.86 |
| garbage_vehicle_times | float64 | 预计车次 | 714 | 58.38 | 10 | 8 | 507 | 41.46 |
| actual_garbage_vehicle_times | float64 | 完成趟次 | 113 | 9.24 | 14 | 11 | 1107 | 90.52 |
| vehicle_type_name | float64 | 车辆类型 | 1223 | 100 | 0 | 0 | 0 | 0 |
| vehicle_license_num | object | 车牌号 | 113 | 9.24 | 359 | 138 | 889 | 72.69 |
| clear_person_name | object | 清运人员 | 113 | 9.24 | 6 | 6 | 1110 | 90.76 |
| clear_person_mobile | float64 | 清运人电话 | 113 | 9.24 | 6 | 6 | 1110 | 90.76 |
| deal_order_time_str | datetime64[ns] | 接单时间 | 14 | 1.14 | 1209 | 0 | 0 | 0 |
| finish_time_str | datetime64[ns] | 完成时间 | 113 | 9.24 | 1110 | 0 | 0 | 0 |
| order_state | int64 | 状态 | 0 | 0 | 4 | 4 | 1223 | 100 |
| order_state_desc | object | 状态描述 | 0 | 0 | 4 | 4 | 1223 | 100 |
| user_remark | object | 备注 | 880 | 71.95 | 143 | 41 | 241 | 19.71 |
| is_over_time | object | 超时完成 | 1202 | 98.28 | 1 | 1 | 21 | 1.72 |
| is_valid | int64 | 订单有效性 1 有效，0 无效 | 0 | 0 | 2 | 2 | 1223 | 100 |
| upgrade_mode_str | object | 推进模式 | 57 | 4.66 | 3 | 3 | 1166 | 95.34 |
- 装修垃圾预约（新模式）

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| appointment_order_id | object | 预约单号 | 0 | 0 | 318 | 0 | 0 | 0 |
| street_name | object | 街道 | 0 | 0 | 11 | 9 | 316 | 99.37 |
| community_name | object | 小区 | 0 | 0 | 77 | 56 | 297 | 93.4 |
| address | object | 详细地址 | 0 | 0 | 171 | 74 | 221 | 69.5 |
| decoration_stage | object | 装修阶段 | 0 | 0 | 8 | 8 | 318 | 100 |
| resident_appointment_time | object | 居民预约时间 | 0 | 0 | 95 | 33 | 256 | 80.5 |
| second_confirmation_time | datetime64[ns] | 二次确认时间 | 6 | 1.89 | 311 | 1 | 2 | 0.63 |
| appointment_bags_number | int64 | 预约投放袋数 | 0 | 0 | 45 | 15 | 288 | 90.57 |
| appointment_large_items_number | int64 | 预约大件数量 | 0 | 0 | 2 | 2 | 318 | 100 |
| estimated_boxes_number | int64 | 预估箱数 | 0 | 0 | 17 | 12 | 313 | 98.43 |
| create_order_time | datetime64[ns] | 建单时间 | 0 | 0 | 318 | 0 | 0 | 0 |
| order_state | object | 预约单状态 | 0 | 0 | 4 | 4 | 318 | 100 |
| order_unit | object | 预约单单位 | 0 | 0 | 1 | 1 | 318 | 100 |
- 巡检详情

| 字段名 | 数据类型 | 备注 | 缺失值数量 | 缺失率(%) | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率(%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id | object | 主键 | 0 | 0 | 316 | 0 | 0 | 0 |
| createtime | object | 巡查时间 | 0 | 0 | 316 | 0 | 0 | 0 |
| total | float64 | 扣分 | 0 | 0 | 25 | 15 | 306 | 96.84 |
| county | object | 区 | 0 | 0 | 1 | 1 | 316 | 100 |
| town | object | 街道 | 0 | 0 | 13 | 13 | 316 | 100 |
| village | object | 居委 | 0 | 0 | 119 | 85 | 282 | 89.24 |
| name | object | 名称 | 0 | 0 | 316 | 0 | 0 | 0 |
| address | object | 地址 | 0 | 0 | 315 | 1 | 2 | 0.63 |
| type | object | 类型 | 0 | 0 | 1 | 1 | 316 | 100 |
- 居民区巡检

| 字段名 | 数据类型 | 缺失值数量 | 缺失率（%） | 唯一值数量 | 重复值种类 | 重复值总行数 | 重复率 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 居住区名称 | object | 0 | 0 | 316 | 0 | 0 | 0 |
| 巡查数 | int64 | 0 | 0 | 1 | 1 | 316 | 100 |
| 问题数 | int64 | 0 | 0 | 2 | 2 | 316 | 100 |
| 整改数 | int64 | 0 | 0 | 2 | 2 | 316 | 100 |
| 待整改数 | int64 | 0 | 0 | 2 | 2 | 316 | 100 |

- 清运单位对应

| 字段名 | 数据类型 | 备注 |
| --- | --- | --- |
| id | integer |  |
| unit_name | varchar(255) |  |
| unit_address | varchar(255) |  |
| vehicle_community_name | varchar(255) |  |
| street_name | varchar(50) |  |

- 清运小区对应

| 字段名 | 数据类型 |
| --- | --- |
| id | integer |
| base_community_name | varchar(255) |
| vehicle_community_name | varchar(255) |
| street_name | varchar(50) |