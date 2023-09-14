#!/opt/homebrew/bin/python3

#---------------------------------------------------------#
#- Script      : gen_verilog.py                          -#
#- Author      : W.A                                     -#
#- Date        : Sep/12/23                               -#
#- Description : generate ECC verilog logic              -#
#---------------------------------------------------------#

import os, sys, re
import math
import pdb

if __name__ == "__main__":
    # source data length
    bitLen = int(input("Input Source Data Length : "))

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
    
    # gen verilog
    verName = "ecc_{0}to{1}".format(bitLen, eccLen)
    encLen = bitLen-1
    decLen = eccLen-1
    posLen = math.ceil(math.log(eccLen, 2))-1
    verFile = open(verName+".v", "w")

    # port
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
        if i & (i-1) == 0:
            vLogic = " ^ ".join(["enc_in[{0}]".format(j) for j in eccDict["enc"]["E"+str(int(math.log(i,2)))]])
        elif i == eccLen:
            vLogic = " ^ ".join(["enc_in[{0}]".format(j) for j in eccDict["enc"]["E"+str(parLen-1)]])
        else:
            vLogic = "enc_in[{0}]".format(filDat[i-1])
        verFile.write("assign enc_out[{0}] = {1};\n".format(i-1, vLogic))
    verFile.write("\n")
    
    # decode logic
    verFile.write("//- ECC Decode Logic\n")
    verFile.write("//  Decode Raw Data\n")
    verFile.write("logic [{0}:0] dec_raw;\n".format(encLen))
    vLogic = "{"+",".join(["dec_in[{0}]".format(j-1) for j in range(1, eccLen)[::-1] if j&(j-1) != 0])+"}"
    verFile.write("assign dec_raw = {1};\n\n".format(i, vLogic))

    verFile.write("//  Syndrome Logic\n")
    verFile.write("logic [{0}:0] syndrome;\n".format(parLen-1))
    for i in range(0, parLen):
        if i == (parLen-1):
            vLogic = "^dec_in[{0}:0]".format(decLen)
        else:
            vLogic = " ^ ".join(["dec_in[{0}]".format(j) for j in eccDict["dec"]["D"+str(i)]])
        #vLogic = " ^ ".join(["dec_in[{0}]".format(j) for j in eccDict["dec"]["D"+str(i)]])
        verFile.write("assign syndrome[{0}] = {1};\n".format(i, vLogic))
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
