@echo off
chcp 65001 >nul 2>&1
:: 启动AlistHelper（通过快捷方式）
start "" "C:\Users\haoxi\AppData\Local\Programs\AlistHelper\alisthelper.exe" autostart
:: 启动PotPlayer并等待其关闭（通过快捷方式）
start "" /wait "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PotPlayer\PotPlayer 64 bit.lnk"
:: PotPlayer关闭后，依次关闭AlistHelper、alist.exe、Rclone进程
taskkill /f /im AlistHelper.exe >nul 2>&1
taskkill /f /im alist.exe >nul 2>&1
taskkill /f /im Rclone.exe >nul 2>&1
exit