#- library var
#set STD_LIB $::env(VERILOG_LIB_WC)
set STD_LIB mycells.lib

#- design var
set DESIGN_FILE ../src/ecc_11to16.v
set DESIGN_NAME ecc_11to16 

yosys -import

#- read design
read_verilog -sv $DESIGN_FILE

#- set top
hierarchy -top $DESIGN_NAME

#- generic synthesis 
synth -top $DESIGN_NAME -nofsm

#- optimize design
opt -purge

#- generic technology mapper
techmap

# technology mapping of flip-flops
dfflibmap -liberty $STD_LIB
opt -undriven

#abc -D [expr $CLK_PERIOD_NS * 1000] -liberty $STD_LIB -showtmp -script $abc_script
abc -liberty $STD_LIB 

# replace undef values with defined constants
setundef -zero

# Splitting nets resolves unwanted compound assign statements in netlist (assign {..} = {..}
splitnets

# remove unused cells and wires
opt_clean -purge

# reports
tee -o synth_check.log check
tee -o synth_stat.log stat -liberty $STD_LIB

# write synthesized design
write_verilog -noattr -noexpr -nohex -nodec ${DESIGN_NAME}_gate.v
