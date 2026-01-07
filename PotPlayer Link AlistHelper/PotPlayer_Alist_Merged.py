# ================= 代码说明 =================
# 文件名: PotPlayer_Alist_Merged copy.py
# 功能: 启动 PotPlayer 和 AlistHelper，并在 PotPlayer 关闭后清理相关进程
# 作者: H_Knight
# 日期: 2024-06
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

def initial_setup_dialog(config):
    """
    弹出配置窗口，允许用户手动输入或选择路径
    如果是第一次运行或配置文件丢失，将会调用此函数
    """
    # 预读取当前配置，如果没有则为空字符串
    current_alist = config.get("alist_helper_path", "")
    current_pot = config.get("potplayer_path", "")
    
    # (不再重置无效路径为空，而是保留并在后续界面中标记为红色)

    # 创建 GUI 主窗口 (tkinter)
    root = tk.Tk()
    root.title("路径配置 - PotPlayer & AlistHelper")
    
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
    window_w, window_h = 600, 200                         # 窗口尺寸 (稍微调高一点适应 padding)
    screen_w = root.winfo_screenwidth()                   # 屏幕宽度
    screen_h = root.winfo_screenheight()                  # 屏幕高度
    x = (screen_w - window_w) // 2                        # 计算居中位置的 X 坐标
    y = (screen_h - window_h) // 2                        # 计算居中位置的 Y 坐标
    root.geometry(f"{window_w}x{window_h}+{x}+{y}")       # 设置窗口大小和位置
    
    # 禁止调整窗口大小，并保持窗口在最前端
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # 定义 tkinter 变量，用于绑定输入框内容
    alist_var = tk.StringVar(value=current_alist)
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

    # --- 第二行: AlistHelper 设置 ---
    ttk.Label(frame, text="AlistHelper 路径:").grid(row=1, column=0, sticky="w", pady=5)
    e1 = tk.Entry(frame, textvariable=alist_var, font=("Microsoft YaHei", 9), relief="flat", bd=1, highlightthickness=1, highlightcolor="#0067C0")
    e1.grid(row=1, column=1, sticky="ew", padx=5, pady=5, ipady=4)
    
    # 如果初始路径无效且非空，显示为红色
    if current_alist and not os.path.exists(current_alist):
        e1.config(fg="#E81123")
        
    # 当用户修改时恢复黑色
    def on_alist_change(*args):
        e1.config(fg="#000000")
    alist_var.trace("w", on_alist_change)
    
    # AlistHelper 选择文件按钮的回调函数
    def sel_alist():
        p = filedialog.askopenfilename(title="选择 AlistHelper.exe", filetypes=[("Executable", "*.exe")])
        if p: alist_var.set(os.path.normpath(p))
    
    ttk.Button(frame, text="选择...", command=sel_alist).grid(row=1, column=2, padx=5, pady=5)
    
    # --- 第三行: 说明文字 ---
    # 第一句红色提示
    ttk.Label(frame, text="请重新指定错误程序的执行文件路径 (.exe)", foreground="#E81123").grid(row=2, column=0, columnspan=3, pady=(5, 0), sticky="w")
    # 第二句黑色/深灰色说明
    ttk.Label(frame, text="指定后将自动保存配置并在下次直接运行。", foreground="#555555").grid(row=3, column=0, columnspan=3, pady=(0, 5), sticky="w")

    # --- 第四行: 底部按钮 ---
    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=4, column=0, columnspan=3, pady=5)

    # 用于在闭包中保存结果状态
    result_state = {"saved": False}

    # "保存并启动" 按钮的回调函数
    def on_confirm():
        # 获取输入框内容并去除首尾空白和引号
        p1 = alist_var.get().strip().strip('"') 
        p2 = pot_var.get().strip().strip('"')
        
        err_msgs = []
        # 简单验证路径是否存在
        if not (p1 and os.path.exists(p1)):
            err_msgs.append("AlistHelper 路径无效或不存在。")
        if not (p2 and os.path.exists(p2)):
            err_msgs.append("PotPlayer 路径无效或不存在。")
        if err_msgs:
            messagebox.showwarning("路径错误", "\n".join(err_msgs), parent=root)
            return

        # 更新配置字典
        config["alist_helper_path"] = p1
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
    
    # 2. 验证路径 (如果路径缺失或无效，则统一弹出设置窗口)
    potplayer_path = config.get("potplayer_path", "")
    alist_helper_path = config.get("alist_helper_path", "")

    is_pot_valid = potplayer_path and os.path.exists(potplayer_path)
    is_alist_valid = alist_helper_path and os.path.exists(alist_helper_path)

    if not (is_pot_valid and is_alist_valid):
        # 任意一个路径无效，弹出配置窗口进行设置
        success = initial_setup_dialog(config)
        if not success:
            sys.exit(0) # 用户取消或关闭窗口
            
        # 重新从更新后的配置中获取路径
        potplayer_path = config.get("potplayer_path")
        alist_helper_path = config.get("alist_helper_path")

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
