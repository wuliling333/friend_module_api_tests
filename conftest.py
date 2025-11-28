# coding=utf-8
# coding=gbk
# @author: rourou
# @file: conftest.py.py
# @time: 2025/11/28 18:47
# @desc:
#!/usr/bin/env python3
"""
pytest配置文件
这个文件会被pytest自动加载
"""

import pytest
import requests
import yaml


def pytest_configure(config):
    """pytest配置钩子函数"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: 标记测试为慢速测试"
    )
    config.addinivalue_line(
        "markers", "api: 标记测试为API测试"
    )
    config.addinivalue_line(
        "markers", "normal: 标记测试为正常情况测试"
    )
    config.addinivalue_line(
        "markers", "abnormal: 标记测试为异常情况测试"
    )


def pytest_sessionstart(session):
    """测试会话开始时的钩子函数"""
    print("🚀 开始Quest API测试会话")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时的钩子函数"""
    print(f"🏁 测试会话结束，退出状态: {exitstatus}")


@pytest.fixture(scope="session")
def api_base_url():
    """提供API基础URL的fixture"""
    return "http://47.245.101.4:25001/api/Quest"


@pytest.fixture(scope="session")
def test_config():
    """提供测试配置的fixture"""
    try:
        with open("test_config.yaml", 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail("❌ test_config.yaml 文件未找到")
    except yaml.YAMLError as e:
        pytest.fail(f"❌ YAML配置文件解析错误: {e}")


@pytest.fixture
def api_session():
    """提供API会话的fixture"""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def log_test_execution(request):
    """自动记录测试执行的fixture"""
    print(f"\n▶️ 开始测试: {request.node.name}")
    yield
    print(f"⏹️ 结束测试: {request.node.name}")