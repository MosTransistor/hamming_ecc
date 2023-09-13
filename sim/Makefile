sim:
	iverilog -g2012 -o sim.o  ./tb_ecc.sv ../src/ecc_11to16.v
	vvp sim.o

wave:
	gtkwave *.vcd

clean:
	rm -rf *.o *.vcd