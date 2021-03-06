#!/usr/bin/env python

import argparse
import os

Pre=0
Gen=0
Cuff=0
Tran=0
Sum=0

########ERCC Spike Ins add to this#######

Library_Info = {}
#Lib=""
#ParamNum=""
def makeArgs():
    parser = argparse.ArgumentParser(
        description = "This script parses input and creates jobs")
    parser.add_argument("-input","--input_file",
                        required=True,
                        help="Input file")
    parser.add_argument("-params","--parameters",
                        required=True,
                        help="Parameter File")
    parser.add_argument("Modules",
                        help="Desired Module",
                        #choices=['pre','gen','cuff','tran','sum','all'],
                        default="all",
                        nargs='*')

    return parser

if __name__ == "__main__":
    arguments = makeArgs()
    arguments = arguments.parse_args()
    Inputfile = arguments.input_file
    Parameters = arguments.parameters
    Modules = arguments.Modules
    if Modules == "all":
        Pre=1
        Gen=1
        Cuff=1
        Tran=1
        Sum=1
    else:
        for module in Modules:
            if module == "pre":
                Pre=1
            if module == "gen":
                Gen=1
            if module == "cuff":
                Cuff=1
            if module == "tran":
                Tran=1
            if module == "sum":
                Sum=1
    ###Getting Contamination Data###
    #os.system("./RQCcontam.py "+Inputfile)
    #os.system("module load R")
    #os.system("Rscript RQCPlot.R ./RQCcontam.csv ./RQCPlot.pdf")
    ###Plotting Contamination Data###

    Input = open(Inputfile,"r")
    for lines in Input:
        line=lines.strip("\n")
        line=line.split()
        if len(line) != 2:
            print "Error Input File needs to have two columns"
            exit()
        else:
            Lib=line[0]
            Library_Info[Lib] = []
            ParamNum=line[1]
            Params=open(Parameters,"r")
            for parameters in Params:
                para=parameters.strip("\n")
                para=para.split()
                if len(para) != 15:
                    print "Error Parameter File needs to have 14 columns"
                    exit()
                else:
                    ParamsNum=para[0]
                    if ParamsNum==ParamNum:
                        Library_Info[Lib].append(Lib)
                        Fasta=para[1]
                        Library_Info[Lib].append(Fasta)
                        Ref=para[2]
                        Library_Info[Lib].append(Ref)
                        Gff=para[3]
                        Library_Info[Lib].append(Gff)
                        GENin=para[4]
                        Library_Info[Lib].append(GENin)
                        TRANin=para[5]
                        Library_Info[Lib].append(TRANin)
                        ERCC=para[6]
                        Library_Info[Lib].append(ERCC)
                        Insert_Size=para[7]
                        Library_Info[Lib].append(Insert_Size)
                        Read_Length=para[8]
                        Library_Info[Lib].append(Read_Length)
                        TopHat_Mate=para[9]
                        Library_Info[Lib].append(TopHat_Mate)
                        Min_Intron=para[10]
                        Library_Info[Lib].append(Min_Intron)
                        Max_Intron=para[11]
                        Library_Info[Lib].append(Max_Intron)
                        Bowtie_Min=para[12]
                        Library_Info[Lib].append(Bowtie_Min)
                        Bowtie_Max=para[13]
                        Library_Info[Lib].append(Bowtie_Max)
                        Ref_id=para[14]
                        Library_Info[Lib].append(Ref_id)

print Library_Info.items()
Qsub_File = open("./qsub.sh","w+")
Qsub_File.write("#!/bin/bash" + "\n" + "\n")

count=1
for key in Library_Info:
    os.mkdir("./%s" % key)
    if Pre > 0:
        Qsub_File.write("qsub -N %s_RNAFil -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd ./RNAFilter.sh " % key +  Library_Info[key][0] + " " + Library_Info[key][1] + " " + Library_Info[key][6] + "\n")
    if Gen > 0:
        Qsub_File.write("qsub -N %s_GenomeMap -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd -hold_jid %s_RNAFil ./GenomeMap.sh " % (key,key) + Library_Info[key][0] + " " + Library_Info[key][9] + " " + Library_Info[key][10] + " " + Library_Info[key][11] + " " + Library_Info[key][3] + " " + Library_Info[key][4] + " " + Library_Info[key][0] + "\n")
    if Cuff > 0:
        Qsub_File.write("qsub -N %s_Cuff -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd -hold_jid %s_GenomeMap ./Cufflinks.sh " % (key,key) + Library_Info[key][3] + " " + Library_Info[key][11] + " " + Library_Info[key][2] + " " + Library_Info[key][0] + "\n")
    if Tran > 0:
        Qsub_File.write("qsub -N %s_TransMap -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd -hold_jid %s_RNAFil ./TransMap.sh " % (key,key) + Library_Info[key][0] + " " + Library_Info[key][12] + " " + Library_Info[key][13] + " " + Library_Info[key][5] + "\n")
    if Sum > 0:
        if count == len(Library_Info.keys()):
            Qsub_File.write("qsub -N %s_Sum -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd -hold_jid %s_Cuff ./CompilingRNASeqResults.py " % (key,key) + Inputfile + "\n")
            #Qsub_File.write("qsub -N Completion_Check -b yes -w e -pe pe_slots 16 -l ram.c=1G -l h_rt=12:00:00 -cwd -hold_jid %s_Sum ./Completion_Check.py " % key + Inputfile + "\n")
    count+=1
Qsub_File.close()
os.system("chmod 755 qsub.sh")
os.system("./qsub.sh")





