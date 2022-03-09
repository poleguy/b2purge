#################################################################################
##
## bash.py
##  To run bash commands from python and stop on error
##  Useful when you know the bash command but are working in python.
##  Eventually commands that can be run natively in python can be replaced
##  But some things are better in bash
##
##  Nicholas Dietz
## 
#################################################################################
import os
import subprocess
import shlex
import argparse
import zipfile

# https://stackoverflow.com/questions/4256107/running-bash-commands-in-python/51950538
def bash(cmd):
    # https://stackoverflow.com/questions/3503719/emulating-bash-source-in-python
    print(f'Runinng bash command: {cmd}')
    if "'" in cmd:
        print("warning: apostrophe's might cause trouble")
    bashCommand = f"env bash -c '{cmd}'"
    bashCommand = shlex.split(bashCommand)
    #bashCommand = "cwm --rdf test.rdf --ntriples > test.nt"
    print(bashCommand)
    process = subprocess.Popen(bashCommand, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True)

    # https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    output = ''
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")
        output = output + stdout_line
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        #raise subprocess.CalledProcessError(return_code, cmd)
        raise ValueError("Bash command failed")
    return output


# https://stackoverflow.com/questions/4256107/running-bash-commands-in-python/51950538
def bash_silent(cmd):
    # run bash command, capture output.
    # https://stackoverflow.com/questions/3503719/emulating-bash-source-in-python
    print(f'Runinng bash command: {cmd}')
    if "'" in cmd:
        print("warning: apostrophe's might cause trouble")
    bashCommand = f"env bash -c '{cmd}'"
    bashCommand = shlex.split(bashCommand)
    #bashCommand = "cwm --rdf test.rdf --ntriples > test.nt"
    print(bashCommand)
    process = subprocess.Popen(bashCommand, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True)

    # https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    output = ''
    for stdout_line in iter(process.stdout.readline, ""):
        #print(stdout_line, end="")
        output = output + stdout_line
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        #raise subprocess.CalledProcessError(return_code, cmd)
        raise ValueError("Bash command failed")
    return output


def main():
    bash('echo "hello world"')

if __name__ == '__main__':
    main()
