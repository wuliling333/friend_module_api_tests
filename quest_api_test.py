# coding=utf-8
# coding=gbk
# @author: rourou
# @file: quest_api_test.py.py
# @time: 2025/11/28 18:46
# @desc:
# !/usr/bin/env python3
"""
Quest API 测试脚本
使用YAML配置文件管理测试用例，支持正常和异常情况测试

功能特点：
1. 通过YAML文件配置测试用例，便于维护
2. 支持正常情况和异常情况测试
3. 自动生成详细的测试报告
4. 包含响应时间统计
5. 支持断言验证

作者: API测试框架
版本: 1.0
"""

import requests
import json
import yaml
import time
from typing import Dict, Any, Optional, List


class QuestAPITester:
    """
    Quest API测试器类
    负责加载配置、执行测试用例和生成报告
    """

    def __init__(self, config_file: str = "test_config.yaml"):
        """
        初始化测试器

        Args:
            config_file: YAML配置文件的路径
        """
        # 加载测试配置
        self.config = self.load_config(config_file)
        # 获取基础URL
        self.base_url = self.config['base_url']
        # 创建HTTP会话，保持连接
        self.session = requests.Session()
        # 存储所有测试结果
        self.results: List[Dict[str, Any]] = []

        print(f"✅ 测试器初始化完成，基础URL: {self.base_url}")

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载YAML配置文件

        Args:
            config_file: 配置文件的路径

        Returns:
            解析后的配置字典

        Raises:
            Exception: 当文件不存在或YAML格式错误时抛出
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                print(f"✅ 成功加载配置文件: {config_file}")
                return config
        except FileNotFoundError:
            # 文件不存在异常
            raise Exception(f"❌ 配置文件 {config_file} 未找到，请检查文件路径")
        except yaml.YAMLError as e:
            # YAML格式解析异常
            raise Exception(f"❌ YAML配置文件解析错误: {e}")

    def send_request(self, endpoint: str, uid: Optional[str], data: Any) -> Dict[str, Any]:
        """
        发送API请求到指定端点

        Args:
            endpoint: API端点路径（如 'FetchQuestList'）
            uid: 用户ID，如果为None则不发送该参数
            data: 请求数据，可以是字典、列表或字符串

        Returns:
            包含响应信息的字典，包括状态码、响应时间、响应内容等
        """
        # 构建完整的API URL
        url = f"{self.base_url}/{endpoint}"

        # 准备表单数据
        form_data = {}
        if uid is not None:
            # 添加UID参数
            form_data['uid'] = str(uid)

        if data is not None:
            if isinstance(data, (dict, list)):
                # 如果是字典或列表，转换为JSON字符串
                form_data['data'] = json.dumps(data, ensure_ascii=False)
            else:
                # 直接使用字符串（用于测试无效JSON的情况）
                form_data['data'] = str(data)

        try:
            # 记录请求开始时间，用于计算响应时间
            start_time = time.time()
            # 发送POST请求，超时设置为10秒
            response = self.session.post(url, data=form_data, timeout=10)
            # 计算响应时间
            response_time = time.time() - start_time

            # 构建结果字典
            result = {
                'url': url,  # 请求的URL
                'form_data': form_data,  # 发送的表单数据
                'status_code': response.status_code,  # HTTP状态码
                'response_time': response_time,  # 响应时间（秒）
                'response_text': response.text,  # 响应文本内容
                'response_json': None,  # 解析后的JSON响应
                'error': None  # 错误信息
            }

            # 尝试解析JSON响应
            if response.text.strip():
                try:
                    result['response_json'] = response.json()
                except json.JSONDecodeError:
                    # JSON解析失败是正常的，特别是在测试异常情况时
                    pass

            return result

        except requests.exceptions.RequestException as e:
            # 处理请求异常（网络错误、超时等）
            return {
                'url': url,
                'form_data': form_data,
                'status_code': None,  # 请求失败，没有状态码
                'response_time': None,
                'response_text': None,
                'response_json': None,
                'error': str(e)  # 记录错误信息
            }

    def run_test_case(self, case_name: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个测试用例

        Args:
            case_name: 测试用例名称
            test_case: 测试用例配置字典

        Returns:
            包含测试结果的字典
        """
        # 打印测试开始信息
        print(f"🧪 执行测试: {case_name}")
        # 如果有描述信息，打印描述
        if 'description' in test_case:
            print(f"   📝 描述: {test_case['description']}")

        # 发送API请求
        result = self.send_request(
            endpoint=test_case['endpoint'],
            uid=test_case.get('uid'),  # 使用get方法避免KeyError
            data=test_case.get('data')
        )

        # 获取期望的状态码，默认为200
        expected_status = test_case.get('expected_status', 200)

        # 补充测试结果信息
        result['case_name'] = case_name  # 测试用例名称
        result['expected_status'] = expected_status  # 期望的状态码
        result['passed'] = self.validate_result(result, expected_status)  # 测试是否通过

        # 打印测试结果
        status_icon = "✅" if result['passed'] else "❌"  # 使用图标表示状态
        print(f"   🎯 状态: {status_icon} (期望: {expected_status}, 实际: {result['status_code']})")
        print(f"   ⏱️  响应时间: {result.get('response_time', 0):.3f}s")

        # 如果有错误信息，打印错误
        if result['error']:
            print(f"   💥 错误: {result['error']}")

        # 如果测试失败且有响应内容，打印部分响应内容用于调试
        if not result['passed'] and result['response_text']:
            print(f"   📄 响应: {result['response_text'][:200]}...")

        print()  # 空行分隔
        return result

    def validate_result(self, result: Dict[str, Any], expected_status: int) -> bool:
        """
        验证测试结果是否符合预期

        Args:
            result: 测试结果字典
            expected_status: 期望的HTTP状态码

        Returns:
            bool: 测试是否通过
        """
        # 如果有网络错误，测试失败
        if result['error']:
            return False

        # 如果状态码不符合预期，测试失败
        if result['status_code'] != expected_status:
            return False

        # 这里可以添加更多的业务逻辑验证
        # 例如：检查响应数据格式、字段完整性等
        # if result['response_json']:
        #     # 验证响应数据结构的示例
        #     if 'success' in result['response_json']:
        #         return result['response_json']['success'] == True

        return True  # 所有验证通过

    def run_all_tests(self) -> None:
        """运行所有测试用例并生成报告"""
        print("=" * 70)
        print("🚀 开始 Quest API 全面测试")
        print("=" * 70)

        # 合并所有测试用例
        test_cases = {}
        test_cases.update(self.config['test_cases']['normal_cases'])  # 正常用例
        test_cases.update(self.config['test_cases']['abnormal_cases'])  # 异常用例

        total_cases = len(test_cases)  # 总测试用例数
        passed_cases = 0  # 通过的测试用例数

        # 运行正常测试用例
        print("\n🔵 正常情况测试:")
        print("-" * 50)
        normal_count = 0
        for case_name, test_case in self.config['test_cases']['normal_cases'].items():
            result = self.run_test_case(case_name, test_case)
            self.results.append(result)
            if result['passed']:
                passed_cases += 1
                normal_count += 1

        # 运行异常测试用例
        print("\n🔴 异常情况测试:")
        print("-" * 50)
        abnormal_count = 0
        for case_name, test_case in self.config['test_cases']['abnormal_cases'].items():
            result = self.run_test_case(case_name, test_case)
            self.results.append(result)
            if result['passed']:
                passed_cases += 1
                abnormal_count += 1

        # 生成测试报告
        self.generate_report(total_cases, passed_cases, normal_count, abnormal_count)

    def generate_report(self, total: int, passed: int, normal_passed: int, abnormal_passed: int) -> None:
        """
        生成详细的测试报告

        Args:
            total: 总测试用例数
            passed: 通过的测试用例数
            normal_passed: 正常用例通过数
            abnormal_passed: 异常用例通过数
        """
        print("=" * 70)
        print("📊 测试报告总结")
        print("=" * 70)

        # 计算成功率
        success_rate = (passed / total) * 100 if total > 0 else 0

        # 打印基本统计信息
        print(f"📈 总体统计:")
        print(f"   总测试用例: {total}")
        print(f"   通过用例: {passed}")
        print(f"   失败用例: {total - passed}")
        print(f"   成功率: {success_rate:.1f}%")

        print(f"\n🔵 正常情况测试:")
        normal_total = len(self.config['test_cases']['normal_cases'])
        normal_rate = (normal_passed / normal_total) * 100 if normal_total > 0 else 0
        print(f"   正常用例总数: {normal_total}")
        print(f"   正常用例通过: {normal_passed}")
        print(f"   正常用例成功率: {normal_rate:.1f}%")

        print(f"\n🔴 异常情况测试:")
        abnormal_total = len(self.config['test_cases']['abnormal_cases'])
        abnormal_rate = (abnormal_passed / abnormal_total) * 100 if abnormal_total > 0 else 0
        print(f"   异常用例总数: {abnormal_total}")
        print(f"   异常用例通过: {abnormal_passed}")
        print(f"   异常用例成功率: {abnormal_rate:.1f}%")

        # 显示失败的测试用例详情
        failed_cases = [r for r in self.results if not r['passed']]
        if failed_cases:
            print(f"\n❌ 失败的测试用例 ({len(failed_cases)}):")
            for case in failed_cases:
                print(f"   - {case['case_name']}")
                # 打印测试用例描述（如果有）
                if case.get('description'):
                    print(f"     描述: {case['description']}")
                print(f"     期望状态码: {case['expected_status']}")
                print(f"     实际状态码: {case.get('status_code', 'N/A')}")
                # 如果有错误信息，打印错误
                if case['error']:
                    print(f"     错误: {case['error']}")
                print()

        # 显示响应时间统计
        response_times = [r['response_time'] for r in self.results if r.get('response_time')]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            print(f"\n⏱️  响应时间统计:")
            print(f"   平均响应时间: {avg_time:.3f}s")
            print(f"   最小响应时间: {min_time:.3f}s")
            print(f"   最大响应时间: {max_time:.3f}s")

        print("\n" + "=" * 70)
        # 根据测试结果输出不同的结束信息
        if passed == total:
            print("🎉 所有测试用例通过！API表现完美！")
        else:
            print(f"⚠️  {total - passed} 个测试用例失败，请检查API实现和错误处理")

        print("=" * 70)

    def close(self):
        """关闭测试器，释放资源"""
        self.session.close()
        print("✅ 测试器已关闭，资源已释放")


def main():
    """主函数 - 程序入口点"""
    tester = None
    try:
        # 创建测试器实例并运行所有测试
        tester = QuestAPITester("test_config.yaml")
        tester.run_all_tests()
        return 0
    except Exception as e:
        # 捕获并显示所有未处理的异常
        print(f"❌ 测试执行失败: {e}")
        return 1
    finally:
        # 确保资源被释放
        if tester:
            tester.close()


if __name__ == "__main__":
    # 当脚本直接运行时执行main函数
    exit_code = main()
    exit(exit_code)