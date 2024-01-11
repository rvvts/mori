import sys
import os
from pathlib import Path
from markdown import Markdown
import re

def bail(code: int, msg: str):
    print('mori: ' + msg, file=sys.stderr)
    sys.exit(code)

if __name__ == '__main__':

    # parse args
    basepath = ''
    if len(sys.argv) < 3:
        print('Usage: mori [MARKDOWN_DIRECTORY] [OUTPUT_DIRECTORY]')
        sys.exit(-1)
    basepath = Path(sys.argv[1])
    if not basepath.is_dir(): # if not directory or doesn't exist
        bail(-1, 'markdown directory "' + str(basepath) + '" doesn\'t exist')
    outputpath = Path(sys.argv[2])
    if not outputpath.is_dir():
        bail(-1, 'mori: output directory "' + str(basepath) + '" doesn\'t exist')

    # create markdown parser
    mdparser = Markdown(extensions=['meta'])

    # find all .txt files
    filepaths = list(basepath.glob('*.md')) # use **/*.md to search subdirectories
    templatepath = Path('template.html')
    for p in filepaths:

        # open markdown file
        md = ''
        with open(p) as f:
            md = f.read()

        # open template file
        html = ''
        with open(templatepath) as f:
            html = f.read()

        # convert markdown to html
        converted = mdparser.reset().convert(md)
        metadata: dict[str, list[str]] = mdparser.Meta

        html = html.replace('{{CONTENT}}', converted)

        # find and replace any macros that match metadata keys
        i = 0
        r = re.compile(r'\{\{(.*)\}\}')
        while True:
            m = r.search(html, i)
            if m is None:
                break
            macro = m.group(0) # entire thing is 0th group
            macro_name = m.group(1) # what was inside the curly brackets

            # check if name is a metadata key
            if macro_name in metadata.keys():
                macro_value = metadata[macro_name][0]

                # replace macro with value
                html = html.replace(macro, macro_value, 1)

            i = m.end(0) # set start index to end of match

        # write html file
        htmlpath = outputpath.joinpath(p.stem + '.html')
        htmlpath.write_text(html)
        print(htmlpath)
