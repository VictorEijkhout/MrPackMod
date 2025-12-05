#! /usr/bin/env python3

import sys
args = sys.argv
if len(args)==1:
    print( f"Usage: {args[0]} action (from download, unpack, configure build)" )
    sys.exit(0)
args = args[1]

import MrPackMod.config
from MrPackMod import download as download
from MrPackMod import info as info
from MrPackMod import modules as modules
from MrPackMod import names as names

configuration = config.read_config()
for action in args:
    if False:
        continue
    elif action=="list":
        info.list_installations( **configuration )
    elif action=="test":
        modules.test_modules( **configuration )
    elif action=="download":
        download.download_from_url( **configuration )
        packagebasename,packageversion = names.packagenames( **configuration )
    ( package=\"${PACKAGE}\",packageversion=\"${PACKAGEVERSION}\" ); \
srcdir=f\"{packagebasename}-{packageversion}\"; \
import download; \
download.unpack_from_url( \
    \"${DOWNLOADURL}\", srcdir=srcdir, \
    system=\"${TACC_SYSTEM}\",compiler=\"${TACC_FAMILY_COMPILER}\",\
    root=\"${PACKAGEROOT}\",package=\"${PACKAGE}\",version=\"${PACKAGEVERSION}\", \
    downloadpath=\"$${downloadpath}\" \

    elif action=="configure":
        builddir = names.builddir_name( **configuration )
        print(builddir)
        prefixdir = names.prefixdir_name( **configuration )
        print(prefixdir)
