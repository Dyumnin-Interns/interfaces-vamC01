import cocotb
import random
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep
from cocotb_bus.drivers import BusDriver

def cb_fn(av):
    global exp_val
    assert actual_value==exp_val.pop(0), "EEEE"

@cocotb.test()
async def dut_test(dut):
    global exp_val
    dut.RST_N.value=1
    await Timer(1,'ns')
    dut.RST_N.value=0
    await Timer(1,'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value=1
    ##dut.RST_N.value=1
    wd=InputDriver(dut,'',dut.CLK)
   
    await Timer(1, 'ns')
    exp_val=[]
    for i in range(10):
        wrd=random.randint(0,1)
        wra=random.randint(4,5)
        x=val(wra,wrd,3)
        exp_val.append(wrd)
        wd.append(x)
    await Timer(500,'ns')
    OutputDriver(dut,'',dut.CLK,cb_fn)


class InputDriver(BusDriver):
    _signals=['read_address','read_data','read_en','write_address','write_data','write_en','write_rdy','read_rdy']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.write_en.value = 0
        self.bus.read_en.value = 0
        self.clk = clk

    async def _driver_send(self,value,sync=True):
        if self.bus.read_rdy.value!=1:
            await RisingEdge(self.bus.read_rdy)
            self.bus.read_en.value=1
            self.bus.read_address.value= value.read_address
            await ReadOnly()
            await RisingEdge(self.clk)
            self.bus.read_en.value=0
            await NextTimeStep()
        if self.bus.write_rdy.value!=1:
            await RisingEdge(self.bus.write_rdy)
            self.bus.read_en.value=1
            self.bus.write_data.value= value.write_data
            self.bus.write_address.value= value.write_address
            await ReadOnly()
            await RisingEdge(self.clk)
            self.bus.read_en.value=0
            await NextTimeStep()


class OutputDriver(BusDriver):
    _signals=['read_address',
	   'read_data',
	   'read_en',
	   'read_rdy',]
    def __init__(self,dut,name,clk,sb_callback):
        BusDriver.__init__(self,dut,name,clk)
        self.bus.read_en.value = 0
        self.clk = clk
        self.callback=sb_callback
        self.append(0)
    async def _driver_send(self,value,sync=True):
        while True:
            if self.bus.read_rdy.value!=1:
                await RisingEdge(self.bus.read_rdy)
                self.bus.read_en.value=1
                #self.bus.data.value= valueawait
                await ReadOnly()
                self.callback(self.bus.read_data.value)
                await RisingEdge(self.clk)
                self.bus.read_en.value=0
                await NextTimeStep()

class val:
    def __init__(self,write_address,write_data,read_address):
        self.write_address=write_address
        self.write_data=write_data
        self.read_address=read_address 
