#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python爱心绘制工具 - 工具函数
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def heart_parametric_equation(t):
    """
    爱心参数方程
    
    参数:
        t (numpy.ndarray): 角度参数，范围 [0, 2π]
    
    返回:
        tuple: (x, y) 坐标数组
    """
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    return x, y

def create_heart_data(num_points=1000):
    """
    生成爱心数据点
    
    参数:
        num_points (int): 点的数量
    
    返回:
        tuple: (x, y) 坐标数组
    """
    t = np.linspace(0, 2 * np.pi, num_points)
    return heart_parametric_equation(t)

def validate_color(color):
    """
    验证颜色值是否有效
    
    参数:
        color (str): 颜色名称或十六进制颜色码
    
    返回:
        bool: 颜色是否有效
    """
    try:
        # 尝试用matplotlib解析颜色
        plt.rcParams['axes.prop_cycle'].by_key()['color']
        # 尝试创建patch来验证颜色
        patch = FancyBboxPatch((0, 0), 1, 1, facecolor=color)
        return True
    except (ValueError, AttributeError):
        return False

def get_color_list():
    """
    获取可用的颜色列表
    
    返回:
        list: 常用颜色名称列表
    """
    return [
        'red', 'pink', 'purple', 'orange', 'blue',
        'green', 'yellow', 'cyan', 'magenta', 'brown',
        'gray', 'black', 'white', 'darkred', 'lightcoral'
    ]

if __name__ == '__main__':
    # 测试工具函数
    print("测试爱心参数方程...")
    x, y = create_heart_data()
    print(f"数据点数量: {len(x)}")
    print(f"X范围: [{x.min():.2f}, {x.max():.2f}]")
    print(f"Y范围: [{y.min():.2f}, {y.max():.2f}]")
    
    print("\n测试颜色验证...")
    test_colors = ['red', 'invalid_color', '#FF0000', '#GGG']
    for color in test_colors:
        valid = validate_color(color)
        print(f"颜色 '{color}': {'有效' if valid else '无效'}")
    
    print("\n可用颜色列表:")
    colors = get_color_list()
    print(', '.join(colors))
