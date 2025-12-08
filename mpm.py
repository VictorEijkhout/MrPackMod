#! /usr/bin/env python3

import sys
args = sys.argv
actions = [ "help",
            "list", "test",
            "download", "unpack", "configure", "build", "module",
            ]
def usage(program):
    print( f"Usage: {program} action (from download, unpack, configure, build, module)" )

if len(args)==1:
    usage; sys.exit(0)
program = args[0]
args = args[1:]

import MrPackMod.config
from MrPackMod import config as config
from MrPackMod import download as download
from MrPackMod import info as info
from MrPackMod import install as install
from MrPackMod import modules as modules
from MrPackMod import names as names
from MrPackMod import process as process

def mpm(args):
    configuration = config.read_config()
    print(configuration)
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
        elif action=="unpack":
            srcdir_local = names.srcdir_local_name( **configuration )
            download.unpack_from_url( srcdir=srcdir_local,**configuration )
        elif action=="configure":
            if ( system := configuration["buildsystem"].lower() ) == "cmake":
                install.cmake_configure( **configuration )
            else: raise Exception( f"Can only configure for cmake, not: {system}" )
        elif action=="build":
            if ( system := configuration["buildsystem"].lower() ) == "cmake":
                install.cmake_build( **configuration )
            else: raise Exception( f"Can only build for cmake, not: {system}" )
        elif action=="module":
            install.write_module_file( **configuration )
        else: process.error_abort( f"Unknown action: {action}" )
                
mpm( args )
