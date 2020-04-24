import os
import subprocess

def exec_cmd(command):
    if "|" in command:
        # make copies of stdin and stdout in order to restore them later
        s_in, s_out = (0, 0)
        s_in = os.dup(0)
        s_out = os.dup(1)
        # first command takes input from stdin
        fd_in = os.dup(s_in)
        # iterate over all piped commands
        for cmd in command.split("|"):
            # fd_in is the readable end of the pipe/stdin
            os.dup2(fd_in, 0)
            os.close(fd_in)
            # if (last command) restore stdout
            if cmd == command.split("|")[-1]:
                fd_out = os.dup(s_out)
            else:
            # redirect stdout to pipe
                fd_in, fd_out = os.pipe()
            os.dup2(fd_out, 1)
            os.close(fd_out)
            #run command again by calling self
            exec_cmd(' '.join(map(str,cmd.strip().split())))
        # restore stdout and stdin
        os.dup2(s_in, 0)
        os.dup2(s_out, 1)
        os.close(s_in)
        os.close(s_out)
    else:
        #run command
        try:
            subprocess.run(command.split(" "))
        except Exception:
            print("!pipe shell: command not found: {}".format(command))
def shell_cd(path):
    try:
        os.chdir(os.path.abspath(path))
    except Exception:
        print("shell: cd: no such file or directory: {}".format(path))
def shell_help():
    print("This is my shell written in python for my Operating Systems class. It should run most commands")
def main():
    while True:
        line = input("$ ")
        if line == "exit":
            break
        elif line[:3] == "cd ":
            shell_cd(inp[3:])
        elif line == "help":
            shell_help()
        else:
            exec_cmd(line)
if '__main__' == __name__:
    main()
