#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################
#    2º Trabalho de Grupo   #
#  Sistemas Operativos LTI  #
# ------------------------- #
#       Grupo sop002        #
#    Andre Nunes 43304      #
#    Miguel Almeida 48314   #
#    Tiago Martins 48299    #
#############################

import os, argparse, signal, time, sys, pickle
from zipfile import ZipFile
from multiprocessing import Process, Value, Queue, Semaphore

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

queue = Queue()
f_queue = Queue()
sem = Semaphore(1)
sem_f = Semaphore(1)
volume_total = Value('i', 0)
completed_files = Value('i', 0)
start_time = time.time()


def choose_files():
    """
    Reads the files to compress ou uncompress from stdin
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
               [-a n] [-f file] [files [files ...]]

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
    parser.add_argument("-a", type=int, default=0, help="write to stdout")
    parser.add_argument("-f", nargs=1, help="binary file name")
    parser.add_argument("files", nargs='*', help="files to Compress/Decompress")

    return parser.parse_args()


def compress_decompress(args_t, args_c, args_d, args_f):
    """Function to compress or decompress a file by the filename

    :param args_t: value of argument t
    :param args_c: value of argument c
    :param args_d: value of argument_d
    :param args_f: value of argument_f
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
                filesize = file_zip.getinfo(filename).compress_size
                volume_total.value += filesize
                completed_files.value += 1
                if args_f:
                    write_f_file(filename, filesize)
                sem.release()

        elif filename != 0 and args_d:
            with ZipFile(filename, 'r') as file_zip:
                file_zip.extract(filename[:-4])
                print "DONE", filename, " ", os.getpid()
                sem.acquire()
                filesize = file_zip.getinfo(filename).compress_size
                volume_total.value += filesize
                completed_files.value += 1
                if args_f:
                    write_f_file(filename, filesize)
                sem.release()


def write_f_file(filename, filesize):
    """Append the information about the compress/decompress file to the list

    :param filename: filename of compress/decompress file
    :param filesize: file size of compress/decompress file
    """
    l = f_queue.get()
    l.append(os.getpid())
    l.append(filename)
    l.append(time.time() - start_time)
    l.append(filesize)
    l.append(volume_total.value)
    f_queue.put(l)


def create_default_processes(n_process, list_process, args_t, func, args_c, args_d, args_f):
    """Function to creates all processes and adds them to the list

    Params:
    :param n_process: number of processes to create
    :param list_process: list to store the processes
    :param t: value of argument t
    :param func: name of function to process execute
    :param args_t: value of argument t
    :param args_c: value of argument c
    :param args_d: value of argument d
    :param args_f: value of argument f
    """
    for _ in xrange(n_process):
        p = Process(target=func, args=(args_t, args_c, args_d, args_f))
        list_process.append(p)


def info():
    """Function to write the information about the program state
    """
    sem.acquire()
    print '==============================='
    print 'Ficheiros cifrados/decifrados =', completed_files.value
    print 'Tempo de execucao =', (time.time() - start_time) * 10000000, 'microsegundos'
    print 'Volume de dados =', volume_total.value, 'Kbytes'
    print '==============================='
    sem.release()


def controlC(sig, NULL):
    """Funtion to handle the SIGINT Signal

    :param sig: signal to handle
    """
    if sem.acquire(block=False):
        queue.get()
        queue.put([])
        sem.release()
    else:
        sem.acquire()
        queue.get()
        queue.put([])
        sem.release()
    info()
    sys.exit()

def signalA(sig, NULL):
    """Function to handle SIGALARM Signal

    :param sig: signal to handle
    """
    info()


signal.signal(signal.SIGINT, controlC)
signal.signal(signal.SIGALRM, signalA)

if __name__ == '__main__':

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

    if args.a != 0:
        sec = int(args.a)
        signal.setitimer(signal.ITIMER_REAL, sec, sec)

    # fill queue with files
    queue.put(filesnames)
    f_queue.put([])

    create_default_processes(args.p, list_process, args.t, compress_decompress, args.c, args.d, args.f)

    for p in list_process:
        p.start()

    for p in list_process:
        p.join()

    if args.f:
        with open(args.f[0], "wb") as outFile:
            sem.acquire()
            l = []
            l.append(time.strftime("%d %B %Y, %H:%M:%S"))
            s = (time.time() - start_time)
            l.append(str(s / 60) + ':' + str(s) + ':' + str(s * 10000000))
            l.append(completed_files.value)
            l.extend(f_queue.get())
            l.append(volume_total.value)
            sem.release()
            pickle.dump(l, outFile)

    info()
