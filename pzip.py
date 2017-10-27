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
from multiprocessing import Process, Value, Queue, Semaphore

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

completed_files = Value('i', 0)
files_queue = Queue()
sem = Semaphore(1)
a = True


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


def fill_queue_with_files(files):
    for f in files:
        files_queue.put(f)


def compress(t):
    global a

    while not files_queue.empty():

        sem.acquire()

        if not files_queue.empty() and a:

            filename = files_queue.get()
            sem.release()

        else:
            a = False
            pass

        try:

            open(filename, "r")

            with ZipFile(filename + ".zip", 'w') as file_zip:
                file_zip.write(filename)

            print "File:", filename, "PID:", os.getpid()
            completed_files.value += 1

        except IOError as e:
            if t:
                print 'ficheiro nao existe', e
                a = False
                while not files_queue.empty():
                    files_queue.get()
            else:
                pass


def decompress():
    pass


def create_default_processes_decompress(n, l_p, t, f):
    # creates all processes and adds them to the list
    for _ in xrange(n):
        p = Process(target=f, args=(t,))
        l_p.append(p)


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
    # print "python pzip.py", args, "filesnames", filesnames

    args = argument_parser()
    filesnames = []
    l_p = []

    if not args.c and not args.d:
        print "Error: choose an option [-c | -d]"
    else:
        if args.files == []:
            choose_files()
        else:
            filesnames = args.files

    # fill the shared queue with files
    # fill_queue_with_files(filesnames)
    for f in filesnames:
        files_queue.put(f)

    if args.c:
            create_default_processes_decompress(args.p, l_p, args.t, compress)
    if args.d:
            create_default_processes_decompress(args.p, l_p, args.t, decompress)

    for p in l_p:
        p.start()

    for p in l_p:
        p.join()

    print "python pzip.py", args, "filesnames", filesnames
    print 'Compress / Decompress Files:', completed_files.value
