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


__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

import os
import sys
from zipfile import ZipFile 
import random
import string
import argparse
from multiprocessing import Semaphore, Value, Queue
from threading import Thread

completed_files = Value('i', 0)
queue = Queue()
sem = Semaphore(1)
a = Value('b', False)
queue_size = Value('i', 0)
n = Value('i', 0)

def compress(t):
	checker = 0
	index = 0
	while queue.qsize() <= completed_files:
		sem.acquire()

		lt = queue.get()
		print 'lt', lt


		if len(lt)+1 != completed_files:
			filename = lt[index]
			checker = 1
			queue.put(lt)
		if not os.path.isfile(filename) and t:
			print "Erro filenotfound"
			print "aqui t true"
			queue.get()
			break
		elif not t:
			print 'aqui t false'


		sem.release()
		if checker == 1:
			with ZipFile(filename + ".zip", 'w') as file_zip:
				file_zip.write(filename)

				print "DONE", os.getpid()
				completed_files.value += 1
				index += 1
				checker = 0

def decompress(t):

    """
    Esta opção ativa o modo de descompressão do comando pzip, pegando num ficheiro zip e
    extraindo os conteúdos para uma dada diretoria.
    :param path: Caminho do(s) ficheiro(s) a ser(em) descomprimido(s)
    :param dirname: Diretoria para onde se quer extrair o(s) ficheiro(s)
    :return: Um ou mais ficheiros descomprimidos
    """
    checker = 0
    index = 0
    while queue.qsize() != 0:
		sem.acquire()

		lt = queue.get()
		print 'lt', lt
		filename = lt[index]
		print filename
		if len(lt) != completed_files:
			checker = 1
			queue.put(lt)
		if not os.path.isfile(filename) and t:
			print "Erro filenotfound"
			print "aqui t true"
			queue.get()
			break
		elif not t:
			print 'aqui t false'
		sem.release()
		if checker == 1:
			zf = ZipFile(filename, 'r')
    		zf.extract()
    		zf.close()
    		index += 1
    		


    
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

	parser.add_argument("-p", type=int, choices=xrange(1, 10), default=1, help="number os process")
	parser.add_argument("-t", help="finish when file not found", action="store_true")
	parser.add_argument("files", nargs='*', help="files to Compress/Decompress")

	return parser.parse_args()

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

def fill_queue_with_files(files):
	for f in files:
		files_queue.put(f)

#Create Threads
def create_threads(n, l_t, v, func):
	for _ in xrange(n):
		p = Thread(target=func, args= (v,))
		l_t.append(p)
	return l_t

if __name__ == '__main__':
	
	args = argument_parser()
	filesnames = []
	l_t = []
	
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
			threadlist = create_threads(args.p, l_t, args.t, compress)
			for s in threadlist:
				s.start()
				s.join()
	if args.d:
			threadlist = create_threads(args.p, l_t, args.t, decompress)
			for s in threadlist:
				s.start()
				s.join()

	print "python pzip_threads.py", args, "filesnames", filesnames
	print 'Compress / Decompress Files:', completed_files.value