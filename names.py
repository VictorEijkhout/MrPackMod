#!/usr/bin/env/python3

#
# standard python modules
#
import datetime
import os
import re
import sys

#
# my own modules
#
import names
import process
from process import echo_string,trace_string
from process import abort_on_nonzero_env,abort_on_zero_env,\
    zero_keyword,nonzero_keyword,abort_on_zero_keyword
from process import error_abort,requirenonzero,nonnull

####
#### General names
####

#
# compute package name and version,
# both lowercase
# in the future we will handle the case of git pulls
# Result: pair package,version
#
def package_names( **kwargs ):
    package = kwargs.get("package").lower()
    version = kwargs.get("packageversion").lower()
    terminal = kwargs.get("terminal")
    if version == "git":
        # raise Exception( "gitdate not yet implemented" )
        today = re.sub( '-','',str(datetime.date.today()) )
        version = f"git{today}"
    echo_string( f"setting internal variables packagebasename={package} packageversion={version}",
                 terminal=terminal )
    return package,version

#
# name of a logfile
# 
def logfile_name( logstage,**kwargs ):
    logfilename = f"{logstage}"
    _,packageversion = package_names( **kwargs )
    logfilename += f"_{packageversion}"
    compiler,cversion,cshortv,mpi,mversion = family_names()
    logfilename += f"_{compiler}-{cversion}"
    if mode := nonzero_keyword( "mode",**kwargs ):
        logfilename += f"_{mpi}-{mversion}"
    logfilename += ".log"
    return logfilename

#
# Create a directory for either building or install
#
def create_homedir( **kwargs ):
    root     = kwargs.get( "root",None )
    package  = kwargs.get( "package","nullpackage" )
    homedir  = kwargs.get( "homedir",None )
    terminal = kwargs.get( "terminal",None )
    package,_ = package_names(package=package,packageversion="0.0",termminal=terminal)
    if root:
        echo_string( f"creating homedir value based on root: {root}",terminal=terminal )
        homedir = f"{root}/{package}"
    else:
        if not nonnull( homedir ): raise Exception( "need either root or homedir" )
        echo_string( f"creating homedir value based on homedir: {homedir}",terminal=terminal )
    echo_string( f"using homedir: {homedir}",terminal=terminal )
    if not os.path.isdir(homedir):
        echo_string( f"creating homedir: {homedir}",terminal=terminal )
        try:
            os.mkdir(homedir)
        except PermissionError:
            echo_string( f"ERROR: no permission to create homedir: {homedir}" )
            sys.exit(1)
    return homedir

##
## Description: compute compiler & mpi name & version
## Result: quadruple cname,cversion,mname,mversion
## Notes:
## this is fully based on Lmod environment variables as in use at TACC
##
def family_names():
    try:
        # in jail we can run without compiler loaded
        compiler = os.environ['TACC_FAMILY_COMPILER']
        cversion = os.environ['TACC_FAMILY_COMPILER_VERSION']
        cshortv = re.sub( r'^([^\.]*)\.([^\.]*)(\.*)?$',r'\1\2',cversion ) # DOESN'T WORK
        mpi = os.environ['TACC_FAMILY_MPI']
        mversion = os.environ['TACC_FAMILY_MPI_VERSION']
        return compiler,cversion,cshortv,mpi,mversion
    except:
        return None,None,None,None,None

def compilers_names( **kwargs ):
    compilers = { 'CC':"unknown_cc", 'CXX':"unknown_cxx", 'FC':"unknown_fc", }
    if ( mode := kwargs.get("mode","mode_not_found") ) in [ "mpi","hybrid", ]:
        compilers["CC"] = "mpicc"; compilers["CXX"] = "mpicxx"; compilers["FC"] = "mpif90"
    elif mode in [ "seq", "omp", ]:
        compilers["CC"]  = abort_on_zero_env( "TACC_CC",**kwargs )
        compilers["CXX"] = abort_on_zero_env( "TACC_CXX",**kwargs )
        compilers["FC"]  = abort_on_zero_env( "TACC_FC",**kwargs )
    elif mode == "core":
        compilers["CC"] = "gcc"; compilers["CXX"] = "g++"; compilers["FC"] = "gfortran"
    else: raise Exception( "Unknown mode: {mode}" )
    return compilers

##
## Description: compute single system/compiler/mpi identifier
##
def environment_code( mode ):
    systemcode = os.environ['TACC_SYSTEM'] # systemnames
    compilercode,compilerversion,compilershortversion,mpicode,mpiversion = family_names()
    if compilercode is None:
        # we are running in jail with only system compilers
        return systemcode
    else:
        envcode = f"{systemcode}-{compilercode}{compilerversion}"
        if mode in ["mpi","hybrid",]:
            envcode = f"{envcode}-{mpicode}{mpiversion}"
        return envcode

def systemnames():
    compilercode,compilerversion,compilershortversion,mpicode,mpiversion = family_names()
    return mpicode,mpiversion

def install_extension( **kwargs ):
    package,packageversion = package_names( **kwargs )
    envcode = environment_code( kwargs.get("mode") )
    installext = f"{packageversion}-{envcode}"
    if nonnull( iext := kwargs.get( "installext","" ) ):
        installext = f"{installext}-{iext}"
    if nonnull( variant := kwargs.get("installvariant","") ):
        installext = f"{installext}-{variant}"
    return installext

def srcdir_local_name( **kwargs ):
    packagebasename,packageversion = package_names( **kwargs )
    return f"{packagebasename}-{packageversion}"

def srcdir_name( **kwargs ):
    homedir = create_homedir( **kwargs )
    downloaddir = kwargs.get( "downloadpath",homedir )
    srcdir_local = srcdir_local_name( **kwargs )
    return f"{downloaddir}/{srcdir_local}"

def builddir_name( **kwargs ):
    if bdir := nonzero_keyword( "root",**kwargs ):
        builddir = bdir
    else:
        homedir = create_homedir( **kwargs )
        builddir = homedir
    package,packageversion = package_names( **kwargs )
    installext = install_extension( **kwargs )
    builddir += f"/{package}/build-{installext}"
    return builddir

def prefixdir_name( **kwargs ):
    package,packageversion = package_names( **kwargs )
    if nonnull( pdir:=kwargs.get("installpath","") ):
        echo_string( f"Using external prefixdir: {pdir}" )
        prefixdir = pdir
    elif nonnull( kwargs.get("noinstall","") ):
        raise Exception( f"use of NOINSTALL not implemented" )
    else:
        # path & "installation"
        if nonnull( idir:=kwargs.get("installroot","") ):
            trace_string( f"prefixdir from installroot: {idir}",**kwargs )
            prefixdir = f"{idir}/installation"
        else: 
            hdir = create_homedir( **kwargs )
            trace_string( f"prefixdir from homedir: {hdir}",**kwargs )
            prefixdir = f"{hdir}/installation"
        # attach package name
        if nonnull( mname:=kwargs.get("modulename","") ):
            prefixdir = f"{prefixdir}-{mname}"
        else:
            prefixdir = f"{prefixdir}-{package}"
        # install extension
        installext = install_extension( **kwargs )
        prefixdir = f"{prefixdir}-{installext}"
    if not nonnull( prefixdir ):
        raise Exception( "failed to set prefixdir" )
    if nonnull( var := kwargs.get("installvariant","") ):
        echo_string( f"using subdir for installvariant: {var}" )
        prefixdir = f"{prefixdir}/{var}"
    return prefixdir

def package_dir_names( **kwargs ):
    prefixdir = names.prefixdir_name( **kwargs )
    # lib
    if zero_keyword( "nolib",**kwargs ):
        libdir = f"{prefixdir}/lib64"
        if not os.path.isdir( libdir ):
            libdir = f"{prefixdir}/lib"
            if not os.path.isdir( libdir ):
                raise Exception( "Could not find lib or lib64 dir" )
    else: libdir = ""
    # inc
    if zero_keyword( "noinc",**kwargs ):
        incdir = f"{prefixdir}/include"
        if not os.path.isdir( incdir ):
            raise Exception( "Could not find include dir" )
    else: incdir = ""
    # bin
    if nonzero_keyword( "hasbin",**kwargs ):
        bindir = f"{prefixdir}/bin"
        if not os.path.isdir( bindir ):
            raise Exception( "Could not find bin dir" )
    else: bindir = ""
    return prefixdir,libdir,incdir,bindir

def modulefile_path_and_name( **kwargs ):
    abort_on_nonzero_env( "MODULEDIRSET" )
    #
    # construct module path
    #
    if nonnull( dirset := kwargs.get("moduledirset") ):
        # in jail we get an explicit path
        modulepath = dirset
    else:
        # otherwise we build the path from system & compiler info
        modulepath = abort_on_zero_keyword( "moduleroot",**kwargs )
        if ( mode := kwargs.get("mode","mode_not_found") ) == "core":
            modulepath += f"/Core"
        else:
            compilercode = abort_on_zero_keyword( "compiler",**kwargs )
            compilerversion = abort_on_zero_keyword( "compilerversion",**kwargs )
            if mode in [ "mpi","hybrid", ]:
                mpicode = abort_on_zero_keyword( "mpi",**kwargs )
                mpiversion = abort_on_zero_keyword( "mpiversion",**kwargs )
                modulepath += f"/MPI/{compilercode}/{compilerversion}/{mpicode}/{mpiversion}"
            elif mode in [ "seq","omp", ]:
                modulepath += f"/Compiler/{compilercode}/{compilerversion}"
            else: error_abort( f"Unknown mode: {mode}" )
    #
    # attach package name
    #
    package,packageversion = package_names( **kwargs )
    modulename,moduleversion = module_names( **kwargs )
    return f"{modulepath}/{modulename}",f"{moduleversion}.lua"

def module_names( **kwargs):
    package,packageversion = package_names( **kwargs )
    modulename = kwargs.get( "modulename",package )
    if alt := nonzero_keyword( "modulenamealt" ):
        modulename = alt
    moduleversion = packageversion
    if nonnull( mx := kwargs.get("moduleversionextra") ):
        moduleversion += f"-{mx}"
    return modulename,moduleversion
