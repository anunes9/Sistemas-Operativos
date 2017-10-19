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

import sys
from zipfile import ZipFile
import argparse

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

if __name__ == '__main__':
    args = sys.argv[1:]

# Combinacoes possivies
# -c -p n -t {files}
# -c -p n {files}
# -c -t {files}
# -c {files}

# try:
#     if args[0] == '-c':
#         print "Compress"

#     elif args[0] == '-d':
#         print "Descompress"

#     else:
#         print "Choose an option: -c | -d"

# except Exception as e:
#     print "Error:", e

parser = argparse.ArgumentParser()

group = parser.add_mutually_exclusive_group()
group.add_argument("-c", help="Compress files", action="store_true")
group.add_argument("-d", help="Decompress files", action="store_true")

parser.add_argument("-p", type=int, choices=range(10), help="Number os process")
parser.add_argument("-t", help="Finish whem file not found", action="store_true")
parser.add_argument("files", nargs='*', help="Files to Compress/Decompress")

args = parser.parse_args()
filesnames = []

if args.files == []:
    filename = raw_input("qual o nome do ficheiro?\n")

    while len(filename) != 0:
        filesnames.append(filename)
        filename = raw_input("qual o nome do ficheiro?\n")
else:
    filesnames = args.files

print "python pzip.py", args, "filesnames", filesnames
