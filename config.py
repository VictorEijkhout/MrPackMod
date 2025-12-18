##
## standard python modules
##
import re
import os

#
# my modules
#
import modules
from process import echo_string,nonnull,nonzero_env

def setting_from_env_or_rc( name,env,default,rc_files ):
    val = ""
    for file in rc_files:
        with open( file,"r" ) as rc:
            for line in rc.readlines():
                line = line.strip()
                if re.match( "\s*#",line ): continue
                if re.match( name,line ):
                    val = re.search( f"^\s*{name}\s*=\s*([A-Za-z0-9_]+)\s*$",line ).groups()[0]
                    #print( f"found setting for {name}: {val}" )
                    return val
    return os.getenv( env,default )


def environment_macros( **kwargs ):
    macros = {}
    for module,_ in modules.loaded_modules( **kwargs ):
        #echo_string( f"investigate module: {module}",**kwargs )
        for ext in [ "dir", "inc", "lib", "bin", ]:
            macro = f"TACC_{module.upper()}_{ext.upper()}"
            if val := nonzero_env( macro,**kwargs ):
                #echo_string( f"Macro {macro}: {val}",**kwargs )
                macros[macro] = val
    return macros

def read_config(configfile,tracing=False):
    rc_name = ".mrpackmodrc"
    rc_files = [ rc for rc in [ rc_name, f"../{rc_name}",
                                f"{os.path.expanduser('~')}/{rc_name}" 
                               ] if os.path.exists(rc) ]
    #print( f"found rc files: {rc_files}" )
    configuration_dict = {
        'scriptdir':os.getcwd(),
        'system':setting_from_env_or_rc(
            "SYSTEM","TACC_SYSTEM","UNKNOWN_SYSTEM",rc_files),
        # paths
        'packageroot':setting_from_env_or_rc(
            "PACKAGEROOT", "PACKAGEROOT","NO_PACKAGE_ROOT_GIVEN",rc_files),
        'installroot':setting_from_env_or_rc(
            "INSTALLROOT", "INSTALLROOT","NO_INSTALLROOT_GIVEN",rc_files),
        'moduleroot':setting_from_env_or_rc(
            "MODULEROOT", "MODULEROOT","NO_MODULEROOT_GIVEN",rc_files),
        # compiler
        'compiler':setting_from_env_or_rc(
            "COMPILER", "TACC_FAMILY_COMPILER","UNKNOWN_COMPILER",rc_files),
        'compilerversion':setting_from_env_or_rc(
            "COMPILERVERSION", "TACC_FAMILY_COMPILER_VERSION","UNKNOWN_COMPILER_VERSION",rc_files),
        'mpi':setting_from_env_or_rc(
            "MPI", "TACC_FAMILY_MPI","UNKNOWN_MPI",rc_files),
        'mpiversion':setting_from_env_or_rc(
            "MPIVERSION", "TACC_FAMILY_MPI_VERSION","UNKNOWN_MPI_VERSION",rc_files),
        # default value:
        'buildsystem':"cmake", 
    }
    macros = environment_macros( **configuration_dict )
    with open(configfile,"r") as configuration_file:
        if tracing:
            echo_string( f"Read configuration: {configfile}" )
        saving = False
        for line in configuration_file.readlines():
            line = line.strip()
            if re.match( r'^#',     line ): continue
            if re.match( r'^[ \t]*$',line ): continue
            if letdef := re.search( r'^let\s*([A-Za-z0-9_]*)\s*=\s*(.*)$',line ):
                key,val = letdef.groups()
                # macro with literal key
                envval = os.getenv( key )
                if nonnull( envval ):
                    macros[key] = envval
                else: macros[key] = val
            elif keyval := re.search( r'^\s*([A-Za-z0-9_]*)\s*=\s*(.*)$',line ):
                key,val = keyval.groups()
                envval = os.getenv( key )
            elif saving:
                # we inherit key from the previous iteration
                # we also inherit val & extend it with the current line
                if tracing:
                    echo_string( f" .. building up key={key} with: {line}" )
                val += line
            else:
                raise Exception( f"Can not parse: <<{line}>>")
            key = key.lower(); val = val.strip('\n').strip(' ')
            if re.search( r'\\$',val ):
                # if the, possibly compounded, line is still to be continued:
                val = val.strip( r'\\' )
                saving = True
                continue
            else: saving = False # time to ship out
            for m in macros:
                searchstring = '${'+m+'}'
                val = val.replace( searchstring,macros[m] )
            if nonnull( envval ):
                configuration_dict[key] = envval
                if tracing:
                    echo_string( f"Setting: {key} = {envval} from environment" )
            else:
                configuration_dict[key] = val
                if tracing:
                    echo_string( f"Setting: {key} = {val} from config" )
    if tracing:
        print(configuration_dict)
    return configuration_dict
