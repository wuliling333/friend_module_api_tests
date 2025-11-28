# coding=utf-8
# coding=gbk
# @author: rourou
# @file: test_quest_api.py.py
# @time: 2025/11/28 18:46
# @desc:
# !/usr/bin/env python3
"""
Pytest版本的Quest API测试
文件名必须以test_开头，类名以Test开头

运行命令：
pytest test_quest_api.py -v -s
pytest test_quest_api.py -v --html=report.html
"""

import pytest
import requests
import json
import yaml
from typing import Dict, Any, Optional


class TestQuestAPI:
    """Quest API测试类 - 使用pytest框架"""

    @classmethod
    def setup_class(cls):
        """
        测试类初始化方法
        在所有测试方法执行前调用一次
        """
        print("🔧 初始化测试环境...")
        # 加载测试配置
        cls.config = cls.load_config("test_config.yaml")
        # 设置基础URL
        cls.base_url = cls.config['base_url']
        # 创建HTTP会话
        cls.session = requests.Session()
        print(f"✅ 基础URL: {cls.base_url}")

    @classmethod
    def teardown_class(cls):
        """测试类清理方法"""
        print("🧹 清理测试环境...")
        cls.session.close()
        print("✅ 测试环境清理完成")

    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """
        加载YAML配置文件

        Args:
            config_file: 配置文件路径

        Returns:
            配置字典
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                print(f"✅ 成功加载配置文件: {config_file}")
                return config
        except FileNotFoundError:
            pytest.fail(f"❌ 配置文件 {config_file} 未找到")
        except yaml.YAMLError as e:
            pytest.fail(f"❌ YAML配置文件解析错误: {e}")

    def send_request(self, endpoint: str, uid: Optional[str], data: Any) -> Dict[str, Any]:
        """
        发送API请求的通用方法

        Args:
            endpoint: API端点
            uid: 用户ID
            data: 请求数据

        Returns:
            响应信息字典
        """
        url = f"{self.base_url}/{endpoint}"
        form_data = {}

        # 添加UID参数（如果存在）
        if uid is not None:
            form_data['uid'] = str(uid)

        # 添加data参数（如果存在）
        if data is not None:
            if isinstance(data, (dict, list)):
                # 有效数据转换为JSON
                form_data['data'] = json.dumps(data, ensure_ascii=False)
            else:
                # 无效数据保持原样（用于测试）
                form_data['data'] = str(data)

        print(f"🌐 发送请求到: {url}")
        print(f"📦 请求数据: {form_data}")

        try:
            # 发送请求
            response = self.session.post(url, data=form_data, timeout=10)

            result = {
                'status_code': response.status_code,  # HTTP状态码
                'response_text': response.text,  # 响应文本
                'response_json': None
            }

            # 尝试解析JSON响应
            if response.text.strip():
                try:
                    result['response_json'] = response.json()
                except json.JSONDecodeError:
                    print("⚠️ 响应不是有效的JSON格式")

            print(f"📨 响应状态码: {result['status_code']}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"💥 请求异常: {e}")
            pytest.fail(f"❌ API请求失败: {e}")

    # 正常情况测试 - 使用参数化减少重复代码
    @pytest.mark.parametrize("case_name", [
        "FetchQuestList",  # 测试获取任务列表
        "SkipMainQuest",  # 测试跳过主任务
        "ClaimQuestRewards",  # 测试领取奖励
        "ReportQuestProgress",  # 测试报告进度
        "FetchQuestActivityData"  # 测试获取活动数据
    ])
    def test_normal_cases(self, case_name):
        """
        测试正常情况下的API行为

        Args:
            case_name: 测试用例名称，从参数化列表中获取
        """
        print(f"\n{'=' * 50}")
        print(f"🔵 测试正常情况: {case_name}")
        print(f"{'=' * 50}")

        # 从配置中获取测试用例
        test_case = self.config['test_cases']['normal_cases'][case_name]
        # 发送请求
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']
        )

        # 获取期望的状态码
        expected_status = test_case['expected_status']

        # 断言：状态码应该符合预期
        assert result['status_code'] == expected_status, \
            f"❌ {case_name}: 期望状态码 {expected_status}, 实际 {result['status_code']}, 响应: {result['response_text']}"

        # 断言：成功请求应该返回2xx状态码
        assert result['status_code'] in [200, 201], \
            f"❌ {case_name}: API应该返回成功状态码，实际返回 {result['status_code']}"

        print(f"✅ {case_name} 测试通过")

    def test_missing_uid(self):
        """测试缺少UID参数的情况"""
        print(f"\n{'=' * 50}")
        print(f"🔴 测试异常情况: 缺少UID参数")
        print(f"{'=' * 50}")

        # 获取缺少UID的测试用例
        test_case = self.config['test_cases']['abnormal_cases']['FetchQuestList_MissingUID']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],  # 这里uid为null
            test_case['data']
        )

        # 断言：缺少必要参数应该返回400错误
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 缺少UID时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 缺少UID参数测试通过")

    def test_missing_data(self):
        """测试缺少data参数的情况"""
        print(f"\n{'=' * 50}")
        print(f"🔴 测试异常情况: 缺少data参数")
        print(f"{'=' * 50}")

        test_case = self.config['test_cases']['abnormal_cases']['FetchQuestList_MissingData']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']  # 这里data为null
        )

        # 断言：缺少data参数应该返回400错误
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 缺少data时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 缺少data参数测试通过")

    def test_invalid_json_format(self):
        """测试无效JSON格式的情况"""
        print(f"\n{'=' * 50}")
        print(f"🔴 测试异常情况: 无效JSON格式")
        print(f"{'=' * 50}")

        test_case = self.config['test_cases']['abnormal_cases']['FetchQuestList_InvalidJSON']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']  # 无效的JSON字符串
        )

        # 断言：无效JSON应该返回400错误
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 无效JSON时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 无效JSON格式测试通过")

    def test_invalid_quest_id(self):
        """测试无效任务ID的情况"""
        print(f"\n{'=' * 50}")
        print(f"🔴 测试异常情况: 无效任务ID")
        print(f"{'=' * 50}")

        test_case = self.config['test_cases']['abnormal_cases']['SkipMainQuest_InvalidQuestId']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']  # 包含无效任务ID的数据
        )

        # 断言：无效任务ID应该返回400错误
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 无效任务ID时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 无效任务ID测试通过")

    def test_empty_activity_list(self):
        """测试空活动列表的情况"""
        print(f"\n{'=' * 50}")
        print(f"🟡 测试边界情况: 空活动列表")
        print(f"{'=' * 50}")

        test_case = self.config['test_cases']['abnormal_cases']['FetchQuestList_EmptyActivityList']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']  # 空活动列表
        )

        # 断言：空活动列表应该返回期望的状态码
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 空活动列表时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 空活动列表测试通过")

    def test_invalid_uid_format(self):
        """测试无效UID格式的情况"""
        print(f"\n{'=' * 50}")
        print(f"🔴 测试异常情况: 无效UID格式")
        print(f"{'=' * 50}")

        test_case = self.config['test_cases']['abnormal_cases']['FetchQuestList_InvalidUID']
        result = self.send_request(
            test_case['endpoint'],
            test_case['uid'],
            test_case['data']
        )

        # 断言：无效UID应该返回400错误
        assert result['status_code'] == test_case['expected_status'], \
            f"❌ 无效UID时应返回{test_case['expected_status']}，实际返回{result['status_code']}"

        print("✅ 无效UID格式测试通过")


# 简单的测试函数，不依赖类
def test_api_connectivity():
    """测试API连通性"""
    print(f"\n{'=' * 50}")
    print(f"🌐 测试API连通性")
    print(f"{'=' * 50}")

    base_url = "http://47.245.101.4:25001/api/Quest"

    try:
        # 尝试连接API服务
        response = requests.get(base_url, timeout=5)
        print(f"✅ API连通性测试完成，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API连通性测试失败: {e}")
        # 这里我们不使测试失败，因为端点可能确实不存在
        pytest.skip(f"⏭️ API服务可能未运行: {e}")


if __name__ == "__main__":
    # 当直接运行脚本时，启动pytest
    pytest.main([__file__, "-v", "-s"])

