from enum import Enum
import re
from email.utils import format_datetime, parsedate_to_datetime
import hashlib

class Urgency(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3
    EMERGENCY = 4

    def __str__(self):
        return self.name.lower()

    def __gt__(self, other):
        return self.value > other.value

class ChangelogBlock(object):
    head_regex = re.compile('([\S]+)\s+\(([\S]+)\)\s+(.*)\;\s+(.*)')
    foot_regex = re.compile('--(.*)\<(\S+)\>\s+(.*)')
    version_semantic_regex = re.compile('(\d+)\.?(\d+)?\.?(\d+)?\.?(\d+)?')

    def __init__(self):
        self.flags = {}
        self.entries = {}
        self.package_name = None
        self.version = None
        self.distros = None
        self.last_author = None
        self.contact = None
        self.date = None
        self.content_hash = None

    def __str__(self):
        distros = ''
        for d in self.distros:
            distros = distros + d + ' '
        flags = ''
        for k, w in self.flags.items():
            flags = flags + '{}={}, '.format(k, w)
        flags = flags.strip(', ')
        retval = '{} ({}) {}; {}\n'.format(self.package_name, self.version, distros.strip(), flags.strip())

        def parse_entry(entry):
            if entry.startswith('\n'):
                return '    ' + entry[1:] + '\n'
            else:
                return '  * ' + entry + '\n'

        if len(self.entries) == 1:
            item = list(self.entries.values())[0]
            retval = retval + '\n'
            for e in item:
                retval = retval + parse_entry(e)
        else:
            for author, entries in self.entries.items():
                retval = retval + '\n  [ {} ]\n'.format(author)
                for e in entries:
                    retval = retval + parse_entry(e)

        retval = retval + '\n -- {} <{}>  {}\n'.format(self.last_author, self.contact, format_datetime(self.date))

        return retval

    def __eq__(self, other):
        return self.content_hash == other.content_hash

    def update_hash(self):
        hash_obj = hashlib.blake2b(bytes(str(self), encoding='utf-8'), digest_size=8)
        hash_obj = int.from_bytes(hash_obj.digest(), 'little')
        self.content_hash = hash_obj

    def parse(self, stream):
        headline :str = stream.readline()

        if not headline:
            return False

        matches = self.head_regex.match(headline.strip())
        self.package_name = matches.group(1)
        self.version = matches.group(2)
        self.distros = matches.group(3).split()
        flags = matches.group(4).split(', ')

        for f in flags:
            kw = f.split('=')
            key = kw[0].strip().lower()
            
            if key == 'urgency':
                self.flags[key] = Urgency[kw[1].strip().upper()]
            else:
                self.flags[key] = kw[1].strip()

        author_name = None
        entries = []
        end_marker = False

        while True:
            line :str = stream.readline().strip()

            if end_marker:
                if len(line) > 0:
                    raise RuntimeError('Invalid format! Expected empty line between version entries.')
                break

            if len(line) == 0:
                continue
            elif line.startswith('[') and line.endswith(']'):
                if author_name and len(entries) > 0:
                    self.entries[author_name] = entries
                    entries = []
                author_name = line.strip('[] \t')
            elif line.startswith('*'):
                entries.append(line.strip('* \t'))
            elif line.startswith('--'):
                end_line = self.foot_regex.match(line)
                self.last_author = end_line.group(1).strip()
                self.contact = end_line.group(2)
                self.date = parsedate_to_datetime(end_line.group(3))
                if not author_name:
                    author_name = self.last_author
                if len(entries) > 0:
                    self.entries[author_name] = entries
                end_marker = True
            else:
                entries.append('\n' + line.strip())

        self.update_hash()

        return True

    def update_flags(self, other):
        for key, value in other.flags.items():
            if not key in self.flags:
                self.flags[key] = value
            elif key == 'urgency':
                self.flags[key] = max(self.flags[key], other.flags[key])
            elif self.flags[key] != value:
                raise RuntimeError('Colliding entry flag: ' + key)

    def parse_version(self):
        matches = self.version_semantic_regex.match(self.version)

        if (matches.group(0) != self.version):
            raise RuntimeError('NonSemantic parser not implemented')

        retval = []
        retval_mask = 0

        for l in matches.groups():
            if l == None:
                retval.append(0)
            else:
                retval.append(int(l))
                retval_mask = retval_mask + 1

        return (retval, retval_mask)

    def merge_version(self, other):
        self_version, self_version_mask = self.parse_version()
        other_version, other_version_mask = other.parse_version()

        for v in range(4):
            if self_version[v] != other_version[v]:
                hi_version = self_version if self_version[v] > other_version[v] else other_version
                self_version[v:] = hi_version[v:]
                break
        
        num_numbers = max(self_version_mask, other_version_mask)
        new_version = ''

        for nv in range(num_numbers):
            new_version = new_version + str(self_version[nv]) + '.'
        new_version = new_version.rstrip('.')
        self.version = new_version

class Changelog:
    def __init__(self):
        self.blocks = []

    def __eq__(self, other):
        return self.blocks == other.blocks

    def merge(self, other):
        if self == other:
            return

        num_blocks = len(self.blocks)
        diff_index = None

        for i in range(num_blocks):
            if self.blocks[i] == other.blocks[i]:
                continue
            diff_index = i
            break


        if diff_index >= 0:
            # case 0: both are last and unreleased
            self_block :ChangelogBlock = self.blocks[i]
            other_block :ChangelogBlock = other.blocks[i]

            if num_blocks == diff_index + 1 and len(self_block.distros) == 1 and self_block.distros[0] == 'UNRELEASED' and len(other_block.distros) == 1 and other_block.distros[0] == 'UNRELEASED':
                if self_block.version != other_block.version:
                    self_block.merge_version(other_block)
                    
                    for author, entries in other_block.entries.items():
                        if not author in self_block.entries:
                             self_block.entries[author] = entries
                        else:
                            self_entries :list = self_block.entries[author]
                            for entry in entries:
                                if not entry in self_entries:
                                    self_entries.append(entry)

                    self_block.update_flags(other_block)

                    if other_block.date > self_block.date:
                        self_block.date = other_block.date
                        self_block.contact = other_block.contact
                        self_block.last_author = other_block.last_author

                    # TODO: what to do when package name changes?

                    print(self_block)
            self_block.update_hash()



    def from_file(self, file_name):
        with open(file_name, 'r') as file:
            retval = True
            while retval:
                data = ChangelogBlock()
                retval = data.parse(file)
                if retval:
                    self.blocks.insert(0, data)
   

ch = Changelog()
ch.from_file('changelogexample')

ch1 = Changelog()
ch1.from_file('ch')
#ch.merge(ch1)
#print(ch.blocks[0])
#print(ch == ch1)


def test_double_unresolved():
    ch = Changelog()
    ch.from_file('000_double_unreleased')

    ch1 = Changelog()
    ch1.from_file('001_double_unreleased')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('002_double_unreleased')

    assert(result == ch)

def test_double_unresolved_flags():
    ch = Changelog()
    ch.from_file('010_double_unreleased_flags')

    ch1 = Changelog()
    ch1.from_file('011_double_unreleased_flags')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('012_double_unreleased_flags')

    assert(result == ch)

def test_double_unresolved_empty():
    ch = Changelog()
    ch.from_file('020_double_unreleased_empty')

    ch1 = Changelog()
    ch1.from_file('021_double_unreleased_empty')

    ch.merge(ch1)

    result = Changelog()
    result.from_file('022_double_unreleased_empty')

    assert(result == ch)

test_double_unresolved()
test_double_unresolved_flags()
test_double_unresolved_empty()
