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

import os
from zipfile import ZipFile
import argparse
from threading import Thread
from multiprocessing import Value, Queue, Semaphore

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

completed_files = Value('i', 0)
queue = Queue()
sem = Semaphore(1)
queue_size = Value('i', 0)


def choose_files():
    """
    Reads the files to compress ou uncompress from stdin

    Return: a list of name files
    """
    filename = raw_input("Name of file: (--q to exit)\n")

    while filename != "--q" or len(filesnames) == 0:
        if filename != '':
            filesnames.append(filename)
        filename = raw_input("Name of file: (--q to exit)\n")


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
        -p {0,1,2,3,4,5,6,7,8,9}    number os threads
        -t                          finish when file not found
    """
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", help="compress files", action="store_true")
    group.add_argument("-d", help="decompress files", action="store_true")

    parser.add_argument("-p", type=int, choices=xrange(1, 10), default=1, help="number os threads")
    parser.add_argument("-t", help="finish when file not found", action="store_true")
    parser.add_argument("files", nargs='*', help="files to Compress/Decompress")

    return parser.parse_args()


def compress_decompress(args_t, args_c, args_d):
    """Function to compress or decompress a file by the filename

    args_t - value of argument t
    args_c - value of argument c
    args_d - value of argument_d
    """
    while queue.qsize() != 0:
        sem.acquire()
        lt = queue.get()

        if len(lt) != 0:
            filename = lt.pop(0)
        else:
            filename = 0

        if len(lt) != 0:
            queue.put(lt)

        if not os.path.isfile(filename) and args_t:
            print "Erro filenotfound"
            queue.get()
            filename = 0

        elif not args_t and not os.path.isfile(filename):
            filename = 0

        sem.release()

        if filename != 0 and args_c:
            with ZipFile(filename + ".zip", 'w') as file_zip:
                file_zip.write(filename)
                # print "DONE", os.getpid()
                completed_files.value += 1

        elif filename != 0 and args_d:
            with ZipFile(filename, 'r') as file_zip:
                file_zip.extract(filename[:-4])
                # print "DONE", os.getpid()
                completed_files.value += 1


def create_default_threads(n_thread, list_thread, args_t, func, args_c, args_d):
    """Function to creates all threads and adds them to the list

    Params:
    n_thread - number of threads to create
    list_thread - list to store the threads
    t - value of argument t
    func - name of function to thread execute
    args_c - value of argument c
    args_d - value of argument_d
    """
    for _ in xrange(n_thread):
        t = Thread(target=func, args=(args_t, args_c, args_d))
        list_thread.append(t)

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
    list_thread = []

    if not args.c and not args.d:
        print "Error: choose an option [-c | -d]"
    else:
        if args.files == []:
            choose_files()
        else:
            filesnames = args.files

    # fill queue with files
    queue.put(filesnames)

    queue_size.value = len(filesnames)

    create_default_threads(args.p, list_thread, args.t, compress_decompress, args.c, args.d)

    for p in list_thread:
        p.start()

    for p in list_thread:
        p.join()

    # print "python pzip_threads.py", args, "filesnames", filesnames
    print 'Compress / Decompress Files:', completed_files.value
