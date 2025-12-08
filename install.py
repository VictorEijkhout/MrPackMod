#!/usr/bin/env/python3

#
# standard python modules
#
import os
import re
import shutil

#
# my own modules
#
import modules
import names
import process
from process import process_execute, echo_string, error_abort
from process import nonnull, nonzero_keyword, zero_keyword, abort_on_zero_keyword

def cmake_configure( **kwargs ):
    modules.test_modules( **kwargs )
    #
    # setup directories
    #
    srcdir    = names.srcdir_name( **kwargs )
    builddir  = names.builddir_name( **kwargs )
    prefixdir = names.prefixdir_name( **kwargs )
    #print(srcdir,builddir,prefixdir)
    try:
        shutil.rmtree(builddir)
    except FileNotFoundError: pass
    os.mkdir(builddir)
    #
    # flags
    #
    cmakeflags = ""; cmakeflagsplatform = ""; exports = ""
    if standard := kwargs.get("cppstandard"):
        cmakeflags += f"-D CMAKE_CXX_FLAGS=-std=c++{standard}"
    cmake = kwargs.get("cmakename","cmake")
    if nonzero_keyword("cmakeuseninja"):
        cmake = f"{cmake} -G Ninja"
    if kwargs.get("cmakebuilddebug"):
        defaultbuild = "Debug"
    else: defaultbuild = "RelWithDebInfo"
    cmakebuildtype = kwargs.get("cmakebuildtype",defaultbuild)
    if static := kwargs.get("buildstaticlibs"):
        buildsharedlibs = "OFF"
    else: buildsharedlibs = "ON"
    if nonnull( source := kwargs.get("cmakesource") ):
        cmakesourcedir = f"-S {srcdir}/{source} -B {builddir}"
    else: cmakesourcedir = f"{srcdir}"
    #
    # execute cmake
    #
    cmdline = f"{cmake} -D CMAKE_INSTALL_PREFIX={prefixdir} \
-D CMAKE_COMPILE_WARNING_AS_ERROR=OFF \
-D CMAKE_POLICY_VERSION_MINIMUM=3.13 \
-D CMAKE_VERBOSE_MAKEFILE=ON \
-D BUILD_SHARED_LIBS={buildsharedlibs} \
-D CMAKE_BUILD_TYPE={cmakebuildtype} \
{cmakeflags} {cmakeflagsplatform} \
{cmakesourcedir} \
"
    os.chdir( builddir )
    process_execute( cmdline )

def cmake_build( **kwargs ):
    #
    # setup directories
    #
    srcdir    = names.srcdir_name( **kwargs )
    builddir  = names.builddir_name( **kwargs )
    prefixdir = names.prefixdir_name( **kwargs )
    #
    # flags and options
    #
    makebuildtarget = kwargs.get("makebuildtarget","")
    jcount          = kwargs.get("jcount","6")
    #
    # execute make & make install
    make = f"make --no-print-directory V=1 VERBOSE=1 -j {jcount}"
    os.chdir( builddir )
    if zero_keyword("noinstall"):
        cmdline = f"{make} {makebuildtarget}"
        process_execute( cmdline )
        if extra_targets := nonzero_keyword( "extrabuildtargets" ):
            cmdline = f"{make} {extra_targets}"
            process_execute( cmdline )
        cmdline = f"{make} install"
        process_execute( cmdline )
        if extra_targets := nonzero_keyword( "extrainstalltargets" ):
            cmdline = f"{make} {extra_targets}"
            process_execute( cmdline )

def autotools_configure( **kwargs ):
    pass
def autotools_build( **kwargs ):
    pass

def write_module_file( **kwargs ):
    #
    # paths
    #
    modulefile_fullname = names.module_file_full_name( **kwargs )
    #
    # module contents
    #
    help_string   = modules.module_help_string( **kwargs )
    pkg_info      = modules.package_info( **kwargs )
    path_settings = modules.path_settings( **kwargs )
    system_paths  = modules.system_paths( ** kwargs )
    #
    # write
    #
    echo_string( f"Writing modulefule: {modulefile_fullname}" )
    with open( f"{modulefile_fullname}","w" ) as modulefile:
        modulefile.write( f"""\
{help_string}

{pkg_info}

{path_settings}

{system_paths}
"""
                          )
