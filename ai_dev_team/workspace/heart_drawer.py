#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心绘制模块 - 提供爱心绘制功能
支持控制台字符画和Tkinter图形界面
"""

import math
import sys

def _calculate_heart_points(scale):
    """
    计算爱心形状的点集
    
    使用参数方程:
    x = 16 * sin^3(t)
    y = 13*cos(t) - 5*cos(2t) - 2*cos(3t) - cos(4t)
    
    参数:
        scale: 缩放比例
    
    返回:
        points: 点集列表，每个元素为 (x, y) 坐标
    """
    points = []
    # 在 0 到 2π 之间采样 1000 个点
    steps = 1000
    for i in range(steps):
        t = 2 * math.pi * i / steps
        # 标准爱心参数方程 (范围约 -17 到 17)
        x = 16 * (math.sin(t) ** 3)
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        # 应用缩放
        x_scaled = x * scale
        y_scaled = y * scale
        points.append((x_scaled, y_scaled))
    return points


def _generate_heart_grid(scale, fill_char):
    """
    生成爱心字符网格
    
    参数:
        scale: 缩放比例
        fill_char: 填充字符
    
    返回:
        字符串网格 (行列表)
    """
    # 获取点集
    points = _calculate_heart_points(scale)
    
    if not points:
        return []
    
    # 计算边界
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # 计算网格尺寸 (字符宽高比约 2:1)
    char_width = 2  # 每个字符占2个空格宽度
    char_height = 1
    
    width = int((max_x - min_x) / char_width * scale) + 2
    height = int((max_y - min_y) / char_height * scale) + 2
    
    # 创建网格 (初始化为空格)
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # 将点映射到网格
    for (x, y) in points:
        # 映射到网格坐标
        grid_x = int((x - min_x) / (max_x - min_x) * (width - 1))
        grid_y = int((y - min_y) / (max_y - min_y) * (height - 1))
        
        # 确保在边界内
        grid_x = max(0, min(width - 1, grid_x))
        grid_y = max(0, min(height - 1, grid_y))
        
        # 填充字符
        grid[grid_y][grid_x] = fill_char
    
    return [''.join(row) for row in grid]


def draw_heart_console(scale, char):
    """
    在控制台绘制爱心
    
    参数:
        scale: 缩放比例
        char: 填充字符
    """
    grid = _generate_heart_grid(scale, char)
    
    if not grid:
        print("错误：无法生成爱心网格")
        return
    
    # 打印爱心
    print(f"\n{'='*40}")
    print(f"爱心绘制 (scale={scale}, char='{char}')")
    print(f"{'='*40}")
    for row in grid:
        print(row)
    print(f"{'='*40}\n")


def draw_heart_gui(scale, char, color):
    """
    使用Tkinter绘制图形界面爱心
    
    参数:
        scale: 缩放比例
        char: 填充字符 (GUI模式使用)
        color: 爱心颜色
    """
    try:
        import tkinter as tk
    except ImportError:
        print("错误：Tkinter 未安装，无法使用 GUI 模式")
        print("请安装 python3-tk 包 (Linux) 或使用 console 模式")
        sys.exit(1)
    
    # 创建主窗口
    root = tk.Tk()
    root.title(f"Python爱心绘制器 - {color}")
    
    # 计算窗口尺寸 (基于缩放)
    base_size = 400
    window_size = int(base_size * scale)
    window_size = max(200, min(800, window_size))  # 限制在200-800之间
    
    root.geometry(f"{window_size}x{window_size}")
    root.resizable(True, True)
    
    # 创建画布
    canvas = tk.Canvas(root, width=window_size, height=window_size, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # 计算爱心路径
    points = _calculate_heart_points(scale)
    
    if not points:
        print("错误：无法生成爱心点集")
        return
    
    # 计算边界和缩放
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    # 计算缩放比例以适应画布 (留边距)
    margin = 40
    usable_width = window_size - 2 * margin
    usable_height = window_size - 2 * margin
    
    range_x = max_x - min_x
    range_y = max_y - min_y
    
    if range_x == 0 or range_y == 0:
        print("错误：爱心范围无效")
        return
    
    scale_x = usable_width / range_x
    scale_y = usable_height / range_y
    plot_scale = min(scale_x, scale_y)
    
    # 计算中心偏移
    center_x = window_size / 2
    center_y = window_size / 2
    
    # 将点转换为画布坐标并绘制多边形
    canvas_points = []
    for (x, y) in points:
        canvas_x = center_x + (x - (min_x + max_x) / 2) * plot_scale
        canvas_y = center_y + (y - (min_y + max_y) / 2) * plot_scale
        canvas_points.append(canvas_x)
        canvas_points.append(canvas_y)
    
    # 绘制填充爱心
    canvas.create_polygon(canvas_points, fill=color, outline='', smooth=True)
    
    # 显示参数信息
    info_text = f"Scale: {scale}  Color: {color}  Char: '{char}'"
    canvas.create_text(window_size/2, window_size - 20, text=info_text, 
                       fill='gray', font=('Arial', 10))
    
    # 运行主循环
    root.mainloop()


def draw_heart(scale=1.0, char='*', color='red', mode='console'):
    """
    核心绘制函数 - 根据模式选择绘制方式
    
    参数:
        scale: 缩放比例 (默认1.0)
        char: 填充字符 (默认'*')
        color: 颜色 (默认'red')
        mode: 模式 ('console' 或 'gui', 默认'console')
    """
    if mode == 'console':
        draw_heart_console(scale, char)
    elif mode == 'gui':
        draw_heart_gui(scale, char, color)
    else:
        print(f"错误：未知模式 '{mode}'，请使用 'console' 或 'gui'")
