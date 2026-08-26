from TestDatas import Comm_Datas

# 导航栏直接跳转
nav_click_datas = [
    {"nav_name": "个人中心", "url": Comm_Datas.per_space_url},
    {"nav_name": '巡课督导', "url": Comm_Datas.round_class_url},
    {"nav_name": '首页', "url": Comm_Datas.index_url},
]

menu_click_datas = [
    {"nav_name": "基础信息", "menu_name": "组织信息", "url": Comm_Datas.organize_info_url},
    {"nav_name": "基础信息", "menu_name": "教室管理", "url": Comm_Datas.classroom_url},
    {"nav_name": "基础信息", "menu_name": "教职工管理", "url": Comm_Datas.teacher_url},
    {"nav_name": "基础信息", "menu_name": "学生管理", "url": Comm_Datas.student_url},
    {"nav_name": "基础信息", "menu_name": "角色权限", "url": Comm_Datas.role_url},
    {"nav_name": "基础信息", "menu_name": "课程管理", "url": Comm_Datas.class_url},
    {"nav_name": "录播管理", "menu_name": "录制管理", "url": Comm_Datas.record_url},
    {"nav_name": "录播管理", "menu_name": "资源管理", "url": Comm_Datas.resource_url},
    {"nav_name": "设备管理", "menu_name": "设备管理", "url": Comm_Datas.device_url},
    {"nav_name": "设备管理", "menu_name": "应用管理", "url": Comm_Datas.app_url},
]
