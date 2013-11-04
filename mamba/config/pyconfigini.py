"""
from: https://bitbucket.org/maascamp/pyconfigini/src/f2b0f95b53d5/pyconfigini.py?at=default

An .ini file parser that follows the same rules as Zend_Config_Ini
(see http://framework.zend.com/manual/en/zend.config.adapters.ini.html
for details) with the exception that the comment character is '#'
instead of ';'.

Values are converted to Python types where possible and returned as 
strings otherwise (i.e. 834 will convert to an int, but /some/path
will convert to a string).

Lines beginning with '#' are treated as comments and will be ignored.
"""
import re
from collections import OrderedDict
from copy import deepcopy
from ast import literal_eval

__all__ = ['parse_ini']

default = '__default__'

reg_sec = re.compile('\[\s?([\w]+)\s?\]', re.IGNORECASE)
reg_isec = re.compile('\[\s?([\w]+)\s?:\s?([\w]+)\s?\]', re.IGNORECASE)

def parse_ini(ini_path, env=None):
    
    ini = _Obj({default: _Obj()})
    current_section = default
    with open(ini_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.isspace() or line[0] == '#': continue
            if line[0] == '[':
                res = reg_sec.search(line)
                if res is not None:
                    section = res.group(1)
                    ini[section] = deepcopy(ini[default])
                else:
                    res = reg_isec.search(line)
                    if res is None:
                        raise SyntaxError('Invalid section declaration.')
                    section = res.group(1)
                    parent = res.group(2)
                    if parent not in ini:
                        raise MissingSectionError("'%s' inherits from '%s' which hasn't been declared." % (section, parent))
                    ini[section] = deepcopy(ini[parent])
                current_section = section
            else:
                pieces = line.split('=')
                vals = pieces[0].strip().split('.')
                vals.reverse()
                data = _cast(pieces[1].strip())
                working_obj = ini[current_section]
                while vals:
                    if len(vals) == 1:
                        working_obj[vals.pop()] = data
                    else:
                        val = vals.pop()
                        if val not in working_obj:
                            working_obj[val] = _Obj()
                        working_obj = working_obj[val]
        
        if env is not None:
            if env not in ini:
                raise MissingSectionError('The section being loaded does not exist.')
            return ini[env]
        return ini

def _cast(val):
    try:
        val = literal_eval(val)
    except:
        pass
    return val
        
class _Obj(OrderedDict):
    """ A dict that allows for object-like property access syntax.
    """
    def __copy__(self):
        data = self.__dict__.copy()
        return _Obj(data)
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            try:
                return self[default][name]
            except KeyError:
                raise AttributeError(name)

class MissingSectionError(Exception):
    """ Thrown when a section header inherits from a section
        that has yet been undeclared.
    """