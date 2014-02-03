from sys import argv, exit
import xml.parsers.expat
import datetime

# argv[1] = filename
# argv[2] = changeset
    # osmchange need to be tagged with the open changeset the file is going in

def ordinal(n):
    n = int(n)
    if 10 <= n % 100 < 20:
        return str(n) + 'th'
    else:
       return  str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, 'th')


def ordinalize(street):
    for index, char in enumerate(street):
        if char.isdigit():
            start = index
            end = index

            while end < len(street) and street[end].isdigit():
                end += 1
            number = street[start:end]

            if street[start+end:end+1].isspace():
                street = ordinal(number) + street[0:start] + street[end:]

    return street


def start_element(name, attrs):
    if name in accepted:
        global current
        if (int(attrs['timestamp'][0:4]) > 2012 and
            int(attrs['timestamp'][5:7]) > 9):
            current = {
                'type': name,
                'attrs': attrs,
                'tags': {},
                'nds': [],
                'modified': False
            }

            if name == 'relation':
                global relations
                relations.append(attrs['id'])
        else:
            current = False

    if name == 'nd' and current:
        global current
        # need to see this in actual use
        current['nds'].append(attrs['ref'])

    if name == 'tag' and current:
        tag(attrs)


def tag(attrs):
    global current
    for attr in attrs:
        current['tags'][attrs['k']] = attrs['v']

    if attrs['k'] == 'addr:street':
        current['tags']['addr:street'] = ordinalize(attrs['v'])
        if current['tags']['addr:street'] != attrs['v']:
            # print attrs['v'] + ' -> ' + current['tags']['addr:street']
            current['modified'] = True
            current['attrs']['version'] = str(int(current['attrs']['version']) + 1)


def end_element(name):
    if name == 'osm':
        closeFile()

    if name in accepted:
        if current and current['modified']:
            addToFile(current)


def startOsmChange():
    return '<osmChange version="0.6" generator="ordinal_fixes.py"><modify>'


def endOsmChange():
    return '</modify></osmChange>'


def addToFile(item):
    global itemCount
    if itemCount > groupLimit:
        if type(currentFile) is file:
            closeFile()
        newFile()
        itemCount = 0
    
    # need to serialize back to xml
    if len(item['nds']):
        print item

    currentFile.write(serializeItem(item) + '\n')
    # currentFile.write(str(itemCount) + '\n')
    itemCount += 1


def serializeItem(item):
    xml = '<' + item['type']
    
    for attr in item['attrs']:
        xml += ' ' + attr + '="' + item['attrs'][attr] + '"'
    xml += '>'

    for tag in item['tags']:
        xml += '<tag k="' + tag + '" v="' + item['tags'][tag] + '"/>'

    xml += '</' + item['type'] + '>'
    return xml


def newFile():
    global fileCount
    fileCount += 1
    global currentFile
    currentFile = open('ordinal_fixed_' + str(fileCount) + '.osc', 'w')
    currentFile.write(startOsmChange())
    print 'created file: ' + 'ordinal_fixed_' + str(fileCount) + '.osc'


def closeFile():
    currentFile.write(endOsmChange())
    currentFile.close()


groupLimit = 2500
current = {}
currentFile = False
out = ''
accepted = ['node', 'way', 'relation']
itemCount = groupLimit + 1
fileCount = 0
relations = []


p = xml.parsers.expat.ParserCreate()
p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.ParseFile(open(argv[1], 'r'))

print '---------------'
print '---------------'
print relations


# save the entire structure of an object until the end of the element
# save a list of all used nodes in a particular group
# ability to create arbitrarily group sizes, based on count
