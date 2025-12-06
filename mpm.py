#! /usr/bin/env python3

import sys
args = sys.argv
actions = [ "help",
            "list", "test",
            "download", "unpack", "configure", "build",
            ]
def usage(program):
    print( f"Usage: {program} action (from download, unpack, configure build)" )

if len(args)==1:
    usage; sys.exit(0)
program = args[0]
args = args[1]

import MrPackMod.config
from MrPackMod import config as config
from MrPackMod import download as download
from MrPackMod import info as info
from MrPackMod import install as install
from MrPackMod import modules as modules
from MrPackMod import names as names

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
            packagebasename,packageversion = names.packagenames( **configuration )
            srcdir=f"{packagebasename}-{packageversion}"
            download.unpack_from_url(
                srcdir=srcdir,
                **configuration )
        elif action=="configure":
            builddir = names.builddir_name( **configuration )
            print(builddir)
            prefixdir = names.prefixdir_name( **configuration )
            print(prefixdir)
            if configuration["buildsystem"].lower() == "cmake":
                install.cmake_configure( **configuration )
                
mpm( args.split() )
