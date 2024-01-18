import subprocess as sb

sb.call("g++ -std=c++17 -o cpp/debug.exe cpp/debug.cpp", shell=True)
sb.call("./cpp/debug.exe", shell=True)
