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

import struct, pickle, sys

def write_file(filename):

    with open(filename, "rb") as inFile:
        x = pickle.load(inFile) 

    print "Inicio de execucao:", x[0]
    print "\nDuracao da execucao <minutos:segundos:microsegundos> :", x[1]
    index = 2
    for i in range(x[2]):
        index += 1
        print "\nProcesso:", x[index]
        index += 1
        print "\tFicheiro processado:", x[index]
        index += 1
        print "\t\tTempo de compressao/descompressao:", str(x[index])[0:5], "microsegundos"
        index += 1
        print "\t\tDimensao do ficheiro depois de ser comprimido/descomprimido <em bytes>:", x[index]
        index +=1
        print "\tVolume total de dados escritos em ficheiros <em bytes>:", x[index]

    if (index + 1) == (len(x)-1):
        print "\nVolume total de dados escritos em todos os ficheiros: <em bytes>:", x[len(x)-1]

if __name__ == '__main__':
    write_file(sys.argv[1])
