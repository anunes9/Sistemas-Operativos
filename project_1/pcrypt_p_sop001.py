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

import os
import sys
from multiprocessing import Process, Value, Queue, Semaphore
from Crypto.Cipher import AES
from Crypto import Random

completed_files = Value('i', 0)
block = Value('i', True)
files_queue = Queue()
sem = Semaphore(1)
a = True

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

    print 'a cifrar ficheiro', filename

    #Chave Generator
    size_chave = 32
    chave = Random.new().read(size_chave)

    #File Key Generator
    file_chave = filename + ".key"

    #Create File .key
    file = open(file_chave,"w") #Creating a new file
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

    #Read key file
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

def encrypt(v):

    global a

    while files_queue.empty() == False:

        sem.acquire()

        if files_queue.empty() == False and a:
            
            filename = files_queue.get()
            sem.release()

        else:
            a = False
            pass

        try:

            open(filename,"r")

            cifrar(filename)

            completed_files.value += 1

        except IOError as e:
            if v:
                print 'ficheiro nao existe', e
                a = False
                while files_queue.empty() == False:
                    files_queue.get()
            else:
                pass


def decrypt(v):
    global a

    while files_queue.empty() == False:

        sem.acquire()

        if files_queue.empty() == False and a:
            
            filename = files_queue.get()
            sem.release()

        else:
            a = False
            pass

        try:

            open(filename,"r")

            decifrar(filename)

            completed_files.value += 1

        except IOError as e:
            if v:
                print 'ficheiro nao existe', e
                a = False
                while files_queue.empty() == False:
                    files_queue.get()
            else:
                pass


def create_processes_encrypt(n, l, v):
    #creates all processes and adds them to the list
    for _ in xrange(n):
        p = Process(target=encrypt, args=(v,))
        l.append(p)

def create_processes_decrypt(n, l, v):
    #creates all processes and adds them to the list
    for _ in xrange(n):
        p = Process(target=decrypt, args=(v,))
        l.append(p)


def chose_files():
    #asks with are the files to encrypt or decrypt
    filename = raw_input("qual o nome do ficheiro?\n")

    while len(filename) != 0:
        files_queue.put(filename)
        filename = raw_input("qual o nome do ficheiro?\n")

def fill_queue_with_files(files):
    for f in files:
        files_queue.put(f)

if __name__ == '__main__':
    l = []
    args = sys.argv[1:]
    a = True

    try:
        if args[0] == '-e':
            #if args[1] == '-p':
            if '-p' in args:
                n_proc = int(args[2])
                #if args[3] == '-v':
                if '-v' in args:
                    files = args[4:]
                    v = True

                    if len(files) == 0:
                        chose_files()
                        create_processes_encrypt(n_proc, l, v)
                    else:
                        fill_queue_with_files(files)
                        create_processes_encrypt(n_proc, l, v)

                    print 'opcao -e -p ', n_proc, '-v', 'files ', l
                #nao ha -v
                else:
                    files = args[3:]
                    v = False

                    if len(files) == 0:
                        chose_files()
                        print files_queue
                        create_processes_encrypt(n_proc, l, v)
                    else:
                        fill_queue_with_files(files)
                        create_processes_encrypt(n_proc, l, v)

                    print 'opcao -e -p', n_proc, 'files', files_queue.qsize()
            #nao ha -p
            #elif args[1] == '-v':
            elif '-v' in args:
                files = args[2:]
                v = True

                if len(files) == 0:
                    chose_files()
                    n_proc = files_queue.qsize()
                    create_processes_encrypt(n_proc, l, v)
                else:
                    n_proc = len(files)
                    fill_queue_with_files(files)
                    create_processes_encrypt(n_proc, l, v)

                print 'opcao -e -v files', files
            #nao ha -p nem -v
            else:
                files = args[1:]
                v = False

                if len(files) == 0:
                    chose_files()
                    n_proc = files_queue.qsize()
                    create_processes_encrypt(n_proc, l, v)
                else:
                    n_proc = len(files)
                    fill_queue_with_files(files)
                    create_processes_encrypt(n_proc, l, v)

                print 'opcao -e files', files

        elif args[0] == '-d':
            #if args[1] == '-p':
            if '-p' in args:
                n_proc = int(args[2])
                #if args[3] == '-v':
                if '-v' in args:
                    files = args[4:]
                    v = True

                    if len(files) == 0:
                        chose_files()
                        create_processes_decrypt(n_proc, l, v)
                    else:
                        fill_queue_with_files(files)
                        create_processes_decrypt(n_proc, l, v)

                        print 'opcao -d -p ', n_proc, '-v', 'files ', l
                #nao ha -v
                else:
                    files = args[3:]
                    v = False

                    if len(files) == 0:
                        chose_files()
                        create_processes_decrypt(n_proc, l, v)
                    else:
                        fill_queue_with_files(files)
                        create_processes_decrypt(n_proc, l, v)

                    print 'opcao -d -p', n_proc, 'files', files
            #nao ha -p
            #elif args[1] == '-v':
            elif '-v' in args:
                files = args[2:]
                v = True

                if len(files) == 0:
                    chose_files()
                    n_proc = files_queue.qsize()
                    create_processes_decrypt(n_proc, l, v)
                else:
                    n_proc = len(files)
                    fill_queue_with_files(files)
                    create_processes_decrypt(n_proc, l, v)

                print 'opcao -d -v files', files
            #nao ha -p nem -v
            else:
                files = args[1:]
                v = False

                if len(files) == 0:
                    chose_files()
                    n_proc = files_queue.qsize()
                    create_processes_decrypt(n_proc, l, v)
                else:
                    n_proc = len(files)
                    fill_queue_with_files(files)
                    create_processes_decrypt(n_proc, l, v)

                print 'opcao -d files', files
        else:
            #nao houver -e -d
            print 'Erro, tem que escolher as opcoes -e ou -d'

        #inicia os processos
        for p in l:
            p.start()
        #faz join dos processos
        for p in l:
            p.join()

        print 'Ficheiros cifrados/decifrados', completed_files.value

    except ValueError as e:
        print 'O valor de -p tem que ser inteiro', e
