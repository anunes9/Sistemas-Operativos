#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################
#    2º Trabalho de Grupo   #
#  Sistemas Operativos LTI  #
#---------------------------#
#         Grupo 01          #
#    Andre Nunes 43304      #
#    Miguel Almeida 48314   #
#    Tiago Martins 48299    #
#############################

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

import sys
import random
import string
from Crypto.Cipher import AES
from multiprocessing import Semaphore, Value, Queue
from threading import Thread
from Crypto import Random

encryptedFiles = 0
decryptedFiles = 0
files_queue = Queue()
sem = Semaphore(1)

#concatena informação adicional à string de modo a que a sua dimensão seja
#AES.block_size. A informação adicional corresponde ao nº de bytes concatenados
def pad(bytestring):
    nbytes = len(bytestring)
    padding_bytes = AES.block_size - nbytes
    padding_str = padding_bytes * chr(padding_bytes)
    return bytestring + padding_str

#cifra um ficheiro com o algoritmo AES
#obs: de forma a simplificar a operação de padding, apenas são lidos do ficheiro
#AES.block_size de cada vez
def cifrar(filename):

    #Chave Generator
    size_chave = 32
    chave = Random.new().read(size_chave)

    #Gera o nome do ficheiro da chave
    file_chave = filename + ".key"

    #Gera o ficheiro .key
    file = open(file_chave,"w")
    file.write(chave)
    file.close()
    
    cipher = AES.new(chave)
    with open(filename) as ifile, open(filename + ".enc", "w") as ofile:
        bytestring = ifile.read(AES.block_size)
        while len(bytestring) == AES.block_size:
            ofile.write(cipher.encrypt(pad(bytestring)))
            bytestring = ifile.read(AES.block_size)
        ofile.write(cipher.encrypt(pad(bytestring)))

#decifra um ficheiro com o algoritmo AES
def decifrar(filename):
    
    #le o ficheiro da chave
    with open(filename + ".key") as f:
        chave = f.readline()

    cipher = AES.new(chave)
    with open(filename + ".enc") as ifile, open(filename + ".dec", "w") as ofile:
        previous = None
        current = None
        NOT_DONE = True
        while NOT_DONE:
            bytestring = cipher.decrypt(ifile.read(AES.block_size))
            if current == None:
                current = bytestring
            else:
                previous = current
                current = bytestring
                nbytes = len(current)
                if nbytes == 0:
                    padding_bytes = ord(previous[-1])
                    previous = previous[:-padding_bytes]
                    NOT_DONE = False
                ofile.write(previous)

#funcao para fazer a atribuicao de ficheiros a processos
#para cifrar
def encrypt(v):
    
    filename = ""
    global encryptedFiles
    
    #Enquanto ha ficheiros em queue
    while files_queue.empty() == False:

        sem.acquire()
        filename = files_queue.get()
        sem.release()

        try:
            open(filename, "r")
            cifrar(filename)
            encryptedFiles += 1

        except IOError as e:
            if v:
                print 'ficheiro nao existe', e
                while files_queue.empty() == False:
                    files_queue.get()
            else:
                pass

#funcao para fazer a atribuicao de ficheiros a processos
#para decifrar
def decrypt(v):
    
    filename = ""
    global decryptedFiles

    #Enquanto ha ficheiros em queue
    while files_queue.empty() == False:

        sem.acquire()
        filename = files_queue.get()
        sem.release()

        try:
            open(filename,"r")
            decifrar(filename)
            decryptedFiles += 1

        except IOError as e:
            if v:
                print 'ficheiro nao existe', e
                while files_queue.empty() == False:
                    files_queue.get()
            else:
                pass

#funcao que adiciona a lista os ficheiros a cifrar/decifrar
def fill_queue_with_files(files):
    
    for f in files:
        files_queue.put(f)

#funcao para ler os ficheiros do stdin
def chose_files():
    #asks with are the files to encrypt or decrypt
    filename = raw_input("qual o nome do ficheiro?\n")

    while len(filename) != 0:
        files_queue.put(filename)
        filename = raw_input("qual o nome do ficheiro?\n")

#funcao para criar as threads para cifrar/decifrar
def create_threads(n, func, v):
    #cria os processos e mete numa lista
    l = []
    for _ in xrange(n):
        p = Thread(target=func, args= (v,))
        l.append(p)
    return l

################################
if __name__ == '__main__':
    args = sys.argv[1:]

    try:
        if args[0] == '-e':
            #if args[1] == '-p':
            if '-p' in args:
                n_threads = int(args[2])
                if '-v' in args:
                    files = args[4:]
                    v = True
                    if len(files) == 0:
                        chose_files()
                        threadlist = create_threads(n_threads, encrypt, v)
                        for s in threadlist:
                            s.start()
                            s.join()
                    else:
                        fill_queue_with_files(files)
                        threadlist = create_threads(n_threads, encrypt, v)
                        for s in threadlist:
                            s.start()
                            s.join()
                else:
                    files = args[3:]
                    v = False
                    if len(files) == 0:
                        chose_files()
                        threadlist = create_threads(n_threads, encrypt, v)
                        for s in threadlist:
                            s.start()
                            s.join()
                    else:
                        fill_queue_with_files(files)
                        print n_threads
                        threadlist = create_threads(n_threads, encrypt, v)
                        for s in threadlist:
                            s.start()
                            s.join()
            elif '-v' in args:
                files = args[2:]
                v = True
                if len(files) == 0:
                    chose_files()
                    n_threads = files_queue.qsize()
                    threadlist = create_threads(n_threads, encrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()
                else:
                    n_threads = len(files)
                    fill_queue_with_files(files)
                    threadlist = create_threads(n_threads, encrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()
            else:
                files = args[1:]
                v = False
                if len(files) == 0:
                    chose_files()
                    n_threads = files_queue.qsize()
                    threadlist = create_threads(n_threads, encrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()
                else:
                    n_threads = len(files)
                    fill_queue_with_files(files)
                    threadlist = create_threads(n_threads, encrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()

        elif args[0] == '-d':
            if '-p' in args:
                n_threads = int(args[2])
                if '-v' in args:
                    files = args[4:]
                    v = True
                    if len(files) == 0:
                        chose_files()
                        threadlist = create_threads(n_threads, decrypt, v)
                        for s in threadlist:
                            s.start()
                        for s in threadlist:
                            s.join()
                    else:
                        fill_queue_with_files(files)
                        threadlist = create_threads(n_threads, decrypt, v)
                        for s in threadlist:
                            s.start()
                        for s in threadlist:
                            s.join()
                else:
                    files = args[3:]
                    v = False
                    if len(files) == 0:
                        chose_files()
                        threadlist = create_threads(n_threads, decrypt, v)
                        for s in threadlist:
                            s.start()
                        for s in threadlist:
                            s.join()
                    else:
                        fill_queue_with_files(files)
                        threadlist = create_threads(n_threads, decrypt, v)
                        for s in threadlist:
                            s.start()
                        for s in threadlist:
                            s.join()
            elif '-v' in args:
                files = args[2:]
                v = True
                if len(files) == 0:
                        chose_files()
                        n_threads = files_queue.qsize()
                        threadlist = create_threads(n_threads, decrypt, v)
                        for s in threadlist:
                            s.start()
                        for s in threadlist:
                            s.join()
                else:
                    n_threads = len(files)
                    fill_queue_with_files(files)
                    threadlist = create_threads(n_threads, decrypt, v)
                    for s in threadlist:
                        s.start()
                    for s in threadlist:
                        s.join()
            else:
                files = args[1:]
                v = False
                if len(files) == 0:
                    chose_files()
                    n_threads = files_queue.qsize()
                    threadlist = create_threads(n_threads, decrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()
                else:
                    n_threads = len(files)
                    fill_queue_with_files(files)
                    threadlist = create_threads(n_threads, decrypt, v)
                    for s in threadlist:
                        s.start()
                        s.join()
        else:
            print 'Erro, tem que escolher as opcoes -e ou -d'

        print "Numero de Threads Criados: ", n_threads
        print "Ficheiros Cifrados: ", encryptedFiles
        print "Ficheiros Decifrados: ", decryptedFiles

    except ValueError as e:
        print 'n_proc tem que ser int', e