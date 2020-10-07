#!/usr/bin/python3.8
# Test normal
# https://www.egr.msu.edu/~khalil/NonlinearSystems/Sample/Lect_ .pdf 1 41 -p 100 -d 1 --quiet
# Test file:
# -i test.txt -o testDir

import sys
import os
import platform
import time
import shlex
from datetime import datetime
from random import random

# Personal Lib
from ArgParse import *

# Parametri Facoltativi, valori di default
pDW = 5
quite = False
fileList = ""

# Url List
urlListParam = []  # [url, name, savePath]


def helpMan():
    print("correct syntax is:")
    print("./parallelDownload.py <baseUrl> <endUrl> <startNum> <endNum> [Options]")
    print("\tbaseUrl:= First part of the url (until XX number)")
    print("\tendUrl:= Second part of the url (after XX number)")
    print("\tstartNum:= First index included")
    print("\tendNum:= Last index (included)")
    print("[Options]:")
    print("\t\t -p --parallelDownload <int> Number of concurrency downdload (default = 5)")
    print("\t\t -o --outSave <path> Saving directory Path (default = ./parallelDowndload)")
    print("\t\t -d --digit <digit> Number of digit (default = 2)")
    print("\t\t --quiet no show all data")

    print("\n Is also possible setup multiple download in a File:")
    print("./parallelDownload.py -i <File List> [Options All]")
    print("[Options All]:")
    print("\t\t -p --parallelDownload <int> Number of concurrency downdload (default = 5)")
    print("\t\t --quiet no show all data")
    print("\n[File List syntax]:")
    print("For EVERY LINE the syntax MUST be is:")
    print("<baseUrl> <endUrl> <startNum> <endNum> [Options file]")
    print("[Options file] (in case of missing, the global option will be used:")
    print("\t\t -o --outSave <path> Saving directory Path (default = see global)")
    print("\t\t -d --digit <digit> Number of digit (default = see global)")

    print("You type the command:")
    print(sys.argv[1:])  # Press Ctrl+8 to toggle the breakpoint.
    exit(-1)


def son(dataList):
    """
    :param dataList: #list: [url, name, savePath]
    :return:
    """
    url = dataList[0]
    name = dataList[1]
    savePath = dataList[2]

    # time.sleep(random() / 100.0)  # per permettere di "deallinearsi al passo successivo
    try:
        os.makedirs(savePath)
        os.chdir(savePath)
    except FileExistsError as e:
        os.chdir(savePath)

    print("\nDownload: " + url + "\n\t Start " + name)
    if platform.system() == "Linux":
        if quite:
            os.system("wget " + url + " --quiet")
        else:
            os.system("xterm -e bash -c '" + "wget " + url + "'")
    # elif (platform.system() == "Windows"):
    #     os.system("Invoke-WebRequest -Uri " + url)
    else:
        print("OS not Supported")
    print("\n\t END " + name)
    exit(0)


def urlListInit():
    """
    Make the urlList in base of the command line params
    :return:
    """
    global urlListParam, pDW, quite, fileList

    if "-i" in sys.argv:
        index = sys.argv.index("-i")
        fileList = sys.argv[index + 1]
        subList = sys.argv[1:index] + sys.argv[index + 2:]
        argvListParse = 0
        try:
            argvListParse = ArgListParse(subList)
        except Exception as e:
            print("Oops!", str(e), "occurred.")
            helpMan()

        # Estraggo i parametri funzionali
        if argvListParse.pDW is not None:
            pDW = argvListParse.pDW
        if argvListParse.quite is not None:
            quite = argvListParse.quite


        # Using readlines()
        file1 = open(fileList, 'r')
        Lines = file1.readlines()
        file1.close()

        list_of_lists = []
        for line in Lines:
            list_of_lists.append(shlex.split(line))

        argvParseFile = 0
        for line in list_of_lists:
            try:
                argvParseFile = ArgParse(line)
            except Exception as e:
                print("Oops!", str(e), "occurred.")
                print(line)
                helpMan()

        # Estraggo i parametri funzionali
        urlListParam += argvParseFile.urlParam

    else:  # Comando Singolo
        if len(sys.argv) < 5:
            helpMan()

        argvParseTerminal = 0
        try:
            argvParseTerminal = ArgParse(sys.argv[1:])
        except Exception as e:
            print("Oops!", str(e), "occurred.")
            helpMan()

        # Estraggo i parametri funzionali
        urlListParam += argvParseTerminal.urlParam

        if argvParseTerminal.pDW is not None:
            pDW = argvParseTerminal.pDW
        if argvParseTerminal.quite is not None:
            quite = argvParseTerminal.quite


def main():
    urlListInit()

    print("The download start with " + str(pDW) + " parallel Connection")
    print("Output quiet = " + str(quite))

    # Start parallel procedure
    start_time = datetime.now()

    tokenActive = 0
    nDownload = 0
    for dwParam in urlListParam:
        tokenActive += 1
        pid = os.fork()
        if pid == 0:  # child process
            son(dwParam)
        else:  # We are in the parent process.
            nDownload += 1
            if tokenActive < pDW:
                continue
            else:
                os.wait()
                tokenActive -= 1

    while tokenActive != 0:
        os.wait()
        tokenActive -= 1

    time_elapsed = datetime.now() - start_time
    print("## Downloads end ##")
    print('Total Time (hh:mm:ss.ms) {}'.format(time_elapsed))
    print('Mean Time (hh:mm:ss.ms) {}'.format(time_elapsed / nDownload))


if __name__ == '__main__':
    main()