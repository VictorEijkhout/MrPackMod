#! /usr/bin/env python3

import sys
args = sys.argv
if len(args)==1:
    print( f"Usage: {args[0]} action (from download, unpack, configure build)" )
    sys.exit(0)
args = args[1]

import MrPackMod.config
from MrPackMod import config as config
from MrPackMod import download as download
from MrPackMod import info as info
from MrPackMod import modules as modules
from MrPackMod import names as names

configuration = config.read_config()
print(configuration)
def mpm(args):
    global configuration
    for action in args:
        print( f"Action: {action}" )
        if False:
            continue
        elif action=="list":
            info.list_installations( **configuration )
        elif action=="test":
            modules.test_modules( **configuration )
        elif action=="download":
            download.download_from_url( **configuration )
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

mpm( args )
