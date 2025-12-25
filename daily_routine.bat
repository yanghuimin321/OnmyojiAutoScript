@echo off
REM 切换目录
cd /d "D:\software\MuMu Player 12\nx_main"

REM 打开模拟器
MuMuManager.exe control -v 0 launch

REM 等待一分钟
timeout /t 60

REM 连接模拟器
adb.exe connect 127.0.0.1:16384

REM 设置PYTHONPATH
set PYTHONPATH=D:\Projects\git\github\OnmyojiAutoScript

REM 切换目录
cd /d D:\Projects\git\github\OnmyojiAutoScript\tasks\Nikki_restart

REM 使用项目虚拟环境的解释器来执行 Python 脚本
D:\Projects\git\github\OnmyojiAutoScript\.venv\Scripts\python.exe script_task.py

REM 切换目录
cd /d D:\Projects\git\github\OnmyojiAutoScript\tasks\Nikki_daily

REM 使用项目虚拟环境的解释器来执行 Python 脚本
D:\Projects\git\github\OnmyojiAutoScript\.venv\Scripts\python.exe script_task.py

REM 暂停，以便查看输出
pause