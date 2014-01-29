import sys
import string
from lxml import etree

def ordinal(n):
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    else:
       return str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, 'th')

filename = sys.argv[1] if (len(sys.argv) > 1) else sys.exit('Invalid file name')
tree = etree.parse(filename)
addr_streets = tree.findall(".//tag[@k='addr:street']")

for addr_street in addr_streets:
    old_name = addr_street.get('v')
    new_name = addr_street.get('v')
    num_bef = ''
    num_aft = ''
    for i, c in enumerate(new_name):
        if c.isdigit():
            start = i
            while i < len(new_name) and new_name[i].isdigit():
                i += 1
            num_bef = new_name[start:i]#obtiene el numero dentro de un string
            if new_name[start+i:i+1].isspace(): #verifica si el caracter es de una forma ejemplo: 117th
                num_aft = ordinal(int(num_bef))
                new_name = new_name.replace(num_bef, num_aft)

            if addr_street.get('v') != new_name:
                addr_street.set('v', new_name)
                parent = addr_street.getparent()
                parent.attrib['action'] = 'modify'
            break
    print '- %s > %s' % (old_name, new_name)

xml = "<?xml version='1.0' encoding='UTF-8'?>\n" + etree.tostring(tree, encoding='utf8').replace('"',"'")
new_file = open(filename[:-4] + '_new' + filename[-4:], 'w')
new_file.write(xml)
