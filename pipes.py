import os
import curses
from curses import wrapper
import subprocess
from pathlib import Path
import sys

def exec_cmd(command,scr):
    printstuff = True
    if ">" in command:
        filename = command.split(">")[1].strip()
        command = command.split(">")[0].strip()
        printstuff = False
    else:
        filename = 'output.txt'
    if "|" in command:
        s_in, s_out = (0,0)
        s_in = os.dup(0)
        s_out = os.dup(1)
        fdin = os.dup(s_in)
        for cmd in command.split("|"):
            os.dup2(fdin,0)
            os.close(fdin)
            if cmd == command.split('|')[-1]:
                fdout = os.dup(s_out)
            else:
                fdin,fdout=os.pipe()
            try:
                subprocess.run(cmd.strip().split())
            except Exception:
                scr.addstr("shell: command not found: {}".format(cmd))
        os.dup2(s_in,0)
        os.dup2(s_out,1)
        os.close(s_in)
        os.close(s_out)
        return
    f_out = open(filename,'w')
    try:
        subprocess.run(command.split(" "),stdout=f_out)
    except Exception:
        scr.addstr("shell: command not found: {}".format(command))
    f_out.close()
    if printstuff:
        f_out = open('output.txt','r')
        scr.addstr(f_out.read())
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
    histpath = os.path.abspath('./history.txt')
    scr.scrollok(True)
    while True:
        scr.addch('[')
        scr.addstr(os.getcwd())
        scr.addstr(']$ ')
        line = ""
        pos = 0
        histpos = 0
        readhist = open(histpath,'r')
        histdict = {}
        while True:
            hline = readhist.readline()
            if not hline:
                break
            histdict[histpos]=hline
            histpos+=1
        readhist.close()
        max_hist=histpos-1
        while True:
            c = scr.getch()
            if c <= 126 and c >= 32:
                line += chr(c)
                scr.addch(c)
                pos+=1
            elif (c == 127 or c == 263) and pos>0:
                pos-=1
                line = line[:-1]
                y,x=scr.getyx()
                scr.move(y,x-1)
                scr.delch()
            elif c == 10:
                break
            elif c == curses.KEY_LEFT and pos>0:
                pos-=1
                y,x=scr.getyx()
                scr.move(y,x-1)
            elif c == curses.KEY_RIGHT and pos<len(line):
                y,x=scr.getyx()
                scr.move(y,x+1)
            elif c == curses.KEY_UP and histpos>0:
                while pos>0:
                    pos-=1
                    y,x=scr.getyx()
                    scr.move(y,x-1)
                    scr.delch()
                histpos -= 1
                line = histdict[histpos].strip()
                scr.addstr(line)
                pos+=len(line)
            elif c == curses.KEY_DOWN and histpos<max_hist:
                while pos>0:
                    pos-=1
                    y,x=scr.getyx()
                    scr.move(y,x-1)
                    scr.delch()
                histpos += 1
                line = histdict[histpos].strip()
                scr.addstr(line)
                pos += len(line)
        scr.addch('\n')
        if line == "exit":
            return
        elif line[:3] == "cd ":
            shell_cd(line[3:],scr)
        elif line == "help":
            shell_help(scr)
        else:
            hist = open(histpath,'a')
            hist.write(line+"\n")
            hist.close()
            exec_cmd(line,scr)
if '__main__' == __name__:
    wrapper(main)
