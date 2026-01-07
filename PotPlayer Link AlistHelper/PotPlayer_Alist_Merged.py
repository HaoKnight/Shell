import subprocess
import time
import os
import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

# ================= 配置区域 =================
# 默认路径（如果配置文件中没有，将使用这些默认值）
DEFAULT_POTPLAYER = r"  "  #  PotPlayer.exe 的默认路径
DEFAULT_ALIST_HELPER = r"  "  #  AlistHelper.exe 的默认路径
# ===========================================

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher_config.json")

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"无法保存配置: {e}")

def get_valid_path(current_path, key_name, display_name, config):
    """
    检查路径是否存在，如果不存在则弹出文件选择框让用户重新选择。
    并自动更新配置文件。
    """
    while True:
        if current_path and os.path.exists(current_path):
            return current_path
        
        # 路径不存在，初始化 tkinter 环境用于弹窗
        root = tk.Tk()
        root.withdraw() # 隐藏主窗口
        root.attributes("-topmost", True) # 确保弹窗在最前
        
        # 提示用户
        msg = f"错误: 找不到路径 [{display_name}]。 \n\n请点击【确定】手动选择正确的 .exe 文件路径。"
        user_response = messagebox.askokcancel(f"配置错误 - [{display_name}]", msg)
        
        if not user_response:
            # 用户点击取消，退出程序
            root.destroy()
            sys.exit(0)
            
        # 弹出文件选择框
        new_path = filedialog.askopenfilename(
            title=f"请选择 [{display_name}] 的执行文件",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
            initialdir=os.path.dirname(current_path) if current_path and os.path.dirname(current_path) else None
        )
        
        root.destroy()
        
        if new_path:
            # 用户选择了新路径
            current_path = os.path.normpath(new_path)
            config[key_name] = current_path
            save_config(config)
        else:
            # 用户在文件选择框点了取消，退出程序
            sys.exit(0)

def kill_process(process_name):
    """
    使用 taskkill 命令强制结束指定名称的进程
    """
    try:
        # stdout=subprocess.DEVNULL 也就是不显示输出信息，保持控制台清爽
        subprocess.run(f'taskkill /F /IM "{process_name}" /T', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[-] 已尝试结束进程: {process_name}")
    except Exception as e:
        print(f"[!] 结束进程 {process_name} 时发生错误: {e}")

def main():
    # 1. 加载配置
    config = load_config()
    
    # 2. 获取并验证路径 (优先使用配置文件的，否则使用默认)
    potplayer_path = config.get("potplayer_path", DEFAULT_POTPLAYER)
    alist_helper_path = config.get("alist_helper_path", DEFAULT_ALIST_HELPER)
    
    # 验证 AlistHelper 路径
    alist_helper_path = get_valid_path(alist_helper_path, "alist_helper_path", "AlistHelper", config)
    
    # 验证 PotPlayer 路径
    potplayer_path = get_valid_path(potplayer_path, "potplayer_path", "PotPlayer", config)

    try:
        # 3. 启动 AlistHelper
        print(f"[+] 正在启动 AlistHelper: {alist_helper_path}")
        # 添加 "-autostart" 参数以实现静默启动/自动开始
        subprocess.Popen([alist_helper_path, "autostart"], cwd=os.path.dirname(alist_helper_path))
        
        # 等待几秒钟，确保 AlistHelper 和其调用的 alist/rclone 已经启动准备好
        time.sleep(0.1)

        # 4. 启动 PotPlayer
        print(f"[+] 正在启动 PotPlayer: {potplayer_path}")
        potplayer_process = subprocess.Popen(potplayer_path, cwd=os.path.dirname(potplayer_path))

        print(f"[*] PotPlayer (PID: {potplayer_process.pid}) 运行中... 脚本正在监控状态")
        
        # 5. 阻塞等待 PotPlayer 关闭
        potplayer_process.wait()

        print("\n[*] 检测到 PotPlayer 已关闭")

    except Exception as e:
        # 运行时发生其他未知错误，弹窗提示
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("运行错误", f"程序运行过程中发生错误:\n{e}")
        root.destroy()
    finally:
        # 6. 执行清理操作
        print("\n[+] 开始清理相关进程...")
        kill_process("AlistHelper.exe")
        kill_process("alist.exe")
        kill_process("rclone.exe")
        
        print("[*] 全部完成，脚本退出。")
        time.sleep(1)

if __name__ == "__main__":
    main()
