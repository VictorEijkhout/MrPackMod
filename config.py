##
## standard python modules
##
import re
import os

def read_config():
    configuration_dict = {
        'system':os.getenv("TACC_SYSTEM","UNKNOWN_SYSTEM"),
        'compiler':os.getenv("TACC_FAMILY_COMPILER","UNKNOWN_COMPILER"),
        'root':os.getenv("PACKAGEROOT",os.getenv("HOME")),
        'installroot':os.getenv("INSTALLROOT","NO_INSTALLROOT_GIVEN"),
        # default value:
        'buildsystem':"cmake",
    }
    macros = {}
    with open("Configuration","r") as configuration_file:
        for line in configuration_file.readlines():
            line = line.strip()
            if re.match( r'^#',     line ): continue
            if re.match( r'^[ \t]*$',line ): continue
            if letdef := re.search( r'^let\s*([A-Z]*)\s*=\s*(.*)$',line ):
                key,val = letdef.groups()
                val = val.strip('\n').strip(' ')
                # macro with literal key
                macros[key] = val
                # everywhere else keys are lowercase
                key = key.lower()
                configuration_dict[key] = val
            elif keyval := re.search( r'^\s*([A-Z]*)\s*=\s*(.*)$',line ):
                key,val = keyval.groups()
                key = key.lower(); val = val.strip('\n').strip(' ')
                for m in macros:
                    searchstring = '${'+m+'}'
                    val = val.replace( searchstring,macros[m] )
                configuration_dict[key] = val
            else:
                raise Exception( f"Can not parse: <<{line}>>")
    #print(configuration_dict)
    return configuration_dict
