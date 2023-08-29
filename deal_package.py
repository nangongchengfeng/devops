# -*- coding: utf-8 -*-
# @Time    : 2023/8/29 9:20
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : deal_package.py
# @Software: PyCharm

import os


def export_package():
    """
    导出当前项目的依赖包
    """
    os.system("pipreqs ./ --encoding='utf-8' --force")


def input_package():
    """
    安装当前项目的依赖包
    """
    os.system("pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple")


if __name__ == '__main__':
    input_package()