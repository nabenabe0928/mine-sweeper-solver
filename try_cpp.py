import subprocess as sb

sb.call("g++ -std=c++17 -o cpp/solver.exe cpp/solver.cpp", shell=True)
sb.call("./cpp/solver.exe", shell=True)
