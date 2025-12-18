#! /usr/bin/env python3

import os
import sys
args = sys.argv
import argparse
parser = argparse.ArgumentParser\
    ( prog="MrPackMod",
      description="Package installer with LMod support",
      add_help=True )
parser.add_argument( '-j','--jcount',default='6' )
parser.add_argument( '-t','--trace',action='store_true' )
parser.add_argument(  '-c','--configuration',default="Configuration")
parser.add_argument( 'actions', nargs='*', help="test configure build module, install=configure+build, module" )

arguments  = parser.parse_args()
configfile = arguments.configuration
jcount     = arguments.jcount
tracing    = arguments.trace

actions = arguments.actions
if "install" in actions:
    index = actions.index("install")
    actions = actions[:index] + ["configure", "build", "module" ] + actions[index+1:]
if tracing:
    print( f"Actions: {actions}" )

from MrPackMod import config 
from MrPackMod import download
from MrPackMod import info 
from MrPackMod import install
from MrPackMod import modules
from MrPackMod import names 
from MrPackMod import process

def mpm( args,**kwargs ):
    configuration = config.read_config(configfile,tracing)
    for arg,val in kwargs.items():
        configuration[arg] = val
    configuration["logfiles"] = {} # name,handle pairs
    configuration["scriptdir"] = os.getcwd()
    #print(configuration)
    for action in args:
        print( f"Action: {action}" )
        if action=="help":
            usage(program); sys.exit(0)
        elif action=="list":
            info.list_installations( **configuration )
        elif action=="test":
            modules.test_modules( **configuration )
        elif action=="download":
            download.download_from_url( **configuration )
        elif action in [ "unpack", "untar", ]:
            srcdir_local = names.srcdir_local_name( **configuration )
            download.unpack_from_url( srcdir=srcdir_local,**configuration )
        elif action=="configure":
            if ( system := configuration["buildsystem"].lower() ) == "cmake":
                install.cmake_configure( **configuration )
            elif system == "autotools":
                install.autotools_configure( **configuration )
            else: raise Exception( f"Can only configure for cmake and autotools, not: {system}" )
        elif action=="build":
            if ( system := configuration["buildsystem"].lower() ) == "cmake":
                install.cmake_build( **configuration )
            elif system == "autotools":
                install.autotools_build( **configuration )
            else: raise Exception( f"Can only build for cmake and autotools, not: {system}" )
        elif action=="module":
            install.write_module_file( **configuration )
        else: process.error_abort( f"Unknown action: {action}" )
                
mpm( actions,tracing=tracing,jcount=jcount )
