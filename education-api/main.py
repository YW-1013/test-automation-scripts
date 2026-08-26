import pytest
import time
import os
import env


args = env.main_options_parser()
print(args)


if __name__ == '__main__':
    cmd_line_base = ['-v', f'--html=.{os.sep}report{os.sep}report_{time.strftime("%Y%m%d%H%M%S")}.html', '--self-contained-html']
    for key,value in args.items():
        if key == "tags":
            # pytest标签筛选通过-m参数，为了习惯使用，设置成--tags
            cmd_line_base.append(f"-m {value}")
        else:
            cmd_line_base.append(f"--{key}={value}")
    print(f"开始执行pytest，参数如下：\n\npytest {' '.join(cmd_line_base)}\n")
    pytest.main(cmd_line_base)
