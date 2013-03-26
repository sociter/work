"""
This module is used to parser matrix excel file.
These modules are required: os, sys, string, re, time, logging, xlrd
"""
###############################################################################
# Copyright (c) 2013 @ Spreadtrum Communication Inc.
# Spreadtrum Confidential Property. All rights are reserved.
#
# File name   : MatrixExcelParser.py {{{
# Author      : 
# Date        : 2013/03/10
# Description : Bus Matrix Generator
#
# Version     : 0.10 - initial version. (2012/11/10) 
#               0.20 - dot generation.  (2013/03/05) 
#}}}
###############################################################################

# -*- coding:utf-8 -*-  
__metaclass__ = type


import os, sys,string,re
import time
import logging
import xlrd

MEP_VERSION   = 0.30

# {{{ global functions
def timestamp():
    return time.strftime('%Y%m%d%H%M%S', time.localtime())

def date():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def year():
    return time.strftime('%Y', time.localtime())

def user():
    return os.environ["USERNAME"]

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def saveFile(filePath, buf):
    print "save file: ", filePath
    if not os.path.exists(filePath):
        temp = os.path.dirname(filePath)
        if not os.path.exists(temp):
            os.makedirs(temp)
    else:
        os.remove(filePath)
    f = open(filePath,'w')
    f.write(buf)
    f.close()

def getopts(argv):
    opts = {}
    last_key = ''
    while argv:
        if not argv[0]:
            pass
        elif len(argv[0])>0:
            if argv[0][0] == '-':
                opts[argv[0]] = ''
                last_key = argv[0]
                last_value = None
            else:
                last_value = argv[0]
                if last_key:
                    if opts[last_key] == '':
                        opts[last_key] = argv[0]
                    else:
                        opts[last_key] = [opts[last_key]]
                        opts[last_key].append(argv[0])
        argv = argv[1:]
        print "opts is ", opts
        return opts

def abs_pos2excel_pos(row, col): 
    excel_row = row + 1
    excel_col = col 

    cur_col_mod = col % 26
    cur_col_div = col / 26

    if cur_col_mod == 0 : excel_col = 'A'
    if cur_col_mod == 1 : excel_col = 'B'
    if cur_col_mod == 2 : excel_col = 'C'
    if cur_col_mod == 3 : excel_col = 'D'
    if cur_col_mod == 4 : excel_col = 'E'
    if cur_col_mod == 5 : excel_col = 'F'
    if cur_col_mod == 6 : excel_col = 'G'
    if cur_col_mod == 7 : excel_col = 'H'
    if cur_col_mod == 8 : excel_col = 'I'
    if cur_col_mod == 9 : excel_col = 'J'
    if cur_col_mod == 10: excel_col = 'K'
    if cur_col_mod == 11: excel_col = 'L'
    if cur_col_mod == 12: excel_col = 'M'
    if cur_col_mod == 13: excel_col = 'N'
    if cur_col_mod == 14: excel_col = 'O'
    if cur_col_mod == 15: excel_col = 'P'
    if cur_col_mod == 16: excel_col = 'Q'
    if cur_col_mod == 17: excel_col = 'R'
    if cur_col_mod == 18: excel_col = 'S'
    if cur_col_mod == 19: excel_col = 'T'
    if cur_col_mod == 20: excel_col = 'U'
    if cur_col_mod == 21: excel_col = 'V'
    if cur_col_mod == 22: excel_col = 'W'
    if cur_col_mod == 23: excel_col = 'X'
    if cur_col_mod == 24: excel_col = 'Y'
    if cur_col_mod == 25: excel_col = 'Z'

    if cur_col_div == 1: excel_col = 'A'+excel_col
    if cur_col_div == 2: excel_col = 'B'+excel_col
    if cur_col_div == 3: excel_col = 'C'+excel_col

   #self.logger.debug("col %3d %3d %3d %s"%(col, cur_col_div, cur_col_mod, excel_col))

    return excel_row, excel_col

# formatbin 
def int2bin(int_val, bit_width):
    str_val = bin(int_val)
    if str_val.startswith('-'):
        return(str_val[0:1] + str_val[3:]).zfill(bit_width)
    return str_val[2:].zfill(bit_width)
def bin2int(bin_str):
    return int(bin_str, 2)
def bin_bits_get(int_val, bit_width, lsb, msb):
    lsb_rvs = bit_width-msb-1
    msb_rvs = bit_width-lsb
    val_str = int2bin(int_val, bit_width)
    fld_str = val_str[lsb_rvs:msb_rvs]
    #print fld_str
    return bin2int(fld_str)
def bin_bits_set(int_val, bit_width, fld_val, lsb, msb):
    val_list = list(int2bin(int_val, bit_width))
    fld_list = list(int2bin(fld_val, msb-lsb+1))
    val_list.reverse()
    fld_list.reverse()
    for n in range(lsb, msb+1):
        val_list[n] = fld_list[n-lsb]
    val_list.reverse()
    val_str = ''.join(val_list)
    return bin2int(val_str)
    
# }}}

class Object: #{{{
    """ 
    Base class used for the module's other class.
"""
    
    def __init__(self, logger, name="un-named-Object", parent=None):
        self.name   = name
        self.logger = logger
        self.parent = parent

    def get_name(self):
        """ Get object's name. """
        return self.name
    def set_name(self, name):
        """ Set object's name. """
        self.name = name

    def get_logger(self):
        """ Get object's logger handle. """
        return self.logger
    def set_logger(self, logger):
        """ Set object's logger handle. """
        self.logger = logger

    def get_parent(self):
        return self.parent
    def set_parent(self, parent):
        self.parent = parent
#}}}

class MatrixChannel(Object): #{{{
    """
    Bus matrix channel class.
    The master or slave channel class extends from this class.
"""
    
    def __init__(self, logger, name="un-name-MatrixChannel", parent=None, protocol='AHB', idx=0, dw=32, active=False):
        Object.__init__(self, logger, name, parent)
        self.protocol = protocol    # channel protocol type: AHB, AXI or APB
        self.idx = idx              # index number in matrix
        self.dw = dw                # data bit width
        self.active = active        # active or passive
        self.clock = ''             # clock signal name
        self.reset = ''             # reset signal name
        self.function_name = ''     # function name, unique in the whole excel range
        self.port_name = ''         # channle port prefix or postfix name unique in the matrix range

        self.type = ''              # master or slave
        self.vfile = ''             # corresponding verilog file
        self.hier = ''              # corresponding instance hierachy path
        self.con_port_list = []     # protocol interface port connect list, support simple regular expression

        #self.path_list = []         # path list
        self.path_list_dict = {}    # path list dictionary
        
        # parameters for AXI protocol, valid only protocol type equal 'AXI'
        self.axi_arbitration = ''
        self.axi_fifo_depth = 0
        self.axi_outstanding = 0
        self.axi_regslice = ''
        self.axi_idw = 0            # AXI id bit width, valid only protocol type equal 'AXI'

    def get_sheet_name(self): #{{{
        return self.parent.get_sheet_name()
    #}}}
    def get_sobj(self): #{{{
        return self.parent.get_sobj()
    #}}}
    def get_mtx_name(self): #{{{
        return self.parent.get_name()    
    #}}}
    def get_parser_obj(self): #{{{
        return self.parent.get_parent()
    #}}}

    def get_type(self): #{{{
        """ Get channel type: master or slave.  """
        return self.type
    #}}}
    def set_type(self, type): #{{{
        """ Set channel type: master or slave. """
        self.type = type
    #}}}
       
    def get_protocol(self):#{{{
        return self.protocol
    #}}}
    def set_protocol(self, protocol): #{{{
        self.protocol = protocol
    #}}}

    def get_idx(self): #{{{
        return self.idx
    #}}}
    def set_idx(self, idx): #{{{
        self.idx = idx
    #}}}

    def get_dw(self): #{{{
        return self.dw
    #}}}
    def set_dw(self, dw): #{{{
        self.dw = dw
    #}}}

    def is_active(self): #{{{
        return self.active
    #}}}
    def set_active(self, active): #{{{
        self.active = active
    #}}}
    
    def get_clock(self): #{{{
        return self.clock
    #}}}
    def set_clock(self, clock): #{{{
        self.clock = clock
    #}}}

    def get_reset(self): #{{{
        return self.reset
    #}}}
    def set_reset(self, reset): #{{{
        self.reset = reset
    #}}}

    def get_function_name(self): #{{{
        return self.function_name
    #}}}
    def set_function_name(self, function_name): #{{{
        self.function_name = function_name
    #}}}
    
    def get_port_name(self): #{{{
        return self.port_name
    #}}}
    def set_port_name(self, port_name): #{{{
        self.port_name = port_name
    #}}}

    def get_vfile(self): #{{{
        return self.vfile
    #}}}
    def set_vfile(self, vfile): #{{{
        self.vfile = vfile
    #}}}

    def get_hier(self): #{{{
        return self.hier
    #}}}
    def set_hier(self, hier): #{{{
        self.hier = hier
    #}}}

    def get_con_port_list(self): #{{{
        return self.con_port_list
    #}}}
    def append_con_port(self, port): #{{{
        self.con_port_list.append(port)
    #}}}

    def get_path_list(self, addr): #{{{
        if(self.path_list_dict.has_key(addr)):
            return self.path_list_dict[addr]
        else:
            return None
    #}}}
    def add_path_list(self, addr, path_list): #{{{
        self.path_list_dict[addr] = path_list
    #}}}

    def get_axi_idw(self): #{{{
        return self.axi_idw
    #}}}
    def set_axi_idw(self, axi_idw): #{{{
        self.axi_idw = axi_idw
    #}}}

    def get_path_str(self, path_list, addr): #{{{
        path_str = "[ADDR: 0x%x] "%addr
        #path_list = self.get_path_list(addr)
        if (path_list == None):
            path_str += 'None' 
        else:
            for node in path_list:
                if isinstance(node, MasterChannel):
                    path_str += "[Mst: %s] --> "%node.get_name()
                elif isinstance(node, SlaveChannel):
                    path_str += "[Slv: %s] "%node.get_name()
                    start_remap_list = node.get_start_remap_list()
                    if(len(start_remap_list)>0):
                        remap_addr = node.remap_addr(addr)
                        path_str += " --> (REMAP: 0x%x to 0x%x) "%(addr, remap_addr)
                    if(node.is_leaf() == False):
                        path_str += " --> "
                else: 
                    path_str += "[Mtx: %s] --> "%node.get_name()
        return path_str
    #}}}

    def __str__(self):
        ret = """[%s.%s]:
            type        :'%s'
            name        :'%s' 
            idx         :'%d'
            protocol    :'%s'
            dw          :'%d'
            active      :'%s'
            clock       :'%s'
            reset       :'%s'
            function    :'%s'
            port_name   :'%s'
            vfile       :'%s', 
            hier        :'%s',
            axi idw     :'%d'"""%(self.parent.sheet_name, self.parent.name, self.type, self.name, self.idx, self.protocol, self.dw, self.active, self.clock, self.reset, self.function_name, self.port_name, self.vfile, self.hier, self.axi_idw)
        return ret


#}}}

class MasterChannel(MatrixChannel): #{{{

    def __init__(self, logger, name="un-named-MasterChannel", parent=None, protocol='AHB', idx=0, dw=32, active=False):
        MatrixChannel.__init__(self, logger, name, parent, protocol, idx, dw, active)
        self.root = False           # is root node or not
        self.slv_dict = {}          # slave dictionary connected with the master
        self.slv_name_dict = {}     # slave name dictionary
        self.type = 'Master'

    def is_root(self): #{{{
        return self.root
    #}}}
    def set_root(self, root): #{{{
        self.root = root
    #}}}

    def get_slv_num(self): #{{{
        return len(self.slv_dict)
    #}}}

    def has_slv_name(self, name): #{{{
        return self.slv_dict.has_key(name)
    #}}}
    def has_slv_idx(self, idx): #{{{
        return self.slv_name_dict.has_key(idx)
    #}}}
    def get_slv_name(self, idx): #{{{
        if(self.slv_name_dict.has_key(idx)):
            return self.slv_name_dict[idx]
        else:
            return ''
    #}}}
    def add_slv(self, idx, slv_obj): #{{{
        if(self.has_slv_idx(idx)):
            self.logger.error("[%s.%s] adding slave id: '%d' has existed already!"%(self.parent.sheet_name, self.parent.name, idx))
            sys.exit()
        slv_name = slv_obj.get_name()
        if(self.has_slv_name(slv_name)):
            self.logger.error("[%s.%s] adding slave name: '%s' has exit already!"%(self.parent.sheet_name, self.parent.name, slv_name))
            sys.exit()
        self.slv_name_dict[idx] = slv_name
        self.slv_dict[slv_name] = slv_obj
    #}}}

    def get_slv_by_name(self, name): #{{{
        if(self.slv_dict.has_key(name)):
            return self.slv_dict[name]
        else:
            return None
    #}}}
    def get_slv_by_idx(self, idx): #{{{
        name = self.get_slv_name(idx)
        if(name != ''):
            return self.get_slv_by_name(name)
        else:
            return None
    #}}}

    def get_slv_idx_list(self): #{{{
        return self.slv_name_dict.keys()
    #}}}

    def get_slv_idx_by_addr(self, addr): #{{{
        hit_cnt = 0
        ret = -1
        slv_idx_list = self.get_slv_idx_list()
        #print slv_idx_list
        for idx in slv_idx_list:
            #print idx
            slv_obj = self.get_slv_by_idx(idx)
            if(slv_obj.is_mem_hit(addr)):
                hit_cnt += 1
                ret = idx
            
        if(hit_cnt>1):
            self.logger.error("[%s.%s.%s] Hit memory address: '0x%h' in %d slaves!"%(self.get_sheet_name(), self.get_mtx_name(), self.get_name(), addr, self.get_name(), hit_cnt))
            sys.exit()
        return ret
    #}}}
    def get_slv_name_by_addr(self, addr): #{{{
        idx = self.get_slv_idx_by_addr(addr)
        if(idx == -1):
            return ''
        else:
            return self.get_slv_name(idx)
    #}}}
    def get_slv_by_addr(self, addr): #{{{
        idx = self.get_slv_idx_by_addr(addr)
        #print "addr=%x, idx=%d"%(addr, idx)
        if(idx == -1):
            return None
        else:
            return self.get_slv_by_idx(idx)
    #}}}

    def seek_path_by_addr(self, path_list, addr): #{{{
        # append self master object to path list
        if(self.is_root()):
            self.add_path_list(addr, path_list)
        #self.logger.debug("Seek path 0x%x: Found a master: '%s'"%(addr, self.name))
        path_list.append(self)
        slv_obj = self.get_slv_by_addr(addr)
        if(slv_obj == None): # can't found mst->slv path
            slv_obj = DummySlave(self.logger, "DUMMY")
            path_list.append(slv_obj)
            return 
        else:
            slv_obj.seek_path_by_addr(path_list, addr)
    #}}}

    def __str__(self): #{{{
        ret = MatrixChannel.__str__(self)
        ret += """
            root        :'%s'
            slv conns   :'%s'"""%(self.root, self.slv_name_dict.keys())
        return ret
    #}}}
#}}}

class SlaveChannel(MatrixChannel): #{{{
    def __init__(self, logger, name="un-name-SlaveChannel", parent=None, protocol='ABH', idx=0, dw=32, active=False):
        MatrixChannel.__init__(self, logger, name, parent, protocol, idx, dw, active)
        self.leaf = False           # is leaf node or not
        self.mst_dict = {}          # master dictionary connected with the slave
        self.mst_name_dict = {}     # master name dictionary
        self.type = "Slave"
        self.start_addr_list = []
        self.end_addr_list = []
        self.start_remap_list = []
        self.end_remap_list = []
        self.addr_dec = ''
        self.addr_remap = ''

    def is_leaf(self): #{{{
        return self.leaf
    #}}}
    def set_leaf(self, leaf): #{{{
        self.leaf = leaf
    #}}}
    def get_mst_num(self): #{{{
        return len(self.mst_dict)
    #}}}
    def has_mst_name(self, name): #{{{
        return self.mst_dict.has_key(name)
    #}}}
    def has_mst_idx(self, idx): #{{{
        return self.mst_name_dict.has_key(idx)
    #}}}
    def get_mst_name(self, idx): #{{{
        if(self.mst_name_dict.has_key(idx)):
            return self.mst_name_dict[idx]
        else:
            return ''
    #}}}
    def add_mst(self, idx, mst_obj): #{{{
        if(self.has_mst_idx(idx)):
            self.logger.error("[%s.%s] adding master id: '%d' has existed already!"%(self.parent.sheet_name, self.parent.name, idx))
            sys.exit()
        mst_name = mst_obj.get_name()
        if(self.has_mst_name(mst_name)):
            self.logger.error("[%s.%s] adding master name: '%s' has exit already!"%(self.parent.sheet_name, self.parent.name, mst_name))
            sys.exit()
        self.mst_name_dict[idx] = mst_name
        self.mst_dict[mst_name] = mst_obj
    #}}}
    def get_mst_by_name(self, name): #{{{
        if(self.mst_dict.has_key(name)):
            return self.mst_dict[name]
        else:
            return None
    #}}}
    def get_mst_by_idx(self, idx): #{{{
        name = self.get_mst_name
        if(name != ''):
            return self.get_mst_by_name(name)
        else:
            return None
    #}}}
    def get_mst_idx_list(self): #{{{
        return self.mst_name_dict.keys()
    #}}}
    def get_start_addr(self, idx): #{{{
        return self.start_addr_list[idx]
    #}}}
    def get_end_addr(self, idx): #{{{
        return self.end_addr_list[idx]
    #}}}
    def get_start_remap(self, idx): #{{{
        return self.start_remap_list[idx]
    #}}}
    def get_end_remap(self, idx): #{{{
        return self.end_remap_list[idx]
    #}}}
    def append_start_addr(self, start_addr): #{{{
        self.start_addr_list.append(start_addr) 
    #}}}
    def append_end_addr(self, end_addr): #{{{
        self.end_addr_list.append(end_addr)
    #}}}
    def append_mem_seg(self, start_addr, end_addr): #{{{
        self.append_start_addr(start_addr)
        self.append_end_addr(end_addr)
    #}}}
    def get_mem_seg(self, idx): #{{{
        saddr = self.get_start_addr(idx)
        eaddr = self.get_end_addr(idx)
        return (saddr, eaddr)
    #}}}
    def get_start_addr_list(self): #{{{
        return self.start_addr_list
    #}}}
    def set_start_addr_list(self, start_addr_list): #{{{
        self.start_addr_list = start_addr_list
    #}}}
    def get_end_addr_list(self): #{{{
        return self.end_addr_list
    #}}}
    def set_end_addr_list(self, end_addr_list): #{{{
        self.end_addr_list = end_addr_list
    #}}}
    def get_start_remap_list(self): #{{{
        return self.start_remap_list
    #}}}
    def set_start_remap_list(self, start_remap_list): #{{{
        self.start_remap_list = start_remap_list
    #}}}
    def get_end_remap_list(self): #{{{
        return self.end_remap_list
    #}}}
    def set_end_remap_list(self, end_remap_list): #{{{
        self.end_remap_list = end_remap_list
    #}}}

    def is_mem_hit(self, addr): #{{{
        hit_cnt = 0
        for idx in range(len(self.start_addr_list)):
            if((addr>=self.start_addr_list[idx]) and (addr<=self.end_addr_list[idx])):
                hit_cnt += 1
        if(hit_cnt > 1):
            self.logger.error("[%s.%s] Hit memory address: '0x%h' in slave '%s' %d times!"%(self.get_sheet_name(), self.get_mtx_name(), addr, self.get_name(), hit_cnt))
            sys.exit()
        return hit_cnt
    #}}}
    def get_mem_list_idx(self, addr): #{{{
        hit_cnt = 0
        ret = -1
        for idx in range(len(self.start_addr_list)):
            if((addr>=self.start_addr_list[idx]) and (addr<=self.end_addr_list[idx])):
                hit_cnt += 1
                ret = idx
        if(hit_cnt > 1):
            self.logger.error("[%s.%s] Hit memory address: '0x%h' in slave '%s' %d times!"%(self.get_sheet_name(), self.get_mtx_name(), addr, self.get_name(), hit_cnt))
            sys.exit()
        return ret
    #}}}

    def get_addr_dec(self): #{{{
        return self.addr_dec
    #}}}
    def set_addr_dec(self, addr_dec): #{{{
        self.addr_dec = addr_dec
    #}}}
    def remap_addr(self, addr): #{{{
        #addr_bin_str = int2bin(addr, 32)
        #print addr_bin_str
        #addr_remap_str = re.sub('\s+', '', addr_remap_str)
        #addr_remap_str = re.sub('_+', '', addr_remap_str)
        #opt = 'eq'
        #if(re.match != ''):
        #    if(re.match('.*\+=', addr_remap_str)):
        #        #print 'found += operator'
        #        [lop, rop] = re.split('\+=', addr_remap_str)
        #        opt = 'plus'
        #    elif(re.match('.*-=', addr_remap_str)):
        #        #print 'found -= operator'
        #        [lop, rop] = re.split('\-=', addr_remap_str)
        #        opt = 'minus'
        #    elif(re.match('.*=', addr_remap_str)):
        #        #print 'found = operator'
        #        [lop, rop] = re.split('=+', addr_remap_str)
        #        opt = 'eq'
        #    else:
        #        self.logger.error("remap addr format invalid: '%s', can't found '=', '+=' or '-=' operator!"%addr_remap_str)
        #        sys.exit()
        ##print 'lop=%s, rop=%s'%(lop, rop)
        #if(re.match("^0?x([0-9a-fA-F]+)|^\d*'?h([0-9a-fA-F]+)", rop)):
        #    #rop = int(rop, 16)
        #    m = re.match("^0?x([0-9a-fA-F]+)|^\d*'?h([0-9a-fA-F]+)", rop)
        #    rop = int(m.group(1), 16)
        #elif(re.match("^\d*'?b([01]+)", rop)):
        #    #rop = int(rop, 2)
        #    m = re.match("^\d*'?b([01]+)", rop)
        #    rop = int(m.group(1), 2)
        #elif(re.match("^\d*'?d([0-9]+)", rop)):
        #    #rop = int(rop)
        #    m = re.match("^\d*'?d([0-9]+)", rop)
        #    rop = int(m.group(1))
        #else:
        #    self.logger.error("remap addr format invalid: %s"%rop)
        #    sys.exit()
        #print "rop=0x%x"%rop
        #b_match = re.match('.*\[(\d+)(:)?(\d+)*\]', lop)
        #if(b_match):
        #    if(b_match.lastindex == 3):
        #        msb = int(b_match.group(1), 10)
        #        lsb = int(b_match.group(3), 10)
        #    else:
        #        lsb = msb = int(b_match.group(1), 10)
        #    #print 'len=%s, lsb=%d, msb=%d'%(b_match.group(0), lsb, msb)
        #    if(opt == 'eq'):
        #        addr = bin_bits_set(addr, 32, rop, lsb, msb) 
        #    elif(opt == 'plus'):
        #        addr_tmp = bin_bits_get(addr, 32, lsb, msb)
        #        addr_tmp += rop
        #        addr = bin_bits_set(addr, 32, addr_tmp, lsb, msb)
        #    elif(opt == 'minus'):
        #        addr_tmp = bin_bits_get(addr, 32, lsb, msb)
        #        addr_tmp -= rop
        #        print "rop=0x%x, addr_tmp=0x%x"%(rop, addr_tmp)
        #        addr = bin_bits_set(addr, 32, addr_tmp, lsb, msb)
        #    #print "addr=0x%x"%addr
        #else:
        #    self.logger.error("remap addr format invalid: '%s', should be addr[lsb:msb]!"%addr_remap_str)
        #    sys.exit()
        idx = self.get_mem_list_idx(addr)
        start_addr = self.get_start_addr(idx)
        start_remap = self.get_start_remap(idx)
        remap_offset = start_remap - start_addr
        remap_addr = addr + remap_offset
        #self.logger.debug("remap addr: 0x%x -> 0x%x(offset:%x)"%(addr, remap_addr, remap_offset))
        return remap_addr
    #}}}
    def seek_path_by_addr(self, path_list, addr): #{{{
        # append parent matrix object and self slave object to path list
        path_list.append(self.get_parent())
        path_list.append(self)
        #self.logger.debug("Seek path 0x%x: Found a matrix: '%s'"%(addr, self.get_mtx_name()))
        #self.logger.debug("Seek path 0x%x: Found a slave: '%s'"%(addr, self.name))
        if(self.is_leaf()): # is the leaf slave and return 
            self.add_path_list(addr, path_list)
            return 
        else: # slave is a path node, to found slv->mst path
            # to found slave's conjoint master object
            parser_obj = self.get_parser_obj()
            mst_obj = parser_obj.get_mst_by_name(self.name)
            if(mst_obj == None):
                self.logger.error("Path node slave '%s' can't found the conjoint master node in [%s.%s]."%(self.name, self.get_sheet_name(), self.get_mtx_name()))
                sys.exit()
            #if(self.addr_remap != ''):
                
            #addr_remap_str = self.get_addr_remap()
            #if(addr_remap_str != ''):
            #    addr = self.remap_addr(addr, addr_remap_str)
            start_remap_list = self.get_start_remap_list()
            if(len(start_remap_list)>0):
                addr = self.remap_addr(addr)
            mst_obj.seek_path_by_addr(path_list, addr)
    #}}}

    def __str__(self): #{{{
        ret = MatrixChannel.__str__(self)
        saddr_hex_list = [hex(addr) for addr in self.start_addr_list]
        eaddr_hex_list = [hex(addr) for addr in self.end_addr_list]
        ret += """
            leaf        :'%s'
            mst conns   :'%s'
            start addr  :'%s', 
            end addr    :'%s'"""%(self.leaf, self.mst_name_dict.keys(), saddr_hex_list, eaddr_hex_list)
        return ret
    #}}}
#}}}

class DummySlave(SlaveChannel): #{{{
    def __init__(self, logger, name="DUMMYSLV"):
        SlaveChannel.__init__(self, logger, name)
        self.leaf = 1
#}}}

class MatrixTableHeader(Object): #{{{

    def __init__(self, logger, name='un-named-MatrixTableHeader', parent=None, sheet_name='', sheet_obj=None, start_row=0):
        Object.__init__(self, logger, name, parent)
        self.sheet_name = sheet_name
        self.sheet_obj = sheet_obj
        self.start_row = start_row
                                      #regr expression             # row number       # col number # width   # height      # value type     # can be empty
        self.matrix_header_dict = {
                    "Name"          : {'regr': "Name"             ,'row':start_row+0 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'string', 'empty':0},
                    "Masters"       : {'regr': "Masters"          ,'row':start_row+1 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'number', 'empty':0},
                    "Slaves"        : {'regr': "Slaves"           ,'row':start_row+2 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'number', 'empty':0},
                    "Vfile"         : {'regr': "Vfile"            ,'row':start_row+3 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'string', 'empty':1},
                    "Instance"      : {'regr': "Instance"         ,'row':start_row+4 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'string', 'empty':1},
                    "GPV"           : {'regr': "GPV"              ,'row':start_row+5 , 'col':3 , 'width':9 , 'height':1 , 'vtype':'string', 'empty':1},

                    "Arbitration"   : {'regr': "Arbitration"      ,'row':start_row+6 , 'col':0 , 'width':12, 'height':12, 'vtype':'string', 'empty':1},
                    "FIFODepth"     : {'regr': "FIFODepth"        ,'row':start_row+7 , 'col':1 , 'width':11, 'height':11, 'vtype':'number', 'empty':1},
                    "Outstanding"   : {'regr': "Outstanding"      ,'row':start_row+8 , 'col':2 , 'width':10, 'height':10, 'vtype':'number', 'empty':1},
                    "Regslice"      : {'regr': "Regslice"         ,'row':start_row+9 , 'col':3 , 'width':9 , 'height':9 , 'vtype':'string', 'empty':1},
                    "IDBitwidth"    : {'regr': "IDBitwidth"       ,'row':start_row+10, 'col':4 , 'width':8 , 'height':8 , 'vtype':'number', 'empty':0},
                    "DataBitwidth"  : {'regr': "DataBitwidth"     ,'row':start_row+11, 'col':5 , 'width':7 , 'height':7 , 'vtype':'number', 'empty':0},
                    "Protocol"      : {'regr': "Protocol"         ,'row':start_row+12, 'col':6 , 'width':6 , 'height':6 , 'vtype':'string', 'empty':0},
                    "Clock"         : {'regr': "Clock"            ,'row':start_row+13, 'col':7 , 'width':5 , 'height':5 , 'vtype':'clock' , 'empty':0},
                    "Function"      : {'regr': "Function"         ,'row':start_row+14, 'col':8 , 'width':4 , 'height':4 , 'vtype':'string', 'empty':0},
                    "PortName"      : {'regr': "PortName"         ,'row':start_row+15, 'col':9 , 'width':3 , 'height':3 , 'vtype':'string', 'empty':1},

                    "M0"            : {'regr': "M0"               ,'row':start_row+16, 'col':12, 'width':0 , 'height':0 , 'vtype':'string', 'empty':1},
                    "AP"            : {'regr': "A|P|^$"           ,'row':start_row+17, 'col':11, 'width':1 , 'height':1 , 'vtype':'string', 'empty':1},
                    "S0"            : {'regr': "S0"               ,'row':start_row+18, 'col':10, 'width':0 , 'height':0 , 'vtype':'string', 'empty':0},
                    "Conn"          : {'regr': "1|^&"             ,'row':start_row+18, 'col':12, 'width':0 , 'height':0 , 'vtype':'string', 'empty':1}}
                    

    def get_start_row(self): #{{{
        return self.start_row
    #}}}

    def matrix_header_check(self): #{{{
        chk_fail = 0
        for (k, v) in self.matrix_header_dict.items():
            #v = self.matrix_header_dict[k]
            row = v['row']
            col = v['col']
            width = v['width']
            regr = v['regr']
            header_cell = self.sheet_obj.cell(row, col)
            #print k
            value = re.sub('\s+', '', str(header_cell.value).strip())
            if(re.match(regr, value, re.I)):
                pass
            else:
                excel_row, excel_col = abs_pos2excel_pos(row, col)
                self.logger.error("Can't find matrix header item: %s @ (%d, %s) in sheet: %s"%(k, excel_row, excel_col, self.sheet_name))
                chk_fail = 1
        return (chk_fail==0)
    #}}}

    def get_cell_pos(self, name): #{{{
        if(self.matrix_header_dict.has_key(name)):
            row = self.matrix_header_dict[name]['row']
            col = self.matrix_header_dict[name]['col']+self.matrix_header_dict[name]['width']
            return (row, col)
        else:
            self.logger.error("Matrix item invalid: %s doesn't existed in header dictionary of sheet: %s!"%(name, self.sheet_name))
            sys.exit()
    #}}}

    def cell_value_check(self, name, cell_value, excel_row, excel_col): #{{{
        # value empty check
        empty = self.matrix_header_dict[name]['empty']
        if(empty == 0 and cell_value == ''):
            self.logger.error("Matrix item invalid: %s can't be empty @ (%d, %s) for sheet: %s!"%(name, excel_row, excel_col, self.sheet_name))
            sys.exit()
        # value format valid check
        vtype = self.matrix_header_dict[name]['vtype']
        if(vtype == 'number'):
            if(re.match("^0x[0-9a-fA-F]+$", cell_value)):
                cell_value = int(cell_value, 16)
            elif(re.match("^[0-9.]+$", cell_value)):
                cell_value = int(float(cell_value))
            elif(re.match("^NA$", cell_value, re.I)):
                cell_value = 0
            else:
                self.logger.error("Matrix item value: '%s' format invalid @ (%d, %s), only digits or 'NA' accepted!"%(cell_value, excel_row, excel_col))
        return cell_value
    #}}}

    def channel_cell_value_check(self, name, cell_value, excel_row, excel_col, chn_name): #{{{
        # value empty check
        empty = self.matrix_header_dict[name]['empty']
        if(empty == 0 and cell_value == ''):
            self.logger.error("[%s.%s.%s] item invalid: %s can't be empty @ (%d, %s)!"%(self.sheet_name, self.name, chn_name, name, excel_row, excel_col))
            sys.exit()
        # value format valid check
        vtype = self.matrix_header_dict[name]['vtype']
        if(vtype == 'number'):
            if(re.match("^0x[0-9a-fA-F]+$", cell_value)):
                cell_value = int(cell_value, 16)
            elif(re.match("^[0-9.]+$", cell_value)):
                cell_value = int(float(cell_value))
            elif(re.match("^NA$", cell_value, re.I)):
                cell_value = 0
            else:
                self.logger.error("[%s.%s.%s] item value: '%s' format invalid @ (%d, %s) in %s.%s, only digits or 'NA' accepted!"%(self.sheet_name, self.name, chn_name, cell_value, excel_row, excel_col))
        return cell_value
    #}}}

    def get_cell_value(self, name): #{{{
        (row, col) = self.get_cell_pos(name)
        (excel_row, excel_col) = abs_pos2excel_pos(row, col)
        cell = self.sheet_obj.cell(row, col)
        cell_value = str(cell.value).strip()
        cell_value = re.sub('\s+', '_', cell_value)
        cell_value = self.cell_value_check(name, cell_value, excel_row, excel_col)
        return cell_value
    #}}}

    def get_m0_cell_pos(self, name): #{{{
        if(self.matrix_header_dict.has_key(name)):
            row = self.matrix_header_dict[name]['row']
            col = self.matrix_header_dict[name]['col']+self.matrix_header_dict[name]['width']
            return (row, col)
        else:
            self.logger.error("[%s.%s] Matrix item invalid: %s doesn't existed in header dictionary of sheet: %s!"%(self.sheet_name, slef.name, name, self.sheet_name))
            sys.exit()
    #}}}

    def get_s0_cell_pos(self, name): #{{{
        if(self.matrix_header_dict.has_key(name)):
            row = self.matrix_header_dict[name]['row']+self.matrix_header_dict[name]['height']
            col = self.matrix_header_dict[name]['col']
            return (row, col)
        else:
            self.logger.error("[%s.%s] Matrix item invalid: %s doesn't existed in header dictionary of sheet: %s!"%(self.sheet_name, self.name, name, self.sheet_name))
            sys.exit()
    #}}}

    def get_mst_cell_pos(self, name, idx): #{{{
        (m0_row, m0_col) = self.get_cell_pos('M0')
        (excel_row, excel_col) = abs_pos2excel_pos(m0_row, m0_col+idx)
        cell = self.sheet_obj.cell(m0_row, m0_col+idx)
        cell_value = str(cell.value).strip()
        exp_value = "^M%d$"%(idx)
        if(re.match(exp_value, cell_value, re.I)):
            pass
        else:
            self.logger.error("[%s.%s] Can't found M%d col @ (%d, %s)"%(self.sheet_name, self.name, idx, excel_row, excel_col))
            sys.exit()

        (row, col) = self.get_m0_cell_pos(name)
        return (row, col+idx)
    #}}}

    def get_slv_cell_pos(self, name, idx): #{{{
        (s0_row, s0_col) = self.get_cell_pos('S0')
        (excel_row, excel_col) = abs_pos2excel_pos(s0_row+idx, s0_col)
        cell = self.sheet_obj.cell(s0_row+idx, s0_col)
        cell_value = str(cell.value).strip()
        exp_value = "^S%d$"%(idx)
        if(re.match(exp_value, cell_value, re.I)):
            pass
        else:
            self.logger.error("[%s.%s] Can't found S%d row @ (%d, %s)"%(self.sheet_name, self.name, idx, excel_row, excel_col))
            sys.exit()

        (row, col) = self.get_s0_cell_pos(name)
        return (row+idx, col)
    #}}}

    def get_mst_cell_value(self, name, idx): #{{{
        chn_name = "M%d"%idx
        (row, col) = self.get_mst_cell_pos(name, idx)
        (excel_row, excel_col) = abs_pos2excel_pos(row, col)
        cell = self.sheet_obj.cell(row, col)
        cell_value = str(cell.value).strip()
        cell_value = re.sub('\s+', '_', cell_value)
        cell_value = self.channel_cell_value_check(name, cell_value, excel_row, excel_col, chn_name)
        return cell_value
    #}}}

    def get_slv_cell_value(self, name, idx): #{{{
        chn_name = "S%d"%idx
        (row, col) = self.get_slv_cell_pos(name, idx)
        (excel_row, excel_col) =  abs_pos2excel_pos(row, col)
        #print excel_row, excel_col
        cell = self.sheet_obj.cell(row, col)
        cell_value = str(cell.value).strip()
        cell_value = re.sub('\s+', '_', cell_value)
        cell_value = self.channel_cell_value_check(name, cell_value, excel_row, excel_col, chn_name)
        return cell_value
    #}}}

    def get_conn_cell_pos(self, mst_idx, slv_idx): #{{{
        if(self.matrix_header_dict.has_key('Conn')):
            row = self.matrix_header_dict['Conn']['row']
            col = self.matrix_header_dict['Conn']['col']
            #self.logger.debug(row)
            return (row+slv_idx, col+mst_idx)
        else:
            self.logger.error("Matrix item invalid: %s doesn't existed in header dictionary of sheet: %s!"%('Conn', self.sheet_name))
            sys.exit()
    #}}}

#}}}

class MatrixTable(Object): #{{{
    
    def __init__(self, logger, name, parent, sheet_name, sheet_obj, mtx_type, mst_num, slv_num, start_row):
        Object.__init__(self, logger, name, parent)
        self.book_name = ''             # excel work book name
        self.sheet_name = sheet_name    # excel sheet table name
        self.sobj = sheet_obj           # excel sheet object
        self.mtx_type = mtx_type        # ahb or pl301 conplicated matrix
        self.mst_num = mst_num          # master number for the matrix
        self.slv_num = slv_num          # slave number for the matrix
        self.start_row = start_row      # matrix table start line number in excel sheet
        self.mst_dict = {}              # master dictionary
        self.slv_dict = {}              # slave dictionary
        self.mst_name_dict = {}         # master name dictionary
        self.slv_name_dict = {}         # slave name dictionary
        
    def get_book_name(self): #{{{
        return self.book_name
    #}}}
    def set_book_name(self, book_name): #{{{
        self.book_name = book_name
    #}}}

    def get_sheet_name(self): #{{{
        return self.sheet_name
    #}}}
    def set_sheet_name(self, sheet_name): #{{{
        self.sheet_name = sheet_name
    #}}}

    def get_sobj(self): #{{{
        return self.sobj
    #}}}
    def set_sobj(self, sobj): #{{{
        self.sobj = sobj
    #}}}

    def get_mtx_type(self): #{{{
        return self.mtx_type
    #}}}
    def set_mtx_type(self, mtx_type): #{{{
        self.mtx_type = mtx_type
    #}}}

    def get_mst_num(self): #{{{
        return len(self.mst_dict)
    #}}}
    def get_slv_num(self): #{{{
        return len(self.slv_dict)
    #}}}

    def get_start_row(self): #{{{
        return self.start_row
    #}}}
    def set_start_row(self, start_row): #{{{
        self.start_row= start_row
    #}}}
    
    def get_mst_dict(self): #{{{
        return self.mst_dict
    #}}}
    def get_slv_dict(self): #{{{
        return self.slv_dict
    #}}}

    def get_mst_name_dict(self): #{{{
        return self.mst_name_dict
    #}}}
    def get_slv_name_dict(self): #{{{
        return self.slv_name_dict
    #}}}

    def get_mst_idx_list(self): #{{{
        return self.mst_name_dict.keys()
    #}}}
    def get_slv_idx_list(self): #{{{
        return self.slv_name_dict.keys()
    #}}}
    
    def has_mst_name(self, name): #{{{
        return self.mst_dict.has_key(name)
    #}}}
    def has_mst_idx(self, idx): #{{{
        return self.mst_name_dict.has_key(idx)
    #}}}
    def add_mst(self, idx, mst_obj): #{{{
        if(self.has_mst_idx(idx)):
            self.logger.error("[%s.%s] adding master id: '%d' has existed already!"%(self.sheet_name, self.name, idx))
            sys.exit()
        mst_name = mst_obj.get_name()
        if(self.has_mst_name(mst_name)):
            self.logger.error("[%s.%s] adding master name: '%s' has exit already!"%(self.sheet_name, self.name, mst_name))
            sys.exit()
        self.mst_name_dict[idx] = mst_name
        self.mst_dict[mst_name] = mst_obj
    #}}}
    def get_mst_name(self, idx): #{{{
        if(self.mst_name_dict.has_key(idx)):
            return self.mst_name_dict[idx]
        else:
            return ''
    #}}}
    def get_mst_by_name(self, name): #{{{
        if(self.mst_dict.has_key(name)):
            return self.mst_dict[name]
        else:
            return None
    #}}}
    def get_mst_by_idx(self, idx): #{{{
        name = self.get_mst_name(idx)
        if(name != ''):
            return self.get_mst_by_name(name)
        else:
            return None
    #}}}

    def has_slv_name(self, name): #{{{
        return self.slv_dict.has_key(name)
    #}}}
    def has_slv_idx(self, idx): #{{{
        return self.slv_name_dict.has_key(idx)
    #}}}
    def add_slv(self, idx, slv_obj): #{{{
        if(self.has_slv_idx(idx)):
            self.logger.error("[%s.%s] adding slave id: '%d' has existed already!"%(self.sheet_name, self.name, idx))
            sys.exit()
        slv_name = slv_obj.get_name()
        if(self.has_slv_name(slv_name)):
            self.logger.error("[%s.%s] adding slave name: '%s' has exit already!"%(self.sheet_name, self.name, slv_name))
            sys.exit()
        self.slv_name_dict[idx] = slv_name
        self.slv_dict[slv_name] = slv_obj
    #}}}
    def get_slv_name(self, idx): #{{{
        if(self.slv_name_dict.has_key(idx)):
            return self.slv_name_dict[idx]
        else:
            return ''
    #}}}
    def get_slv_by_name(self, name): #{{{
        if(self.slv_dict.has_key(name)):
            return self.slv_dict[name]
        else:
            return None
    #}}}
    def get_slv_by_idx(self, idx): #{{{
        name = self.get_slv_name(idx)
        if(name != ''):
            return self.get_slv_by_name(name)
        else:
            return None
    #}}}

    def get_slv_idx_by_addr(self, addr): #{{{{
        hit_cnt = 0
        ret = -1
        slv_idx_list = self.get_slv_idx_list()
        for idx in slv_idx_list:
            slv_obj = self.get_slv_by_idx(idx)
            if(slv_obj.is_mem_hit(addr)):
                hit_cnt += 1
                ret = idx
            
        if(hit_cnt>1):
            self.logger.error("[%s.%s] Hit memory address: '0x%h' in %d slaves!"%(self.get_sheet_name(), self.get_mtx_name(), addr, self.get_name(), hit_cnt))
            sys.exit()
        return ret
    #}}}
    def get_slv_name_by_addr(self, addr): #{{{
        idx = self.get_slv_idx_by_addr(addr)
        if(idx == -1):
            return ''
        else:
            return self.get_slv_name(idx)
    #}}}
    def get_slv_by_addr(self, addr): #{{{
        idx = self.get_slv_idx_by_addr(addr)
        if(idx == -1):
            return None
        else:
            return self.get_slv_by_idx(idx)
    #}}}


#}}}

class MatrixExcelParser(Object): #{{{
    
    def __init__(self, logger, name='un-named-MatrixExcelParser'): 
        Object.__init__(self, logger, name)
        self.book          = None
        self.sheet_dict    = {}
        self.mtx_dict      = {}
        self.root_mst_dict = {}
        self.leaf_slv_dict = {}
        self.mst_dict      = {}
        self.slv_dict      = {}
        self.start_addr_dict = {}
        self.end_addr_dict = {}

        # master paths
        self.root_mst_path_dict = {}

    def set_work_dir(self, work_dir): #{{{
        self.work_dir = work_dir
    #}}}

    def parser_xls(self, xls_name): #{{{
        self.logger.info("Parsing excel file '%s'..."%(xls_name))
        book = xlrd.open_workbook(xls_name)
        sheet_names = book.sheet_names()
        for sn in sheet_names:
            self.logger.info("Parsing sheet '%s'"%(sn))

            sobj = book.sheet_by_name(sn)
            self.sheet_dict[sn] = sobj
            self.parser_sheet(sn, sobj)
        
        self.generate_ahb_cfg()

        self.logger.debug(self.__str__())
    #}}}
    def parser_sheet(self, sheet_name, sheet_obj): #{{{
        col_a = sheet_obj.col(0)
        row_idx = 0
        for c in col_a:
            value = c.value
            parser_flg = 0
            mtx_type = 0
            if re.match("#PL301", value, re.I): # found a pl301 matrix table
                excel_row, excel_col = abs_pos2excel_pos(row_idx, 0) 
                self.logger.info("Found a PL301 matrix table at (%d, %s) of sheet: %s"%(excel_row, excel_col, sheet_name))
                parser_flg = 1
                mtx_type = 'pl301'
            elif re.match("#AHB", value, re.I): # found a ahb matrix table
                excel_row, excel_col = abs_pos2excel_pos(row_idx, 0) 
                self.logger.info("Found a AHB matrix table at (%d, %s) of sheet: %s"%(excel_row, excel_col, sheet_name))
                parser_flg = 1
                mtx_type = 'ahb'

            if(parser_flg):
                mtx_header = MatrixTableHeader(self.logger, "header", self,  sheet_name, sheet_obj, row_idx)
                chk_ok = mtx_header.matrix_header_check()
                if chk_ok:
                    self.parser_matrix_table(sheet_name, sheet_obj, mtx_header, mtx_type)
                else:
                    self.logger.error("Matrix header check failed!")
                    sys.exit()

            row_idx += 1

    #}}}
    def parser_matrix_table(self, sheet_name, sheet_obj, mtx_header, mtx_type): #{{{
        start_row = mtx_header.get_start_row()

        # get mtx name
        mtx_name = mtx_header.get_cell_value('Name')
        mtx_header.set_name(mtx_name)
        # found mtx mst_num
        mst_num = mtx_header.get_cell_value('Masters')
        # found mtx slv_num
        slv_num = mtx_header.get_cell_value('Slaves')
        # found verilog file name
        vfile = mtx_header.get_cell_value('Vfile')
        # found instance hierachy path
        inst = mtx_header.get_cell_value('Instance')
        # found GPV address
        gpv = mtx_header.get_cell_value('GPV')

        self.logger.info("Parsing matrix: %s, mst_num=%d, slv_num=%d"%(mtx_name, mst_num, slv_num))

        # create matrix table
        mtx_obj = MatrixTable(self.logger, mtx_name, self, sheet_name, sheet_obj, mtx_type, mst_num, slv_num, start_row)

        # found all master
        for mst_idx in range(mst_num): #{{{
            name = "M%d"%mst_idx
            # found mst protocol 
            mst_protocol = mtx_header.get_mst_cell_value('Protocol', mst_idx)
            regr = "^AXI$|^AHB$|^APB\d?$"
            if re.match(regr, mst_protocol, re.I):
                pass
            else:
                (row, col) = mtx_header.get_mst_cell_pos('Protocol', mst_idx)
                (excel_row, excel_col) = abs_pos2excel_pos(row, col)
                self.logger.error("[%s.%s.%s] Protocol format: '%s' invalid @(%d, %s). "%(sheet_name, mtx_name, name, mst_protocol, excel_row, excel_col))
                sys.exit()
            # found mst IDBitwidth 
            mst_idw = mtx_header.get_mst_cell_value('IDBitwidth', mst_idx)
            # found mst DataBitwidth
            mst_dw = mtx_header.get_mst_cell_value('DataBitwidth', mst_idx)
            # found mst clock and reset signal
            mst_clock = mtx_header.get_mst_cell_value('Clock', mst_idx)
            mst_reset = re.sub('clk', 'resetn', mst_clock)
            mst_clock = mst_clock.lower()
            mst_reset = mst_reset.lower()
            # found function name 
            mst_function = mtx_header.get_mst_cell_value('Function', mst_idx)
            mst_function = mst_function.lower()
            # found port name 
            mst_port_name = mtx_header.get_mst_cell_value('PortName', mst_idx)
            mst_port_name = mst_port_name.lower()
            # found active and root flag
            mst_ap = mtx_header.get_mst_cell_value('AP', mst_idx)
            if(re.match('A', mst_ap, re.I)):
                mst_active = True
            else:
                mst_active = False
            if(re.match('P', mst_ap, re.I)):
                mst_root = False
            else:
                mst_root = True

            # create master channel
            mst_obj = MasterChannel(self.logger, mst_function, mtx_obj, mst_protocol, mst_idx, mst_dw, mst_active)
            mst_obj.set_function_name(mst_function)
            mst_obj.set_clock(mst_clock)
            mst_obj.set_reset(mst_reset)
            mst_obj.set_port_name(mst_port_name)
            mst_obj.set_axi_idw(mst_idw)
            mst_obj.set_root(mst_root)

            #self.logger.debug(mst_obj)
            
            # add mst to matrix 
            mtx_obj.add_mst(mst_idx, mst_obj)
            #add mst to root mst and all mst dict
            if(self.has_mst(mst_function)):
                mst_obj = self.get_mst_by_name(mst_function)
                self.logger.error("[%s.%s.%s] master function name: '%s' has already existed in [%s.%s.M%d]. "%(sheet_name, mtx_name, name, mst_function, mst_obj.get_parent().get_sheet_name(), mst_obj.get_parent().get_name(), mst_obj.get_idx()))
                sys.exit()
            else:
                self.mst_dict[mst_function] = mst_obj
                if(mst_root):
                    self.root_mst_dict[mst_function] = mst_obj


        #}}}

        #found all slave
        for slv_idx in range(slv_num): #{{{
            name = "S%d"%slv_idx
            #print name
            # found slv protocol 
            slv_protocol = mtx_header.get_slv_cell_value('Protocol', slv_idx)
            regr = "^AXI$|^AHB$|^APB\d?$"
            if re.match(regr, slv_protocol, re.I):
                pass
            else:
                (row, col) = mtx_header.get_slv_cell_pos('Protocol', slv_idx)
                (excel_row, excel_col) = abs_pos2excel_pos(row, col)
                self.logger.error("[%s.%s.%s] Protocol format: '%s' invalid @(%d, %s). "%(sheet_name, mtx_name, name, slv_protocol, excel_row, excel_col))
                sys.exit()
            # found slv IDBitwidth 
            slv_idw = mtx_header.get_slv_cell_value('IDBitwidth', slv_idx)
            # found slv DataBitwidth
            slv_dw = mtx_header.get_slv_cell_value('DataBitwidth', slv_idx)
            # found slv clock and reset signal
            slv_clock = mtx_header.get_slv_cell_value('Clock', slv_idx)
            slv_reset = re.sub('clk', 'resetn', slv_clock)
            slv_clock = slv_clock.lower()
            slv_reset = slv_reset.lower()
            # found function name
            slv_function = mtx_header.get_slv_cell_value('Function', slv_idx)
            slv_function = slv_function.lower()
            # found port name
            slv_port_name = mtx_header.get_slv_cell_value('PortName', slv_idx)
            slv_port_name = slv_port_name.lower()
            # found active and leaf flag
            slv_ap = mtx_header.get_slv_cell_value('AP', slv_idx)
            if(re.match('A', slv_ap, re.I)):
                slv_active = True
            else:
                slv_active = False
            if(re.match('P', slv_ap, re.I)):
                slv_leaf = False
            else:
                slv_leaf = True

            (row, col) = mtx_header.get_slv_cell_pos('AP', slv_idx)
            (excel_row, excel_col) = abs_pos2excel_pos(row, col)
            self.logger.debug("[%s.%s.%s] leaf flag: %s:%s"%(sheet_name, mtx_name, name, slv_ap, slv_leaf))

            # found start_address, end_address, addr_dec
            (s0_row, s0_col) = mtx_header.get_cell_pos('S0')
            row = s0_row+slv_idx
            col = s0_col+2+mst_num
            (excel_row, excel_col) = abs_pos2excel_pos(row, col)
            start_addr_cell  = sheet_obj.cell(row, col  )
            end_addr_cell    = sheet_obj.cell(row, col+1)
            start_remap_cell = sheet_obj.cell(row, col+2)
            end_remap_cell   = sheet_obj.cell(row, col+3)
            addr_dec_cell    = sheet_obj.cell(row, col+4)
                
            start_address = start_addr_cell.value.strip()
            end_address   = end_addr_cell.value.strip()
            start_remap   = start_remap_cell.value.strip()
            end_remap     = end_remap_cell.value.strip()
            addr_dec      = addr_dec_cell.value.strip()

            # self.logger.debug("[%s.%s] start_address=%s @ (%d, %s)"%(sheet_name, mtx_name, start_address, excel_row, excel_col))
            # self.logger.debug("[%s.%s] end_address  =%s @ (%d, %s)"%(sheet_name, mtx_name, end_address  , excel_row, excel_col))
            # self.logger.debug("[%s.%s] addr_dec     =%s @ (%d, %s)"%(sheet_name, mtx_name, addr_dec     , excel_row, excel_col))

            # create slave channel
            slv_obj = SlaveChannel(self.logger, slv_function, mtx_obj, slv_protocol, slv_idx, slv_dw, slv_active)
            slv_obj.set_function_name(slv_function)
            slv_obj.set_clock(slv_clock)
            slv_obj.set_reset(slv_reset)
            slv_obj.set_port_name(slv_port_name)
            slv_obj.set_axi_idw(slv_idw)
            slv_obj.set_leaf(slv_leaf)

            slv_obj.set_addr_dec(addr_dec)
            #slv_obj.set_addr_remap(addr_remap)
            
            #slv_obj.set_start_addr(start_address)
            #slv_obj.set_end_addr(end_address)
            
            # parser address space to create memory segment for slave
            if(re.match('^[0-9a-fA-Fx_\s]+$', start_address)): # start address
                start_address = str(re.sub('_', '', start_address))
                start_addr_list = re.split('\s+', start_address)
                #print start_addr_list
                for idx in range(len(start_addr_list)):
                    if(re.match('^0x[0-9a-fA-F]+$', start_addr_list[idx])):
                        start_addr_list[idx] = int(start_addr_list[idx], 16)
                        self.add_start_addr(start_addr_list[idx])
                    else:
                        self.logger.error("[%s.%s] address format invalid: '%s' @ (%d, %s). [Only hex format is accepted]"%(sheet_name, mtx_name, start_addr_list[idx], excel_row, excel_col))
                        sys.exit()
                    self.logger.debug("start_addr_list[%d]=0x%x"%(idx, start_addr_list[idx]))
            else:
                self.logger.error("[%s.%s] invalid char found in start address: '%s' @ (%d, %s)"%(sheet_name, mtx_name, start_address, excel_row, excel_col))
                sys.exit()

            if(re.match('^[0-9a-fA-Fx_\s]+$', end_address)): # end address
                end_address = str(re.sub('_', '', end_address))
                end_addr_list = re.split('\s+', end_address)
                #print end_addr_list
                for idx in range(len(end_addr_list)):
                    if(re.match('^0x[0-9a-fA-F]+$', end_addr_list[idx])):
                        end_addr_list[idx] = int(end_addr_list[idx], 16)
                        self.add_end_addr(end_addr_list[idx])
                    else:
                        self.logger.error("[%s.%s] address format invalid: '%s' @ (%d, %s). [Only hex format is accepted]"%(sheet_name, mtx_name, end_addr_list[idx], excel_row, excel_col))
                        sys.exit()
                    self.logger.debug("end_addr_list[%d]  =0x%x"%(idx, end_addr_list[idx]))
            else:
                self.logger.error("[%s.%s] invalid char found in end address: '%s' @ (%d, %s)"%(sheet_name, mtx_name, end_address, excel_row, excel_col))
                sys.exit()
            
            # parser remap address space to create memory segment for slave
            if(start_remap == ''):
                start_remap_list = []
            else:
                if(re.match('^[0-9a-fA-Fx_\s]+$', start_remap)): # start address
                    start_remap = str(re.sub('_', '', start_remap))
                    start_remap_list = re.split('\s+', start_remap)
                    #print start_remap_list
                    for idx in range(len(start_remap_list)):
                        if(re.match('^0x[0-9a-fA-F]+$', start_remap_list[idx])):
                            start_remap_list[idx] = int(start_remap_list[idx], 16)
                        else:
                            self.logger.error("[%s.%s] address format invalid: '%s' @ (%d, %s). [Only hex format is accepted]"%(sheet_name, mtx_name, start_remap_list[idx], excel_row, excel_col))
                            sys.exit()
                        self.logger.debug("start_remap_list[%d]=0x%x"%(idx, start_remap_list[idx]))
                    if(len(start_remap_list) != len(start_addr_list)):
                        self.logger.error("[%s.%s] start remap address list number: '%d' should equal start address list number: '%d' @ (%d, %s)"%(sheet_name, mtx_name, len(start_remap_list), len(start_addr_list), excel_row, excel_col))
                        sys.exit()
                else:
                    self.logger.error("[%s.%s] invalid char found in start remap address: '%s' @ (%d, %s)"%(sheet_name, mtx_name, start_remap, excel_row, excel_col))
                    sys.exit()

            if(end_remap == ''):
                end_remap_list = []
            else:
                if(re.match('^[0-9a-fA-Fx_\s]+$', end_remap)): # end address
                    end_remap = str(re.sub('_', '', end_remap))
                    end_remap_list = re.split('\s+', end_remap)
                    #print end_remap_list
                    for idx in range(len(end_remap_list)):
                        if(re.match('^0x[0-9a-fA-F]+$', end_remap_list[idx])):
                            end_remap_list[idx] = int(end_remap_list[idx], 16)
                        else:
                            self.logger.error("[%s.%s] address format invalid: '%s' @ (%d, %s). [Only hex format is accepted]"%(sheet_name, mtx_name, end_remap_list[idx], excel_row, excel_col))
                            sys.exit()
                        self.logger.debug("end_remap_list[%d]  =0x%x"%(idx, end_remap_list[idx]))
                    if(len(end_remap_list) != len(end_addr_list)):
                        self.logger.error("[%s.%s] end remap address list number: '%d' should equal end address list number: '%d' @ (%d, %s)"%(sheet_name, mtx_name, len(end_remap_list), len(end_addr_list), excel_row, excel_col))
                        sys.exit()
                else:
                    self.logger.error("[%s.%s] invalid char found in end remap address: '%s' @ (%d, %s)"%(sheet_name, mtx_name, end_remap, excel_row, excel_col))
                    sys.exit()
            
            # set memory segment to slave
            slv_obj.set_start_addr_list(start_addr_list)
            slv_obj.set_end_addr_list(end_addr_list)
            # set memory remap segment to slave
            slv_obj.set_start_remap_list(start_remap_list)
            slv_obj.set_end_remap_list(end_remap_list)
            
            # add slv to matrix
            mtx_obj.add_slv(slv_idx, slv_obj)

            # add slv to root slv and all slv dict
            if(self.has_slv(slv_function)):
                slv_obj = self.get_slv_by_name(slv_function)
                self.logger.error("[%s.%s.%s] slave function name: '%s' has already existed in [%s.%s.S%d]. "%(sheet_name, mtx_name, name, slv_function, slv_obj.get_parent().get_sheet_name(), slv_obj.get_parent().get_name(), slv_obj.get_idx()))
                sys.exit()
            else:
                self.slv_dict[slv_function] = slv_obj
                if(slv_leaf):
                    self.leaf_slv_dict[slv_function] = slv_obj
        #}}}

        # connect matrix's master and slave
        for mst_idx in range(mst_num): #{{{
            mst_obj = mtx_obj.get_mst_by_idx(mst_idx)
            # added slave connect to master
            for slv_idx in range(slv_num):
                slv_obj = mtx_obj.get_slv_by_idx(slv_idx)
                (row, col) = mtx_header.get_conn_cell_pos(mst_idx, slv_idx)
                (excel_row, excel_col) = abs_pos2excel_pos(row, col)
                #self.logger.debug("[%s.%s] found conn flag @ (%d, %s)"%(sheet_name, mtx_name, excel_row, excel_col))
                conn_cell = sheet_obj.cell(row, col)
                conn_flg = conn_cell.value
                #self.logger.debug("conn_flg=%s"%conn_flg)
                if(conn_flg == ''):
                    conn_flg = 0
                elif((conn_cell.ctype>0) and (conn_cell.ctype<5) and (conn_flg==1)):
                    conn_flg = 1
                    mst_obj.add_slv(slv_idx, slv_obj)
                    slv_obj.add_mst(mst_idx, mst_obj)
                    #print mst_idx, slv_idx
                else:
                    conn_flg = 0
        #}}}
        
        # add matrix to mtx_dict
        if(self.has_mtx(mtx_name)):
            mtx_obj = self.get_mtx_by_name(mtx_name)
            self.logger.error("[%s] matrix name '%s' @ (row:%d) has already existed in sheet: '%s' (row:%d)"%(sheet_name, mtx_name, start_row, mtx_obj.get_sheet_name(), mtx_obj.get_start_row()))
            sys.exit()
        else:
            self.mtx_dict[mtx_name] = mtx_obj

        # print debug information
        for mst_name, mst_obj in mtx_obj.get_mst_dict().items():
            self.logger.debug(mst_obj)
        for slv_name, slv_obj in mtx_obj.get_slv_dict().items():
            self.logger.debug(slv_obj)
            
    #}}} parser_matrix_table

    def get_mtx_by_name(self, mtx_name): #{{{
        if(self.has_mtx(mtx_name)):
            return self.mtx_dict[mtx_name]
        else:
            return None
    #}}}
    def get_root_mst_by_name(self, mst_name): #{{{
        if(self.has_root_mst(mst_name)):
            return self.root_mst_dict[mst_name]
        else:
            return None
    #}}}
    def get_mst_by_name(self, mst_name): #{{{
        if(self.has_mst(mst_name)):
            return self.mst_dict[mst_name]
        else:
            return None
    #}}}
    def get_root_slv_by_name(self, slv_name): #{{{
        if(self.has_root_slv(slv_name)):
            return self.leaf_slv_dict[slv_name]
        else:
            return None
    #}}}
    def get_slv_by_name(self, slv_name): #{{{
        if(self.has_slv(slv_name)):
            return self.slv_dict[slv_name]
        else:
            return None
    #}}}
    def has_root_mst(self, mst_name): #{{{
        return self.root_mst_dict.has_key(mst_name)
    #}}}
    def has_mst(self, mst_name): #{{{
        return self.mst_dict.has_key(mst_name)
    #}}}
    def has_leaf_slv(self, slv_name): #{{{
        return self.leaf_slv_dict.has_key(slv_name)
    #}}}
    def has_slv(self, slv_name): #{{{
        return self.slv_dict.has_key(slv_name)
    #}}}
    def has_mtx(self, mtx_name): #{{{
        return self.mtx_dict.has_key(mtx_name)
    #}}}
    def generate_ahb_cfg(self): #{{{
        for mtx_obj in self.mtx_dict.values():
            if(mtx_obj.get_mtx_type() == 'ahb'):
                mst_contents = ''
                slv_contents = ''
                for mst_idx in range(len(mtx_obj.get_mst_name_dict())):
                    mst_obj = mtx_obj.get_mst_by_idx(mst_idx)
                    slv_str_list = [str(slv_idx) for slv_idx in mst_obj.get_slv_idx_list()]
                    mst_contents += "AHB,same,%d,%d,%s"%(mst_obj.get_dw(), mst_obj.get_slv_num(), ','.join(slv_str_list))
                    if mst_idx != len(mtx_obj.get_mst_name_dict()):
                        mst_contents += '\n'
                    #print mst_contents

                for slv_idx in range(len(mtx_obj.get_slv_name_dict())):
                    slv_obj = mtx_obj.get_slv_by_idx(slv_idx)
                    mst_str_list = [str(mst_idx) for mst_idx in slv_obj.get_mst_idx_list()]
                    slv_contents += "AHB,same,%d,%d,%s,%s,1"%(slv_obj.get_dw(), slv_obj.get_mst_num(), ','.join(mst_str_list), slv_obj.get_addr_dec())
                    if slv_idx != len(mtx_obj.get_slv_name_dict()):
                        slv_contents += '\n'
                    #print slv_contents

                cfg_file_contents = """#Master Attribute List
%s
#Slave Attribute List
%s
"""%(mst_contents, slv_contents)
                #print cfg_file_contents
                dir_path = self.work_dir+os.sep+"matrix_cfg"+os.sep
                saveFile(os.path.join(dir_path+mtx_obj.get_name()+'.cfg'), cfg_file_contents)
    #}}}
    def add_start_addr(self, addr): #{{{
        self.start_addr_dict[addr] = addr
    #}}}
    def add_end_addr(self, addr): #{{{
        self.end_addr_dict[addr] = addr
    #}}}
    def has_start_addr(self, addr): #{{{
        return self.start_addr_dict.has_key(addr)
    #}}}
    def has_end_addr(self, addr): #{{{
        return self.end_addr_dict.has_key(addr)
    #}}}
    def get_start_addr_list(self): #{{{
        return self.start_addr_dict.keys()
    #}}}
    def get_end_addr_list(self): #{{{
        return self.end_addr_dict.keys()
    #}}}

    def seek_path(self, mst_name, addr): #{{{
        path_list = []
        mst_obj = self.get_root_mst_by_name(mst_name)
        if(mst_obj == None):
            self.logger.error("Can't found root master: '%s' in [%s.%s]."%(mst_obj.get_name(), mst_obj.get_sheet_name(), mst_obj.get_mtx_name()))
            sys.exit()
        else:
            mst_obj.seek_path_by_addr(path_list, addr)
        return path_list
    #}}}

    def seek_start_addr_list_path(self, mst_name, addr): #{{{

    #}}}

    def __str__(self): #{{{
        ########################################
        # print matrix debug information
        ########################################
        ret = '\n'
        ret += "Matrix list: \n"
        for mtx_obj in self.mtx_dict.values():
            ret += "    %s (%s)\n"%(mtx_obj.get_name(), mtx_obj.get_mtx_type())
            for mst_idx in range(len(mtx_obj.get_mst_name_dict())):
                mst_obj = mtx_obj.get_mst_by_idx(mst_idx)
                ret += ("        M%d: %s\n"%(mst_idx, mst_obj.get_name()))
            for slv_idx in range(len(mtx_obj.get_slv_name_dict())):
                slv_obj = mtx_obj.get_slv_by_idx(slv_idx)
                ret += ("        S%d: %s\n"%(slv_idx, slv_obj.get_name()))
        ret += ("Master list:\n")
        idx=0
        for mst_obj in self.mst_dict.values():
            ret += ("    %d) %s in matrix: '%s'\n"%(idx, mst_obj.get_name(), mst_obj.get_parent().get_name()))
            idx += 1
        ret += ("Root master list:\n")
        idx=0
        for mst_obj in self.root_mst_dict.values():
            ret += ("    %d) %s in matrix: '%s'\n"%(idx, mst_obj.get_name(), mst_obj.get_parent().get_name()))
            idx += 1
        ret += ("Slave list:\n")
        idx=0
        for slv_obj in self.slv_dict.values():
            ret += ("    %d) %s in matrix: '%s'\n"%(idx, slv_obj.get_name(), slv_obj.get_parent().get_name()))
            idx += 1
        ret += ("Leaf slave list:\n")
        idx=0
        for slv_obj in self.leaf_slv_dict.values():
            ret += ("    %d) %s in matrix: '%s'\n"%(idx, slv_obj.get_name(), slv_obj.get_parent().get_name()))
            idx += 1

        return ret
    #}}}

#}}}

# vim: fdm=marker

