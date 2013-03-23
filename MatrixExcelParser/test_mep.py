
"""
This is file description.
"""
###############################################################################
# Copyright (c) 2013 @ Spreadtrum Communication Inc.
# Spreadtrum Confidential Property. All rights are reserved.
#
# File name   : BusMatrixParser.py {{{
# Author      : gary.gao@spreadtrum.com and junhao.zheng@spreadtrum.com
# Date        : 2013/03/10
# Description : Bus Matrix Generator
#
# Version     : 0.10 - initial version. (2012/11/10) 
#               0.20 - dot generation.  (2013/03/05) 
#}}}
###############################################################################

# -*- coding:utf-8 -*-  
__metaclass__ = type



import os, sys,string,re,glob
import time
import ConfigParser
import logging
import xlrd
#import yapgvb
from string import Template

import MatrixExcelParser as mep

# main {{{
def main():

    print "\n=-------------------------------------------------------------------------------------="
    print "Bus Matrix Builder version %s."%mep.MEP_VERSION
    print "Copyright (c) 2013 @ Spreadtrum Communication Inc."
    print "Spreadtrum Confidential Property. All rights are reserved."
    print "Authors: Gary.Gao and Junhao.Zheng (IC Group, Tech Dept.)."
    print "=-------------------------------------------------------------------------------------=\n"

    argv = sys.argv
    if len(argv) < 3:
        print """
    usage: %s [Excel_name] [Work_dir]
        """%(argv[0])
        #xls_name = "SC9620 Bus Matrix List.xls"
        #work_dir = cur_file_dir()+os.sep+"result"
        sys.exit()
    else:
        xls_name = argv[1]
        work_dir = argv[2]

    if not os.path.isfile(xls_name):
        print "Excel file: '%s' doesn't exist!"%xls_name
        sys.exit()

    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
        #print "Work Directory: '%s' doesn't exist!"%work_dir
        #sys.exit()

    dir_path = work_dir+os.sep+"matrix_cfg"+os.sep
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    #dir_path = work_dir+os.sep+"dot_cfg"+os.sep
    #os.mkdir(dir_path)

    bmb_pass_file = os.path.join(work_dir+os.sep+"bmb_py_pass")
    if os.path.exists(bmb_pass_file):
        os.remove(bmb_pass_file)

    #formatter = '%(levelname)s %(filename)s %(message)s'
    formatter = '[%(levelname)s] %(message)s'
    log_fname = os.path.join(work_dir+os.sep+"BusMatrixBuilder_excel.log")
    logging.basicConfig(filename=log_fname, filemode='w', format=formatter, level=logging.DEBUG)
    logger = logging.getLogger('logger')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(formatter))
    logging.getLogger('logger').addHandler(console)

    parser = mep.MatrixExcelParser(logger, 'bmb_cfg')
    parser.set_work_dir(work_dir)
    parser.parser_xls(xls_name)

    path_list = parser.seek_mst_path('apx', 0x0)
    path_list = parser.seek_mst_path('apx', 0x60000000)
    path_list = parser.seek_mst_path('apx', 0x20000000)
    path_list = parser.seek_mst_path('apx', 0x70000000)
    path_list = parser.seek_mst_path('apx', 0x40000000)
    path_list = parser.seek_mst_path('apx', 0x50000000)
    path_list = parser.seek_mst_path('apx', 0x80000000)
    path_list = parser.seek_mst_path('apx', 0x4f000000)

    mst_obj = parser.get_mst_by_name('apx')

    print mst_obj.get_path_str(0x0)
    print mst_obj.get_path_str(0x60000000)
    print mst_obj.get_path_str(0x20000000)
    print mst_obj.get_path_str(0x70000000)
    print mst_obj.get_path_str(0x40000000)
    print mst_obj.get_path_str(0x50000000)
    print mst_obj.get_path_str(0x80000000)
    print mst_obj.get_path_str(0x4f000000)


    #graph = mtx_graph(logger, 'mtx_graph', parser.ahb_mtxs, parser.axi_mtxs)
    #graph.set_work_dir(work_dir)
    #graph.generate_graph ()
#}}}

if __name__ == '__main__':
    main()

# vim: fdm=marker

