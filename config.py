##
## standard python modules
##
import re
import os

#
# my modules
#
from process import echo_string

def read_config(configfile,tracing=False):
    configuration_dict = {
        'system':os.getenv("TACC_SYSTEM","UNKNOWN_SYSTEM"),
        # paths
        'root':os.getenv("PACKAGEROOT",os.getenv("HOME")),
        'installroot':os.getenv("INSTALLROOT","NO_INSTALLROOT_GIVEN"),
        'moduleroot':os.getenv("MODULEROOT","NO_MODULEROOT_GIVEN"),
        # compiler
        'compiler':os.getenv("TACC_FAMILY_COMPILER","UNKNOWN_COMPILER"),
        'compilerversion':os.getenv("TACC_FAMILY_COMPILER_VERSION","UNKNOWN_COMPILER_VERSION"),
        'mpi':os.getenv("TACC_FAMILY_MPI","UNKNOWN_MPI"),
        'mpiversion':os.getenv("TACC_FAMILY_MPI_VERSION","UNKNOWN_MPI_VERSION"),
        # default value:
        'buildsystem':"cmake", 
    }
    macros = {}
    with open(configfile,"r") as configuration_file:
        if tracing:
            echo_string( "Read configuration: {configfile}" )
        saving = False
        for line in configuration_file.readlines():
            line = line.strip()
            if re.match( r'^#',     line ): continue
            if re.match( r'^[ \t]*$',line ): continue
            if letdef := re.search( r'^let\s*([A-Za-z0-9_]*)\s*=\s*(.*)$',line ):
                key,val = letdef.groups()
                # macro with literal key
                macros[key] = val
            elif keyval := re.search( r'^\s*([A-Za-z0-9_]*)\s*=\s*(.*)$',line ):
                key,val = keyval.groups()
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
            configuration_dict[key] = val
            if tracing:
                echo_string( f"Setting: {key} = {val}" )
    if tracing:
        print(configuration_dict)
    return configuration_dict
