import subprocess as sb
import sys

args = sys.argv
name = args[1].split(".")[0]
sb.call("g++ -o {0}.exe {0}.cpp -D_LOCAL".format(name), shell=True)
sb.call("./{0}.exe".format(name), shell=True)
