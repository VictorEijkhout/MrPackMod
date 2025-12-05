import re

def read_config():
    configuration_dict = {}
    with open("Configuration","r") as configuration_file:
        for line in configuration_file.readlines():
            line = line.strip()
            if re.match( r'^#',     line ): continue
            if re.match( r'^[ \t]*$',line ): continue
            if not ( keyval := re.search( r'^([A-Z]*) = (.*)$',line ) ):
                raise Exception( f"Can not parse: <<{line}>>")
            key,val = keyval.groups()
            key = key.lower(); val = val.strip('\n')
            #print(key,val)
            configuration_dict[key] = val
    print(configuration_dict)
