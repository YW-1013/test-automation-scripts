from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
import logging

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
    # DOCK栏工具应用栏
    tool_bar = 'com.h3c.launcher:id/fl_left'
    # DOCK栏常用应用栏
    favorite_bar = 'com.h3c.launcher:id/ll_favorite_app'
    # 音量图标
    volume = 'com.h3c.launcher:id/iv_volume'
    # 下课图标
    finish_class = 'com.h3c.launcher:id/iv_finish_class'
    # 左右同屏图标
    mirror = 'com.h3c.launcher:id/iv_mirror'
    # 更多应用
    more_app = 'com.h3c.launcher:id/ll_more_app'
    # 书写颜色-第一个颜色-红色
    write_color1 = 'com.h3c.launcher:id/csv_blackboardos_ui_color_1'
    # 书写颜色-第二个颜色-黄色
    write_color2 = 'com.h3c.launcher:id/csv_blackboardos_ui_color_2'
    # 书写颜色-第三个颜色-白色
    write_color3 = 'com.h3c.launcher:id/csv_blackboardos_ui_color_3'
    # 书写颜色-颜色库
    write_colorful = 'com.h3c.launcher:id/csv_blackboardos_ui_colorful'
    # 书写颜色-颜色库_颜色弹窗
    write_colorful_pop = 'com.h3c.launcher:id/cl_ui_more_color'
    # 书写颜色-颜色库-颜色弹窗-颜色选择
    write_colorful_pop_select = 'com.h3c.launcher:id/mcv_ui_color'
    # 书写颜色-颜色库-颜色弹窗-颜色选择历史栏
    write_colorful_pop_history = 'com.h3c.launcher:id/cl_ui_history'
    # 橡皮图标
    rubber_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                  '"com.h3c.launcher:id/tbv_ui_rubber").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 橡皮弹窗-橡皮图标
    rubber_rubber_icon = '("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child(' \
                         '"android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_erase").offspring(' \
                         '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 橡皮弹窗-橡皮文字
    rubber_rubber_text = '("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child(' \
                         '"android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_erase").offspring(' \
                         '"com.h3c.launcher:id/tv_ui_button_text")'
    # 橡皮弹窗-清屏图标
    rubber_clear_icon = '("android.widget.FrameLayout").offspring("android.widget.FrameLayout").child(' \
                        '"android.view.ViewGroup").offspring("com.h3c.launcher:id/tbv_ui_clear_screen").offspring(' \
                        '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 选择图标
    select_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                  '"com.h3c.launcher:id/tbv_ui_select").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 插入图标
    insert_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                  '"com.h3c.launcher:id/tbv_ui_insert").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 插入-图片图标
    insert_image_icon = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                        '"android.widget.FrameLayout").offspring(' \
                        '"com.h3c.launcher:id/tbv_ui_insert_picture").offspring(' \
                        '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 插入-书写模板图标
    insert_template_icon = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                           '"android.widget.FrameLayout").offspring(' \
                           '"com.h3c.launcher:id/tbv_ui_writing_template").offspring(' \
                           '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 插入-图片-图片弹窗
    insert_image_pop = 'com.h3c.launcher:id/simpleFilePickView'
    # 插入-图片-图片弹窗-右侧文件归属文件夹名称
    insert_image_pop_file_belong = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                   '"android.widget.FrameLayout").offspring(' \
                                   '"com.h3c.launcher:id/simpleFilePickView").child(' \
                                   '"android.view.ViewGroup").offspring("com.h3c.launcher:id/tv_text")'
    # 插入-图片-图片弹窗-右侧文件缩略图
    insert_image_pop_file_thumbnail = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                      '"android.widget.FrameLayout").offspring(' \
                                      '"com.h3c.launcher:id/simpleFilePickView").child(' \
                                      '"android.view.ViewGroup").offspring(' \
                                      '"com.h3c.launcher:id/ry_m_file_picker_file_browse_fragment").child(' \
                                      '"android.widget.RelativeLayout")[0].child(' \
                                      '"com.h3c.launcher:id/file_item_c_ly").offspring(' \
                                      '"com.h3c.launcher:id/adapter_img")'
    # 插入-图片-图片弹窗-右侧文件类型名称
    insert_image_pop_file_type = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                 '"android.widget.FrameLayout").offspring(' \
                                 '"com.h3c.launcher:id/simpleFilePickView").child(' \
                                 '"android.view.ViewGroup").offspring(' \
                                 '"com.h3c.launcher:id/ry_m_file_picker_file_browse_fragment").child(' \
                                 '"android.widget.RelativeLayout")[0].child(' \
                                 '"com.h3c.launcher:id/file_item_c_ly").offspring(' \
                                 '"com.h3c.launcher:id/adapter_num_text")'
    # 插入-图片-图片弹窗-右侧文件名称
    insert_image_pop_file_name = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                 '"android.widget.FrameLayout").offspring(' \
                                 '"com.h3c.launcher:id/simpleFilePickView").child(' \
                                 '"android.view.ViewGroup").offspring(' \
                                 '"com.h3c.launcher:id/ry_m_file_picker_file_browse_fragment").child(' \
                                 '"android.widget.RelativeLayout")[0].offspring(' \
                                 '"com.h3c.launcher:id/adapter_content_text")'
    # 插入-图片-图片弹窗-暂无文件图标
    insert_image_pop_file_empty = 'com.h3c.launcher:id/iv_empty'
    # 插入-书写模板-书写模板弹窗
    insert_template_pop = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                          '"android.widget.FrameLayout").child("android.view.ViewGroup")'
    # 插入-书写模板-书写模板弹窗-点阵格
    insert_template_pop_lattices = 'com.h3c.launcher:id/wt_ui_dian_zhen_ge'
    # 插入-书写模板-书写模板弹窗-点阵格图案
    insert_template_pop_lattices_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                           '"android.widget.FrameLayout").offspring(' \
                                           '"com.h3c.launcher:id/wt_ui_dian_zhen_ge").offspring(' \
                                           '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 插入-书写模板-书写模板弹窗-米字格
    insert_template_pop_mi = 'com.h3c.launcher:id/wt_ui_mi_zi_ge'
    # 插入-书写模板-书写模板弹窗-米字格图案
    insert_template_pop_mi_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                     '"android.widget.FrameLayout").offspring(' \
                                     '"com.h3c.launcher:id/wt_ui_mi_zi_ge").offspring(' \
                                     '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 插入-书写模板-书写模板弹窗-田字格
    insert_template_pop_tian = 'com.h3c.launcher:id/wt_ui_tian_zi_ge'
    # 插入-书写模板-书写模板弹窗-田字格图案
    insert_template_pop_tian_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                       '"android.widget.FrameLayout").offspring(' \
                                       '"com.h3c.launcher:id/wt_ui_tian_zi_ge").offspring(' \
                                       '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 插入-书写模板-书写模板弹窗-三线四格
    insert_template_pop_4grids = 'com.h3c.launcher:id/wt_ui_three_lines_four_grids'
    # 插入-书写模板-书写模板弹窗-三线四格图案
    insert_template_pop_4grids_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                         '"android.widget.FrameLayout").offspring(' \
                                         '"com.h3c.launcher:id/wt_ui_three_lines_four_grids").offspring(' \
                                         '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 插入-书写模板-书写模板弹窗-拼音格
    insert_template_pop_pinyin = 'com.h3c.launcher:id/wt_ui_ping_yin_grids'
    # 插入-书写模板-书写模板弹窗-拼音格图案
    insert_template_pop_pinyin_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                         '"android.widget.FrameLayout").offspring(' \
                                         '"com.h3c.launcher:id/wt_ui_ping_yin_grids").offspring(' \
                                         '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 插入-书写模板-书写模板弹窗-五线谱
    insert_template_pop_staff = 'com.h3c.launcher:id/wt_ui_staff'
    # 插入-书写模板-书写模板弹窗-五线谱图案
    insert_template_pop_staff_pattern = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                        '"android.widget.FrameLayout").offspring(' \
                                        '"com.h3c.launcher:id/wt_ui_staff").offspring(' \
                                        '"com.h3c.launcher:id/iv_ui_writing_template")'
    # 撤回图标
    withdraw_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                    '"com.h3c.launcher:id/tbv_ui_revoke").offspring(' \
                    '"com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 黑板图标
    blackboard_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                      '"com.h3c.launcher:id/tbv_ui_infinite_canvas").offspring(' \
                      '"com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 黑板弹窗
    blackboard_pop = 'com.h3c.launcher:id/rv_ui_infinitecanvas'
    # 上一页图标
    previous_page = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                    '"com.h3c.launcher:id/tbv_ui_previous_page").offspring(' \
                    '"com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 下一页图标
    next_page = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                '"com.h3c.launcher:id/tbv_ui_next_page").offspring(' \
                '"com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 分享图标
    share_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                 '"com.h3c.launcher:id/tbv_ui_scan_share").offspring(' \
                 '"com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 分享弹窗-顶部栏
    share_pop_top = 'com.h3c.launcher:id/top_bar'
    # 分享弹窗-分享页选择
    share_pop_page_select = 'com.h3c.launcher:id/rv_page_preview'
    # 分享弹窗-二维码上方文字提示
    share_pop_tips = 'com.h3c.launcher:id/tv_connect_tips'
    # 分享弹窗-二维码
    share_pop_qrcode = 'com.h3c.launcher:id/iv_qrcode'
    # 分享弹窗-二维码放大按钮
    share_pop_qrcode_enlarge = 'com.h3c.launcher:id/iv_enlarge_qrcode'
    # 分享弹窗-放大后的二维码
    share_enlarge_qrcode = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                           '"android.widget.ImageView")'
    # 文件图标
    file_icon = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                '"com.h3c.launcher:id/tbv_ui_file").offspring("com.h3c.launcher:id/iv_ui_blackboardos_button_icon")'
    # 文件弹窗_保存图标
    file_save = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                '"com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_save_save").offspring(' \
                '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 文件弹窗_另存为图标
    file_save_as = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                   '"com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_save_as").offspring(' \
                   '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 文件弹窗_打开图标
    file_save_open = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                     '"com.h3c.launcher:id/ll_content").offspring("com.h3c.launcher:id/tbv_ui_open_file").offspring(' \
                     '"com.h3c.launcher:id/iv_ui_button_icon")'
    # 保存弹窗
    save_pop = 'androidx.appcompat.widget.LinearLayoutCompat'
    # 保存弹窗-顶部栏
    save_pop_top = 'com.h3c.launcher:id/top_bar'
    # 保存弹窗-顶部栏标题
    save_pop_title = 'com.h3c.launcher:id/tv_top_bar_title'
    # 保存弹窗-文件名称输入框
    file_name_input = 'com.h3c.launcher:id/et_file_name'
    # 保存弹窗-保存路径输入框
    save_path_input = 'com.h3c.launcher:id/tv_save_path'
    # 保存弹窗-保存路径下拉按钮
    save_path_dropdown = 'com.h3c.launcher:id/iv_save_path_arrow'
    # 音量条
    volume_bar = 'com.h3c.launcher:id/vsb_volume'
    # 音量条内声音icon
    volume_bar_icon = 'com.h3c.launcher:id/img_volume_icon'
    # 文件管理器
    file_manager = '文件管理器的标题栏。'
    # 文件管理器搜索输入框
    file_manage_search_input = 'com.h3c.filemanager:id/et_key_word'
    # 文件管理器搜索按钮
    file_manage_search_icon = 'com.h3c.filemanager:id/img_search'
    # 本地文件总控件
    local_files = 'com.h3c.filemanager:id/local_file_layout'
    # 本地文件总控件-本地下拉框
    local_files_select = '("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(' \
                         '"android.widget.ScrollView").offspring("com.h3c.filemanager:id/ll_title").child(' \
                         '"com.h3c.filemanager:id/img_icon")'
    # 本地文件总控件-本地文件类型总控件
    local_files_type_all = 'com.h3c.filemanager:id/recycler'
    # 外部文件总控件
    external_files = '("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(' \
                     '"android.widget.ScrollView").offspring("com.h3c.filemanager:id/recyclerView")'
    # 外部文件总控件-U盘名称
    external_files_name = '("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(' \
                          '"android.widget.ScrollView").offspring("com.h3c.filemanager:id/tv_name")'
    # 文件管理可用空间
    files_available = 'com.h3c.filemanager:id/tv_available'
    # 文件管理可用空间条
    files_available_bar = 'com.h3c.filemanager:id/progress_bar'
    # 文件显示宫格模式
    file_grid_type = '("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(' \
                     '"com.h3c.filemanager:id/contentRight").offspring(' \
                     '"com.h3c.filemanager:id/title_bar_action").child("android.widget.LinearLayout").offspring(' \
                     '"com.h3c.filemanager:id/fr_grid").child("android.widget.ImageView")'
    # 文件显示列表模式
    file_list_type = '("文件管理器的标题栏。").child("android.widget.LinearLayout").offspring(' \
                     '"com.h3c.filemanager:id/contentRight").offspring(' \
                     '"com.h3c.filemanager:id/title_bar_action").child("android.widget.LinearLayout").offspring(' \
                     '"com.h3c.filemanager:id/fr_grid").child("android.widget.ImageView")'
    # 新建文件夹弹窗
    new_folder_pop = '("android.widget.FrameLayout").offspring("com.h3c.filemanager:id/centerPopupContainer").child(' \
                     '"android.widget.LinearLayout")'
    # 新建文件夹弹窗-文件名输入窗
    new_folder_pop_name_input = 'com.h3c.filemanager:id/et_input'
    # 新建文件夹弹窗-文件名输入窗-清除按钮
    new_folder_pop_name_input_clear = 'com.h3c.filemanager:id/iv_delete'
    # 新建文件夹弹窗-文件名输入错误提示文字
    new_folder_pop_name_error_tip = 'com.h3c.filemanager:id/textError'
    # 文件夹名称排序
    folder_sort = 'com.h3c.filemanager:id/iv_sort'
    # 文件夹名称排序类型
    folder_sort_type = 'com.h3c.filemanager:id/tv_sortType'
    # 文件夹名称排序下拉框
    folder_sort_select = 'com.h3c.filemanager:id/arrow'
    # 书写模式按钮
    commentary_write_mode = 'com.h3c.commentary:id/menuitem_write_main_commentary'
    # 触控模式按钮
    commentary_touch_mode = 'com.h3c.commentary:id/menuitem_touch_main_commentary'
    # 触控模式下保存按钮
    touch_save_icon = '("com.h3c.commentary:id/floatmenu_touch_commentary").child(' \
                      '"android.widget.FrameLayout").child("android.widget.ImageView")'
    # 书写模式下保存按钮
    write_save_icon = '("com.h3c.commentary:id/menuitem_write_main_commentary").child("android.widget.ImageView")'
    # 书写模式下退出按钮
    write_mode_exit = 'com.h3c.commentary:id/menuitem_write_exit_commentary'
    # 触控模式下退出按钮
    touch_mode_exit = 'com.h3c.commentary:id/menuitem_touch_exit_commentary'
    # 批注顶部书写模式控件
    top_commentary_mode = '("com.h3c.commentary:id/tv_write_model")'
    # 录屏主页控件
    record_homepage = 'com.h3c.screencap:id/record_start'
    # 录屏主页-录屏图标控件
    record_record_icon = 'com.h3c.screencap:id/img_start'
    # 录屏主页-录屏文字控件
    record_record_text = 'com.h3c.screencap:id/tv_record'
    # 录屏主页-清晰度总控件
    record_qulity_all = 'com.h3c.screencap:id/btn_qulity'
    # 录屏主页-清晰度-图标控件
    record_qulity_icon = 'com.h3c.screencap:id/img_qulity'
    # 录屏主页-清晰度-下拉框控件
    record_qulity_imgarrow = 'com.h3c.screencap:id/imgArrow'
    # 录屏主页-清晰度-清晰度文字控件
    record_qulity_text = 'com.h3c.screencap:id/tv_qulity'
    # 录屏主页-麦克风总控件
    record_mic_all = 'com.h3c.screencap:id/btn_mic_start'
    # 录屏主页-麦克风-麦克风图标控件
    record_mic_icon = 'com.h3c.screencap:id/img_mic_start'
    # 录屏主页-麦克风-麦克风文字控件
    record_mic_text = 'com.h3c.screencap:id/tv_mic'
    # 录屏主页-关闭控件
    record_close = 'com.h3c.screencap:id/btn_close'
    # 录屏主页-正在录屏时-时间显示-时间显示控件
    recording_time_show = 'com.h3c.screencap:id/tvTime'
    # 录屏主页-正在录屏时-麦克风控件
    recording_mic = 'com.h3c.screencap:id/btn_mic'
    # 录屏主页-正在录屏时-开始按钮控件
    recording_start = 'com.h3c.screencap:id/btn_play'
    # 录屏主页-正在录屏时-停止按钮控件
    recording_stop = 'com.h3c.screencap:id/btnStop'
    # 录屏主页-结束录屏时-主页录屏标题控件
    recorded_title = 'com.h3c.screencap:id/title'
    # 录屏主页-结束录屏时-主页录屏画面控件
    recorded_frame = 'com.h3c.screencap:id/surface'
    # 录屏主页-结束录屏时-主页-录屏进度栏总栏控件
    recorded_schedule = 'com.h3c.screencap:id/layout_bottom'
    # 录屏主页-结束录屏时-主页-录屏进度栏-开始/暂停按钮控件
    recorded_start = '("录屏的标题栏。").offspring("com.h3c.screencap:id/content").offspring(' \
                     '"com.h3c.screencap:id/gsyVideoPlayer").offspring("com.h3c.screencap:id/start")'
    # 录屏主页-结束录屏时-主页-录屏进度栏-视频已播放时长控件
    recorded_current = 'com.h3c.screencap:id/current'
    # 录屏主页-结束录屏时-主页-录屏进度栏-视频播放进度条控件
    recorded_seek_progress = 'com.h3c.screencap:id/bottom_seek_progress'
    # 录屏主页-结束录屏时-主页-录屏进度栏-视频总时长控件
    recorded_total_duration = 'com.h3c.screencap:id/total'
    # 录屏主页-结束录屏时-主页-重新录制控件
    recorded_restart = 'com.h3c.screencap:id/re_record'
    # 录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-关闭控件
    recorded_save_pop_close = 'com.h3c.screencap:id/imgClose'
    # 录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-文件名称标题输入框控件
    recorded_save_pop_file_name_input = 'com.h3c.screencap:id/editFileName'
    # 录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-保存路径下拉框控件
    recorded_save_pop_path_arrow = 'com.h3c.screencap:id/imgArrow'
    # 录屏主页-结束录屏时-点击本地保存时-本地保存弹窗-保存路径下拉控件（当下拉只有一个）
    recorded_save_pop_path_onlyone = '("android.widget.FrameLayout").offspring("com.h3c.screencap:id/textPath")'
    # 录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-关闭按钮控件
    recorded_scan_pop_close = 'com.h3c.screencap:id/close'
    # 录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-二维码图片控件
    recorded_scan_pop_code = 'com.h3c.screencap:id/cardView'
    # 录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-二维码图片-放大按钮控件
    recorded_scan_pop_code_enlarge = 'com.h3c.screencap:id/img_enlarge'
    # 录屏主页-结束录屏时-点击扫码带走时-扫码带走弹窗-放大后的二维码控件
    recorded_scan_pop_qrcode_amplify = 'com.h3c.screencap:id/imgQrCode'
    # 截屏主页控件
    screenshot_homepage = 'com.h3c.screenshot:id/crop_guide'
    # 截屏后截图关闭按钮
    screenshoted_close = 'com.h3c.screenshot:id/iv_close'
    # 截屏完成-分享文字+图标控件
    screenshoted_share = 'com.h3c.screenshot:id/tv_share'
    # 截屏完成-本地保存文字+图标控件
    screenshoted_save = 'com.h3c.screenshot:id/tv_save'
    # 截屏完成-本地保存弹窗-文件名称输入框控件
    screenshoted_save_name_input = 'com.h3c.screenshot:id/et_file_name'
    # 截屏完成-本地保存弹窗-保存路径-下拉框图标控件
    screenshoted_save_path_arrow = 'com.h3c.screenshot:id/iv_storage'
    # 截屏完成-分享弹窗-关闭
    screenshoted_share_pop_close = 'com.h3c.screenshot:id/share_close'
    # 截屏完成-分享弹窗-分享应用列表
    screenshoted_share_pop_applist = 'com.h3c.screenshot:id/share_list'
    # 截屏完成-分享弹窗-扫码带走弹窗-二维码
    screenshoted_scan_code = 'com.h3c.screenshot:id/iv_qrcode'
    # 截屏完成-分享弹窗-扫码带走弹窗-二维码放大按钮
    screenshoted_scan_enlarge_code = 'com.h3c.screenshot:id/iv_enlarge'
    # 截屏完成-分享弹窗-扫码带走弹窗-关闭
    screenshoted_scan_close = 'com.h3c.screenshot:id/iv_close'
    # 截屏完成-分享弹窗-扫码带走弹窗-放大后的二维码图片
    screenshoted_scan_code_enlarge = 'com.h3c.screenshot:id/iv'
    # 设置主页控件
    setting_homepage = '设置的标题栏。'
    # 设置主页-左侧总控件
    setting_left_all = 'com.h3c.settings:id/rv_main_iv_left_bg'
    # 设置主页-左侧-设置搜索栏总控件
    setting_search = 'com.h3c.settings:id/ev_main_search'
    # 设置主页-左侧-设置搜索输入框控件
    setting_search_input = 'com.h3c.settings:id/universal_common_ipv_inputTextView'
    # 设置主页-左侧tab页总控件
    setting_left_mainlist = 'com.h3c.settings:id/rv_main_list'
    # 设置主页-右侧-声音与显示页面总控件
    setting_volume_home = 'com.h3c.settings:id/nav_host_fragment'
    # 设置主页-右侧-声音与显示页面-音量图标
    setting_volume_icon = '("设置的标题栏。").child("android.widget.LinearLayout").offspring(' \
                          '"android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring(' \
                          '"com.h3c.settings:id/recycler_view").child(' \
                          '"androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")[0]'
    # 设置主页-右侧-声音与显示页面-音量条
    setting_volume_seekbar = 'android.widget.SeekBar'
    # 设置主页-右侧-声音与显示页面-麦克风开关
    setting_volume_mic = 'com.h3c.settings:id/switch_microphone'
    # 设置主页-右侧-摄像头设置页面-摄像头设置总控件
    setting_camera_home = 'com.h3c.settings:id/nav_host_fragment'
    # 设置主页-右侧-摄像头设置页面-连接状态栏-摄像头连接状态文字控件
    setting_camera_status = 'com.h3c.settings:id/tv_connect_status'
    # 设置主页-右侧-摄像头设置页面-摄像头打开状态控件
    setting_camera_switch = 'com.h3c.settings:id/switch_camera'
    # 设置主页-右侧-摄像头设置页面-智能取景栏控件
    setting_camera_viewfinder = 'com.h3c.settings:id/cl_intelligent_viewfinder'
    # 设置主页-右侧-摄像头设置页面-智能取景栏-智能取景开关控件
    setting_camera_viewfinder_switch = 'com.h3c.settings:id/switch_intelligent_viewfinder'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏总控件
    setting_camera_adjust = 'com.h3c.settings:id/cl_adjust'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-摄像头画面控件
    setting_camera_frame = 'com.h3c.settings:id/preview_container_adjust'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节总控件
    setting_camera_direction = 'com.h3c.settings:id/control_layout'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-左方向控件
    setting_camera_left = 'com.h3c.settings:id/btn_left'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-上方向控件
    setting_camera_top = 'com.h3c.settings:id/btn_top'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-还原控件
    setting_camera_reset = 'com.h3c.settings:id/btn_reset'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-下方向控件
    setting_camera_down = 'com.h3c.settings:id/btn_bottom'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-方向调节-右方向控件
    setting_camera_right = 'com.h3c.settings:id/btn_right'
    # 设置主页-右侧-摄像头设置页面-方向和焦距调节栏-焦距调节控件
    setting_camera_focal_length = 'com.h3c.settings:id/sb_zoom'
    # 设置主页-右侧-摄像头设置页面-未接入摄像头时的摄像头接入演示画面总控件
    setting_camera_disconnect_frame_all = '("设置的标题栏。").child("android.widget.LinearLayout").offspring(' \
                                          '"android:id/content").offspring(' \
                                          '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                                          '"com.h3c.settings:id/recycler_view").child(' \
                                          '"android.widget.FrameLayout").offspring(' \
                                          '"com.h3c.settings:id/disconnected_layout").child(' \
                                          '"androidx.appcompat.widget.LinearLayoutCompat")'
    # 设置主页-右侧-摄像头设置页面-未接入摄像头时的摄像头接入演示画面控件（去除两侧黑边）
    setting_camera_disconnect_frame = 'com.h3c.settings:id/cameraView'
    # 设置主页-右侧-时间与日期页面-时区栏总控件
    setting_timezone = 'com.h3c.settings:id/ll_timezone'
    # 设置主页-右侧-时间与日期页面-时区栏-时区下拉框控件
    setting_timezone_select = 'com.h3c.settings:id/tv_timezone'
    # 设置主页-右侧-时间与日期页面-时区栏-时区下拉框图标控件
    setting_timezone_select_icon = '("设置的标题栏。").child("android.widget.LinearLayout").offspring(' \
                                   '"android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child(' \
                                   '"androidx.appcompat.widget.LinearLayoutCompat").child(' \
                                   '"androidx.appcompat.widget.LinearLayoutCompat").offspring(' \
                                   '"android.widget.ImageView")'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟选择控件
    setting_auto_time = 'com.h3c.settings:id/switch_auto_time'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-时间控件
    setting_time = 'com.h3c.settings:id/tv_time'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-日期控件
    setting_date = 'com.h3c.settings:id/tv_date'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-时间编辑图标控件
    setting_time_arrow = 'com.h3c.settings:id/iv_time_arrow'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-自动同步时钟-日期编辑图标控件
    setting_date_arrow = 'com.h3c.settings:id/iv_date_arrow'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗总控件
    setting_time_pop = 'android:id/timePicker'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-左侧时间-小时数控件
    setting_time_pop_hours = 'android:id/hours'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-左侧时间-分钟数控件
    setting_time_pop_minutes = 'android:id/minutes'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-右侧时间选择总控件
    setting_time_pop_roulette = 'android:id/radial_picker'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-切换键盘/图像模式控件
    setting_time_pop_toggle = 'android:id/toggle_mode'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-键盘模式下-输入小时数控件
    setting_time_pop_hour_input = 'android:id/input_hour'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-时间弹窗-键盘模式下-输入分钟数控件
    setting_time_pop_minute_input = 'android:id/input_minute'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-左侧日期-年份控件
    setting_date_pop_year = 'android:id/date_picker_header_year'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-左侧日期-日期控件
    setting_date_pop_date = 'android:id/date_picker_header_date'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表总控件
    setting_date_pop_calendar = 'android:id/month_view'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-上一页控件
    setting_date_pop_pre = 'android:id/prev'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-下一页控件
    setting_date_pop_next = 'android:id/next'
    # 设置主页-右侧-时间与日期页面-时区栏-时间与日期-日期弹窗-右侧日历表-选择年份文字控件（选择的时间要为当前显示的年份）
    setting_date_pop_year_roll = '("android.widget.FrameLayout").offspring("android:id/datePicker").child(' \
                                 '"android.widget.LinearLayout").offspring(' \
                                 '"android:id/date_picker_year_picker").child("android:id/text1")[0]'
    # 设置主页-右侧-无线网络-当前网络信号栏-当前网络信号连接状态文字控件
    setting_net_status = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                         '"com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring(' \
                         '"com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child(' \
                         '"android.view.ViewGroup").child("android.widget.TextView")[1]'
    # 设置主页-右侧-无线网络-已连接wifi栏-wifi文字控件
    setting_net_connect_name = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                               '"com.h3c.settings:id/nav_host_fragment").child("android.view.ViewGroup").offspring(' \
                               '"com.h3c.settings:id/root_scrollView").child("android.widget.LinearLayout").child(' \
                               '"android.widget.LinearLayout")[0].offspring("android.widget.TextView")'
    # 设置主页-右侧-无线网络-wifi栏-wifi选择控件
    setting_net_switch = 'android.widget.Switch'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi选择标志控件
    setting_net_connect_sign = 'com.h3c.settings:id/m_wireless_connecting_item'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗总控件
    setting_net_pop = 'androidx.appcompat.widget.LinearLayoutCompat'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-标题栏-标题名称名称控件
    setting_net_pop_title = 'com.h3c.settings:id/m_wireless_detail_title'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-标题栏-关闭按钮控件
    setting_net_pop_close = 'com.h3c.settings:id/m_wireless_closed'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-自动获取ip选择状态控件
    setting_net_pop_automatic = 'com.h3c.settings:id/cb_touch_tone'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-ip地址控件
    setting_net_pop_ip_address = 'com.h3c.settings:id/m_wireless_ev_ip_setting_address'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-子网掩码地址控件
    setting_net_pop_netmask = 'com.h3c.settings:id/m_wireless_ev_ip_setting_netmask'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-网关地址控件
    setting_net_pop_gateway = 'com.h3c.settings:id/m_wireless_ev_ip_setting_gateway'
    # 设置主页-右侧-无线网络-wifi栏-已连接的wifi-wifi详情弹窗-DNS服务器地址控件
    setting_net_pop_dns = 'com.h3c.settings:id/m_wireless_ev_ip_setting_dns1'
    # 设置主页-右侧-无线热点-无线热点开关按钮控件
    setting_hotspot_switch = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                             '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                             '"android.widget.ScrollView").offspring("android.widget.Switch")'
    # 设置主页-右侧-无线热点-无线热点栏-已连接的热点名称文字控件
    setting_hotspot_name = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                           '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                           '"android.widget.ScrollView").offspring(' \
                           '"com.h3c.settings:id/wireless_hotspot_ll_content").child("android.view.ViewGroup")[' \
                           '0].child("android.widget.TextView")'
    # 设置主页-右侧-无线热点-无线热点栏-热点编辑按钮控件
    setting_hotspot_name_edit = 'com.h3c.settings:id/hotspot_name_tv_more'
    # 设置主页-右侧-无线热点-无线热点栏-热点编辑按钮-热点编辑弹窗-输入框控件（热点密码编辑弹窗控件与此一致）
    setting_hotspot_name_input = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                                 '"com.h3c.settings:id/et_input")'
    # 设置主页-右侧-无线热点-无线热点栏-安全性-选择WPA2-PSK栏-选中标志竖线控件
    setting_hotspot_safe_tag = 'com.h3c.settings:id/list_item_v_tag'
    # 设置主页-右侧-无线热点-无线热点栏-安全性-选择WPA2-PSK栏-勾选标志打勾控件
    setting_hotspot_safe_sign = 'com.h3c.settings:id/list_item_iv'
    # 设置主页-右侧-无线热点-无线热点栏-安全性-热点密码栏-热点密码文字控件
    setting_hotspot_password = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                               '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                               '"android.widget.ScrollView").offspring(' \
                               '"com.h3c.settings:id/wireless_hotspot_ll_content").child("android.view.ViewGroup")[' \
                               '1].child("android.widget.TextView")'
    # 设置主页-右侧-无线热点-无线热点栏-安全性-热点密码栏-热点密码编辑图标控件
    setting_hotspot_password_edit = 'com.h3c.settings:id/hotspot_pwd_iv_more'
    # 设置主页-右侧-蓝牙栏-蓝牙开关按钮控件
    setting_bluetooth_switch = 'android.widget.Switch'
    # 设置主页-右侧-蓝牙栏-下方提示文字控件
    setting_bluetooth_tips = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                             '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                             '"com.h3c.settings:id/sv_bluetooth_devices").child("android.widget.LinearLayout").child(' \
                             '"android.widget.TextView")'
    # 设置主页-右侧-蓝牙-蓝牙配对总弹窗控件
    setting_bluetooth_pair = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                             '"android.view.ViewGroup")'
    # 设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙标志控件
    setting_bluetooth_pair_icon = 'com.h3c.settings:id/iv_icon'
    # 设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙配对码总控件
    setting_bluetooth_pair_code = 'com.h3c.settings:id/tv_pairing_code'
    # 设置主页-右侧-蓝牙-蓝牙配对总弹窗-蓝牙配对码文字控件
    setting_bluetooth_pair_message = 'com.h3c.settings:id/tv_message_code'
    # 设置主页-右侧-设备管理-USB屏蔽栏USB屏蔽开关按钮控件
    usb_block_switch = 'com.h3c.settings:id/switch_disable_usb'
    # 设置主页-右侧-设备管理-外设自检编辑按钮
    peripheral_self_check = '("设置的标题栏。").child("android.widget.LinearLayout").offspring(' \
                            '"android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").child(' \
                            '"androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")'
    # 设置主页-右侧-设备管理-外设自检弹窗-关闭按钮
    peripheral_self_check_pop_close = 'com.h3c.settings:id/iv_close'
    # 设置主页-右侧-应用管理-应用权限管理弹窗总控件
    application_management_pop = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                 '"android.widget.FrameLayout").offspring("android.view.ViewGroup")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-应用名称控件
    application_management_pop_name = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                      '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_name")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-弹窗关闭控件
    application_management_pop_close = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                       '"android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-版本号控件
    application_management_pop_version = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                         '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_version")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-运行状态控件
    application_management_pop_status = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                        '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_run_status")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-占用大小控件
    application_management_pop_total = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                       '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_total")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-用户数据占用大小控件
    application_management_pop_user_data = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                           '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_user_data")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-应用大小控件
    application_management_pop_app_storage = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                             '"android.widget.FrameLayout").offspring(' \
                                             '"com.h3c.settings:id/tv_app_storage")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-缓存大小控件
    application_management_pop_cache = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                       '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_cache")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-应用的launcher模式-开关按钮控件
    application_management_pop_launcher_screen = '("android.widget.FrameLayout").offspring(' \
                                                 '"android:id/content").child(' \
                                                 '"android.widget.FrameLayout").offspring(' \
                                                 '"com.h3c.settings:id/switch_tv_auto_run")'
    # 设置主页-右侧-应用管理-应用权限管理弹窗-竖屏应用强制横屏显示-开关按钮控件
    application_management_pop_landscape_screen = 'com.h3c.settings:id/switch_tv_app_show_in_landscape'
    # 设置主页-右侧-定时关机-关机计划弹窗总控件
    shutdown_plan_pop = '("android.widget.FrameLayout").offspring("android:id/content").offspring(' \
                        '"android.view.ViewGroup")'
    # 设置主页-右侧-定时关机-关机计划弹窗-关机时间选择-小时数滑动列控件
    shutdown_plan_pop_hour_row = 'com.h3c.settings:id/wheel_hour'
    # 设置主页-右侧-定时关机-关机计划弹窗-关机时间选择-分钟数滑动列控件
    shutdown_plan_pop_minute_row = 'com.h3c.settings:id/wheel_minute'
    # 设置主页-右侧-关于-设备名称栏-设备名称控件
    device_name = 'com.h3c.settings:id/tv_device_name'
    # 设置主页-右侧-关于-设备名称栏-设备名称编辑栏控件
    device_name_edit = '("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring(' \
                       '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                       '"com.h3c.settings:id/recycler_view").child(' \
                       '"androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.ImageView")[0]'
    # 设置主页-右侧-关于-设备型号栏-设备型号显示栏控件
    device_model = '("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring(' \
                   '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                   '"com.h3c.settings:id/recycler_view").offspring("android.widget.LinearLayout").offspring(' \
                   '"com.h3c.settings:id/tv_device_model")[0]'
    # 设置主页-右侧-关于-系统容量栏-系统容量显示控件
    device_stroge = '("设置的标题栏。").child("android.widget.LinearLayout").offspring("android:id/content").offspring(' \
                    '"com.h3c.settings:id/nav_host_fragment").offspring(' \
                    '"com.h3c.settings:id/recycler_view").offspring("android.widget.LinearLayout").offspring(' \
                    '"com.h3c.settings:id/tv_system_storage")[1]'
    # 设置主页-右侧-关于-设备信息编辑栏图标控件
    device_message_edit_icon = '("设置的标题栏。").child("android.widget.LinearLayout").offspring(' \
                               '"android:id/content").offspring("com.h3c.settings:id/nav_host_fragment").offspring(' \
                               '"com.h3c.settings:id/recycler_view").offspring("android.widget.ImageView")'
    # 设置主页-右侧-关于-协议说明-用户协议控件
    user_agreement = 'com.h3c.settings:id/tv_user_agreement'
    # 设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗控件
    user_agreement_pop = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                         '"android.widget.FrameLayout").offspring("android.view.ViewGroup")'
    # 设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-关闭控件
    user_agreement_pop_close = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                               '"android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")'
    # 设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-用户协议具体内容控件
    user_agreement_pop_content = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                 '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_content")'
    # 设置主页-右侧-关于-协议说明-隐私协议控件
    privacy_agreement = 'com.h3c.settings:id/tv_privacy_agreement'
    # 设置主页-右侧-关于-协议说明-用户协议-隐私协议弹窗控件
    privacy_agreement_pop = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                            '"android.widget.FrameLayout").offspring("android.view.ViewGroup")'
    # 设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-关闭控件
    privacy_agreement_pop_close = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                  '"android.widget.FrameLayout").offspring("com.h3c.settings:id/iv_close")'
    # 设置主页-右侧-关于-协议说明-用户协议-用户协议弹窗-用户协议具体内容控件
    privacy_agreement_pop_content = '("android.widget.FrameLayout").offspring("android:id/content").child(' \
                                    '"android.widget.FrameLayout").offspring("com.h3c.settings:id/tv_content")'
    # 设置主页-右侧-系统升级-保持系统自动升级开关按钮控件
    update_auto_switch = '("设置的标题栏。").offspring("android:id/content").offspring("android.widget.ScrollView").child(' \
                         '"androidx.appcompat.widget.LinearLayoutCompat").offspring("android.widget.Switch")[1]'
    # 设置主页-右侧-系统升级-系统升级检测异常提示文字控件
    update_check_abnormal = '("设置的标题栏。").offspring("android:id/content").offspring(' \
                            '"android.widget.ScrollView").offspring("com.h3c.settings:id/ll_check_items").offspring(' \
                            '"com.h3c.settings:id/tv_msg")'
    # 更多应用窗口
    more_app_window = 'com.h3c.launcher:id/ll_all_app'

    # 点击文字控件，调用如click_text("设置")
    # number = 0 参数可不输入，默认为0，如果存在多个相同文字，可输入相应的数字代表第几个
    @staticmethod
    def click_text(text,number=0):
        poco(text=text)[number].click()

    #滑动文字控件，调用如swipe("设置",[0.5,1])
    # number = 0 参数可不输入，默认为0，如果存在多个相同文字，可输入相应的数字代表第几个
    @staticmethod
    def swipe_text(text,swipe,number=0):
        poco(text=text)[number].swipe(swipe)

    #断言文字控件存在，调用如exist_text("设置","判断设置存在")
    @staticmethod
    def exist_text(text,msg):
        assert_equal(poco(text=text).exists(), True, msg)

    #断言文字控件不存在，调用如not_exist_text("设置","判断设置不存在")
    @staticmethod
    def not_exist_text(text,msg):
        assert_equal(poco(text=text).exists(), False, msg)

    #上滑呼出应用栏
    @staticmethod
    def open_dock():
        poco(text="上滑呼出应用栏")[0].swipe([0.5, -1])
        sleep(5)

    #打开launcher主页的dock栏下的应用，调用如open_dock_application("H3C传屏助手")
    #若DOCK栏未找到该应用，则会抛出NameError异常
    @staticmethod
    def open_dock_application(application_name):
        HeyboardOs.open_dock()
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
    def open_more_app_application(application_name):
        HeyboardOs.open_dock()
        poco(HeyboardOs.more_app).click()
        sleep(5)
        for num in range(30):
            try:
                text = poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/grid_all_app").child("android.view.ViewGroup")[num].child("com.h3c.launcher:id/tv_title").get_text()
                logger.debug(text)
                if text == application_name:
                    poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.h3c.launcher:id/grid_all_app").child("android.view.ViewGroup")[num].child("com.h3c.launcher:id/iv_icon").click()
                    sleep(5)
                    break
            except:
                raise NameError("未找到该应用")


    #返回白板历史颜色选择控件
    #前提条件：需要打开历史颜色选择界面
    #输入参数值超出或者没有历史颜色选择时会抛出异常
    @staticmethod
    def select_history_color(select_num):
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
    def get_blackboard_page(page_num):
        page_num_out = int(2*page_num-1)
        return (poco("android.widget.FrameLayout").offspring("com.h3c.launcher:id/rv_ui_infinitecanvas").child("android.widget.RelativeLayout")[page_num_out].child("com.h3c.launcher:id/iv_ui_rv_infinitecanvas_item_preview"))

    # 返回的是poco(控件id)
    #1表示第一页，2表示第2页
    @staticmethod
    def get_blackboard_share(page_num):
        page_num_out = int((page_num+2)/2)
        return (poco("android.widget.FrameLayout").offspring("android:id/content").child("android.widget.FrameLayout").child("android.view.ViewGroup").offspring("com.h3c.launcher:id/rv_page_preview").child("android.widget.FrameLayout")[page_num_out].child("com.h3c.launcher:id/iv_page_preview"))



class MegaosInternational:
    pass

class MegaDomestic:
    pass