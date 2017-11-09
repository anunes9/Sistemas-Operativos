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
queue = Queue()
sem = Semaphore(1)
a = Value('b', False)
queue_size = Value('i', 0)
n = Value('i', 0)


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


def compress(t):
    while queue.qsize() != 0:
        sem.acquire()

        lt = queue.get()
        print 'lt', lt
        if len(lt) != 0:
            filename = lt.pop(0)
        else:
            filename = 0
        print filename
        if len(lt) != 0:
            queue.put(lt)

        if not os.path.isfile(filename) and t:
            print "Erro filenotfound"
            print "aqui t true"
            queue.get()
            break

        elif not t and not os.path.isfile(filename):
            print 'aqui t false'
            filename = 0

        sem.release()

        if filename != 0:
            with ZipFile(filename + ".zip", 'w') as file_zip:
                file_zip.write(filename)

                print "DONE", os.getpid()
                completed_files.value += 1


def decompress(t):
    while queue.qsize() != 0:
        sem.acquire()

        lt = queue.get()
        print 'lt', lt
        if len(lt) != 0:
            filename = lt.pop(0)
        else:
            filename = 0
        print filename
        if len(lt) != 0:
            queue.put(lt)

        if not os.path.isfile(filename) and t:
            print "Erro filenotfound"
            print "aqui t true"
            queue.get()
            break

        elif not t and not os.path.isfile(filename):
            print 'aqui t false'
            filename = 0

        sem.release()

        if filename != 0:
            with ZipFile(filename, 'r') as file_zip:
                file_zip.extract(filename[:-4])

                print "DONE", os.getpid()
                completed_files.value += 1


def create_default_processes_decompress(n, l_p, t, f):
    # creates all processes and adds them to the list
    for _ in xrange(n):
        p = Process(target=f, args=(t,)).start()
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
    queue.put(filesnames)
    print queue.qsize()

    queue_size.value = len(filesnames)

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
