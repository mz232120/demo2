"""
Python爱心绘制工具 - 主入口文件
展示爱心图形的绘制功能
"""

from heart_drawer import draw_heart, draw_heart_with_text

def main():
    """主函数，展示示例用法"""
    print("=" * 50)
    print("Python爱心绘制工具")
    print("=" * 50)
    
    # 示例1：绘制默认红色爱心
    print("\n示例1：绘制默认红色爱心")
    draw_heart()
    
    # 示例2：绘制粉色爱心并保存
    print("\n示例2：绘制粉色爱心并保存")
    draw_heart(color='pink', size=1.2, save_path='pink_heart.png')
    
    # 示例3：绘制带文字的爱心
    print("\n示例3：绘制带文字的爱心")
    draw_heart_with_text(text="Love", color='red', size=1.0)

if __name__ == "__main__":
    main()