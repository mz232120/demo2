#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证爱心绘制器的各项功能
"""

import sys
import io
from heart_drawer import draw_heart, _calculate_heart_points, _generate_heart_grid

def test_calculate_points():
    """测试点集计算"""
    print("测试1: 点集计算...")
    points = _calculate_heart_points(1.0)
    assert len(points) > 0, "点集不应为空"
    assert len(points) == 1000, f"应生成1000个点，实际{len(points)}"
    
    # 验证点集范围
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    assert max(xs) <= 17, f"x最大值应<=17，实际{max(xs)}"
    assert min(xs) >= -17, f"x最小值应>=-17，实际{min(xs)}"
    assert max(ys) <= 18, f"y最大值应<=18，实际{max(ys)}"
    assert min(ys) >= -18, f"y最小值应>=-18，实际{min(ys)}"
    print("  通过!")
    return True

def test_generate_grid():
    """测试网格生成"""
    print("测试2: 网格生成...")
    grid = _generate_heart_grid(1.0, '*')
    assert len(grid) > 0, "网格不应为空"
    
    # 检查是否包含填充字符
    all_chars = ''.join(grid)
    assert '*' in all_chars, "网格中应包含填充字符"
    print("  通过!")
    return True

def test_different_scales():
    """测试不同缩放比例"""
    print("测试3: 不同缩放比例...")
    for scale in [0.5, 1.0, 2.0]:
        grid = _generate_heart_grid(scale, '*')
        assert len(grid) > 0, f"scale={scale} 时网格不应为空"
    print("  通过!")
    return True

def test_different_chars():
    """测试不同填充字符"""
    print("测试4: 不同填充字符...")
    for char in ['*', '#', '@', '♥']:
        grid = _generate_heart_grid(1.0, char)
        all_chars = ''.join(grid)
        assert char in all_chars, f"网格中应包含字符 '{char}'"
    print("  通过!")
    return True

def test_console_output():
    """测试控制台输出"""
    print("测试5: 控制台输出...")
    # 捕获标准输出
    captured_output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        draw_heart(scale=0.5, char='*', mode='console')
        output = captured_output.getvalue()
        assert '爱心绘制' in output, "输出应包含标题"
        assert '*' in output, "输出应包含填充字符"
        print("  通过!")
        return True
    finally:
        sys.stdout = old_stdout

def test_invalid_params():
    """测试参数校验"""
    print("测试6: 参数校验...")
    
    # 测试无效scale
    try:
        grid = _generate_heart_grid(0, '*')
        # 应该不会崩溃，但可能返回空网格
        print(f"  scale=0 生成网格行数: {len(grid)}")
    except Exception as e:
        print(f"  scale=0 抛出异常: {e}")
    
    print("  通过!")
    return True

def run_all_tests():
    """运行所有测试"""
    print("="*50)
    print("Python爱心绘制器 - 测试套件")
    print("="*50)
    
    tests = [
        test_calculate_points,
        test_generate_grid,
        test_different_scales,
        test_different_chars,
        test_console_output,
        test_invalid_params
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            failed += 1
    
    print("="*50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*50)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
