# https://github.com/systemt1st
import os
import re
import random
import string
import threading
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from playwright.sync_api import Playwright, sync_playwright, expect
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import time
import subprocess

# 添加一个全局锁和计数器
dial_lock = threading.Lock()
processed = 0
dial_event = threading.Event()


def try_click_element(page: Page, selector: str, selector_type: str = "css", timeout: int = 5000):
    try:
        if selector_type == "css":
            element = page.locator(selector)
        elif selector_type == "xpath":
            element = page.locator(f"xpath={selector}")
        elif selector_type == "text":
            element = page.get_by_text(selector)
        elif selector_type == "role":
            role, name = selector.split(',')
            element = page.get_by_role(role, name=name)
        elif selector_type == "test_id":
            element = page.get_by_test_id(selector)
        else:
            raise ValueError(f"Unsupported selector type: {selector_type}")

        if element.is_visible(timeout=timeout):
            element.click()
            print(f"成功点击元素: {selector}")
        else:
            print(f"元素不可见，跳过点击: {selector}")
    except PlaywrightTimeoutError:
        print(f"等待元素超时，跳过点击: {selector}")
    except PlaywrightError as e:
        print(f"Playwright错误，跳过点击: {selector}, 错误: {str(e)}")
    except Exception as e:
        print(f"尝试点击元素时发生未知错误: {selector}, 错误: {str(e)}")


def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_email():
    username = generate_random_string(random.randint(9, 12))
    return f"{username}@gmail.com"


def generate_name():
    return generate_random_string(random.randint(9, 12))


def generate_password():
    return generate_random_string(random.randint(10, 12)) + "1@"


def get_credentials():
    connection_name = '宽带连接'
    username = '12205658'
    password = '204296'
    print(f"{connection_name}-{username}-{password}")
    return (connection_name, username, password)


def dial(connection_info):
    connection_name, username, password = connection_info
    try:
        print(f"开始拨号过程...")
        print(f"正在断开当前连接: {connection_name}...")
        result = subprocess.run(["rasdial", connection_name, "/disconnect"], capture_output=True, text=True)
        print(f"断开连接命令输出: {result.stdout}")
        if result.returncode != 0:
            print(f"断开连接错误: {result.stderr}")
        print("断开连接命令已执行，等待 5 秒...")
        time.sleep(5)

        print(f"正在拨号更换IP... 使用账号: {username}")
        result = subprocess.run(["rasdial", connection_name, username, password], capture_output=True, text=True)
        print(f"拨号命令输出: {result.stdout}")
        if result.returncode != 0:
            print(f"拨号错误: {result.stderr}")
        print("拨号命令已执行，等待 5 秒...")
        time.sleep(5)
        print("IP已更换,准备开始处理账号...")
    except Exception as e:
        print(f"拨号过程中出错: {str(e)}")
    finally:
        dial_event.set()  # 拨号完成，设置事件


def process_account(connection_info):
    global processed

    # 等待拨号完成
    dial_event.wait()

    with dial_lock:
        processed += 1
        current_process = processed

    email = generate_email()
    name = generate_name()
    password = generate_password()

    print(f"开始处理第 {current_process} 个账号: {email}")

    try:
        with sync_playwright() as playwright:
            browser = playwright.firefox.launch(headless=False, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()

            try:
                print(f"开始: {email}")
                page.goto("https://vimeo.com/")
                page.goto("https://vimeo.com/")
                page.get_by_role("banner").get_by_role("button", name="Join").click()

                page.frame_locator("#modal-root iframe").get_by_placeholder("you@email.com").click()
                page.frame_locator("#modal-root iframe").get_by_placeholder("you@email.com").fill(email)
                page.frame_locator("#modal-root iframe").get_by_role("button", name="Continue with email").click()

                page.frame_locator("#modal-root iframe").get_by_placeholder("First and last name").click()
                page.frame_locator("#modal-root iframe").get_by_placeholder("First and last name").fill(name)

                page.frame_locator("#modal-root iframe").get_by_placeholder("Password").click()
                page.frame_locator("#modal-root iframe").get_by_placeholder("Password").fill(password)

                page.frame_locator("#modal-root iframe").get_by_test_id("join-continue-button").click()

                if page.locator("text=Sorry, you have made too many requests in a short period of time.").is_visible():
                    print(f"账号 {email} 遇到请求限制,跳过此账号")
                    return None

                page.wait_for_timeout(5000)
                try_click_element(page, "button,Close", "role")
                try_click_element(page, "close-upsell-button", "test_id")

                page.goto("https://vimeo.com/home")
                all_cookies = context.cookies()
                vimeo_cookies = [cookie for cookie in all_cookies if '.vimeo.com' in cookie['domain']]
                cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in vimeo_cookies])
                with open('cookies.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{cookie_string}\n")

                with open('zhanghao.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{email}----{name}----{password}\n")
                print(f"成功----{email}")
                return cookie_string

            except PlaywrightError as e:
                print(f"处理账号 {email} 时遇到 Playwright 错误: {str(e)}")
                return None
            except Exception as e:
                print(f"处理账号 {email} 时遇到未知错误: {str(e)}")
                return None
            finally:
                context.close()
                browser.close()
    except Exception as e:
        print(f"创建 Playwright 实例时遇到错误: {str(e)}")
        return None


def process_batch(connection_info, num_threads, start, end, dial_frequency):
    global processed
    processed = start

    if start % dial_frequency == 0:
        dial_event.clear()  # 清除拨号事件
        dial(connection_info)  # 在需要时进行拨号
    else:
        dial_event.set()  # 如果不需要拨号，直接设置事件

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_account, connection_info) for _ in range(start, end)]
        wait(futures, return_when=ALL_COMPLETED)


def main():
    num_accounts = int(input("请输入要处理的账号数量: "))
    num_threads = int(input("请输入线程数: "))
    dial_frequency = int(input("请输入拨号频率 (处理多少个账号后拨号一次): "))

    connection_info = get_credentials()

    print("开始处理账号...")

    for i in range(0, num_accounts, num_threads):
        end = min(i + num_threads, num_accounts)
        print(f"处理第 {i + 1} 到第 {end} 个账号")
        process_batch(connection_info, num_threads, i, end, dial_frequency)

    print("所有账号处理完成")


if __name__ == "__main__":
    main()
