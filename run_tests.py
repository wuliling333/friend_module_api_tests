#!/usr/bin/env python3
"""
测试运行脚本
提供多种运行测试的方式

运行方式：
python run_tests.py
"""

import subprocess
import sys
import os


def run_pytest_tests():
    """使用pytest运行测试"""
    print("🔧 使用pytest运行测试...")

    # pytest命令行参数
    args = [
        "pytest",
        "test_quest_api.py",  # 指定测试文件
        "-v",  # 详细输出
        "-s",  # 显示print输出
        "--tb=short",  # 简短的错误回溯
        "--strict-markers",  # 严格的标记检查
    ]

    # 如果存在html插件，生成HTML报告
    try:
        import pytest_html
        args.extend(["--html=test_report.html", "--self-contained-html"])
        print("📊 将生成HTML测试报告: test_report.html")
    except ImportError:
        print("⚠️  未安装pytest-html，跳过HTML报告生成")

    print(f"执行命令: {' '.join(args)}")
    print("-" * 60)

    # 运行pytest
    result = subprocess.run(args)
    return result.returncode


def run_simple_test():
    """运行简单的测试脚本"""
    print("🔧 运行简单测试脚本...")
    print("-" * 60)

    try:
        # 动态导入主测试模块
        from quest_api_test import QuestAPITester
        tester = QuestAPITester("test_config.yaml")
        tester.run_all_tests()
        return 0
    except Exception as e:
        print(f"❌ 简单测试运行失败: {e}")
        return 1


def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")

    required_packages = ['requests', 'yaml', 'pytest']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")

    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("✅ 所有依赖已安装")
    return True


def main():
    """主函数"""
    print("🎯 Quest API 测试套件")
    print("=" * 60)

    # 检查配置文件是否存在
    if not os.path.exists("test_config.yaml"):
        print("❌ 错误: test_config.yaml 文件不存在")
        print("请确保配置文件在当前目录中")
        return 1

    # 检查依赖
    if not check_dependencies():
        return 1

    print("\n" + "=" * 60)

    # 让用户选择运行方式
    print("请选择运行方式:")
    print("1. 使用pytest运行测试 (推荐)")
    print("2. 运行简单测试脚本")
    print("3. 两种方式都运行")
    print("4. 只检查环境")

    try:
        choice = input("\n请输入选择 (1-4): ").strip()

        if choice == "1":
            return run_pytest_tests()
        elif choice == "2":
            return run_simple_test()
        elif choice == "3":
            print("\n" + "=" * 60)
            print("🔄 运行两种测试方式...")
            result1 = run_simple_test()
            print("\n" + "=" * 60)
            result2 = run_pytest_tests()
            return result1 or result2
        elif choice == "4":
            print("✅ 环境检查完成")
            return 0
        else:
            print("❌ 无效选择，请输入1-4")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
        return 130
    except Exception as e:
        print(f"\n💥 运行错误: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

#python run_tests.py
