# mori
A static site generator powered by markdown and lua.

## Features
- Convert markdown files to html via custom html templates.
- Specify custom data fields in markdown frontmatter.
- Evaluate lua code inside html files.
- Provides a powerful lua api.
- Build sites in one command.
- Supports in-source and out-of-source builds.

## Architecture
mori is really two things in one: A preprocessor that runs lua macros, and a templating engine that generates lua macros.

## How it works
- First, all files are copied into the build directory.
- Then, for each markdown file that has a `template` field in its frontmatter, a unique copy of the template is created.
  - Files without a `template` field are ignored.
  - Special macros such as `{{ markdown content }}` are replaced with generated lua code specific to that file.
- After that, lua macros in all html files are evaluated.
  - Each macro is replaced by its return value.
- Finally, markdown files in the build directory are removed.

## Getting started
1. Install rust + cargo.
2. Clone this repo.
3. Build it with `cargo build`.
4. `cd` into your website's folder.
5. Create a `build` folder inside.
6. Build your site using `mori build`

## Options
- `mori new <project_name>` - Creates a new project. A named folder for the project will be created in the current directory. Default `build/` and `templates/` folders will be created. A minimal `index.html`, html template, and markdown file will be created. 
- `mori build` - Builds a project. Defaults to `./build/` as the target directory, `./templates/` as the templates directory, and the current directory as the source directory.
  - `-q` / `--quiet` - Don't print output.
  - `-v` / `--verbose` - Print extra diagnostic info.
  - `-b` / `--build <directory>` - Override build folder. Defaults to `build/`.
  - `-t` / `--templates <directory>` - Override templates folder. Defaults to `templates/`.
  - `-s` / `--source <directory>` - Override source folder. Defaults to current directory.
  - `-T` / `--template-only` - Convert markdown files to html templates, but don't run macros.
  - `-E` / `--evaluate-only` - Skip markdown to html conversion, only run macros.
- `mori version` - Print version info.
- `mori help [subcommand] [-o|--option]` - Displays help info for mori itself, or any of its subcommands (`new`, `build`, etc.), or any of their options.

To perform an out-of-source build, you might do something like: `mori build --build ~/projects/site --templates ~/projects/site/assets --build ~/projects/temp`.

## Macros
Except for the special `{{ markdown content }}` and `{{ markdown <field> }}` macros, anything between `{{` and `}}` will be treated as lua code. Macros are evaluated in the order they appear in each file, but there is no guarantee about which files will be evaluated first. You should avoid depending on execution order.

Macros are replaced by their return value. For example, `<h1>{{ return "Hello, world!" }}</h1>` becomes `<h1>Hello, world!</h1>`.

Macros can be multi-line. For example:

```html
<ul>
    {{
    result = ""
    for i = 0..9 do
        result = result .. "<li>" .. i .. "</li>\n"
    end
    }}
</li>
```

It's considered an error if a macro doesn't return a string. mori will continue the build, but will generate a warning. If you just want to run lua code (ie. declaring functions, etc.), you'll need to put `return ""` at the end of the macro.

## Lua API
These are built-in functions you can call from inside lua macros.

- `md_to_html(filepath: string) -> string` - Converts a markdown file to html.
- `get_field(filepath: string, field: string) -> string` - Fetches metadata from a variety of file types (markdown YAML frontmatter, JSON, YAML, TOML).
- `get_file(filepath: string) -> string` - Gets the contents of a file. Useful for including repeated elements like nav links or footers.
- `get_time(format: string) -> string` - Gets the current time, formatted accordingly.
- `ls_files(directory: string) -> map<int, string>` - Lists files in a directory as a map (keys are indices, starting at 1).
- `ls_recursive(directory: string) -> map<int, string>` - Recursively lists files and directories. Returns a map (keys are indices, starting at 1) containing the relative path (from the current working directory) to each file/directory. The paths start with `/`.  Directory paths end with `/`.

## TODO
- [x] rust `get_line_number(text: &str, char_idx: usize) -> usize`
  - Given an index of a character in a file, returns the line number.
  - Useful for giving diagnostic error messages.
  - We don't usually have line number info because files are parsed as a sequence of characters.
- [ ] implement lua api
  - [x] `md_to_html()`
  - [ ] `get_field()`
  - [ ] `get_time()`
  - [ ] `ls_files()`
  - [ ] `ls_recursive()`
  - [ ] string manipulation helper functions
- [ ] implement first step (templating)
  - Evaluate the special markdown macros multiple times, until none left or iteration limit exceeded (probable recursion).
  - This is because markdown fields can contain macros too! We'll need multiple passes to evaluate them.
  - [ ] copying from source folder to build folder
  - [ ] expand code generation macros (like `{{ markdown content }}`)
- [x] implement second steps (lua evaluation)
- [ ] implement commandline options
  - [ ] `mori new`
  - [ ] `mori build`
    - [ ] `--quiet`
    - [ ] `--verbose`
    - [ ] `--build`
    - [ ] `--templates`
    - [ ] `--source`
    - [ ] `--template-only`
    - [ ] `--evaluate-only`
  - [ ] `mori version`
  - [ ] `mori help`
- [ ] cleanly architect the code
  - [x] lua setup
  - [ ] divide first step and second step into their own modules
- [ ] parse commandline args
- [ ] (not happening but would be super cool) make a custom language instead of using lua
