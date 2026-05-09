import os
import sys
import tempfile
import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免显示窗口
import matplotlib.pyplot as plt

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import draw_heart, draw_heart_with_text


class TestDrawHeart:
    """测试 draw_heart 函数"""
    
    def test_draw_heart_default_parameters(self):
        """测试默认参数绘制爱心"""
        fig = draw_heart()
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_draw_heart_custom_color(self):
        """测试自定义颜色"""
        fig = draw_heart(color='pink')
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_custom_size(self):
        """测试自定义大小"""
        fig = draw_heart(size=2.0)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_small_size(self):
        """测试极小尺寸"""
        fig = draw_heart(size=0.1)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_large_size(self):
        """测试极大尺寸"""
        fig = draw_heart(size=10.0)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_save_to_file(self):
        """测试保存到文件"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            save_path = tmp.name
        
        try:
            fig = draw_heart(save_path=save_path, show=False)
            assert fig is not None
            assert os.path.exists(save_path), f"文件 {save_path} 应该被创建"
            assert os.path.getsize(save_path) > 0, "文件大小应大于0"
            plt.close(fig)
        finally:
            if os.path.exists(save_path):
                os.unlink(save_path)
    
    def test_draw_heart_with_show_false(self):
        """测试不显示窗口"""
        fig = draw_heart(show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_returns_figure_object(self):
        """测试返回值类型"""
        fig = draw_heart(show=False)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
    
    def test_draw_heart_all_parameters(self):
        """测试所有参数组合"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            save_path = tmp.name
        
        try:
            fig = draw_heart(color='purple', size=1.5, save_path=save_path, show=False)
            assert fig is not None
            assert os.path.exists(save_path)
            plt.close(fig)
        finally:
            if os.path.exists(save_path):
                os.unlink(save_path)


class TestDrawHeartWithText:
    """测试 draw_heart_with_text 函数"""
    
    def test_draw_heart_with_text_default(self):
        """测试默认带文字爱心"""
        fig = draw_heart_with_text(show=False)
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        plt.close(fig)
    
    def test_draw_heart_with_text_custom_text(self):
        """测试自定义文字"""
        fig = draw_heart_with_text(text="Hello", show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_with_text_empty_text(self):
        """测试空文字"""
        fig = draw_heart_with_text(text="", show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_with_text_custom_color(self):
        """测试自定义颜色"""
        fig = draw_heart_with_text(text="Love", color='blue', show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_with_text_custom_size(self):
        """测试自定义大小"""
        fig = draw_heart_with_text(text="Love", size=2.0, show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_with_text_save(self):
        """测试保存带文字的爱心"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            save_path = tmp.name
        
        try:
            fig = draw_heart_with_text(text="Love", save_path=save_path, show=False)
            assert fig is not None
            assert os.path.exists(save_path)
            assert os.path.getsize(save_path) > 0
            plt.close(fig)
        finally:
            if os.path.exists(save_path):
                os.unlink(save_path)
    
    def test_draw_heart_with_text_chinese(self):
        """测试中文文字"""
        fig = draw_heart_with_text(text="爱", show=False)
        assert fig is not None
        plt.close(fig)
    
    def test_draw_heart_with_text_long_text(self):
        """测试长文字"""
        long_text = "I Love You Very Much" * 5
        fig = draw_heart_with_text(text=long_text, show=False)
        assert fig is not None
        plt.close(fig)


class TestHeartShapeQuality:
    """测试爱心形状质量"""
    
    def test_heart_shape_points_count(self):
        """测试生成的坐标点数量"""
        t = np.linspace(0, 2 * np.pi, 1000)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        
        assert len(x) == 1000, f"x坐标应有1000个点，实际有{len(x)}个"
        assert len(y) == 1000, f"y坐标应有1000个点，实际有{len(y)}个"
    
    def test_heart_shape_symmetry(self):
        """测试爱心形状的对称性"""
        t = np.linspace(0, 2 * np.pi, 1000)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        
        # 检查x轴对称性：x(t) 应该等于 -x(2π - t)
        x_reverse = 16 * np.sin(2 * np.pi - t) ** 3
        assert np.allclose(x, -x_reverse, atol=1e-10), "x坐标应关于y轴对称"
    
    def test_heart_shape_center(self):
        """测试爱心中心点"""
        t = np.linspace(0, 2 * np.pi, 1000)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        
        # 检查中心点附近是否有数据点
        center_x = 0
        center_y = 0
        distances = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        assert np.min(distances) < 1.0, "爱心应该经过中心点附近"


class TestModule1Imports:
    """测试 module_1.py 中的导入问题"""
    
    def test_module1_import_error(self):
        """测试 module_1.py 的导入错误"""
        # 这个测试验证 module_1.py 中的错误导入
        with pytest.raises(ModuleNotFoundError):
            from heart_drawer import draw_heart