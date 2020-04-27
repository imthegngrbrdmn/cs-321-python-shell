import os
import curses
from curses import wrapper
import subprocess
from pathlib import Path
import sys
import shlex

def exec_cmd(command,scr):
    if "|" in command:
        s_in, s_out = (0,0)
        s_out = os.dup(1)
        s_in = os.dup(0)
        fd_in = os.dup(s_in)
        for cmd in command.split("|"):
            os.dup2(fd_in,0)
            os.close(fd_in)
            if cmd == command.split("|")[-1]:
                f_out = open('output.txt','w')
                try:
                    subprocess.run(cmd.strip().split(),stdout=f_out)
                except Exception:
                    scr.addstr("shell: command not found: {}".format(cmd))
                f_out.close()
            else:
                fd_in,fd_out=os.pipe()
                os.dup2(fd_out,1)
                os.close(fd_out)
                try:
                    subprocess.run(cmd.strip().split())
                except Exception:
                    scr.addstr("shell: command not found{}".format(cmd.strip()))
        os.dup2(s_in, 0)
        os.dup2(s_out, 1)
        os.close(s_in)
        os.close(s_out)
        
    else:
        #run command
        f_out = open('output.txt','w')
        try:
            subprocess.run(command.split(" "),stdout=f_out)
        except Exception:
            scr.addstr("!pipe shell: command not found: {}".format(command))
        f_out.close
def shell_cd(req_path,scr):
    safe_dir = Path('/home/')
    common = os.path.commonpath([os.path.realpath(req_path), safe_dir])
    if os.path.normpath(common) != os.path.normpath(safe_dir):
        scr.addstr("You have tried to escape!\n")
        return
    try:
        os.chdir(os.path.abspath(req_path))
    except Exception:
        scr.addstr("shell: cd: no such file or directory: {}\n".format(req_path))
def shell_help(scr):
    scr.addstr("This is my shell written in python for my Operating Systems class. It should run most commands\n")
def main(scr):
    while True:
        scr.addch('[')
        scr.addstr(os.getcwd())
        scr.addstr(']$ ')
        line = ""
        while True:
            c = scr.getch()
            if c <= 126 and c >= 32:
                line += chr(c)
                scr.addch(c)
            elif c == 127:
                line = line[:-1]
                y,x=scr.getyx()
                scr.move(y,x-1)
                scr.delch()
            elif c == 10:
                break
            elif c == curses.KEY_UP:
                return
        scr.addch('\n')
        if line == "exit":
            return
        elif line[:3] == "cd ":
            shell_cd(line[3:],scr)
        elif line == "help":
            shell_help(scr)
        else:
            exec_cmd(line,scr)
if '__main__' == __name__:
    wrapper(main)
