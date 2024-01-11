import sys
import os
from pathlib import Path
from shutil import copytree
from markdown import Markdown
import re

def bail(code: int, msg: str):
    print('mori: ' + msg, file=sys.stderr)
    sys.exit(code)

class Macro:
    def __init__(self) -> None:
        self.macro = '' # the entire macro, including {{ and }}
        self.contents = '' # the part inside the curly braces
        self.startidx = 0 # index of start of macro (inclusive)
        self.endidx = 0 # index of end of macro (exclusive)

def find_macro(text: str, startidx: int) -> Macro:
    r = re.compile(r'\{\{(.*?)\}\}') # lazy match (as opposed to greedy)
    match = r.search(text, startidx)

    if match is None:
        return None
    
    m = Macro()
    m.macro = match.group(0)
    m.contents = match.group(1)
    m.startidx = match.start(0)
    m.endidx = match.end(0)

    return m

def build_md_file(filepath: Path, templatepath: Path) -> None:
    # create markdown parser
    # TODO: move this outside in a clean way
    mdparser = Markdown(extensions=['meta'])

    # open markdown file
    md = ''
    with open(filepath) as f:
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
    while True:
        m = find_macro(html, i)
        if m is None:
            break
    
        # check if name is a metadata key
        if m.contents in metadata.keys():
            macro_value = metadata[m.contents][0]

            # replace macro with value
            html = html.replace(m.macro, macro_value, 1)

            i += len(macro_value)
        
        else:
            i = m.endidx

    # write html file
    htmlpath = buildpath.joinpath(filepath.stem + '.html')
    htmlpath.write_text(html)
    return htmlpath

def get_html_title(filepath: Path) -> str:
    title = ''
    with open(filepath) as f:
        html = f.read()
    m = re.search('<title>(.*)</title>', html)
    if m is not None:
        title = m.group(1) # what was inside the title tags
    return title

def macro_nav(navpaths: list[Path]) -> str:
    navhtml = '<ul>\n'
    for p in navpaths:
        # get page name
        title = get_html_title(p)
        if title == '':
            title = str(p)
        
        # create link html
        navhtml += '<li><a href="' + str(p) + '">' + title + '</a></li>\n'
    navhtml += '</ul>\n'
    return navhtml

def build_html_file(filepath: Path, navpaths: list[Path]) -> None:
    # open html file
    html = ''
    with open(filepath) as f:
        html = f.read()
    
    # evaluate macros
    i = 0
    while True:
        m = find_macro(html, i)
        if m is None:
            break

        macro_result = m.macro # default result is the macro itself

        if m.contents == 'NAV':
            # generate nav html
            macro_result = macro_nav(navpaths)
            html = html.replace(m.macro, macro_result)

            i += len(macro_result)

        else:
            i = m.endidx

    filepath.write_text(html)

def build(sourcepath: Path, buildpath: Path) -> None:
    # copy source directory to build directory
    copytree(sourcepath, buildpath, dirs_exist_ok=True)

    # find all .md files
    filepaths = list(buildpath.glob('*.md')) # use **/*.md to search subdirectories
    templatepath = buildpath.joinpath(Path('template.html'))

    # convert markdown files to html files
    for p in filepaths:
        build_md_file(p, templatepath)
    
    # find all .html files
    filepaths = list(buildpath.glob('*.html'))
    for p in filepaths:
        # find all other html files
        otherfiles = []
        for o in filepaths:
            if o.samefile(templatepath):
                continue
            otherfiles.append(o)

        # apply macros in html files
        build_html_file(p, otherfiles)

if __name__ == '__main__':
    # parse args
    sourcepath = None
    if len(sys.argv) < 3:
        print('Usage: mori [SOURCE_DIRECTORY] [BUILD_DIRECTORY]')
        sys.exit(-1)
    sourcepath = Path(sys.argv[1])
    if not sourcepath.is_dir(): # if not directory or doesn't exist
        bail(-1, 'source directory "' + str(sourcepath) + '" doesn\'t exist')
    buildpath = Path(sys.argv[2])
    if not buildpath.is_dir():
        bail(-1, 'build directory "' + str(buildpath) + '" doesn\'t exist')
    
    build(sourcepath, buildpath)
