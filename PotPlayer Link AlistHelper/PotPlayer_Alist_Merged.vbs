' 创建 WScript.Shell 对象以运行命令
Set ws = WScript.CreateObject("WScript.Shell")

' 启动 AlistHelper：1=显示窗口，False=不等待程序结束立即执行下一行
ws.Run """C:\Users\haoxi\AppData\Local\Programs\AlistHelper\alisthelper.exe"" autostart", 1, False

' 启动 PotPlayer：1=显示窗口，True=脚本暂停等待 PotPlayer 关闭
ws.Run """C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PotPlayer\PotPlayer 64 bit.lnk""", 1, True

' PotPlayer 关闭后执行：强制结束 AlistHelper 进程，0=隐藏窗口
ws.Run "taskkill /f /im AlistHelper.exe", 0, True

' 强制结束 alist 进程，避免后台残留
ws.Run "taskkill /f /im alist.exe", 0, True

' 强制结束 Rclone 进程，清理挂载服务
ws.Run "taskkill /f /im Rclone.exe", 0, True
