#!/usr/bin/env python3

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

# 如果没有config.json文件，那么默认使用服务器上最新版本并自动创建config.json文件
# 也可以手动创建一个并填上期望的版本号
# config.json
# {
#     "normandy_version": "202505190230",
#     "assistant_version": "1.0.8",
#     "xrlink_version": "1.0.8"
# }
#
# 下载的文件在downloaded目录下
# -rw-rw-r-- 1 peter peter  24455215 May 19 16:08 Assistant_1.0.8_202505190000_debug.apk
# -rw-rw-r-- 1 peter peter 159733967 May 19 16:07 Launcher_1.0_20250519_0230_debug.apk
# -rw-rw-r-- 1 peter peter  43458099 May 19 16:08 translator-debug.apk
# -rw-rw-r-- 1 peter peter  13732361 May 19 16:08 xrlinkapp_1.0.8-202505161720-debug.apk
#


CONFIG_FILE = "config.json"

MAIN_URL = "https://package.xjsdtech.com/daily/app/normandy/main/"
ASSISTANT_MASTER_URL = "https://package.xjsdtech.com/daily/app/assistant/master/"
XR_LINK_MASTER_URL = "https://package.xjsdtech.com/daily/app/xrlink/master/"

SUB_PATHS = {
    "launcher/debug/": "Launcher_",
    "translator/debug/": "translator"
}

DOWNLOAD_DIR = "./downloaded"


# ----------- HTML解析 -----------

class DirectoryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.subdirs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    # 目录名为12位数字（时间戳格式）
                    if value.endswith('/') and value[:-1].isdigit() and len(value[:-1]) == 12:
                        self.subdirs.append(value[:-1])


class VersionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.subdirs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    # 目录名为版本号格式，如1.0.5
                    if value.endswith('/') and all(c.isdigit() or c == '.' for c in value[:-1]):
                        self.subdirs.append(value[:-1])


class FileParser(HTMLParser):
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attr, value) in attrs:
                if attr == 'href' and value.startswith(self.prefix):
                    self.links.append(value)


# ----------- 获取最新版本 -----------

def get_latest_time_from_main():
    try:
        with urllib.request.urlopen(MAIN_URL) as response:
            html = response.read().decode('utf-8')

        parser = DirectoryParser()
        parser.feed(html)

        valid_times = []
        for t in parser.subdirs:
            try:
                datetime.strptime(t, "%Y%m%d%H%M")
                valid_times.append(t)
            except ValueError:
                continue

        return max(valid_times) if valid_times else None

    except Exception as e:
        print(f"无法获取最新 normandy 目录：{e}")
        return None


def get_latest_version_from_assistant_master():
    try:
        with urllib.request.urlopen(ASSISTANT_MASTER_URL) as response:
            html = response.read().decode('utf-8')

        parser = VersionParser()
        parser.feed(html)

        if not parser.subdirs:
            return None
        return sorted(parser.subdirs)[-1]

    except Exception as e:
        print(f"无法获取 assistant master 版本列表：{e}")
        return None


def get_latest_version_from_xrlink_master():
    try:
        with urllib.request.urlopen(XR_LINK_MASTER_URL) as response:
            html = response.read().decode('utf-8')

        parser = VersionParser()
        parser.feed(html)

        if not parser.subdirs:
            return None
        return sorted(parser.subdirs)[-1]

    except Exception as e:
        print(f"无法获取 xrlink master 版本列表：{e}")
        return None


# ----------- 读写配置 -----------

def read_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败：{e}")
        return {}


def write_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"写配置文件失败：{e}")


# ----------- 下载进度 -----------

def download_progress_hook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size) if total_size > 0 else 0
    percent = min(100, percent)
    bar_length = 30
    filled_length = int(bar_length * percent // 100)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    print(f"\r下载进度: |{bar}| {percent}%", end='')
    if percent == 100:
        print()


# ----------- 下载文件 -----------

def download_file_from_subdir(base_url, prefix, save_dir):
    try:
        with urllib.request.urlopen(base_url) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        print(f"[{base_url}] 访问失败：{e}")
        return None

    parser = FileParser(prefix)
    parser.feed(html)

    if parser.links:
        first_file = parser.links[0]
        local_filename = os.path.join(save_dir, os.path.basename(first_file))

        if os.path.exists(local_filename):
            print(f"文件已存在，跳过下载：{local_filename}")
            return local_filename

        file_url = urllib.request.urljoin(base_url, first_file)

        print(f"在 [{base_url}] 中发现文件：{first_file}")
        print(f"正在下载：{file_url}")

        try:
            urllib.request.urlretrieve(file_url, local_filename, reporthook=download_progress_hook)
            print(f"下载完成：{local_filename}")
            return local_filename
        except Exception as e:
            print(f"下载失败：{e}")
            return None
    else:
        print(f"[{base_url}] 中未找到以 {prefix} 开头的文件。")
        return None


# ----------- 批量下载所有需要的文件 -----------

def download_all():
    config = read_config()

    # normandy 版本号，格式 YYYYMMDDHHMM
    normandy_version = config.get("normandy_version")
    if normandy_version:
        try:
            datetime.strptime(normandy_version, "%Y%m%d%H%M")
        except ValueError:
            print("配置文件中 normandy_version 格式错误，应为 YYYYMMDDHHMM，自动抓取最新。")
            normandy_version = None
    if not normandy_version:
        normandy_version = get_latest_time_from_main()
        if not normandy_version:
            print("未能从服务器获取最新 normandy 目录")
            return []
        print(f"未指定 normandy 版本，自动使用最新时间目录：{normandy_version}")
        config['normandy_version'] = normandy_version
    else:
        print(f"从配置文件读取 normandy 版本：{normandy_version}")

    # assistant 版本号，类似 1.0.5
    assistant_version = config.get("assistant_version")
    if not assistant_version:
        assistant_version = get_latest_version_from_assistant_master()
        if not assistant_version:
            print("未能获取 assistant master 版本号")
            return []
        print(f"未指定 assistant 版本，自动使用最新版本：{assistant_version}")
        config['assistant_version'] = assistant_version
    else:
        print(f"从配置文件读取 assistant 版本：{assistant_version}")

    # xrlink 版本号，类似 1.0.8
    xrlink_version = config.get("xrlink_version")
    if not xrlink_version:
        xrlink_version = get_latest_version_from_xrlink_master()
        if not xrlink_version:
            print("未能获取 xrlink master 版本号")
            return []
        print(f"未指定 xrlink 版本，自动使用最新版本：{xrlink_version}")
        config['xrlink_version'] = xrlink_version
    else:
        print(f"从配置文件读取 xrlink 版本：{xrlink_version}")

    write_config(config)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    downloaded_files = []

    # normandy launcher 和 translator
    for sub_path, prefix in SUB_PATHS.items():
        target_url = f"{MAIN_URL}{normandy_version}/{sub_path}"
        file_path = download_file_from_subdir(target_url, prefix, DOWNLOAD_DIR)
        if file_path:
            downloaded_files.append(file_path)

    # assistant
    assistant_url = f"{ASSISTANT_MASTER_URL}{assistant_version}/debug/"
    f = download_file_from_subdir(assistant_url, "Assistant_", DOWNLOAD_DIR)
    if f:
        downloaded_files.append(f)

    # xrlink
    xrlink_url = f"{XR_LINK_MASTER_URL}{xrlink_version}/debug/"
    f = download_file_from_subdir(xrlink_url, "xrlinkapp_", DOWNLOAD_DIR)
    if f:
        downloaded_files.append(f)

    return downloaded_files


def calculate_md5(file_path, chunk_size=8192):
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"无法计算 {file_path} 的 MD5: {e}")
        return None


# ----------- adb设备检测和安装 -----------

def check_devices():
    result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    devices = []
    for line in result.stdout.splitlines()[1:]:
        if line.strip() and 'device' in line:
            devices.append(line.split()[0])
    return devices


def choose_device(devices):
    if len(devices) == 0:
        print("没有连接的设备！请连接设备后重试。")
        sys.exit(1)
    elif len(devices) == 1:
        print(f"检测到一个设备，使用设备：{devices[0]}")
        return devices[0]
    else:
        print("检测到多个设备：")
        for i, d in enumerate(devices):
            print(f"{i + 1}: {d}")
        while True:
            choice = input("请输入要使用的设备序列号或编号：").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    return devices[idx]
            elif choice in devices:
                return choice
            print("输入无效，请重新输入。")


def adb_sync_and_reboot(device_serial):
    try:
        print("执行 adb shell sync ...")
        subprocess.run(['adb', '-s', device_serial, 'shell', 'sync'], check=True)

    except subprocess.CalledProcessError as e:
        print("sync失败:", e)

    try:
        print("尝试执行 adb shell reboot ...")
        subprocess.run(['adb', '-s', device_serial, 'shell', 'reboot'], capture_output=True, text=True)
        print("设备正在重启...")
    except subprocess.CalledProcessError as e:
        print("err", e)


def adb_install(apk_path, device_serial):
    try:
        cmd = ['adb', '-s', device_serial, 'install', '-r', apk_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("安装成功！")
        else:
            print("安装失败！")
            print("错误信息:", result.stderr)
    except FileNotFoundError:
        print("找不到 adb 命令，请确认 adb 已安装且在系统 PATH 中。")
    except Exception as e:
        print("执行 adb 安装时出错:", e)


def adb_push_to_dir(local_path, remote_dir, device_serial):
    file_name = os.path.basename(local_path)
    remote_dir = remote_dir.rstrip("/")
    remote_path = f"{remote_dir}/{file_name}"

    print(f"准备处理设备目录: {remote_dir}")

    try:
        # 1. 创建目录
        mkdir_cmd = f'adb -s {device_serial} shell "su 0 sh -c \\"mkdir -p {remote_dir}\\""'
        print(f"创建目录命令: {mkdir_cmd}")
        subprocess.run(mkdir_cmd, shell=True)

        # 2. 清空目录
        rm_cmd = f'adb -s {device_serial} shell "su 0 sh -c \\"rm -rf {remote_dir}/*\\""'
        print(f"清空目录命令: {rm_cmd}")
        rm_result = subprocess.run(rm_cmd, shell=True, capture_output=True, text=True)
        if rm_result.returncode != 0:
            print("删除远程目录内容失败:")
            print(rm_result.stderr)
            return

        # 3. 推送文件
        push_cmd = ['adb', '-s', device_serial, 'push', local_path, remote_path]
        print(f"执行推送命令: {' '.join(push_cmd)}")
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"推送成功: {local_path} -> {remote_path}")
        else:
            print(f"推送失败: {local_path}")
            print("错误信息:", result.stderr)

    except Exception as e:
        print("执行 adb push 时出错:", e)


def adb_push_to_dir2(local_path, remote_dir, device_serial):
    file_name = os.path.basename(local_path)
    remote_dir = remote_dir.rstrip("/")
    remote_path = f"{remote_dir}/{file_name}"

    print(f"准备处理设备目录: {remote_dir}")

    try:
        # 创建目录（如果不存在）
        mkdir_cmd = [
            'adb', '-s', device_serial,
            'shell', 'su', '-c',
            f'"mkdir -p {remote_dir}"'
        ]
        print(f"创建目录命令: {' '.join(mkdir_cmd)}")
        subprocess.run(" ".join(mkdir_cmd), shell=True)

        # 清空目录内容
        rm_cmd = [
            'adb', '-s', device_serial,
            'shell', 'su', '-c',
            f'"rm -rf {remote_dir}/*"'
        ]
        print(f"清空目录命令: {' '.join(rm_cmd)}")
        rm_result = subprocess.run(" ".join(rm_cmd), shell=True, capture_output=True, text=True)
        if rm_result.returncode != 0:
            print("删除远程目录内容失败:")
            print(rm_result.stderr)
            return

        # 推送文件
        push_cmd = ['adb', '-s', device_serial, 'push', local_path, remote_path]
        print(f"执行推送命令: {' '.join(push_cmd)}")
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"推送成功: {local_path} -> {remote_path}")
        else:
            print(f"推送失败: {local_path}")
            print("错误信息:", result.stderr)

    except Exception as e:
        print("执行 adb push 时出错:", e)


def run_cmd(cmd, capture_output=True, check=False):
    return subprocess.run(cmd, capture_output=capture_output, text=True, shell=False, check=check)


def wait_for_device(device_serial, timeout=120):
    print("等待设备重新连接...")
    start = time.time()
    while time.time() - start < timeout:
        result = run_cmd(['adb', '-s', device_serial, 'get-state'])
        if result.stdout.strip() == 'device':
            print("设备已连接")
            return True
        time.sleep(2)
    print("等待设备连接超时")
    return False


def prepare_device(device_serial):
    # adb root
    print("执行 adb root ...")
    result = run_cmd(['adb', '-s', device_serial, 'root'])
    print(result.stdout.strip())
    if 'adbd cannot run as root' in result.stdout or 'adbd cannot run as root' in result.stderr:
        print("设备不支持 adb root，继续尝试 remount")

    # adb remount
    print("执行 adb remount ...")
    remount = run_cmd(['adb', '-s', device_serial, 'remount'])
    out = remount.stdout.lower() + remount.stderr.lower()
    print(remount.stdout.strip())
    print(remount.stderr.strip())

    if remount.returncode != 0 or ('not allowed' in out or 'remount failed' in out or 'permission denied' in out):
        print("remount 失败，尝试重启设备...")

        # 重启设备
        reboot = run_cmd(['adb', '-s', device_serial, 'reboot'])
        if reboot.returncode != 0:
            print("重启命令失败:", reboot.stderr)
            return False

        # 等待设备重启上线
        if not wait_for_device(device_serial):
            return False

        # 设备重启后，尝试再次 adb root 和 remount
        print("设备重启后再次执行 adb root ...")
        run_cmd(['adb', '-s', device_serial, 'root'])
        print("设备重启后再次执行 adb remount ...")
        remount = run_cmd(['adb', '-s', device_serial, 'remount'])
        if remount.returncode != 0:
            print("重启后 remount 仍然失败")
            return False

    print("设备准备完成")
    return True


def run_update_install_process():
    print("开始下载更新文件...")
    downloaded_files = download_all()
    if not downloaded_files:
        print("没有文件下载，退出。")
        return False

    print("\n下载完成，准备安装 APK。\n")

    apk_files = [f for f in downloaded_files if f.lower().endswith(".apk")]
    if not apk_files:
        print("没有找到下载的 APK 文件，退出。")
        return False

    devices = check_devices()
    device = choose_device(devices)

    if prepare_device(device):
        print("执行后续 adb 命令")
        for apk_path in apk_files:
            file_name = os.path.basename(apk_path)
            print(f"\n处理文件: {file_name}")

            if file_name.startswith("Launcher_"):
                print(f"执行安装: {apk_path}  ,MD5: {calculate_md5(apk_path)}")
                adb_install(apk_path, device)
            elif file_name.startswith("translator"):
                print(f"执行安装: {apk_path}  ,MD5: {calculate_md5(apk_path)}")
                adb_install(apk_path, device)
            elif file_name.startswith("xrlinkapp"):
                print(f"执行push: {apk_path}  ,MD5: {calculate_md5(apk_path)}")
                adb_push_to_dir(apk_path, "/system_ext/app/xrlinkapp", device)

            elif file_name.startswith("Assistant_"):
                print(f"执行push: {apk_path}  ,MD5: {calculate_md5(apk_path)}")
                adb_push_to_dir(apk_path, "/system/app/Assistant", device)
            else:
                print("未识别的 APK 类型，跳过。")

        adb_sync_and_reboot(device)
    else:
        print("设备准备失败，无法继续操作")
        return False

    return True


if __name__ == "__main__":
    success = run_update_install_process()
    if not success:
        sys.exit(1)
