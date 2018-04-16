#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################
#    1º Trabalho de Grupo   #
#  Sistemas Operativos LTI  #
# ------------------------- #
#       Grupo sop002        #
#    Andre Nunes 43304      #
#    Miguel Almeida 48314   #
#    Tiago Martins 48299    #
#############################

import os, argparse
from zipfile import ZipFile
from multiprocessing import Process, Value, Queue, Semaphore

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

queue = Queue()
sem = Semaphore(1)
completed_files = Value('i', 0)

def choose_files():
    """
    Reads the files to compress ou uncompress from stdin

    Return: a list of name files
    """
    try:
        filename = raw_input("Name of file: (--q to exit)\n")

        while filename != "--q" or len(filesnames) == 0:
            if filename != '':
                filesnames.append(filename)
            filename = raw_input("Name of file: (--q to exit)\n")
    except EOFError as e:
        pass
    except KeyboardInterrupt as p:
        pass

def argument_parser():
    """
    Parser to read the arguments from command line

    Argumments avalilable:
    usage: pzip.py [-h] [-c | -d] [-p {0,1,2,3,4,5,6,7,8,9}] [-t]
               [files [files ...]]

    positional arguments:
        files                       files to Compress/Decompress

    optional arguments:
        -h, --help                  show this help message and exit
        -c                          compress files
        -d                          decompress files
        -p {0,1,2,3,4,5,6,7,8,9}    number os process
        -t                          finish when file not found
    """
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", help="compress files", action="store_true")
    group.add_argument("-d", help="decompress files", action="store_true")

    parser.add_argument("-p", type=int, choices=xrange(1, 10), default=1, help="number os process")
    parser.add_argument("-t", help="finish when file not found", action="store_true")
    parser.add_argument("files", nargs='*', help="files to Compress/Decompress")

    return parser.parse_args()


def compress_decompress(args_t, args_c, args_d):
    """Function to compress or decompress a file by the filename

    args_t - value of argument t
    args_c - value of argument c
    args_d - value of argument_d
    args_f - value of argument_f
    """
    global a
    while a:
        sem.acquire()

        lt = queue.get()

        if len(lt) == 0:
            filename = 0
            a = False
            queue.put([])

        else:
            filename = lt.pop(0)

            if not os.path.isfile(filename) and args_t:
                print "Erro filenotfound"
                filename = 0

            elif not args_t and not os.path.isfile(filename):
                filename = 0

            if lt == []:
                a = False

            queue.put(lt)

        sem.release()

        if filename != 0 and args_c:
            with ZipFile(filename + ".zip", 'w') as file_zip:
                file_zip.write(filename)
                print "DONE", filename, " ", os.getpid()
                sem.acquire()
                completed_files.value += 1
                sem.release()

        elif filename != 0 and args_d:
            with ZipFile(filename, 'r') as file_zip:
                file_zip.extract(filename[:-4])
                print "DONE", filename, " ", os.getpid()
                sem.acquire()
                completed_files.value += 1
                sem.release()

def create_default_processes(n_process, list_process, args_t, func, args_c, args_d):
    """Function to creates all processes and adds them to the list

    Params:
    n_process - number of processes to create
    list_process - list to store the processes
    t - value of argument t
    func - name of function to process execute
    args_c - value of argument c
    args_d - value of argument_d
    """
    for _ in xrange(n_process):
        p = Process(target=func, args=(args_t, args_c, args_d))
        list_process.append(p)

if __name__ == '__main__':

    # Combinacoes possivies
    # -c -p n -t {files}
    # -c -p n {files}
    # -c -t {files}
    # -c {files}
    # -d -p n -t {files}
    # -d -p n {files}
    # -d -t {files}
    # -d {files}
    args = argument_parser()
    filesnames = []
    list_process = []
    a = True

    if not args.c and not args.d:
        print "Error: choose an option [-c | -d]"
    else:
        if args.files == []:
            choose_files()
        else:
            filesnames = args.files

    # fill queue with files
    queue.put(filesnames)

    create_default_processes(args.p, list_process, args.t, compress_decompress, args.c, args.d)

    for p in list_process:
        p.start()

    for p in list_process:
        p.join()

    print 'Compress / Decompress Files:', completed_files.value

