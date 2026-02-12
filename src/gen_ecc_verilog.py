#!/usr/bin/python3

#---------------------------------------------------------#
#- Script      : gen_ecc_verilog.py                      -#
#- Author      : W.A                                     -#
#- Date        : Sep/12/23                               -#
#- Description : generate ECC verilog logic              -#
#---------------------------------------------------------#

import os, sys, re
import math
import time
import pdb

def calc_ecc_structure(bitLen):
    # calculate parity number
    parLen = 1
    filDat = []
    filNum = 0
    eccLen = 1
    locList = []
    while filNum < bitLen:
        if eccLen & (eccLen - 1) == 0:
            filDat.append("P"+str(parLen-1))
            parLen += 1
        else:
            locList.append(re.sub("0b", "", bin(eccLen)))
            filDat.append(filNum)
            filNum += 1
        eccLen += 1
    filDat.append("P"+str(parLen-1))

    eccDict = {"enc":{}, "dec":{}}
    for i in range(0, parLen):
        eccDict["enc"]["E"+str(i)] = []
        eccDict["dec"]["D"+str(i)] = []

    # encode data
    for datLoc in range(0, len(locList)):
        evenNum = 0
        revList = list(reversed(locList[datLoc]))
        for loc in range(0, len(revList)):
            lKey = "E" + str(loc)
            if int(revList[loc]) == 1:
                evenNum += 1
                eccDict["enc"][lKey].append(datLoc)
        if evenNum%2 != 1:
            lKey = "E" + str(parLen - 1)
            eccDict["enc"][lKey].append(datLoc)
    
    # decode data
    for parNum in range(0, parLen):
        encKey = "E" + str(parNum)
        decKey = "D" + str(parNum)
        for dPos in range(0, eccLen):
            if parNum == (parLen - 1):
                eccDict["dec"][decKey].append(str(dPos))
            elif ("P" + str(parNum)) == filDat[dPos]:
                eccDict["dec"][decKey].append(str(dPos))
            elif filDat[dPos] in eccDict["enc"][encKey]:
                eccDict["dec"][decKey].append(str(dPos))
                
    return parLen, eccLen, filDat, eccDict

def write_xor_logic(verFile, prefix, signals):
    verFile.write(prefix)
    indent = " " * len(prefix)
    line_items = 6
    
    max_len = max([len(s) for s in signals]) if signals else 0
    
    for i, sig in enumerate(signals):
        is_last = (i == len(signals) - 1)
        is_line_end = ((i + 1) % line_items == 0)
        
        if not is_last:
            verFile.write("{0:<{1}}".format(sig, max_len))
            if is_line_end:
                verFile.write(" ^\n" + indent)
            else:
                verFile.write(" ^ ")
        else:
            verFile.write(sig)
            verFile.write(" ;\n")

def gen_verilog_code(bitLen, eccLen, parLen, filDat, eccDict):
    verName = "ecc_{0}to{1}".format(bitLen, eccLen)
    encLen = bitLen-1
    decLen = eccLen-1
    posLen = math.ceil(math.log(eccLen, 2))-1
    verFile = open(verName+".v", "w")

    # port
    f1 = lambda x, y: x if len(x) > y else x+" "*(y-len(x))
    verFile.write("""
//---------------------------------------------------------//
//- Author      : W.A                                     -//
//- Date        : {0}          -//
//- Description : auto generate by gen_ecc_verilog.py     -//
//---------------------------------------------------------//\n
""".format(f1(time.strftime("%A %b-%d-%Y", time.localtime()), 30)))
    
    verFile.write("module "+ verName + "(\n")
    verFile.write("  input   logic  [{0}:0]  enc_in,\n".format(encLen))
    verFile.write("  output  logic  [{0}:0]  enc_out,\n".format(decLen))
    verFile.write("  input   logic  [{0}:0]  dec_in,\n".format(decLen))
    verFile.write("  output  logic  [{0}:0]  dec_out,\n".format(encLen))
    verFile.write("  output  logic           err_correct,\n")
    verFile.write("  output  logic           err_uncorrect,\n")
    verFile.write("  output  logic  [{0}:0]  err_location\n".format(posLen))
    verFile.write(");\n\n")

    # encode logic
    verFile.write("//- ECC Encode Logic\n")
    for i in range(1, eccLen+1):
        signals = []
        if i & (i-1) == 0:
            signals = ["enc_in[{0}]".format(j) for j in eccDict["enc"]["E"+str(int(math.log(i,2)))]]
            write_xor_logic(verFile, "assign enc_out[{0}] = ".format(i-1), signals)
        elif i == eccLen:
            signals = ["enc_in[{0}]".format(j) for j in eccDict["enc"]["E"+str(parLen-1)]]
            write_xor_logic(verFile, "assign enc_out[{0}] = ".format(i-1), signals)
        else:
            vLogic = "enc_in[{0}]".format(filDat[i-1])
            verFile.write("assign enc_out[{0}] = {1};\n".format(i-1, vLogic))
    verFile.write("\n")
    
    # decode logic
    verFile.write("//- ECC Decode Logic\n")
    verFile.write("//  Decode Raw Data\n")
    verFile.write("logic [{0}:0] dec_raw;\n".format(encLen))
    
    vLogic = "{"+",".join(["dec_in[{0}]".format(j-1) for j in range(1, eccLen)[::-1] if j&(j-1) != 0])+"}"
    verFile.write("assign dec_raw = {0};\n\n".format(vLogic))

    verFile.write("//  Syndrome Logic\n")
    verFile.write("logic [{0}:0] syndrome;\n".format(parLen-1))
    for i in range(0, parLen):
        signals = []
        if i == (parLen-1):
            verFile.write("assign syndrome[{0}] = ^dec_in[{1}:0];\n".format(i, decLen))
        else:
            signals = ["dec_in[{0}]".format(j) for j in eccDict["dec"]["D"+str(i)]]
            write_xor_logic(verFile, "assign syndrome[{0}] = ".format(i), signals)
    verFile.write("\n")
    
    verFile.write("//  Decode Data output\n")
    verFile.write("logic [{0}:0] ecc_xor;\n".format(decLen))
    vLogic = "1'b1 << {{!syndrome[{0}], syndrome[{1}:0]}}".format(parLen-1, parLen-2)
    verFile.write("assign ecc_xor = {0};\n".format(vLogic))
    verFile.write("logic [{0}:0] dec_xor;\n".format(encLen))
    vLogic = "{"+",".join(["ecc_xor[{0}]".format(j) for j in range(1, eccLen)[::-1] if j&(j-1) != 0])+"}"
    verFile.write("assign dec_xor = {0};\n".format(vLogic))
    verFile.write("assign dec_out = dec_raw ^ dec_xor;\n\n")

    verFile.write("//  Decode Error message\n")
    verFile.write("assign err_correct = syndrome[{0}];\n".format(parLen-1))
    verFile.write("assign err_uncorrect = (!syndrome[{0}]) & (|syndrome[{1}:0]);\n".format(parLen-1, parLen-2))
    verFile.write("assign err_location = syndrome[{0}:0]-1;\n\n".format(parLen-2))

    verFile.write("endmodule\n")
    verFile.close()

if __name__ == "__main__":
    # source data length
    bitLen = int(input("Input Source Data Length : "))
    
    parLen, eccLen, filDat, eccDict = calc_ecc_structure(bitLen)
    gen_verilog_code(bitLen, eccLen, parLen, filDat, eccDict)
