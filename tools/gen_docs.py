#!/usr/bin/env python3
"""Extract doc strings from source module(s) and build the module specific READMEs
"""

#==========================================================
#
#  Chris Nelson, 2024
#
#==========================================================

import pathlib
import re


modules = [
    {'outfile':'../README.md',     'head':'./DS18B20_head.md',         'source':'../src/DS18B20/DS18B20.py'},
    # {'outfile':'../configman.md',   'head':'./configman_head.md',   'source':'../src/cjnfuncs/configman.py'},
    # {'outfile':'../timevalue.md',   'head':'./timevalue_head.md',   'source':'../src/cjnfuncs/timevalue.py'},
    # {'outfile':'../mungePath.md',   'head':'./mungePath_head.md',   'source':'../src/cjnfuncs/mungePath.py'},
    # {'outfile':'../deployfiles.md', 'head':'./deployfiles_head.md', 'source':'../src/cjnfuncs/deployfiles.py'},
    # {'outfile':'../resourcelock.md','head':'./resourcelock_head.md','source':'../src/cjnfuncs/resourcelock.py'},
    # {'outfile':'../SMTP.md',        'head':'./SMTP_head.md',        'source':'../src/cjnfuncs/SMTP.py'},
]

def main():
    for module in modules:
        print (f"Processing {module['outfile']}")
        links       = build_links_list(module['source'])
        docstrings  = extract_docstrings(module['source'])

        with pathlib.Path(module['outfile']).open('w') as ofile:
            ofile.write(pathlib.Path(module['head']).read_text())

            ofile.write(r"""

<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

""")
            ofile.write(links)

            ofile.write(r"""

""")
            ofile.write(docstrings)

# Doc string format example:
'''
def snd_notif(subj="Notification message", msg="", to="NotifList", log=False):
    """
## snd_notif (subj="Notification message, msg="", to="NotifList", log=False) - Send a text message using info from the config file
(...documentation...)
    """
'''

comment_block = re.compile(r'"""\s+##\s([\s\S]+?)(?:""")')

def build_links_list(source):

    all = pathlib.Path(source).read_text()
    # Build the links list
    links = ''
    for block in comment_block.finditer(all):
        link_name = get_linkname(block)
        links += f"- [{link_name}](#{link_name})\n"
    return links

        # link = funcline.replace(" ", "-").lower()
        # deleted = ":()\n,.=\"\'"
        # for char in deleted:
        #     link = link.replace(char, "")
        # links += f"- [{link_name}](#{link})\n"


def extract_docstrings(source):
    xx = ''
    all = pathlib.Path(source).read_text()

    # xx += (links)

    for block in comment_block.finditer(all):
        link_name = get_linkname(block)
        print (f"    Processing {link_name}")
        xx += "\n<br/>\n\n"
        xx += f'<a id="{link_name}"></a>\n\n'
        xx += "---\n\n"
        xx += "# " + block.group(1)

    return xx


def get_linkname(block):
    funcline = block.group(1).split('\n')[0]
    return funcline.replace("Class ", "").split(maxsplit=1)[0].lower()

if __name__ == '__main__':
    main()


