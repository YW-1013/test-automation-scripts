from airtest.cli.runner import AirtestCase, run_script
from argparse import *
import airtest.report.report as report
import jinja2
import shutil
import os
import io
from conf import *
import time
import datetime
import subprocess
from airtest.core.settings import Settings as ST
import logcat
import cpuinfo
import multiprocessing


class CustomAirtestCase(AirtestCase):
    devices = DEVICE_INFO  # 设备ip及平台
    devices_url = DEVICES_URL
    suit_dir = CASE_PATH  # 总目录
    log_all_path = LOG_ALL_PATH  # 日志目录
    report_html_path = TEMPLATE_REPORT_PATH  # 模板报告目录
    report_name = REPORT_NAME  # 报告名称
    reboot_num = int(REBOOT_NUM)#运行多少条用例重启一次
    threshold = float(THRESHOLD)#全局相似度
    image_maxsize = int(IMAGE_MAXSIZE)#全局截图最大边长
    save_image = bool(SAVE_IMAGE)#全局是否保存图片


    total_cases = 0  # 总用例数
    cases_success = 0  # 成功用例数
    cases_fail = 0  # 失败用例数

    # ST.OPDELAY = 10
    ST.THRESHOLD = threshold
    ST.IMAGE_MAXSIZE = image_maxsize
    ST.SAVE_IMAGE = save_image

    def setUp(self):  # 执行脚本前的前置环境准备操作
        print("custom setup")
        time.sleep(10)

        # super(CustomAirtestCase, self).setUp()

    def tearDown(self):
        # 执行脚本后的后置环境恢复操作
        print("custom tearDown")

        # super(CustomAirtestCase, self).setUp()



    def set_report_name(self, name, add_time):
        time_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if add_time == "False":
            report_name = f"{name}.html"
        elif add_time == "True":
            report_name = f"{name}{time_now}.html"
        else:
            report_name = "summary.html"
        return report_name

    def get_root_log_path(self,report_name):#获取log总路径
        time_now_is = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        root_log = os.path.join(LOG_ALL_PATH, f"{report_name}_{time_now_is}_log")
        return root_log



    def get_all_cases(self):
        cases = []
        cases_name = []
        for dirpath, dirnames, failenames in os.walk(self.suit_dir):
            for dirname in dirnames:
                if dirname.endswith(".air"):
                    cases.append(os.path.join(dirpath, dirname))
                    cases_name.append(dirname)
        return cases, cases_name

    def create_root_log(self,root_log):
        if os.path.isdir(root_log):  # 判断该路径是否为目录，如果是目录，表示已存在上次的结果，则删除
            shutil.rmtree(root_log)
        else:
            os.makedirs(root_log)  # 如果不是目录，则新建目录，递归创建
            print(str(root_log) + 'is created')

    def create_case_log(self, log):
        # 判断case日志在不在，在，则删除目录中的内容，否则，新建每个脚本log目录
        if os.path.isdir(log):
            shutil.rmtree(log)
        else:
            os.makedirs(log)
            print(str(log) + 'is created')
            # 日志的输出html文件，是airtest生成的日志文件
            output_file = os.path.join(log, 'log.html')
        return output_file

    def get_result_num(self, result):
        if result["result"] is True:
            self.cases_success += 1  # 得到成功的用例数
        elif result["result"] is False:
            self.cases_fail += 1  # 得到失败的用例数
        try:
            success_rate = ('{:.2f}%'.format(self.cases_success / self.total_cases * 100))  # 得到成功率
        except:
            success_rate = "none"
        return self.cases_success, self.cases_fail, success_rate

    def format_seconds(self,seconds):
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes, seconds = divmod(seconds, 60)
            return f"{minutes}分{seconds}秒"
        else:
            hours, remaining_seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(remaining_seconds, 60)
            return f"{hours}小时{minutes}分{seconds}秒"


    # root_dir是项目根目录，device是默认连接设备，可以把常用的设备设置成默认的设备
    def run_air(self, device=devices):  # 聚合结果
        results = []  # 获取所有用例集

        start_time_all = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')# 获取当前用例运行的开始时间，写在报告的表头概况中
        int_start_time_all = int(time.time())  # 获取用例总的运行时长

        self.root_log = self.get_root_log_path(self.report_name)#获取log总路径
        self.create_root_log(self.root_log)  # 处理日志目录
        cases_total_list, cases_name_list = self.get_all_cases()  # 获取总用例的路径和名称


        if IS_REBOOT == "True":  # 首次运行时是否重启
            try:
                subprocess.run(["adb", "-s", f"{DEVICES_URL}", "shell", "reboot"])
                time.sleep(80)
            except:
                subprocess.run(f"adb connect {DEVICES_URL}")
        for number in range(0,len(cases_total_list)):  # 运行获取到的每一条用例
            if "[" in cases_name_list[number] and "]" in cases_name_list[number]:
                if cases_name_list[number].split("[")[1].split("]")[0] != SUIT_SELECT:
                    number += 1
                    continue


            if (number + 1) % self.reboot_num == 0 and self.reboot_num != 1:
                try:
                    subprocess.run(["adb", "-s", f"{DEVICES_URL}", "shell", "reboot"])
                    time.sleep(80)
                except:
                    a = 1
                    while a < 10:
                        subprocess.run(f"adb connect {DEVICES_URL}")
                        time.sleep(2)
                        if f"{DEVICES_URL}" in str(subprocess.getoutput("adb devices")):
                            break
                        a +=1
                        time.sleep(10)

            print(f"-----------------------------------{cases_name_list[number]}开始运行--------------------------------------------")
            print(f"-----------------------------------{cases_name_list[number]}开始运行--------------------------------------------")
            print(f"-----------------------------------{cases_name_list[number]}开始运行--------------------------------------------")
            self.total_cases += 1  # 总用例数
            # log为存放日志的最里面那层文件夹的路径加文件夹名称
            log = os.path.join(self.root_log,cases_name_list[number].replace('.air', ''))

            output_file = self.create_case_log(log)

            args = Namespace(device=device, log=log, recording=None, script=cases_total_list[number], compress=0, no_image=False,scale=0.5)

            try:
                self.setUp()
                start_time = int(time.time())  # 获取每条用例运行的起始时间，用来获取用例运行时长
                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取用例的运行起始时间，写在报告中
                run_script(args, AirtestCase)  # 运行用例
                self.tearDown()
            except:
                print("该条用例运行失败")

            finally:
                end_time = int(time.time())  # 每条用例运行的结束时间
                time_use = end_time - start_time  # 每条用例运行的时长
                time_use = self.format_seconds(time_use)
                user_all = end_time - int_start_time_all  # 用例运行的总时长
                user_all = self.format_seconds(user_all)

                rpt = report.LogToHtml(cases_total_list[number],
                                       log)  # 创建一个html格式的测试报告，第一个参数是测试用例的名称，第二个参数是日志路径，生成的是airtest自身的测试报告
                # 结果模板渲染，"log_template.html"是airtest自带的模板，output_file日志存放路径，生成airtest自带的测试报告
                rpt.report("log_template.html", output_file=output_file)

                # 结果保存在result对象中
                result = {"name": cases_name_list[number].replace('.air', ''), "result": rpt.test_result,
                          "time_use": time_use, "time_now": time_now}
                results.append(result)  # 获得resuts数组，用来写入测试报告中的数据

                self.cases_success, self.cases_fail, success_rate = self.get_result_num(result)  # 获取用例成功、失败、成功率的数据

                # 根据summary_template.html模板，生成聚合报告
                env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.report_html_path), extensions=(),
                                         autoescape=True)  # 加载器加载模板，env是jinja2的环境变量，用来加载模板并提供渲染模板的方法
                # summary_template.html相对路径
                template = env.get_template("summary_template.html")  # 获取模板对象
                # 渲染模板
                html = template.render(
                    {"results": results, "report_name_title": self.report_name, "start_time_all": start_time_all,
                     # 运行结果
                     "total_cases": self.total_cases, "cases_success": self.cases_success,
                     "cases_fail": self.cases_fail, "success_rate": success_rate, "user_all": user_all})

                output_file = os.path.join(self.root_log, f"{self.report_name}.html")
                with io.open(output_file, 'w', encoding="utf-8") as f:
                    f.write(html)
                time.sleep(10)


if __name__ == '__main__':
    for i in range(RUN_TIMES+1):
        test = CustomAirtestCase()

        p1 = multiprocessing.Process(target=test.run_air)
        p2 = multiprocessing.Process(target=logcat.logcat_time)
        p3 = multiprocessing.Process(target=cpuinfo.get_cpuinfo)

        p3.start()
        p2.start()
        p1.start()



        while True:
            time.sleep(10)
            if not p1.is_alive():
                print("Process 1 terminated")
                p2.terminate()
                print("Process 2 terminated")
                p3.terminate()
                print("Process 3 terminated")
                break
        time.sleep(60)


