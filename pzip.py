#!/bin/sh
# -*- coding: utf-8 -*-

##############################
#           Autores:         #
#   André Nunes, NºXXXXX     #
#   Miguel Almeida, Nº48314  #
#   Tiago Martins, Nº48299   #
##############################

# Projeto Sistemas Operativos 2017/2018
# Professores: Dulce Domingos e Pedro Ferreira

# Versão com Processos

from zipfile import ZipFile as Zip
from multiprocessing import Process, Value, Queue, Semaphore
import argparse
import sys
import os

# Sintaxe do comando:
# >python pzip -c|-d [-p n] [-t] {ficheiros}

# Comandos possíveis:

# >python pzip -c -p n -t {ficheiros}
# >python pzip -c -p n {ficheiros}
# >python pzip -c -t {ficheiros}
# >python pzip -c {ficheiros}
# >python pzip -d -p n -t {ficheiros}
# >python pzip -d -p n {ficheiros}
# >python pzip -d -t {ficheiros}
# >python pzip -d {ficheiros}
# >python pzip -c -p n -t
# >python pzip -c -p n
# >python pzip -c -t
# >python pzip -c
# >python pzip -d -p n -t
# >python pzip -d -p n
# >python pzip -d -t
# >python pzip -d


def main():

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-c", help="Comprime um ficheiro", action="store_true")
    group.add_argument("-d", help="Descomprime um ficheiro", action="store_true")

    parser.add_argument("-p", type=int, help="Ativa paralelização", choices=range(10))
    parser.add_argument("-t", help="Ativa qq coisa", action="store_true")
    parser.add_argument("files", help="Lista de ficheiro", nargs="*")

    args = parser.parse_args()
    filenames = []

    procslist = []

    if not args.files:
        filename = raw_input("File Name\n")

        while len(filename) != 0:
            filenames.append(filename)
            filename=raw_input("File Name\n")

    else:

        filenames = args.files

    if not args.c or args.d:
        filename = raw_input("Option (-c/-d)?\n")

        while len(filename) != 0:
            filenames.append(filename)
            filename=raw_input("File Name\n")

    else:

        filenames = args.files

    print args
    print filenames
    print args.p

    if args.c:

        if args.p and args.t:

            arg = True

            for _ in range(args.p):
                proc = Process(target=compress(filename=args.files, files=args.files),
                               args=(arg,))
                procslist.append(proc)

            print procslist

            print ">python pzip -c -p n -t {ficheiros}"

        elif args.p and not args.t:

            arg = True

            for _ in range(args.p):
                proc = Process(target=compress(filename=args.files, files=args.files),
                               args=(arg,))
                procslist.append(proc)

            print procslist

            print ">python pzip -c -p n {ficheiros}"

        elif args.t and not args.p:

            print ">python pzip -c -t {ficheiros}"

        else:

            print ">python pzip -c {ficheiros}"

    if args.d:

        if args.p and args.t:

            arg = True

            create_processes_compress(args.p, procslist, arg)
            print ">python pzip -d -p n -t {ficheiros}"

        elif args.p and not args.t:

            arg = True

            create_processes_compress(args.p, procslist, arg)
            print ">python pzip -d -p n {ficheiros}"

        elif args.t and not args.p:

            print ">python pzip -d -t {ficheiros}"

        else:

            print ">python pzip -d {ficheiros}"


def compress(files, filename):

    """
    Esta opção ativa o modo de compressão do comando pzip, pegando em ficheiros descomprimidos
    e comprime-os num único ficheiro zip.

    :param files: Lista de ficheiros a serem comprimidos
    :param filename: Nome do ficheiro zip a ser criado
    :param dirname: Nome da diretoria onde o ficheiro zip será armazenado
    :return: Ficheiro zip contendo os ficheiros dados
    """

    zf = Zip(filename, 'w')
    zf.write(filename)

    for f in files:
        zf.write(os.path.join(f))

    zf.close()


def decompress(path):

    """
    Esta opção ativa o modo de descompressão do comando pzip, pegando num ficheiro zip e
    extraindo os conteúdos para uma dada diretoria.

    :param path: Caminho do(s) ficheiro(s) a ser(em) descomprimido(s)
    :param dirname: Diretoria para onde se quer extrair o(s) ficheiro(s)
    :return: Um ou mais ficheiros descomprimidos
    """

    zf = Zip(path, 'r')
    zf.extractall()
    zf.close()


def create_processes_compress(num, lis, arg):

    """
    Cria o espaço de memória partilhada para os processos da função compress()
    :param num: Número de processos paralelos
    :param lis: Espaço de memória partilhada dos processos
    :param arg: Assume valores de True ou False
    :return: Uma lista que é um espaço de memória dos processos
    """




def create_processes_decompress(num, lis, arg):
    """
    Cria o espaço de memória partilhada para os processos da função decompress()
    :param num: Número de processos paralelos
    :param lis: Espaço de memória partilhada dos processos
    :param arg: Argumentos de cada processo
    :return: Uma lista que é um espaço de memória dos processos
    """

    for _ in range(num):
        proc = Process(target=decompress(), args=(arg,))
        lis.append(proc)

    return lis

if __name__ == "__main__":
    main()