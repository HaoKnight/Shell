# ================= 代码说明 =================
# 文件名: PotPlayer_OpenList_Merged.py
# 功能: 启动 PotPlayer 和 OpenList，并在 PotPlayer 关闭后关闭 OpenList 服务
# 作者: H_Knight
# 日期: 2026-01-09
# ===========================================

import subprocess
import time
import os
import json
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from ctypes import windll, byref, c_int, sizeof

# ================= 配置区域 =================
# 确定配置文件路径 (兼容打包后的 exe 环境)
if getattr(sys, 'frozen', False):
    # 如果是打包后的 exe，使用 exe 所在目录
    base_path = os.path.dirname(sys.executable)
else:
    # 如果是脚本直接运行，使用脚本所在目录
    base_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(base_path, "launcher_config.json")

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

def initial_setup_dialog(config):
    """
    弹出配置窗口，允许用户手动输入或选择路径
    如果是第一次运行或配置文件丢失，将会调用此函数
    """
    # 预读取当前配置，如果没有则为空字符串
    current_pot = config.get("potplayer_path", "")
    
    # (不再重置无效路径为空，而是保留并在后续界面中标记为红色)

    # 创建 GUI 主窗口 (tkinter)
    root = tk.Tk()
    root.title("PotPlayer Link OpenList    By：H_Knight")
    
    # --- Windows 11 风格优化 ---
    # 尝试开启 Windows 11 窗口圆角 (DWMWA_WINDOW_CORNER_PREFERENCE = 33, DWMWCP_ROUND = 2)
    try:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        VAL = c_int(2)
        windll.dwmapi.DwmSetWindowAttribute(c_int(root.winfo_id()), DWMWA_WINDOW_CORNER_PREFERENCE, byref(VAL), sizeof(VAL))
    except Exception:
        pass
    
    # 配置 ttk 样式
    style = ttk.Style()
    # 'vista' 主题在 Windows 上通常对应较现代的系统控件样式
    if 'vista' in style.theme_names():
        style.theme_use('vista')
    
    # 配置通用字体
    default_font = ("Microsoft YaHei", 9)
    style.configure(".", font=default_font)
    style.configure("TButton", font=default_font)
    style.configure("TLabel", font=default_font)
    style.configure("TEntry", font=default_font)

    # 计算屏幕中心位置，使窗口居中显示
    window_w, window_h = 600, 160                         # 窗口尺寸 (调整以适应更少的内容)
    screen_w = root.winfo_screenwidth()                   # 屏幕宽度
    screen_h = root.winfo_screenheight()                  # 屏幕高度
    x = (screen_w - window_w) // 2                        # 计算居中位置的 X 坐标
    y = (screen_h - window_h) // 2                        # 计算居中位置的 Y 坐标
    root.geometry(f"{window_w}x{window_h}+{x}+{y}")       # 设置窗口大小和位置
    
    # 禁止调整窗口大小，并保持窗口在最前端
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # 定义 tkinter 变量，用于绑定输入框内容
    pot_var = tk.StringVar(value=current_pot)
    
    # 创建布局容器 Frame
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Grid 网格布局配置，让输入框(column 1)自动拉伸
    frame.columnconfigure(1, weight=1)

    # --- 第一行: PotPlayer 设置 ---
    ttk.Label(frame, text="PotPlayer 路径:").grid(row=0, column=0, sticky="w", pady=5)
    e2 = tk.Entry(frame, textvariable=pot_var, font=("Microsoft YaHei", 9), relief="flat", bd=1, highlightthickness=1, highlightcolor="#0067C0")
    e2.grid(row=0, column=1, sticky="ew", padx=5, pady=5, ipady=4)
    
    # 如果初始路径无效且非空，显示为红色
    if current_pot and not os.path.exists(current_pot):
        e2.config(fg="#E81123")
    
    # 当用户修改时恢复黑色
    def on_pot_change(*args):
        e2.config(fg="#000000")
    pot_var.trace("w", on_pot_change)
    
    # PotPlayer 选择文件按钮的回调函数
    def sel_pot():
        p = filedialog.askopenfilename(title="选择 PotPlayer.exe", filetypes=[("Executable", "*.exe")])
        if p: pot_var.set(os.path.normpath(p)) # 规范化路径分隔符
    
    ttk.Button(frame, text="选择...", command=sel_pot).grid(row=0, column=2, padx=5, pady=5)

    # --- 说明文字 ---
    # 第一句红色提示
    ttk.Label(frame, text="请重新指定 PotPlayer 的执行文件路径 (.exe)", foreground="#E81123").grid(row=2, column=0, columnspan=3, pady=(5, 0), sticky="w")
    # 第二句黑色/深灰色说明
    ttk.Label(frame, text="注：指定后将自动保存配置并在下次直接运行,不再显示此窗口。", foreground="#6A6A6A").grid(row=3, column=0, columnspan=3, pady=(0, 5), sticky="w")

    # --- 底部按钮 ---
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=4, column=0, columnspan=3, pady=10)

    # 用于在闭包中保存结果状态
    result_state = {"saved": False}

    # "保存并启动" 按钮的回调函数
    def on_confirm():
        # 获取输入框内容并去除首尾空白和引号
        p2 = pot_var.get().strip().strip('"')
        
        err_msgs = []
        # 简单验证路径是否存在
        if not (p2 and os.path.exists(p2)):
            err_msgs.append("PotPlayer 路径无效或不存在。")
        if err_msgs:
            messagebox.showwarning("路径错误", "\n".join(err_msgs), parent=root)
            return

        # 更新配置字典
        config["potplayer_path"] = p2
        # 保存到本地 JSON 文件
        save_config(config)
        result_state["saved"] = True
        root.destroy() # 关闭窗口

    # "取消" 按钮的回调函数
    def on_cancel():
        root.destroy()

    # 放置按钮
    ttk.Button(btn_frame, text="保存并启动", command=on_confirm, width=15).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="取消", command=on_cancel, width=15).pack(side=tk.LEFT, padx=10)

    # 处理窗口右上角关闭按钮事件，等同于取消
    root.protocol("WM_DELETE_WINDOW", on_cancel)
    
    # 进入 GUI 事件循环，等待用户操作
    root.mainloop()
    
    # 返回保存状态：True 表示已保存配置可继续，False 表示用户取消
    return result_state["saved"]

def manage_service(action, service_name):
    """
    管理 Windows 服务 (需要管理员权限或足够权限)
    action: "start" | "stop"
    使用 net start / net stop 命令
    """
    try:
        cmd = f"net {action} {service_name}"
        
        # 尝试隐藏控制台窗口 (针对 Windows)
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
        print(f"[-] 已执行服务命令: {cmd}")
    except Exception as e:
        print(f"[!] 执行服务命令 {cmd} 时发生错误: {e}")

def main():
    # 1. 加载配置
    config = load_config()
    
    # 2. 验证路径 (如果路径缺失或无效，则统一弹出设置窗口)
    potplayer_path = config.get("potplayer_path", "")
    # alist_helper_path 已经不需要了

    is_pot_valid = potplayer_path and os.path.exists(potplayer_path)

    if not is_pot_valid:
        # 路径无效，弹出配置窗口进行设置
        success = initial_setup_dialog(config)
        if not success:
            sys.exit(0) # 用户取消或关闭窗口
            
        # 重新从更新后的配置中获取路径
        potplayer_path = config.get("potplayer_path")

    try:
        # 3. 启动 OpenList Desktop Service
        service_name = "openlist_desktop_service"
        print(f"[+] 正在启动服务: {service_name}")
        manage_service("start", service_name)
        
        # 等待几秒钟，确保服务启动
        time.sleep(0.1)

        # 4. 启动 PotPlayer
        print(f"[+] 正在启动 PotPlayer: {potplayer_path}")
        potplayer_process = subprocess.Popen(potplayer_path, cwd=os.path.dirname(potplayer_path))

        print(f"[*] PotPlayer (PID: {potplayer_process.pid}) 运行中... 脚本正在监控状态")
        
        # 5. 阻塞等待 PotPlayer 关闭
        potplayer_process.wait()

        print("\n[*] 检测到 PotPlayer 已关闭")

    except KeyboardInterrupt:
        print("\n[!] 用户中断操作")
    except Exception as e:

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror("运行错误", f"程序运行过程中发生错误:\n{e}")
        root.destroy()
    finally:
        # 6. 执行清理操作 (关闭服务)
        print("\n[+] 正在关闭服务...")
        manage_service("stop", "openlist_desktop_service")
        
        print("[*] 全部完成，脚本退出。")
        time.sleep(1)

if __name__ == "__main__":
    def is_admin():
        try:
            return windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
        main()
    else:
        # 以管理员权限重新运行程序
        if getattr(sys, 'frozen', False):
             #针对已编译的 exe（pyinstaller --onefile 等）
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
        else:
             # 用于 Python 脚本
            windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1)

