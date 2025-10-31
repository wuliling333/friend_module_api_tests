# coding=utf-8
# coding=gbk
# @author: rourou
# @file: test_script.py.py
# @time: 2025/10/31 18:49
# @desc:
import requests
import yaml
import json
from datetime import datetime

# 加载 YAML 配置文件
def load_config(file_path="config.yaml"):
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

# 保存测试结果到文件
def save_result(test_name, response, payload=None, expected_result=None, passed=False):
    with open("test_results.txt", "a", encoding="utf-8") as file:
        file.write(f"Test: {test_name}\n")
        file.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"URL: {response.url}\n")
        file.write(f"Payload: {json.dumps(payload, indent=2) if payload else 'None'}\n")
        file.write(f"Status Code: {response.status_code}\n")
        file.write(f"Response: {response.text}\n")
        if expected_result:
            file.write(f"Expected Status Code: {expected_result.get('status_code', 'None')}\n")
            file.write(f"Expected Response Contains: {expected_result.get('response_contains', 'None')}\n")
        file.write(f"Test Result: {'PASSED' if passed else 'FAILED'}\n")
        file.write("-" * 50 + "\n")

# 判断测试结果是否符合预期
def assert_response(response, expected_result):
    if expected_result is None:
        return True  # 如果没有定义预期结果，则不进行断言

    # 检查状态码
    if "status_code" in expected_result and response.status_code != expected_result["status_code"]:
        return False

    # 检查响应内容是否包含预期的关键字
    if "response_contains" in expected_result:
        try:
            response_json = response.json()
            if expected_result["response_contains"] not in json.dumps(response_json):
                return False
        except json.JSONDecodeError:
            if expected_result["response_contains"] not in response.text:
                return False

    return True

# 通用函数：发送请求并保存结果
def send_request(method, url, payload=None, headers=None, test_name="", expected_result=None):
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=payload, headers=headers)
        else:
            print(f"Unsupported HTTP method: {method}")
            return

        # 判断测试是否通过
        passed = assert_response(response, expected_result)

        # 保存测试结果
        save_result(test_name, response, payload, expected_result, passed)
        print(f"Test '{test_name}' completed. Status Code: {response.status_code}. Result: {'PASSED' if passed else 'FAILED'}")
    except requests.exceptions.RequestException as e:
        print(f"Test '{test_name}' failed. Error: {e}")
        with open("test_results.txt", "a", encoding="utf-8") as file:
            file.write(f"Test: {test_name}\n")
            file.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Error: {str(e)}\n")
            file.write("-" * 50 + "\n")

# 运行测试用例
def run_tests(config):
    base_url = config["base_url"]
    headers = config["headers"]

    for endpoint_name, endpoint_data in config["endpoints"].items():
        print(f"\n--- Testing {endpoint_name} ---")
        url = f"{base_url}{endpoint_data['route']}"
        method = endpoint_data["method"]

        # 如果有多个 payload，逐个测试
        if "payloads" in endpoint_data:
            for idx, payload in enumerate(endpoint_data["payloads"]):
                test_name = f"{endpoint_name} - Test Case {idx + 1}"
                expected_result = payload.get("expected_result", None)
                send_request(method, url, payload, headers, test_name, expected_result)
        else:
            # 没有 payload 的情况，例如 GET 请求
            test_name = f"{endpoint_name} - Normal"
            expected_result = endpoint_data.get("expected_result", None)
            send_request(method, url, headers=headers, test_name=test_name, expected_result=expected_result)

# 测试入口
if __name__ == "__main__":
    config = load_config()
    run_tests(config)
