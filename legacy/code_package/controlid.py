from airtest.core.api import *
from airtest.core.android.android import *
from airtest.core.android.touch_methods.base_touch import *
from airtest.aircv.utils import cv2_2_pil
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import logging
import subprocess
import math
import time
import re
import random
import json
import requests
from datetime import datetime, timedelta
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=True)
auto_setup(__file__)
android = device()
logger = logging.getLogger('test')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')


class HeyboardOs:

    #DOCK栏工具应用栏
    @staticmethod
    def tool_bar(poco):
        return poco('com.h3c.launcher:id/fl_left')


    #DOCK栏常用应用栏
    @staticmethod
    def favorite_bar(poco):
        return poco('com.h3c.launcher:id/ll_favorite_app')


    #音量图标
    @staticmethod
    def volume(poco):
        return poco('com.h3c.launcher:id/iv_volume')


    #下课图标
    @staticmethod
    def finish_class(poco):
        return poco('com.h3c.launcher:id/iv_finish_class')


    #左右同屏图标
    @staticmethod
    def mirror(poco):
        return poco('com.h3c.launcher:id/iv_mirror')


    #更多应用
    @staticmethod
    def more_app(poco):
        return poco('com.h3c.launcher:id/ll_more_app')


    #书写颜色-第一个颜色-红色
    @staticmethod
    def write_color1(poco):
        return poco('com.h3c.launcher:id/csv_blackboardos_ui_color_1')


    #书写颜色-第二个颜色-黄色
    @staticmethod
    def write_color2(poco):
        return poco('com.h3c.launcher:id/csv_blackboardos_ui_color_2')


    #书写颜色-第三个颜色-白色
    @staticmethod
    def write_color3(poco):
        return poco('com.h3c.launcher:id/csv_blackboardos_ui_color_3')


    #书写颜色-颜色库
    @staticmethod
    def write_colorful(poco):
        return poco('com.h3c.launcher:id/csv_blackboardos_ui_colorful')


    #书写颜色-颜色库_颜色弹窗
    @staticmethod
    def write_colorful_pop(poco):
        return poco('com.h3c.launcher:id/cl_ui_more_color')


    #书写颜色-颜色库-颜色弹窗-颜色选择
    @staticmethod
    def write_colorful_pop_select(poco):
        return poco('com.h3c.launcher:id/mcv_ui_color')


    #书写颜色-颜色库-颜色弹窗-颜色选择历史栏
    @staticmethod
    def write_colorful_pop_history(poco):
        return poco('com.h3c.launcher:id/cl_ui_history')


    #橡皮图标
    @staticmethod
    def rubber_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_rubber").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #橡皮弹窗-橡皮图标
    @staticmethod
    def rubber_rubber_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_erase").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #橡皮弹窗-橡皮文字
    @staticmethod
    def rubber_rubber_text(poco):
        return poco("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_erase").offspring("com.h3c.launcher:id/tv_ui_button_text")


    #橡皮弹窗-清屏图标
    @staticmethod
    def rubber_clear_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_clear_screen").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #选择图标
    @staticmethod
    def select_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_select").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #插入图标
    @staticmethod
    def insert_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_insert").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #插入-图片图标
    @staticmethod
    def insert_image_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/tbv_ui_insert_picture").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #插入-书写模板图标
    @staticmethod
    def insert_template_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/tbv_ui_writing_template").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #插入-图片-图片弹窗
    @staticmethod
    def insert_image_pop(poco):
        return poco('com.h3c.launcher:id/simpleFilePickView')


    #插入-图片-图片弹窗-右侧文件归属文件夹名称
    @staticmethod
    def insert_image_pop_file_belong(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/simpleFilePickView").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/tv_text")


    #插入-图片-图片弹窗-暂无文件图标
    @staticmethod
    def insert_image_pop_file_empty(poco):
        return poco('com.h3c.launcher:id/iv_empty')


    #插入-书写模板-书写模板弹窗
    @staticmethod
    def insert_template_pop(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").child("android.view.ViewGroup")


    #插入-书写模板-书写模板弹窗-点阵格
    @staticmethod
    def insert_template_pop_lattices(poco):
        return poco('com.h3c.launcher:id/wt_ui_dian_zhen_ge')


    #插入-书写模板-书写模板弹窗-点阵格图案
    @staticmethod
    def insert_template_pop_lattices_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_dian_zhen_ge").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #插入-书写模板-书写模板弹窗-米字格
    @staticmethod
    def insert_template_pop_mi(poco):
        return poco('com.h3c.launcher:id/wt_ui_mi_zi_ge')


    #插入-书写模板-书写模板弹窗-米字格图案
    @staticmethod
    def insert_template_pop_mi_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_mi_zi_ge").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #插入-书写模板-书写模板弹窗-田字格
    @staticmethod
    def insert_template_pop_tian(poco):
        return poco('com.h3c.launcher:id/wt_ui_tian_zi_ge')


    #插入-书写模板-书写模板弹窗-田字格图案
    @staticmethod
    def insert_template_pop_tian_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_tian_zi_ge").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #插入-书写模板-书写模板弹窗-三线四格
    @staticmethod
    def insert_template_pop_4grids (poco):
        return poco('com.h3c.launcher:id/wt_ui_three_lines_four_grids')


    #插入-书写模板-书写模板弹窗-三线四格图案
    @staticmethod
    def insert_template_pop_4grids_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_three_lines_four_grids").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #插入-书写模板-书写模板弹窗-拼音格
    @staticmethod
    def insert_template_pop_pinyin(poco):
        return poco('com.h3c.launcher:id/wt_ui_ping_yin_grids')


    #插入-书写模板-书写模板弹窗-拼音格图案
    @staticmethod
    def insert_template_pop_pinyin_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_ping_yin_grids").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #插入-书写模板-书写模板弹窗-五线谱
    @staticmethod
    def insert_template_pop_staff(poco):
        return poco('com.h3c.launcher:id/wt_ui_staff')


    #插入-书写模板-书写模板弹窗-五线谱图案
    @staticmethod
    def insert_template_pop_staff_pattern(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.launcher:id/wt_ui_staff").offspring("com.h3c.launcher:id/iv_ui_writing_template")


    #撤回图标
    @staticmethod
    def withdraw_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_revoke").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #黑板图标
    @staticmethod
    def blackboard_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_infinite_canvas").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #黑板弹窗
    @staticmethod
    def blackboard_pop(poco):
        return poco('com.h3c.launcher:id/rv_ui_infinitecanvas')


    #上一页图标
    @staticmethod
    def previous_page(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_previous_page").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #下一页图标
    @staticmethod
    def next_page(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_next_page").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #分享图标
    @staticmethod
    def share_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_scan_share").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #分享弹窗-顶部栏
    @staticmethod
    def share_pop_top(poco):
        return poco('com.h3c.launcher:id/top_bar')


    #分享弹窗-分享页选择
    @staticmethod
    def share_pop_page_select(poco):
        return poco('com.h3c.launcher:id/rv_page_preview')


    #分享弹窗-二维码上方文字提示
    @staticmethod
    def share_pop_tips(poco):
        return poco('com.h3c.launcher:id/tv_connect_tips')


    #分享弹窗-二维码
    @staticmethod
    def share_pop_qrcode(poco):
        return poco('com.h3c.launcher:id/iv_qrcode')


    #分享弹窗-二维码放大按钮
    @staticmethod
    def share_pop_qrcode_enlarge(poco):
        return poco('com.h3c.launcher:id/iv_enlarge_qrcode')


    #分享弹窗-放大后的二维码
    @staticmethod
    def share_enlarge_qrcode(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("android.widget.ImageView")


    #文件图标
    @staticmethod
    def file_icon(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/tbv_ui_file").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")


    #文件弹窗_保存图标
    @staticmethod
    def file_save(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_save_save").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #文件弹窗_另存为图标
    @staticmethod
    def file_save_as(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_save_as").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #文件弹窗_打开图标
    @staticmethod
    def file_save_open(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_open_file").offspring("com.h3c.launcher:id/iv_ui_button_icon")


    #保存弹窗
    @staticmethod
    def save_pop(poco):
        return poco('androidx.appcompat.widget.LinearLayoutCompat')


    #保存弹窗-顶部栏
    @staticmethod
    def save_pop_top(poco):
        return poco('com.h3c.launcher:id/top_bar')


    #保存弹窗-顶部栏标题
    @staticmethod
    def save_pop_title(poco):
        return poco('com.h3c.launcher:id/tv_top_bar_title')


    #保存弹窗-文件名称输入框
    @staticmethod
    def file_name_input(poco):
        return poco('com.h3c.launcher:id/et_file_name')


    #保存弹窗-保存路径输入框
    @staticmethod
    def save_path_input(poco):
        return poco('com.h3c.launcher:id/tv_save_path')


    #保存弹窗-保存路径下拉按钮
    @staticmethod
    def save_path_dropdown(poco):
        return poco('com.h3c.launcher:id/iv_save_path_arrow')


    #音量条
    @staticmethod
    def volume_bar(poco):
        return poco('com.h3c.launcher:id/vsb_volume')


    #音量条内声音icon
    @staticmethod
    def volume_bar_icon(poco):
        return poco('com.h3c.launcher:id/img_volume_icon')


    #文件管理器
    @staticmethod
    def file_manager(poco):
        return poco('文件管理器的标题栏。')


    #文件管理器搜索输入框
    @staticmethod
    def file_manage_search_input(poco):
        return poco('com.h3c.filemanager:id/et_key_word')


    #文件管理器搜索按钮
    @staticmethod
    def file_manage_search_icon(poco):
        return poco('com.h3c.filemanager:id/img_search')


    #本地文件总控件
    @staticmethod
    def local_files(poco):
        return poco('com.h3c.filemanager:id/local_file_layout')


    #本地文件总控件-本地下拉框
    @staticmethod
    def local_files_select(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("android.widget.ScrollView").offspring("com.h3c.filemanager:id/ll_title").child("com.h3c.filemanager:id/img_icon")


    #本地文件总控件-本地文件类型总控件
    @staticmethod
    def local_files_type_all(poco):
        return poco('com.h3c.filemanager:id/recycler')


    #外部文件总控件
    @staticmethod
    def external_files(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("android.widget.ScrollView").offspring("com.h3c.filemanager:id/recyclerView")


    #外部文件总控件-U盘名称
    @staticmethod
    def external_files_name(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("android.widget.ScrollView").offspring("com.h3c.filemanager:id/tv_name")


    #文件管理可用空间
    @staticmethod
    def files_available(poco):
        return poco('com.h3c.filemanager:id/tv_available')


    #文件管理可用空间条
    @staticmethod
    def files_available_bar(poco):
        return poco('com.h3c.filemanager:id/progress_bar')


    #文件管理器选择控件的文本
    @staticmethod
    def files_name_select(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/title_bar_action").child("com.h3c.filemanager:id/recyclerView").child("android.widget.LinearLayout")[2].child("com.h3c.filemanager:id/tv_name")


    #文件显示宫格模式
    @staticmethod
    def file_grid_type(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/title_bar_action").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/fr_grid").child("android.widget.ImageView")


    #文件显示列表模式
    @staticmethod
    def file_list_type(poco):
        return poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/title_bar_action").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/fr_grid").child("android.widget.ImageView")


    #新建文件夹弹窗
    @staticmethod
    def new_folder_pop(poco):
        return poco("android.widget.FrameLayout").offspring("com.h3c.filemanager:id/centerPopupContainer").child("android.widget.LinearLayout")


    #新建文件夹弹窗-文件名输入窗
    @staticmethod
    def new_folder_pop_name_input(poco):
        return poco('com.h3c.filemanager:id/et_input')


    #新建文件夹弹窗-文件名输入窗-清除按钮
    @staticmethod
    def new_folder_pop_name_input_clear(poco):
        return poco('com.h3c.filemanager:id/iv_delete')


    #新建文件夹弹窗-文件名输入错误提示文字
    @staticmethod
    def new_folder_pop_name_error_tip(poco):
        return poco('com.h3c.filemanager:id/textError')


    #新建文件弹窗-确认
    @staticmethod
    def files_confirm(poco):
        return poco("com.h3c.filemanager:id/confirm")


    #新建文件弹窗-取消
    @staticmethod
    def files_cancel(poco):
        return poco("com.h3c.filemanager:id/cancel")


    #获取粘贴弹窗-左上角文本
    @staticmethod
    def files_copy_text(poco):
        return poco("com.h3c.filemanager:id/tv_title")


    #复制到弹窗-粘贴
    @staticmethod
    def files_copy(poco):
        return poco("com.h3c.filemanager:id/copy")


    #复制到弹窗-关闭
    @staticmethod
    def files_copy_close(poco):
        return poco("com.h3c.filemanager:id/close")


    #复制到弹窗-新建文件夹
    @staticmethod
    def files_copy_newfolder(poco):
        return poco("com.h3c.filemanager:id/build_new_dir")


    #文件夹名称排序
    @staticmethod
    def folder_sort(poco):
        return poco('com.h3c.filemanager:id/iv_sort')


    #文件夹名称排序类型
    @staticmethod
    def folder_sort_type(poco):
        return poco('com.h3c.filemanager:id/tv_sortType')


    #文件夹名称排序下拉框
    @staticmethod
    def folder_sort_select(poco):
        return poco('com.h3c.filemanager:id/arrow')


    #书写模式按钮
    @staticmethod
    def commentary_write_mode(poco):
        return poco('com.h3c.commentary:id/menuitem_write_main_commentary')


    #触控模式按钮
    @staticmethod
    def commentary_touch_mode(poco):
        return poco('com.h3c.commentary:id/menuitem_touch_main_commentary')


    #触控模式下保存按钮
    @staticmethod
    def touch_save_icon(poco):
        return poco("com.h3c.commentary:id/floatmenu_touch_commentary").child("android.widget.FrameLayout").child("android.widget.ImageView")


    #书写模式下保存按钮
    @staticmethod
    def write_save_icon(poco):
        return poco("com.h3c.commentary:id/menuitem_write_main_commentary").child("android.widget.ImageView")


    #书写模式下退出按钮
    @staticmethod
    def write_mode_exit(poco):
        return poco('com.h3c.commentary:id/menuitem_write_exit_commentary')


    #触控模式下退出按钮
    @staticmethod
    def touch_mode_exit(poco):
        return poco('com.h3c.commentary:id/menuitem_touch_exit_commentary')


    #批注顶部书写模式控件
    @staticmethod
    def top_commentary_mode(poco):
        return poco("com.h3c.commentary:id/tv_write_model")


    #录屏主页控件
    @staticmethod
    def record_homepage(poco):
        return poco('com.h3c.screencap:id/record_start')


    #录屏主页-录屏图标控件
    @staticmethod
    def record_record_icon(poco):
        return poco('com.h3c.screencap:id/img_start')


    #录屏主页-录屏文字控件
    @staticmethod
    def record_record_text(poco):
        return poco('com.h3c.screencap:id/tv_record')


    #录屏主页-清晰度总控件
    @staticmethod
    def record_qulity_all(poco):
        return poco('com.h3c.screencap:id/btn_qulity')


    #录屏主页-清晰度-图标控件
    @staticmethod
    def record_qulity_icon(poco):
        return poco('com.h3c.screencap:id/img_qulity')


    #录屏主页-清晰度-下拉框控件
    @staticmethod
    def record_qulity_imgarrow(poco):
        return poco('com.h3c.screencap:id/imgArrow')


    #录屏主页-清晰度-清晰度文字控件
    @staticmethod
    def record_qulity_text(poco):
        return poco('com.h3c.screencap:id/tv_qulity')


    #录屏主页-麦克风总控件
    @staticmethod
    def record_mic_all(poco):
        return poco('com.h3c.screencap:id/btn_mic_start')


    #录屏主页-麦克风-麦克风图标控件
    @staticmethod
    def record_mic_icon(poco):
        return poco('com.h3c.screencap:id/img_mic_start')


    #录屏主页-麦克风-麦克风文字控件
    @staticmethod
    def record_mic_text(poco):
        return poco('com.h3c.screencap:id/tv_mic')


    #录屏主页-关闭控件
    @staticmethod
    def record_close(poco):
        return poco('com.h3c.screencap:id/btn_close')


    #录屏主页-正在录屏时-时间显示-时间显示控件
    @staticmethod
    def recording_time_show(poco):
        return poco('com.h3c.screencap:id/tvTime')


    #录屏主页-正在录屏时-麦克风控件
    @staticmethod
    def recording_mic(poco):
        return poco('com.h3c.screencap:id/btn_mic')


    #录屏主页-正在录屏时-开始按钮控件
    @staticmethod
    def recording_start(poco):
        return poco('com.h3c.screencap:id/btn_play')


    #录屏主页-正在录屏时-停止按钮控件
    @staticmethod
    def recording_stop(poco):
        return poco('com.h3c.screencap:id/btnStop')


    #录屏主页-结束录屏时-主页录屏标题控件
    @staticmethod
    def recorded_title(poco):
        return poco('com.h3c.screencap:id/title')


    #录屏主页-结束录屏时-主页录屏画面控件
    @staticmethod
    def recorded_frame(poco):
        return poco('com.h3c.screencap:id/surface')


    #录屏主页-结束录屏时-主页-录屏进度栏总栏控件
    @staticmethod
    def recorded_schedule(poco):
        return poco('com.h3c.screencap:id/layout_bottom')


    #录屏主页-结束录屏时-主页-录屏进度栏-开始/暂停按钮控件
    @staticmethod
    def recorded_start(poco):
        return poco("录屏的标题栏。").offspring("com.h3c.screencap:id/content").offspring("com.h3c.screencap:id/gsyVideoPlayer").offspring("com.h3c.screencap:id/start")


    #录屏主页-结束录屏时-主页-录屏进度栏-视频已播放时长控件
    @staticmethod
    def recorded_current(poco):
        return poco('com.h3c.screencap:id/current')


    #录屏主页-结束录屏时-主页-录屏进度栏-视频播放进度条控件
    @staticmethod
    def recorded_seek_progress(poco):
        return poco('com.h3c.screencap:id/bottom_seek_progress')


    #录屏主页-结束录屏时-主页-录屏进度栏-视频总时长控件
    @staticmethod
    def recorded_total_duration(poco):
        return poco('com.h3c.screencap:id/total')


    #录屏主页-结束录屏时-主页-重新录制控件
    @staticmethod
    def recorded_restart(poco):
        return poco('com.h3c.screencap:id/re_record')


    #录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-关闭控件
    @staticmethod
    def recorded_save_pop_close(poco):
        return poco('com.h3c.screencap:id/imgClose')


    #录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-文件名称标题输入框控件
    @staticmethod
    def recorded_save_pop_file_name_input(poco):
        return poco('com.h3c.screencap:id/editFileName')


    #录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-保存路径下拉框控件
    @staticmethod
    def recorded_save_pop_path_arrow(poco):
        return poco('com.h3c.screencap:id/imgArrow')


    #录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-保存路径下拉控件（当下拉只有一个）
    @staticmethod
    def recorded_save_pop_path_onlyone(poco):
        return poco("android.widget.FrameLayout").offspring("com.h3c.screencap:id/textPath")


    #录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-关闭按钮控件
    @staticmethod
    def recorded_scan_pop_close(poco):
        return poco('com.h3c.screencap:id/close')


    #录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-二维码图片控件
    @staticmethod
    def recorded_scan_pop_code(poco):
        return poco('com.h3c.screencap:id/cardView')


    #录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-二维码图片-放大按钮控件
    @staticmethod
    def recorded_scan_pop_code_enlarge(poco):
        return poco('com.h3c.screencap:id/img_enlarge')


    #录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-放大后的二维码控件
    @staticmethod
    def recorded_scan_pop_qrcode_amplify(poco):
        return poco('com.h3c.screencap:id/imgQrCode')


    #截屏主页控件
    @staticmethod
    def screenshot_homepage(poco):
        return poco('com.h3c.screenshot:id/crop_guide')


    #截屏后截图关闭按钮
    @staticmethod
    def screenshoted_close(poco):
        return poco('com.h3c.screenshot:id/iv_close')


    #截屏完成-分享文字+图标控件
    @staticmethod
    def screenshoted_share(poco):
        return poco('com.h3c.screenshot:id/tv_share')


    #截屏完成-本地保存文字+图标控件
    @staticmethod
    def screenshoted_save(poco):
        return poco('com.h3c.screenshot:id/tv_save')


    #截屏完成-本地保存弹窗-文件名称输入框控件
    @staticmethod
    def screenshoted_save_name_input(poco):
        return poco('com.h3c.screenshot:id/et_file_name')


    #截屏完成-本地保存弹窗-保存路径-下拉框图标控件
    @staticmethod
    def screenshoted_save_path_arrow(poco):
        return poco('com.h3c.screenshot:id/iv_storage')


    #截屏完成-分享弹窗-关闭
    @staticmethod
    def screenshoted_share_pop_close(poco):
        return poco('com.h3c.screenshot:id/share_close')


    #截屏完成-分享弹窗-分享应用列表
    @staticmethod
    def screenshoted_share_pop_applist(poco):
        return poco('com.h3c.screenshot:id/share_list')


    #截屏完成-分享弹窗-扫码带走弹窗-二维码
    @staticmethod
    def screenshoted_scan_code(poco):
        return poco('com.h3c.screenshot:id/iv_qrcode')


    #截屏完成-分享弹窗-扫码带走弹窗-二维码放大按钮
    @staticmethod
    def screenshoted_scan_enlarge_code(poco):
        return poco('com.h3c.screenshot:id/iv_enlarge')


    #截屏完成-分享弹窗-扫码带走弹窗-关闭
    @staticmethod
    def screenshoted_scan_close(poco):
        return poco('com.h3c.screenshot:id/iv_close')


    #截屏完成-分享弹窗-扫码带走弹窗-放大后的二维码图片
    @staticmethod
    def screenshoted_scan_code_enlarge(poco):
        return poco('com.h3c.screenshot:id/iv')


    #设置主页控件
    @staticmethod
    def setting_homepage(poco):
        return poco('设置的标题栏。')


    #设置主页-左侧总控件
    @staticmethod
    def setting_left_all(poco):
        return poco('com.h3c.settings:id/rv_main_iv_left_bg')


    #设置主页-左侧-设置搜索栏总控件
    @staticmethod
    def setting_search(poco):
        return poco('com.h3c.settings:id/ev_main_search')


    #设置主页-左侧-设置搜索输入框控件
    @staticmethod
    def setting_search_input(poco):
        return poco('com.h3c.settings:id/universal_common_ipv_inputTextView')


    #设置主页-左侧tab页总控件
    @staticmethod
    def setting_left_mainlist(poco):
        return poco('com.h3c.settings:id/rv_main_list')


    #设置主页-右侧-声音与显示页面总控件
    @staticmethod
    def setting_volume_home(poco):
        return poco('com.h3c.settings:id/nav_host_fragment')


    #设置主页-右侧-声音与显示页面-音量图标
    @staticmethod
    def setting_volume_icon(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")[0]


    #设置主页-右侧-声音与显示页面-音量条
    @staticmethod
    def setting_volume_seekbar(poco):
        return poco('android.widget.SeekBar')


    #设置主页-右侧-声音与显示页面-麦克风开关
    @staticmethod
    def setting_volume_mic(poco):
        return poco('com.h3c.settings:id/switch_microphone')


    #设置主页-右侧-摄像头设置页面-摄像头设置总控件
    @staticmethod
    def setting_camera_home(poco):
        return poco('com.h3c.settings:id/nav_host_fragment')


    #设置主页-右侧-摄像头设置页面-连接状态栏-摄像头连接状态文字控件
    @staticmethod
    def setting_camera_status(poco):
        return poco('com.h3c.settings:id/tv_connect_status')


    #设置主页-右侧-摄像头设置页面-摄像头打开状态控件
    @staticmethod
    def setting_camera_switch(poco):
        return poco('com.h3c.settings:id/switch_camera')


    #设置主页-右侧-摄像头设置页面-智能取景栏控件
    @staticmethod
    def setting_camera_viewfinder(poco):
        return poco('com.h3c.settings:id/cl_intelligent_viewfinder')


    #设置主页-右侧-摄像头设置页面-智能取景栏-智能取景开关控件
    @staticmethod
    def setting_camera_viewfinder_switch(poco):
        return poco('com.h3c.settings:id/switch_intelligent_viewfinder')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏总控件
    @staticmethod
    def setting_camera_adjust(poco):
        return poco('com.h3c.settings:id/cl_adjust')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-摄像头画面控件
    @staticmethod
    def setting_camera_frame(poco):
        return poco('com.h3c.settings:id/preview_container_adjust')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节总控件
    @staticmethod
    def setting_camera_direction(poco):
        return poco('com.h3c.settings:id/control_layout')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-左方向控件
    @staticmethod
    def setting_camera_left(poco):
        return poco('com.h3c.settings:id/btn_left')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-上方向控件
    @staticmethod
    def setting_camera_up(poco):
        return poco('com.h3c.settings:id/btn_top')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-还原控件
    @staticmethod
    def setting_camera_reset(poco):
        return poco('com.h3c.settings:id/btn_reset')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-下方向控件
    @staticmethod
    def setting_camera_down(poco):
        return poco('com.h3c.settings:id/btn_bottom')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-右方向控件
    @staticmethod
    def setting_camera_right(poco):
        return poco('com.h3c.settings:id/btn_right')


    #设置主页-右侧-摄像头设置页面-方向和焦距调节栏-焦距调节控件
    @staticmethod
    def setting_camera_focal_length(poco):
        return poco('com.h3c.settings:id/sb_zoom')


    #设置主页-右侧-摄像头设置页面-未接入摄像头时的摄像头接入演示画面总控件
    @staticmethod
    def setting_camera_disconnect_frame_all(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/disconnected_layout").child("androidx.appcompat.widget.LinearLayoutCompat")


    #设置主页-右侧-摄像头设置页面-未接入摄像头时的摄像头接入演示画面控件（去除两侧黑边）
    @staticmethod
    def setting_camera_disconnect_frame(poco):
        return poco('com.h3c.settings:id/cameraView')


    #设置主页-右侧-时间与日期页面-时区栏总控件
    @staticmethod
    def setting_timezone(poco):
        return poco('com.h3c.settings:id/ll_timezone')


    #设置主页-右侧-时间与日期页面-时区栏-时区下拉框控件
    @staticmethod
    def setting_timezone_select(poco):
        return poco('com.h3c.settings:id/tv_timezone')


    #设置主页-右侧-时间与日期页面-时区弹窗总控件
    @staticmethod
    def setting_timezone_list(poco):
        return poco("com.h3c.settings:id/rv_list")


    #设置主页-右侧-时间与日期页面-时区弹窗总控件-选中的某个具体时区
    @staticmethod
    def setting_select_content(poco,a):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.settings:id/rv_list").child("android.view.ViewGroup")[a].child("com.h3c.settings:id/tv_content")


    #设置主页-右侧-时间与日期页面-时区栏-时区下拉框图标控件
    @staticmethod
    def setting_timezone_select_icon(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("androidx.appcompat.widget.LinearLayoutCompat").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟选择控件
    @staticmethod
    def setting_auto_time(poco):
        return poco('com.h3c.settings:id/switch_auto_time')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-时间控件
    @staticmethod
    def setting_time(poco):
        return poco('com.h3c.settings:id/tv_time')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-日期控件
    @staticmethod
    def setting_date(poco):
        return poco('com.h3c.settings:id/tv_date')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-时间编辑图标控件
    @staticmethod
    def setting_time_arrow(poco):
        return poco('com.h3c.settings:id/iv_time_arrow')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-日期编辑图标控件
    @staticmethod
    def setting_date_arrow(poco):
        return poco('com.h3c.settings:id/iv_date_arrow')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗总控件
    @staticmethod
    def setting_time_pop(poco):
        return poco('android:id/timePicker')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-左侧时间-小时数控件
    @staticmethod
    def setting_time_pop_hours(poco):
        return poco('android:id/hours')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-左侧时间-分钟数控件
    @staticmethod
    def setting_time_pop_minutes(poco):
        return poco('android:id/minutes')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-右侧时间选择总控件
    @staticmethod
    def setting_time_pop_roulette(poco):
        return poco('android:id/radial_picker')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-切换键盘/图像模式控件
    @staticmethod
    def setting_time_pop_toggle(poco):
        return poco('android:id/toggle_mode')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-键盘模式下-输入小时数控件
    @staticmethod
    def setting_time_pop_hour_input(poco):
        return poco('android:id/input_hour')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-键盘模式下-输入分钟数控件
    @staticmethod
    def setting_time_pop_minute_input(poco):
        return poco('android:id/input_minute')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-左侧日期-年份控件
    @staticmethod
    def setting_date_pop_year(poco):
        return poco('android:id/date_picker_header_year')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-左侧日期-年份控件-选择任意年份
    @staticmethod
    def setting_random_year(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/datePicker").child("android.widget.LinearLayout").offspring("android:id/date_picker_year_picker").child("android:id/text1")[random.randint(0,4)]


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-左侧日期-日期控件
    @staticmethod
    def setting_date_pop_date(poco):
        return poco('android:id/date_picker_header_date')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表总控件
    @staticmethod
    def setting_date_pop_calendar(poco):
        return poco('android:id/month_view')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-上一页控件
    @staticmethod
    def setting_date_pop_pre(poco):
        return poco('android:id/prev')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-下一页控件
    @staticmethod
    def setting_date_pop_next(poco):
        return poco('android:id/next')


    #设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-选择年份文字控件（选择的时间要为当前显示的年份）
    @staticmethod
    def setting_date_pop_year_roll(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/datePicker").child("android.widget.LinearLayout").offspring("android:id/date_picker_year_picker").child("android:id/text1")[0]


    #设置主页-右侧-无线网络-当前网络信号栏-当前网络信号连接状态文字控件
    @staticmethod
    def setting_net_status(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child("android.view.ViewGroup").child("android.widget.TextView")[1]


    #设置主页-右侧-无线网络-已连接wifi栏-wifi文字控件
    @staticmethod
    def setting_net_connect_name(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child("android.widget.LinearLayout")[0].offspring("android.widget.TextView")


    #设置主页-右侧-无线网络-wifi栏-wifi选择控件
    @staticmethod
    def setting_net_switch(poco):
        return poco('android.widget.Switch')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi选择标志控件
    @staticmethod
    def setting_net_connect_sign(poco):
        return poco('com.h3c.settings:id/m_wireless_connecting_item')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi名称控件
    @staticmethod
    def setting_wifi_connected_name(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").offspring("com.h3c.settings:id/tv_wifi")[0]


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi信号强度符号控件
    @staticmethod
    def setting_wifi_connected_singal(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").offspring("com.h3c.settings:id/img_level")[0]


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情按钮控件
    @staticmethod
    def setting_wifi_connected_details(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").offspring("com.h3c.settings:id/img_enter")[0]


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗总控件
    @staticmethod
    def setting_net_pop(poco):
        return poco('androidx.appcompat.widget.LinearLayoutCompat')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-标题栏-标题名称名称控件
    @staticmethod
    def setting_net_pop_title(poco):
        return poco('com.h3c.settings:id/m_wireless_detail_title')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-标题栏-关闭按钮控件
    @staticmethod
    def setting_net_pop_close(poco):
        return poco('com.h3c.settings:id/m_wireless_closed')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-自动获取ip选择状态控件
    @staticmethod
    def setting_net_pop_automatic(poco):
        return poco('com.h3c.settings:id/cb_touch_tone')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-ip地址控件
    @staticmethod
    def setting_net_pop_ip_address(poco):
        return poco('com.h3c.settings:id/m_wireless_ev_ip_setting_address')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-子网掩码地址控件
    @staticmethod
    def setting_net_pop_netmask(poco):
        return poco('com.h3c.settings:id/m_wireless_ev_ip_setting_netmask')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-网关地址控件
    @staticmethod
    def setting_net_pop_gateway(poco):
        return poco('com.h3c.settings:id/m_wireless_ev_ip_setting_gateway')


    #设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-DNS服务器地址控件
    @staticmethod
    def setting_net_pop_dns(poco):
        return poco('com.h3c.settings:id/m_wireless_ev_ip_setting_dns1')


    #设置主页-右侧-无线热点-无线热点开关按钮控件
    @staticmethod
    def setting_hotspot_switch(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("android.widget.ScrollView").offspring("android.widget.Switch")


    #设置主页-右侧-无线热点-无线热点栏-已连接的热点名称文字控件
    @staticmethod
    def setting_hotspot_name(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("android.widget.ScrollView").offspring("com.h3c.settings:id/wireless_hotspot_ll_content").child("android.view.ViewGroup")[0].child("android.widget.TextView")


    #设置主页-右侧-无线热点-无线热点栏-热点编辑按钮控件
    @staticmethod
    def setting_hotspot_name_edit(poco):
        return poco('com.h3c.settings:id/hotspot_name_tv_more')


    #设置主页-右侧-无线热点-无线热点栏-热点编辑按钮-热点编辑弹窗-输入框控件（热点密码编辑弹窗控件与此一致）
    @staticmethod
    def setting_hotspot_name_input(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.settings:id/et_input")


    #设置主页-右侧-无线热点-无线热点栏-安全性-选择WPA2-PSK栏-选中标志竖线控件
    @staticmethod
    def setting_hotspot_safe_tag(poco):
        return poco('com.h3c.settings:id/list_item_v_tag')


    #设置主页-右侧-无线热点-无线热点栏-安全性-选择WPA2-PSK栏-勾选标志打勾控件
    @staticmethod
    def setting_hotspot_safe_sign(poco):
        return poco('com.h3c.settings:id/list_item_iv')


    #设置主页-右侧-无线热点-无线热点栏-安全性-热点密码栏-热点密码文字控件
    @staticmethod
    def setting_hotspot_password(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("android.widget.ScrollView").offspring("com.h3c.settings:id/wireless_hotspot_ll_content").child("android.view.ViewGroup")[1].child("android.widget.TextView")


    #设置主页-右侧-无线热点-无线热点栏-安全性-热点密码栏-热点密码编辑图标控件
    @staticmethod
    def setting_hotspot_password_edit(poco):
        return poco('com.h3c.settings:id/hotspot_pwd_iv_more')


    #设置主页-右侧-蓝牙栏-蓝牙开关按钮控件
    @staticmethod
    def setting_bluetooth_switch(poco):
        return poco('android.widget.Switch')


    #设置主页-右侧-蓝牙栏-下方提示文字控件
    @staticmethod
    def setting_bluetooth_tips(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/sv_bluetooth_devices").child("android.widget.LinearLayout").child("android.widget.TextView")


    #设置主页-右侧-蓝牙-蓝牙配对总弹窗控件
    @staticmethod
    def setting_bluetooth_pair(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("android.view.ViewGroup")


    #设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙标志控件
    @staticmethod
    def setting_bluetooth_pair_icon(poco):
        return poco('com.h3c.settings:id/iv_icon')


    #设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙配对码总控件
    @staticmethod
    def setting_bluetooth_pair_code(poco):
        return poco('com.h3c.settings:id/tv_pairing_code')


    #设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙配对码文字控件
    @staticmethod
    def setting_bluetooth_pair_message(poco):
        return poco('com.h3c.settings:id/tv_message_code')


    #设置主页-右侧-设备管理-USB屏蔽栏USB屏蔽开关按钮控件
    @staticmethod
    def usb_block_switch(poco):
        return poco('com.h3c.settings:id/switch_disable_usb')


    #设置主页-右侧-设备管理-外设自检编辑按钮
    @staticmethod
    def peripheral_self_check(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")


    #设置主页-右侧-设备管理-外设自检弹窗-关闭按钮
    @staticmethod
    def peripheral_self_check_pop_close(poco):
        return poco('com.h3c.settings:id/iv_close')


    #设置主页-右侧-应用管理-应用权限管理弹窗总控件
    @staticmethod
    def application_management_pop(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("android.view.ViewGroup")


    #设置主页-右侧-应用管理-应用权限管理弹窗-应用名称控件
    @staticmethod
    def application_management_pop_name(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_name")


    #设置主页-右侧-应用管理-应用权限管理弹窗-弹窗关闭控件
    @staticmethod
    def application_management_pop_close(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")


    #设置主页-右侧-应用管理-应用权限管理弹窗-版本号控件
    @staticmethod
    def application_management_pop_version(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_version")


    #设置主页-右侧-应用管理-应用权限管理弹窗-运行状态控件
    @staticmethod
    def application_management_pop_status(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_run_status")


    #设置主页-右侧-应用管理-应用权限管理弹窗-占用大小控件
    @staticmethod
    def application_management_pop_total(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_total")


    #设置主页-右侧-应用管理-应用权限管理弹窗-用户数据占用大小控件
    @staticmethod
    def application_management_pop_user_data(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_user_data")


    #设置主页-右侧-应用管理-应用权限管理弹窗-应用大小控件
    @staticmethod
    def application_management_pop_app_storage(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_app_storage")


    #设置主页-右侧-应用管理-应用权限管理弹窗-缓存大小控件
    @staticmethod
    def application_management_pop_cache(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_cache")


    #设置主页-右侧-应用管理-应用权限管理弹窗-应用的launcher模式-开关按钮控件
    @staticmethod
    def application_management_pop_launcher_screen(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/switch_tv_auto_run")


    #设置主页-右侧-应用管理-应用权限管理弹窗-竖屏应用强制横屏显示-开关按钮控件
    @staticmethod
    def application_management_pop_landscape_screen(poco):
        return poco('com.h3c.settings:id/switch_tv_app_show_in_landscape')


    #设置主页-右侧-定时关机-关机计划弹窗总控件
    @staticmethod
    def shutdown_plan_pop(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").offspring("android.view.ViewGroup")


    #设置主页-右侧-定时关机-关机计划弹窗-关机时间选择-小时数滑动列控件
    @staticmethod
    def shutdown_plan_pop_hour_row(poco):
        return poco('com.h3c.settings:id/wheel_hour')


    #设置主页-右侧-定时关机-关机计划弹窗-关机时间选择-分钟数滑动列控件
    @staticmethod
    def shutdown_plan_pop_minute_row(poco):
        return poco('com.h3c.settings:id/wheel_minute')


    #设置主页-右侧-关于-设备名称栏-设备名称控件
    @staticmethod
    def device_name(poco):
        return poco('com.h3c.settings:id/tv_device_name')


    #设置主页-右侧-关于-设备名称栏-设备名称编辑栏控件
    @staticmethod
    def device_name_edit(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")[0]


    #设置主页-右侧-关于-设备型号栏-设备型号显示栏控件
    @staticmethod
    def device_model(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").offspring("android.widget.LinearLayout").offspring("com.h3c.settings:id/tv_device_model")[0]


    #设置主页-右侧-关于-系统容量栏-系统容量显示控件
    @staticmethod
    def device_stroge(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").offspring("android.widget.LinearLayout").offspring("com.h3c.settings:id/tv_system_storage")[1]


    #设置主页-右侧-关于-设备信息编辑栏图标控件
    @staticmethod
    def device_message_edit_icon(poco):
        return poco("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/recycler_view").offspring("android.widget.ImageView")


    #设置主页-右侧-关于-协议说明-用户协议控件
    @staticmethod
    def user_agreement(poco):
        return poco('com.h3c.settings:id/tv_user_agreement')


    #设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗控件
    @staticmethod
    def user_agreement_pop(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("android.view.ViewGroup")


    #设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-关闭控件
    @staticmethod
    def user_agreement_pop_close(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")


    #设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-用户协议具体内容控件
    @staticmethod
    def user_agreement_pop_content(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_content")


    #设置主页-右侧-关于-协议说明-隐私协议控件
    @staticmethod
    def privacy_agreement(poco):
        return poco('com.h3c.settings:id/tv_privacy_agreement')


    #设置主页-右侧-关于-协议说明-用户协议-隐私协议弹窗控件
    @staticmethod
    def privacy_agreement_pop(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("android.view.ViewGroup")


    #设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-关闭控件
    @staticmethod
    def privacy_agreement_pop_close(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")


    #设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-用户协议具体内容控件
    @staticmethod
    def privacy_agreement_pop_content(poco):
        return poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_content")


    #设置主页-右侧-系统升级-保持系统自动升级开关按钮控件
    @staticmethod
    def update_auto_switch(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("android.widget.ScrollView").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.Switch")[1]


    #设置主页-右侧-系统升级-系统升级检测异常提示文字控件
    @staticmethod
    def update_check_abnormal(poco):
        return poco("设置的标题栏。").offspring("android:id/content").offspring("android.widget.ScrollView").offspring("com.h3c.settings:id/ll_check_items").offspring("com.h3c.settings:id/tv_msg")


    #图片浏览器-图片整体
    @staticmethod
    def whole_image(poco):
        return poco("com.h3c.photos:id/iv_image")


    #图片浏览器-全景模式按钮
    @staticmethod
    def panoramic_mode(poco):
        return poco("com.h3c.photos:id/ic_panorama")


    #图片浏览器-工具栏
    @staticmethod
    def image_tool_bar(poco):
        return poco("com.h3c.photos:id/card_view")


    #图片浏览器-工具栏-已选中的图片缩略图的名称
    @staticmethod
    def image_select_name(poco):
        return poco("com.h3c.photos:id/tv_name")


    #图片浏览器-工具栏-已选中的图片缩略图的大小
    @staticmethod
    def image_select_size(poco):
        return poco("com.h3c.photos:id/tv_size")


    #图片浏览器-分享-关闭按钮
    @staticmethod
    def image_share_pop_close(poco):
        return poco("com.h3c.photos:id/imgClose")


    #图片浏览器-自适应-悬浮图片框-图片整体
    @staticmethod
    def image_content(poco):
        return poco("com.h3c.photos:id/img_content")


    #图片浏览器-自适应-悬浮图片框-缩放比例
    @staticmethod
    def image_scale(poco):
        return poco("com.h3c.photos:id/tv_scale")


    #图片浏览器-自适应-悬浮图片框-关闭按钮
    @staticmethod
    def image_content_close(poco):
        return poco("com.h3c.photos:id/img_close_aerial")


    #图片浏览器-幻灯片-播放/停止按钮
    @staticmethod
    def image_slide_play(poco):
        return poco("com.h3c.photos:id/img_play")


    #图片浏览器-幻灯片-播放间隔
    @staticmethod
    def image_slide_play_interval(poco):
        return poco("com.h3c.photos:id/number_picker")


    #图片浏览器-幻灯片-关闭
    @staticmethod
    def image_slide_close(poco):
        return poco("com.h3c.photos:id/img_close")


    #图片浏览器-幻灯片-播放模式
    @staticmethod
    def image_slide_play_mode(poco):
        return poco("com.h3c.photos:id/tv_play_mode")


    #图片浏览器-幻灯片-播放模式-下拉框按钮
    @staticmethod
    def image_slide_play_mode_arrow(poco):
        return poco("com.h3c.photos:id/img_arrow")


    #图片浏览器-悬浮框总控件
    @staticmethod
    def image_suspension(poco):
        return poco("com.h3c.photos:id/card_view")


    #图片浏览器-悬浮框-缩放比例
    @staticmethod
    def image_suspension_scale(poco):
        return poco("com.h3c.photos:id/tv_scale")


    #图片浏览器-悬浮框-返回原图片
    @staticmethod
    def image_suspension_back(poco):
        return poco("com.h3c.photos:id/img_close_overlay")


    #图片浏览器-悬浮框-移动按钮
    @staticmethod
    def image_suspension_move(poco):
        return poco("com.h3c.photos:id/img_drag")


    #更多应用窗口
    @staticmethod
    def more_app_window(poco):
        return poco('com.h3c.launcher:id/ll_all_app')

#-------------------------------------------------------------------------上为单独控件封装----------------------------------------------------------------------------



    # 点击文字控件，调用如click_text("设置")
    # number = 0 参数可不输入，默认为0，如果存在多个相同文字，可输入相应的数字代表第几个
    #未加
    @staticmethod
    def click_text(poco,text,number=0):
        poco(text=text)[number].click()

    #滑动文字控件，调用如swipe("设置",[0.5,1])
    # number = 0 参数可不输入，默认为0，如果存在多个相同文字，可输入相应的数字代表第几个
    # 未加
    @staticmethod
    def swipe_text(poco,text,swipe,number=0):
        poco(text=text)[number].swipe(swipe)

    #断言文字控件存在，调用如exist_text("设置","判断设置存在")
    # 未加
    @staticmethod
    def exist_text(poco,text,msg):
        assert_equal(poco(text=text).exists(), True, msg)

    #断言文字控件不存在，调用如not_exist_text("设置","判断设置不存在")
    # 未加
    @staticmethod
    def not_exist_text(poco,text,msg):
        assert_equal(poco(text=text).exists(), False, msg)

    #上滑呼出应用栏
    # 未加
    @staticmethod
    def open_dock(poco):
        poco(text="上滑呼出应用栏")[0].swipe([0.5, -1])
        sleep(5)

    #打开launcher主页的dock栏下的应用，调用如open_dock_application("H3C传屏助手")
    #若DOCK栏未找到该应用，则会抛出NameError异常
    @staticmethod
    def open_dock_application(poco,application_name):
        HeyboardOs.open_dock(poco)
        for num in range(30):
            try:
                text = poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/rv_list").child("android.view.ViewGroup")[num].child("com.h3c.launcher:id/tv_title").get_text()
                # print(text)
                logger.debug(text)
                if text == application_name:
                    poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/rv_list").child("android.view.ViewGroup")[num].child("com.h3c.launcher:id/iv_icon").click()
                    sleep(5)
                    break
            except:
                raise NameError("未找到该应用")

    #打开launcher主页的dock栏下的应用，调用如open_dock_application("H3C传屏助手")
    #若DOCK栏未找到该应用，则会抛出NameError异常
    @staticmethod
    def open_more_app_application(poco,application_name):
        HeyboardOs.open_dock(poco)
        HeyboardOs.more_app(poco).wait(30).click()
        sleep(5)
        for i in range(5):
            try:
                for num in range(12):
                    text = poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/grid_all_app").child("android.view.ViewGroup")[2*num+1].child("com.h3c.launcher:id/tv_title").get_text()
                    # print(text)
                    logger.debug(text)
                    if text == application_name:
                        poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/grid_all_app").child("android.view.ViewGroup")[2*num+1].child("com.h3c.launcher:id/iv_icon").click()
                        sleep(5)
                        return ("已找到应用")
                HeyboardOs.more_app_window(poco).wait(10).swipe([-0.5, 0.5], [0.9, 0.5])
            except:
                raise NameError("未找到该应用")


    #返回白板历史颜色选择控件
    #前提条件：需要打开历史颜色选择界面
    #输入参数值超出或者没有历史颜色选择时会抛出异常
    @staticmethod
    def select_history_color(poco,select_num):
        select_num = int(select_num)
        start_num = 1
        for num in range(1,6):
            if poco(f"com.h3c.launcher:id/csv_ui_history_color_{num}").exists():
                start_num = num
                continue
            else:
                break
        if start_num == 1:
            raise ZeroDivisionError("当前没有历史颜色存在")

        elif 1<=select_num<=start_num:
            return f"com.h3c.launcher:id/csv_ui_history_color_{select_num}"
        else:
            raise IndexError(f"输入的参数值应在1到{start_num}之间，包含1和{start_num}")

    #返回的是poco(控件id)
    #输入参数page_num为1表示选择上一页，2表示当前页，3表示下一页
    @staticmethod
    def get_blackboard_page(poco,page_num):
        page_num_out = int(2*page_num-1)
        return (poco("android.widget.FrameLayout").offspring("com.h3c.launcher:id/rv_ui_infinitecanvas").child("android.widget.RelativeLayout")[page_num_out].child("com.h3c.launcher:id/iv_ui_rv_infinitecanvas_item_preview"))

    # 返回的是poco(控件id)
    #1表示第一页，2表示第二页
    @staticmethod
    def get_blackboard_share(poco,page_num):
        page_num_out = int((page_num+2)/2)
        return (poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/rv_page_preview").child("android.widget.FrameLayout")[page_num_out].child("com.h3c.launcher:id/iv_page_preview"))

    #返回的是输入的文件类型名称下的文件数量
    #输入不存在的文件类型会抛出异常
    #输入参数为字符串类型
    @staticmethod
    def get_folder_type_count(poco,folder_name):
        for num in range(10):
            try:
                text = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("android.widget.ScrollView").offspring("com.h3c.filemanager:id/recycler").child("android.widget.LinearLayout")[num].child("com.h3c.filemanager:id/tv_name").get_text()
                # logger.debug(text)
                if text == folder_name:
                    folder_name_count = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("android.widget.ScrollView").offspring("com.h3c.filemanager:id/recycler").child("android.widget.LinearLayout")[num].child("com.h3c.filemanager:id/tv_count").get_text()
                    return folder_name_count
            except:
                raise NameError("未找到该文件类型")


    #返回的是当前所有文件夹的文件名、文件大小、文件类型、文件修改日期的二维数组如：[['Alarms', '—', '文件夹', '2023.06.29 04:39'], ['Android', '—', '文件夹', '2023.07.04 03:28']]
    #返回的是当前已显示的画面
    @staticmethod
    def get_folder_message(poco):
        all_folder = []
        for num in range(20):
            try:
                single_folder = []
                folder_name = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child("com.h3c.filemanager:id/item_root")[num].offspring("com.h3c.filemanager:id/tv_name").get_text()
                single_folder.append(folder_name)
                folder_length = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child("com.h3c.filemanager:id/item_root")[num].offspring("com.h3c.filemanager:id/tv_fileLength").get_text()
                single_folder.append(folder_length)
                folder_type = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child("com.h3c.filemanager:id/item_root")[num].offspring("com.h3c.filemanager:id/tv_fileExtension").get_text()
                single_folder.append(folder_type)
                folder_time = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child("com.h3c.filemanager:id/item_root")[num].child("com.h3c.filemanager:id/tv_updateTime").get_text()
                single_folder.append(folder_time)
                all_folder.append(single_folder)
                # logger.debug(all_folder)
            except IndexError:
                break
        return all_folder


    #输入字符串型文件名称，返回该文件名称文件的信息如：['—', '文件夹', '2023.07.04 03:59']
    #若输入的文件在当前显示页面找不到，则抛出NameError("未找到该文件")异常
    @staticmethod
    def get_single_folder_message(poco,folder_name):
        single_folder = []
        for num in range(20):
            try:
                text = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/contentRight").offspring("com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child("android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child("com.h3c.filemanager:id/item_root")[num].offspring("com.h3c.filemanager:id/tv_name").get_text()
                # logger.debug(text)
                if text == folder_name:
                    folder_length = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(
                        "com.h3c.filemanager:id/contentRight").offspring(
                        "com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child(
                        "android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child(
                        "com.h3c.filemanager:id/item_root")[num].offspring(
                        "com.h3c.filemanager:id/tv_fileLength").get_text()
                    single_folder.append(folder_length)
                    folder_type = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(
                        "com.h3c.filemanager:id/contentRight").offspring(
                        "com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child(
                        "android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child(
                        "com.h3c.filemanager:id/item_root")[num].offspring(
                        "com.h3c.filemanager:id/tv_fileExtension").get_text()
                    single_folder.append(folder_type)
                    folder_time = poco("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(
                        "com.h3c.filemanager:id/contentRight").offspring(
                        "com.h3c.filemanager:id/fragment_container").offspring("com.h3c.filemanager:id/smart").child(
                        "android.widget.LinearLayout").offspring("com.h3c.filemanager:id/recyclerView").child(
                        "com.h3c.filemanager:id/item_root")[num].child(
                        "com.h3c.filemanager:id/tv_updateTime").get_text()
                    single_folder.append(folder_time)
                    return single_folder
            except:
                raise NameError("未找到该文件")

    #返回当前页面可分享的应用
    #前提：需要将大屏页面进入到截屏后的分享页面
    @staticmethod
    def get_screenshot_share(poco):
        num = 0
        name_list = []
        while True:
            try:
                text = poco("android.widget.FrameLayout").child("android.widget.FrameLayout").offspring("com.h3c.screenshot:id/share_list").child("android.widget.LinearLayout")[num].child("com.h3c.screenshot:id/share_name").get_text()
                # logger.debug(text)
                name_list.append(text)
                num += 1
            except IndexError:
                name_list = list(set(name_list))
                return name_list

    #点击时间选择轮盘，点击输入参数指定的小时数和分钟数
    #小时数输入1-24，分钟数只能输入5的倍数
    @staticmethod
    def select_time(poco,hour,minute):
        poco("android.widget.FrameLayout").offspring("android:id/timePicker").child("android.widget.LinearLayout").offspring(f"{hour}").wait(10).click()
        poco("android.widget.FrameLayout").offspring("android:id/timePicker").child("android.widget.LinearLayout").offspring(f"{minute}").wait(10).click()


    #点击日期数选择日期，点击输入参数指定的日期数
    #前提条件：需要将年份先选择至指定年份
    #输入参数的年月日都输入数字
    @staticmethod
    def select_date(poco,year,month,day):
        month_name = ["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"]
        month_num = month_name[int(month)-1]
        if int(day) < 10:
            day = f"0{day}"
        poco("android.widget.FrameLayout").offspring("android:id/datePicker").child(
            "android.widget.LinearLayout").offspring(f"{day} {month_num} {year}").click()

    #新建文件夹
    #前提：当前页面在文件管理器页面
    @staticmethod
    def new_folder(poco):
        shell("settings put secure default_input_method com.android.inputmethod.latin/.LatinIME")
        sleep(2)
        poco(text = "新建文件夹")[0].click()
        sleep(10)
        poco(text = "确定").click()
        sleep(5)

    #获取当前我的wifi列表
    #返回我的wifi名称数组
    @staticmethod
    def get_my_wifi(poco):
        num = 0
        name_list = []
        while True:
            try:
                text = poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child("android.widget.LinearLayout")[1].offspring("com.h3c.settings:id/m_wireless_rv_wifi_my_list")[0].child("android.view.ViewGroup")[num].child("com.h3c.settings:id/tv_wifi").get_text()
                # logger.debug(text)
                name_list.append(text)
                num += 1
            except IndexError:
                name_list = list(set(name_list))
                return name_list


    #获取当前其他网络的wifi列表
    #返回其他网络的wifi名称数组
    @staticmethod
    def get_other_wifi(poco):
        num = 0
        name_list = []
        while True:
            try:
                text = poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring("com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child("android.widget.LinearLayout")[1].offspring("com.h3c.settings:id/m_wireless_rv_wifi_list")[0].child("android.view.ViewGroup")[num].child("com.h3c.settings:id/tv_wifi").get_text()
                # logger.debug(text)
                name_list.append(text)
                num += 1
            except IndexError:
                name_list = list(set(name_list))
                return name_list
    #获取当前其他设备下的蓝牙列表
    #返回获取到的蓝牙列表
    @staticmethod
    def get_other_bluetooth(poco):
        num = 0
        name_list = []
        while True:
            try:
                text = poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring("com.h3c.settings:id/sv_bluetooth_devices").child("android.widget.LinearLayout").offspring("androidx.recyclerview.widget.RecyclerView").child("android.view.ViewGroup")[num].child("com.h3c.settings:id/bluetooth_tv_name").get_text()
                # logger.debug(text)
                name_list.append(text)
                num += 1
            except IndexError:
                name_list = list(set(name_list))
                return name_list



    #获取当前应用管理页面可见的应用大小和名称
    #返回二维数组返回可见页面的应用大小和名称
    @staticmethod
    def get_app_manager(poco):
        all_app_message = []
        num = 0
        while True:
            try:
                single_app_message = []
                app_name = poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("com.h3c.settings:id/rv_app_list").child("android.view.ViewGroup")[num].child("com.h3c.settings:id/tv_name").get_text()
                single_app_message.append(app_name)
                app_length = poco("设置的标题栏。").offspring("android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child("androidx.appcompat.widget.LinearLayoutCompat").offspring("com.h3c.settings:id/rv_app_list").child("android.view.ViewGroup")[num].child("com.h3c.settings:id/tv_storage").get_text()
                single_app_message.append(app_length)
                all_app_message.append(single_app_message)
                # logger.debug(all_app_message)
                num += 1
            except IndexError:
                return all_app_message

    #返回所有可以分享的应用的名称
    @staticmethod
    def get_image_share_list(poco):
        num = 0
        name_list = []
        while True:
            try:
                text = poco("android.widget.FrameLayout").offspring("com.h3c.photos:id/centerPopupContainer").offspring("com.h3c.photos:id/recyclerView").child("android.widget.LinearLayout")[num].child("com.h3c.photos:id/textName") .get_text()
                # logger.debug(text)
                name_list.append(text)
                num += 1
            except IndexError:
                name_list = list(set(name_list))
                return name_list



# ---------------------------------------------------------------------上为复杂控件封装------------------------------------------------------------------------
# ---------------------------------------------------------------------下为自定义封装------------------------------------------------------------------------

    #测试前的准备工作
    @staticmethod
    def start_test(poco):
        poco.click([0.01, 0.01])
        try:
            poco(text = "上滑呼出应用栏")[0].wait(5).swipe([0.5,-1])
        except:
            poco(text="Swipe up to bring up the application bar")[0].wait(5).swipe([0.5, -1])
        poco("com.h3c.launcher:id/iv_finish_class").wait(30).click()
        poco(text = "确认下课").wait(30).click()
        sleep(5)
        shell("am start -n com.netease.open.pocoservice/.TestActivity")
        sleep(5)
        while poco(text="取消").exists():
            poco(text="取消").click()
            sleep(5)



    @staticmethod
    def get_touch_event_name(device_name):
        result = subprocess.run(["adb", "shell", "getevent", "-p"], capture_output=True, text=True)

        #
        escaped_device_name = re.escape(device_name)

        #
        match = re.findall(rf"add device \d+: /dev/input/(event\d+)\n\s+name:\s+\"{escaped_device_name}\"", result.stdout)

        max_event_num = -1
        for event in match:
            event_num = int(event[5:])
            max_event_num = max(max_event_num, event_num)

        if max_event_num != -1:
            return f"/dev/input/event{max_event_num}"
        else:
            raise RuntimeError("Touch event not found")


    # 获取屏幕分辨率
    @staticmethod
    def get_screen_size():
        result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True)
        match = re.search(r"Physical size: (\d+)x(\d+)", result.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            raise RuntimeError("Screen size not found")


    # 获取触摸框分辨率
    @staticmethod
    def get_touch_coordinate_range(event_name, device_name):
        escaped_device_name = re.escape(device_name)
        result = subprocess.run(["adb", "shell", "getevent", "-p"], capture_output=True, text=True)
        match_x = re.search(
            rf"{event_name}\s+name:\s+\"{escaped_device_name}\"\n\s+events:\n(?:.+\n)+\s+0035\s+:\s+value\s+\d+, min\s+\d+, max\s+(\d+), fuzz\s+\d+, flat\s+\d+, resolution\s+\d+",
            result.stdout)
        match_y = re.search(
            rf"{event_name}\s+name:\s+\"{escaped_device_name}\"\n\s+events:\n(?:.+\n)+\s+0036\s+:\s+value\s+\d+, min\s+\d+, max\s+(\d+), fuzz\s+\d+, flat\s+\d+, resolution\s+\d+",
            result.stdout)

        if match_x and match_y:
            max_x = int(match_x.group(1))
            max_y = int(match_y.group(1))
            return max_x, max_y
        else:
            raise RuntimeError("Touch coordinate range not found")


    # 将屏幕分辨率转化为触摸框分辨率
    @staticmethod
    def pixel_to_touch_coordinates(pixel_x, pixel_y, eventid, device_name):
        screen_size = HeyboardOs.get_screen_size()
        touch_coordinate_range = HeyboardOs.get_touch_coordinate_range(eventid, device_name)
        touch_x = int(pixel_x * touch_coordinate_range[0] / screen_size[0])
        touch_y = int(pixel_y * touch_coordinate_range[1] / screen_size[1])
        return touch_x, touch_y


    # 画线初次封装
    @staticmethod
    def send_touch_event(event_name, x, y, pressure, other_info, touch_id, touch_state, move_x=0, move_y=0, steps=10,
                         delay=0.01):
        y = y/2
        move_y = move_y/2
        commands = [
            f"sendevent {event_name} 3 57 {touch_id}",
            f"sendevent {event_name} 3 53 {x}",
            f"sendevent {event_name} 3 54 {y}",
            f"sendevent {event_name} 3 48 {pressure}",
            f"sendevent {event_name} 3 49 {other_info}",
            f"sendevent {event_name} 1 330 {touch_state}",
            f"sendevent {event_name} 0 0 0"
        ]

        for command in commands:
            subprocess.run(["adb", "shell", command])

        if move_x != 0 or move_y != 0:
            for i in range(steps):
                x += move_x // steps
                y += move_y // steps
                commands = [
                    f"sendevent {event_name} 3 53 {x}",
                    f"sendevent {event_name} 3 54 {y}",
                    f"sendevent {event_name} 0 0 0"
                ]
                for command in commands:
                    subprocess.run(["adb", "shell", command])
                time.sleep(delay)


    # 将画线举例转化为实际分辨率
    @staticmethod
    def distance_turn(event_thing, thing, distance, device_name):
        actually_x, actually_y = HeyboardOs.get_screen_size()  # 分辨率
        start_x, start_y = HeyboardOs.get_touch_coordinate_range(event_thing, device_name)  # 触摸框
        if thing == "up" or thing == "down":
            distance_fina = distance * start_y / actually_y
            return distance_fina
        if thing == "left" or thing == "right":
            distance_fina = distance * start_x / actually_x
            return distance_fina
        else:
            raise RuntimeError("no things")


    # 画线二次封装
    # 示例：从(540, 960)开始，向右画一条长度为200的线
    # event_name = get_touch_event_name()
    # draw_line(540, 960, 'down', 1000)
    # 参数介绍::start_x-起点X坐标；start_y:起点y坐标;direction:只能填"up","down","left","right"四个参数，表示向上下左右进行画线
    # 接上:distance_set:表示移动的距离;event_name:默认可不填
    @staticmethod
    def draw_line(start_x, start_y, direction, distance_set, screen_select):
        if screen_select == "主屏":
            device_name = "Linux 4.9.125 with mtu3 Composite Gadget(HID + MS)"
        if screen_select == "副屏":
            device_name = "iSolution X86XH02+084"

        event_name = HeyboardOs.get_touch_event_name(device_name)
        start_x, start_y = HeyboardOs.pixel_to_touch_coordinates(start_x, start_y, event_name, device_name)

        if direction == "up":
            distance = HeyboardOs.distance_turn(event_name, "up", distance_set, device_name)
            move_x, move_y = 0, -distance
        elif direction == "down":
            distance = HeyboardOs.distance_turn(event_name, "down", distance_set, device_name)
            move_x, move_y = 0, distance
        elif direction == "left":
            distance = HeyboardOs.distance_turn(event_name, "left", distance_set, device_name)
            move_x, move_y = -distance, 0
        elif direction == "right":
            distance = HeyboardOs.distance_turn(event_name, "right", distance_set, device_name)
            move_x, move_y = distance, 0
        else:
            raise ValueError("Invalid direction")

        touch_id = 62  # You can change this value if needed
        pressure = 300
        other_info = 171

        HeyboardOs.send_touch_event(event_name, start_x, start_y, pressure, other_info, touch_id, 1)  # 开始触摸
        HeyboardOs.send_touch_event(event_name, start_x, start_y, pressure, other_info, touch_id, 1, move_x, move_y)  # 移动
        HeyboardOs.send_touch_event(event_name, start_x, start_y, 0, 0, 4294967295, 0)  # 抬起


    #写一个正字
    @staticmethod
    def draw_zheng(start_x, start_y, long, screen_select):
        HeyboardOs.draw_line(start_x, start_y, 'right', long, screen_select)
        HeyboardOs.draw_line(start_x + long / 2, start_y, 'down', long, screen_select)
        HeyboardOs.draw_line(start_x + long / 2, start_y + long / 2, 'right', long / 2, screen_select)
        HeyboardOs.draw_line(start_x + long / 4, start_y, 'down', long, screen_select)
        HeyboardOs.draw_line(start_x, start_y + long, 'right', long, screen_select)

    #画一个正方形
    @staticmethod
    def draw_block(start_x, start_y, long, screen_select):
        HeyboardOs.draw_line(start_x, start_y, 'right', long, screen_select)
        HeyboardOs.draw_line(start_x+long, start_y, 'down', long, screen_select)
        HeyboardOs.draw_line(start_x+long, start_y+long, 'left', long, screen_select)
        HeyboardOs.draw_line(start_x, start_y+long, 'up', long, screen_select)
    #画线压测
    @staticmethod
    def draw_presstest(times, screen_select, max_x=7680, max_y=2160):
        times_a = 0
        while True:
            move_distance = 100
            x = random.randint(0,max_x)
            y = random.randint(0,max_y)
            movex = random.randint(0,max_x-x)
            movey = random.randint(0,max_y-y)
            move_list = ["up","down","left","right"]
            move_num = random.randint(1,4)
            if move_num == 1 or move_num == 2:
                move_distance = movey
            elif move_num == 3 or move_num == 4:
                move_distance = movex
            HeyboardOs.draw_line(x, y, move_list[move_num-1], move_distance, screen_select)
            if times < 10000 :
                times_a += 1
            if times_a == times:
                break
    #三指上滑
    @staticmethod
    def gesture_operation(start_x, start_y, direction, screen_select):
        if screen_select == "主屏":
            device_name = "Linux 4.9.125 with mtu3 Composite Gadget(HID + MS)"
        if screen_select == "副屏":
            device_name = "iSolution X86XH02+084"
        event_name = HeyboardOs.get_touch_event_name(device_name)
        start_x, start_y = HeyboardOs.pixel_to_touch_coordinates(start_x, start_y, event_name, device_name)
        x1 = start_x
        y1 = start_y
        if direction == "up" or direction == "down":
            x2 = start_x + 300
            y2 = start_y
            x3 = start_x + 600
            y3 = start_y
        if direction == "left" or direction == "right":
            x2 = start_x
            y2 = start_y + 300
            x3 = start_x
            y3 = start_y + 600

        shell(f"sendevent {event_name} 3 47 0")
        shell(f"sendevent {event_name} 3 57 221")
        shell(f"sendevent {event_name} 3 53 {x1}")
        shell(f"sendevent {event_name} 3 54 {y1}")
        shell(f"sendevent {event_name} 3 47 1")
        shell(f"sendevent {event_name} 3 57 222")
        shell(f"sendevent {event_name} 3 53 {x2}")
        shell(f"sendevent {event_name} 3 54 {y2}")
        shell(f"sendevent {event_name} 3 47 2")
        shell(f"sendevent {event_name} 3 57 223")
        shell(f"sendevent {event_name} 3 53 {x3}")
        shell(f"sendevent {event_name} 3 54 {y3}")
        shell(f"sendevent {event_name} 1 330 1")
        shell(f"sendevent {event_name} 0 0 0")
        for i in range(15):
            if direction == "up":
                move_x1 = x1
                move_x2 = x2
                move_x3 = x3
                move_y1 = y1 - i * 1000
                move_y2 = y1 - i * 1000
                move_y3 = y1 - i * 1000
            if direction == "down":
                move_x1 = x1
                move_x2 = x2
                move_x3 = x3
                move_y1 = y1 + i * 1000
                move_y2 = y1 + i * 1000
                move_y3 = y1 + i * 1000

            if direction == "left":
                move_y1 = y1
                move_y2 = y2
                move_y3 = y3
                move_x1 = x1 - i * 1000
                move_x2 = x1 - i * 1000
                move_x3 = x1 - i * 1000

            if direction == "right":
                move_y1 = y1
                move_y2 = y2
                move_y3 = y3
                move_x1 = x1 + i * 1000
                move_x2 = x1 + i * 1000
                move_x3 = x1 + i * 1000

            shell(f"sendevent {event_name} 3 47 0")
            shell(f"sendevent {event_name} 3 53 {move_x1}")
            shell(f"sendevent {event_name} 3 54 {move_y1}")
            shell(f"sendevent {event_name} 3 47 1")
            shell(f"sendevent {event_name} 3 53 {move_x2}")
            shell(f"sendevent {event_name} 3 54 {move_y2}")
            shell(f"sendevent {event_name} 3 47 2")
            shell(f"sendevent {event_name} 3 53 {move_x3}")
            shell(f"sendevent {event_name} 3 54 {move_y3}")
            shell(f"sendevent {event_name} 0 0 0")

        shell(f"sendevent {event_name} 3 47 0")
        shell(f"sendevent {event_name} 3 57 4294967295")
        shell(f"sendevent {event_name} 3 47 1")
        shell(f"sendevent {event_name} 3 57 4294967295")
        shell(f"sendevent {event_name} 3 47 2")
        shell(f"sendevent {event_name} 3 57 4294967295")
        shell(f"sendevent {event_name} 1 330 0")
        shell(f"sendevent {event_name} 0 0 0")

    #获取setting中设置的媒体音量
    @staticmethod
    def get_volume_music_line():
        volume = shell("settings list system")
        volume = int(volume.split("volume_music_line=")[1].split("\n")[0])
        return volume

    # 获取setting中设置的通话音量
    @staticmethod
    def get_volume_voice_line():
        volume = shell("settings list system")
        volume = int(volume.split("volume_voice_line=")[1].split("\n")[0])
        return volume
    #截图部分区域
    #输入参数：x1,x2,y1,y2表示截图的左上角+右下角的点；path:表示图像的保存路径及文件名称（如：./APK/setting.png）；
    @staticmethod
    def screen_shot_part(x1,y1,x2,y2,path):
        screen_shot_part = G.DEVICE.snapshot()
        screen_shot_part = aircv.crop_image(screen_shot_part, (x1,y1,x2,y2))
        pil_img = cv2_2_pil(screen_shot_part)
        pil_img.save(path, quality=99, optimize=True)
        sleep(5)

    #计算当前时间的差值时间，用来计算不同时区的当前时间
    #输入的参数中，delta_hours表示时区中的小时数，delta_minutes表示时区中的当前分钟数
    @staticmethod
    def add_time(delta_hours, delta_minutes):
        delta_hours = delta_hours - 8
        time_obj = datetime.now()

        # 创建一个表示时间差的 timedelta 对象
        time_delta = timedelta(hours=delta_hours, minutes=delta_minutes)

        # 将时间差加到原始时间上
        new_time_obj = time_obj + time_delta

        # 将结果转换为字符串格式，只保留小时
        new_time_str = new_time_obj.strftime('%H')
        return new_time_str

    @staticmethod
    def get_url_test(apk):
        # base_url = "http://your-server.example.com"
        base_url = "https://your-server.example.com/stage-api/ota"
        url = f'{base_url}/auth/login'
        headers1 = {
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.'
                          '0.0.0 Safari/537.36',
            'connection': 'keep-alive'
            }
        data1 = {
            "username": "admin",
            "password": "YOUR_PASSWORD"
            }
        response = requests.post(url=url, headers=headers1, data=json.dumps(data1))
        print(response)
        token = response.json()['data']['access_token']
        headers2 = {
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108'
                              '.0.0.0 Safari/537.36',
                'Authorization': 'Bearer ' + token
            }


        url = f'{base_url}/appstore/api/app-by-package?packageNames=' + apk
        rsp = requests.get(url=url, headers=headers2)
        rsp.close()
        dl_url = rsp.json()['data'][0]['downloadUrl']
        return dl_url

    #通过下载链接下载应用至本地再安装到大屏，安装成功或失败后删除应用
    #需要正确填入参数应用的包名和应用名称，app_package表示应用包名，app_name表示应用名称
    @staticmethod
    def install_app_on_big_screen(app_package,max_retries=10):
        app_name = "测试应用.apk"
        # 2. 通过一个下载链接下载应用至当前程序运行目录下
        apk_url = HeyboardOs.get_url_test(app_package)
        apk_file = app_name
        response = requests.get(apk_url)
        with open(apk_file, 'wb') as f:
            f.write(response.content)
        print("APK已下载至本地")

        # 3. 安装该应用至大屏
        # 4. 检查应用安装到大屏，如未成功安装则再安装一次，未成功则继续，未成功十次抛出安装失败的异常
        installed = False
        retries = 0

        while not installed and retries < max_retries:
            install(apk_file)
            print(f"尝试安装APK（第{retries + 1}次）")

            if device().check_app(app_package):
                installed = True
                print("APK已成功安装至大屏")
            else:
                retries += 1

        if not installed:
            os.remove(apk_file)
            print("已删除本地APK文件")
            raise Exception("安装失败：尝试了十次安装仍未成功")

        # 5. 安装成功后删掉放在本地的应用
        os.remove(apk_file)
        print("已删除本地APK文件")

    #打开设置
    @staticmethod
    def start_setting(poco):
        shell("am start com.h3c.settings/.main.ui.activity.SettingActivity")  # 待修改点----封装为函数
        if poco(text="我知道了").wait(5).exists():
            poco(text="我知道了").click()
        sleep(5)


#---------------------------------------------------------------------上为自定义函数封装-----------------------------------------------------------------------
#---------------------------------------------------------------------下为mega-----------------------------------------------------------------------
class MegaosOversea:

    # 获取eventID
    @staticmethod
    def get_touch_event_name():
        result = subprocess.run(["adb", "shell", "getevent", "-p"], capture_output=True, text=True)
        match = re.search(
            r"add device \d+: (/dev/input/event\d+)\n\s+name:\s+\"Linux 4.9.125 with mtu3 Composite Gadget\(HID \+ MS\)\"",
            result.stdout, re.MULTILINE)
        if match:
            return match.group(1)
        else:
            raise RuntimeError("Touch event not found")

    # 获取屏幕分辨率
    @staticmethod
    def get_screen_size():
        result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True)
        match = re.search(r"Physical size: (\d+)x(\d+)", result.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            raise RuntimeError("Screen size not found")

    # 获取触摸框分辨率
    @staticmethod
    def get_touch_coordinate_range(event_name):
        result = subprocess.run(["adb", "shell", "getevent", "-p"], capture_output=True, text=True)
        match_x = re.search(
            rf"{event_name}\s+name:\s+\"Linux 4.9.125 with mtu3 Composite Gadget\(HID \+ MS\)\"\n\s+events:\n(?:.+\n)+\s+0035\s+:\s+value\s+\d+, min\s+\d+, max\s+(\d+), fuzz\s+\d+, flat\s+\d+, resolution\s+\d+",
            result.stdout)
        match_y = re.search(
            rf"{event_name}\s+name:\s+\"Linux 4.9.125 with mtu3 Composite Gadget\(HID \+ MS\)\"\n\s+events:\n(?:.+\n)+\s+0036\s+:\s+value\s+\d+, min\s+\d+, max\s+(\d+), fuzz\s+\d+, flat\s+\d+, resolution\s+\d+",
            result.stdout)

        if match_x and match_y:
            max_x = int(match_x.group(1))
            max_y = int(match_y.group(1))
            return max_x, max_y
        else:
            raise RuntimeError("Touch coordinate range not found")

    # 将屏幕分辨率转化为触摸框分辨率
    @staticmethod
    def pixel_to_touch_coordinates(pixel_x, pixel_y, eventid):
        screen_size = MegaosOversea.get_screen_size()
        touch_coordinate_range = MegaosOversea.get_touch_coordinate_range(eventid)
        touch_x = int(pixel_x * touch_coordinate_range[0] / screen_size[0])
        touch_y = int(pixel_y * touch_coordinate_range[1] / screen_size[1])
        return touch_x, touch_y

    # 画线初次封装
    @staticmethod
    def send_touch_event(event_name, x, y, pressure, other_info, touch_id, touch_state, move_x=0, move_y=0, steps=10,
                         delay=0.01):
        commands = [
            f"sendevent {event_name} 3 57 {touch_id}",
            f"sendevent {event_name} 3 53 {x}",
            f"sendevent {event_name} 3 54 {y}",
            f"sendevent {event_name} 3 48 {pressure}",
            f"sendevent {event_name} 3 49 {other_info}",
            f"sendevent {event_name} 1 330 {touch_state}",
            f"sendevent {event_name} 0 0 0"
        ]

        for command in commands:
            subprocess.run(["adb", "shell", command])

        if move_x != 0 or move_y != 0:
            for i in range(steps):
                x += move_x // steps
                y += move_y // steps
                commands = [
                    f"sendevent {event_name} 3 53 {x}",
                    f"sendevent {event_name} 3 54 {y}",
                    f"sendevent {event_name} 0 0 0"
                ]
                for command in commands:
                    subprocess.run(["adb", "shell", command])
                time.sleep(delay)

    # 将画线举例转化为实际分辨率
    @staticmethod
    def distance_turn(event_thing, thing, distance):
        actually_x, actually_y = MegaosOversea.get_screen_size()  # 分辨率
        start_x, start_y = MegaosOversea.get_touch_coordinate_range(event_thing)  # 触摸框
        if thing == "up" or thing == "down":
            distance_fina = distance * start_y / actually_y
            return distance_fina
        if thing == "left" or thing == "right":
            distance_fina = distance * start_x / actually_x
            return distance_fina
        else:
            raise RuntimeError("no things")

    # 画线二次封装
    # 示例：从(540, 960)开始，向右画一条长度为200的线
    # event_name = get_touch_event_name()
    # draw_line(540, 960, 'down', 1000)
    #参数介绍::start_x-起点X坐标；start_y:起点y坐标;direction:只能填"up","down","left","right"四个参数，表示向上下左右进行画线
    #接上:distance_set:表示移动的距离;event_name:默认可不填
    @staticmethod
    def draw_line(start_x, start_y, direction, distance_set):
        event_name = MegaosOversea.get_touch_event_name()
        start_x, start_y = MegaosOversea.pixel_to_touch_coordinates(start_x, start_y, event_name)

        if direction == "up":
            distance = MegaosOversea.distance_turn(event_name, "up", distance_set)
            move_x, move_y = 0, -distance
        elif direction == "down":
            distance = MegaosOversea.distance_turn(event_name, "down", distance_set)
            move_x, move_y = 0, distance
        elif direction == "left":
            distance = MegaosOversea.distance_turn(event_name, "left", distance_set)
            move_x, move_y = -distance, 0
        elif direction == "right":
            distance = MegaosOversea.distance_turn(event_name, "right", distance_set)
            move_x, move_y = distance, 0
        else:
            raise ValueError("Invalid direction")

        touch_id = 62  # You can change this value if needed
        pressure = 300
        other_info = 171

        MegaosOversea.send_touch_event(event_name, start_x, start_y, pressure, other_info, touch_id, 1)  # 开始触摸
        MegaosOversea.send_touch_event(event_name, start_x, start_y, pressure, other_info, touch_id, 1, move_x, move_y)  # 移动
        MegaosOversea.send_touch_event(event_name, start_x, start_y, 0, 0, 4294967295, 0)  # 抬起

    #写正字
    @staticmethod
    def draw_zheng(start_x,start_y,long):
        MegaosOversea.draw_line(start_x, start_y, 'right', long)
        MegaosOversea.draw_line(start_x + long/2, start_y, 'down', long)
        MegaosOversea.draw_line(start_x + long/2, start_y + long/2, 'right', long/2)
        MegaosOversea.draw_line(start_x + long/4, start_y, 'down', long)
        MegaosOversea.draw_line(start_x, start_y + long, 'right', long)

    #画一个正方形
    @staticmethod
    def draw_block(start_x, start_y, long):
        MegaosOversea.draw_line(start_x, start_y, 'right', long)
        MegaosOversea.draw_line(start_x+long, start_y, 'down', long)
        MegaosOversea.draw_line(start_x+long, start_y+long, 'left', long)
        MegaosOversea.draw_line(start_x, start_y+long, 'up', long)

    @staticmethod
    def draw_presstest(max_x,max_y,times):
        times_a = 0
        while True:
            move_distance = 100
            x = random.randint(0,max_x)
            y = random.randint(0,max_y)
            movex = random.randint(0,max_x-x)
            movey = random.randint(0,max_y-y)
            move_list = ["up","down","left","right"]
            move_num = random.randint(1,4)
            if move_num == 1 or move_num == 2:
                move_distance = movey
            elif move_num == 3 or move_num == 4:
                move_distance = movex
            MegaosOversea.draw_line(x, y, move_list[move_num-1], move_distance)
            times_a += 1
            if times_a == times:
                break

class Megaos:
    pass