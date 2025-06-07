SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO1.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/wrappers/dut_test.v

MODULE=dut_test
TOPLEVEL=dut_test
include $(shell cocotb-config --makefiles)/Makefile.sim
