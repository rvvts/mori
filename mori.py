import sys
import os
from pathlib import Path
from shutil import copytree
from markdown import Markdown
import re

def bail(code: int, msg: str):
    """
    Write a message to stderr and exit.
    """
    print('mori: ' + msg, file=sys.stderr)
    sys.exit(code)

class Macro:
    def __init__(self) -> None:
        self.macro = ''    # the entire macro, including {{ and }}
        self.contents = '' # the part inside the curly braces
        self.startidx = 0  # index of start of macro (inclusive)
        self.endidx = 0    # index of end of macro (exclusive)

def find_macro(text: str, startidx: int) -> Macro:
    """
    Finds the next macro in the text at or after the start index.
    """
    r = re.compile(r'\{\{(.*?)\}\}') # lazy match (as opposed to greedy)
    match = r.search(text, startidx)

    if match is None:
        return None
    
    m = Macro()
    m.macro = match.group(0)    # 0th match group is everything, including braces
    m.contents = match.group(1) # 1st match group is everything inside the parenthesis
    m.startidx = match.start(0) # start index of entire macro (inclusiv3)
    m.endidx = match.end(0)     # end index of entire macro (exclusive)

    return m

def build_md_file(filepath: Path, templatepath: Path) -> None:
    """
    Converts a markdown file into an html file using a template html file.
    The new html file will be created next to the markdown file
    and will have the same base filename.
    Evaluates the following macros:
    - {{CONTENT}}
    - frontmatter data (e.g. {{title}})
    """
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
            print('[warning] ' + str(templatepath) + ': unknown macro ' + m.macro + ' while processing ' + str(filepath))
            i = m.endidx

    # write html file
    htmlpath = buildpath.joinpath(filepath.stem + '.html')
    htmlpath.write_text(html)
    return htmlpath

def get_html_title(filepath: Path) -> str:
    """
    Gets the title of an html file.
    Returns an empty string if it doesn't have one.
    """
    title = ''
    with open(filepath) as f:
        html = f.read()
    m = re.search('<title>(.*)</title>', html)
    if m is not None:
        title = m.group(1) # what was inside the title tags
    return title

def macro_nav(navpaths: list[Path]) -> str:
    """
    Generates an html nav for a list of html file paths.
    """
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
    """
    Evaluates macros in html files.
    The files are modified in-place.

    Evaluates the following macros:
    - {{NAV}}
    """
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
            print('[warning] ' + str(filepath) + ': unknown macro ' + m.macro)
            i = m.endidx

    filepath.write_text(html)

def build(sourcepath: Path, buildpath: Path) -> None:
    """
    Builds all markdown and html files in the source directory
    and writes the results to the build directory.

    The build directory is not created if it doesn't already exist.
    Files in the build directory will be updated if they already exist.
    """
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
            print(f'{o} != {templatepath}')
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
