# mori

mori is a static site generator.
it converts markdown to html by using a template html file.
it also evaluates some macros in html files.

## installation

all you need is `mori.py`

## usage

usage: `python mori.py [SOURCE_DIRECTORY] [BUILD_DIRECTORY]`

for example:
to build all markdown files in the current directory
and output the results in a subfolder called "build", run
`python mori.py . build`

mori won't automatically create the build directory if it doesn't already exist.
mori will update existing files in the build directory if it already exists.
mori will look for a `template.html` file in the source directory.

## macros

format: `{{macro text goes here}}`

| macro | description |
|-------|-------------|
| `{{CONTENT}}` | when used in a template, expands to the contents of a markdown file |

if a macro isn't found in the list above,
then mori searches for an entry with the same name
in the frontmatter of the markdown file,
and the macro will be expanded to that entry's value.

for example:
if your markdown files contain a frontmatter entry like `title: Hello, world!`,
you can use the macro `{{title}}` to get that value.

if a macro is unkown (not found in the list above and not found in frontmatter),
it will remain as-is, and mori will output a warning.

capitalized macros (e.g. `{{CONTENT}}`) are reserved for mori.
you *can* use them, but they may be overridden by mori's own behavior
in the future.
