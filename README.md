# hamming_ecc
[Verilog+Python] python script automatic generated hamming ECC verilog code

## 概述/Overview
基于汉明码规则的python脚本，可以自动生成数字逻辑电路代码，支持输入任意的数据长度
>An python script based on the hamming code arithmetic that can automatic generate verilog code. the script support input any data bit width
>
## 接口/interface  
| IO | direction | description | 
| --- | --- | --- |
| enc_in | input | pre data without encode |
| enc_out | output | post data with encode, raw data and parity |
| dec_in | input | pre data without decode, raw data and parity |
| dec_out | output | post data with decode |
| err_correct | output | 1-bit correctable error occurred |
| err_uncorrect | output | multi-bit uncorrectable error occurred |
| err_location | output | the location where the correctable error occurred (for example, output 2 means dec_in[2] is the error position) |  

## 脚本介绍/script introduce  
1. 脚本使用启动：”python3 ./gen_ecc_verilog.py“
2. 输入需要ecc保护的数据长度：”Input Source Data Length : “
3. 产生对应的verilog代码，ecc_xtox.v
比如：输入数据长度：11，则会产生ecc_11to16.v。命名规则：11是原始数据长度，16为数据加上校验码的长度
>1. script usage: "python3 ./gen_ecc_verilog.py"
>2. input the unprotected raw data length: "Input Source Data Length: "
>3. generate verilog code, like ecc_xtox.v
>for example: input data length: 11, will generate ecc_11to16.v. 11 means raw data length, 16 means raw data with parity length
>
## 数据统计/statistics
| data length | parity length |
| --- | --- |
| 1 | 3 |
| 2~4 | 4 |
| 5~11 | 5 |
| 12~26 | 6 |
| 27~57 | 7 |
| 58~120 | 8 |
| 121~247 | 9 |

## 数据结构/database
src -> python源代码    
sim(Icarus Verilog + gtkwave) -> 仿真   
syn(yosys) -> 综合  
>python script in "src" folder, simulation in "sim" folder, synthesis in "syn" folder
>
## 备注/comment
仿真目录：“make sim”执行编译，“make wave”打开波形；综合目录：“make syn”执行综合  
> in "sim" folder, "make sim" for compile, "make wave" for open waveform; in "syn" folder, "make syn" for synthesis
> 
    
