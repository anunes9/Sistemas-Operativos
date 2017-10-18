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

__author__ = "André Nunes 43304, Miguel Almeida 48314, Tiago Martins 48299"

if __name__ == '__main__':
    args = sys.argv[1:]

try:
    if args[0] == '-c':
        print "Compress"

    elif args[0] == '-d':
        print "Descompress"

    else:
        print "Choose an option: -c | -d"

except Exception as e:
    print "Error:", e
