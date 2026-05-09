import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def draw_heart(color='red', size=1.0, save_path=None, show=True):
    """
    绘制爱心图形
    
    Parameters:
        color (str): 爱心颜色，默认红色
        size (float): 缩放比例，默认1.0
        save_path (str or None): 保存路径，如果为None则不保存
        show (bool): 是否显示窗口，默认显示
    
    Returns:
        matplotlib.figure.Figure: 图形对象
    """
    # 生成角度参数 t，范围 0 到 2π
    t = np.linspace(0, 2 * np.pi, 1000)
    
    # 心形线参数方程
    # x = 16 * sin³(t)
    # y = 13 * cos(t) - 5 * cos(2t) - 2 * cos(3t) - cos(4t)
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    
    # 应用缩放
    x = x * size
    y = y * size
    
    # 创建图形和坐标轴
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 绘制爱心填充
    ax.fill(x, y, color=color, alpha=0.9)
    
    # 绘制爱心轮廓
    ax.plot(x, y, color=color, linewidth=2)
    
    # 设置坐标轴比例相等，使爱心不变形
    ax.set_aspect('equal')
    
    # 隐藏坐标轴
    ax.axis('off')
    
    # 设置背景透明
    ax.set_facecolor('none')
    fig.patch.set_alpha(0)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', transparent=True)
        print(f"爱心图形已保存至: {save_path}")
    
    # 显示窗口
    if show:
        plt.show()
    
    return fig

def draw_heart_with_text(text="", color='red', size=1.0, save_path=None):
    """
    绘制带文字的爱心图形
    
    Parameters:
        text (str): 要显示的文字
        color (str): 爱心颜色
        size (float): 缩放比例
        save_path (str or None): 保存路径
    
    Returns:
        matplotlib.figure.Figure: 图形对象
    """
    t = np.linspace(0, 2 * np.pi, 1000)
    
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    
    x = x * size
    y = y * size
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.fill(x, y, color=color, alpha=0.9)
    ax.plot(x, y, color=color, linewidth=2)
    
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加文字
    if text:
        ax.text(0, 0, text, fontsize=20, ha='center', va='center', 
                color='white', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', transparent=True)
        print(f"带文字的爱心图形已保存至: {save_path}")
    
    plt.show()
    return fig