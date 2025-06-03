import cocotb
import random
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os

def cb_fn(av):
    global exp_val
    assert exp_val,"no exp_val"
    ee=exp_val.pop(0)
    assert av==ee, "EEEE"

@CoverPoint("top.write_address",xf=lambda x, y, z:x, bins=[4,5])

@CoverPoint("top.read_address",xf=lambda x, y, z:y, bins=[0,1,2,3])

@CoverPoint("top.write_data",xf=lambda x, y, z:z, bins=[0,1])

@CoverCross("top.cross.wwr",items=['top.write_address','top.read_address','top.write_data'])

def dum(write_address,read_address,write_data):
    pass

@CoverPoint("top.port.wr.current",
           xf=lambda x:x['current'],
           bins=['IDLE','wrt_read_and_write_rdy_tnx','read_rdy_wrt_tnx','write_rdy_rd_tnx','read_and_write']
           )

@CoverPoint("top.port.wr.previous",
           xf=lambda x:x['previous'],
           bins=['IDLE','wrt_read_and_write_rdy_tnx','read_rdy_wrt_tnx','write_rdy_rd_tnx','read_and_write']
           )

@CoverCross("top.cross.wr_port.cross",
            items=["top.port.wr.current",
                   "top.port.wr.previous"]
            )

def wr_port_cover(tnx):
    pass


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
    exp_val=[]
    wd=InputDriver(dut,'',dut.CLK)
    #await Timer(10, 'ns')
    IO_monitor(dut,'',dut.CLK,callback=wr_port_cover)
    OutputDriver(dut,'',dut.CLK,cb_fn)
    #exp_val=[]
    for i in range(300):
        wdx=random.randint(0,1)
        wax=random.randint(4,5)
        rax=random.randint(0,3)
        x=val(wax,wdx,rax)
        #exp_val.append(wdx)
        wd.append(x)
        exp_val.append(wdx)
        dum(wax,rax,wdx)
    #while len(exp_val)>0:
      #await Timer(2,'ns')
    await Timer(len(exp_val)*2,'ns')

    #OutputDriver(dut,'',dut.CLK,cb_fn)

    

    coverage_db.report_coverage(cocotb.log.info,bins=True)
    coverage_file=os.path.join(os.getenv('RESULT_PATH', "./"),'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)
   


class InputDriver(BusDriver):
    _signals=['write_rdy','read_rdy','write_address','write_data','write_en','read_address','read_en','read_data']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.write_en.value = 0
        self.bus.read_en.value = 0
        self.clk = clk

    async def _driver_send(self,value,sync=True):
        if self.bus.write_rdy.value!=1:
            await RisingEdge(self.bus.write_rdy)
        self.bus.write_en.value=1
        self.bus.write_data.value= value.write_data
        self.bus.write_address.value= value.write_address
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.write_en.value=0
        await NextTimeStep()
        if self.bus.read_rdy.value!=1:
            await RisingEdge(self.bus.read_rdy)
        self.bus.read_en.value=1
        self.bus.read_address.value= value.read_address
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.read_en.value=0
        await NextTimeStep()

class  IO_monitor(BusMonitor):
    _signals =['write_rdy','read_rdy','write_en','write_address','write_data','read_en','read_address']
    async def _monitor_recv(self):
        fallingedge=FallingEdge(self.clock)
        rdonly=ReadOnly()
        phases={
                0:'IDLE',
                5:'wrt_read_and_write_rdy_tnx',
                7:'read_rdy_wrt_tnx',
                13:'write_rdy_rd_tnx',
                15:'read_and_write'
        }
        prev='IDLE'
        while True:
            await fallingedge
            await rdonly
            tnx= (self.bus.read_en.value<<3)|(self.bus.read_rdy.value<<2)|(self.bus.write_en.value<<1)|(self.bus.write_rdy.value)
            self._recv({'previous':prev,'current':phases.get(tnx,'NOTHING')})
            prev=phases.get(tnx,'NOT')
            

class OutputDriver(BusDriver):
    _signals=['read_rdy','read_address',
	   'read_en',
	   'read_data',]
    def __init__(self,dut,name,clk,sb_callback):
        BusDriver.__init__(self,dut,name,clk)
        self.bus.read_en.value = 0
        self.clk = clk
        self.callback=sb_callback
        self._driver_send(0)
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
