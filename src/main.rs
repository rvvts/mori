use markdown as md;
use std::fs;
use mlua::Lua;
use fs_extra;
use std::path::Path;

/// Given the index of a character, finds the line number.
/// O(n).
fn get_line_number(text: &str, char_idx: usize) -> usize {
    let mut line = 1;
    let mut idx = 0;
    for c in text.chars() {
        if c == '\n' {
            line += 1;
        }

        if idx >= char_idx {
            break;
        }

        idx += 1;
    }

    return line;
}

/// Creates an Options object for the markdown parser
fn md_init() -> md::Options {
    let mut commonmark = md::Constructs::default();
    commonmark.frontmatter = true;
    commonmark.math_flow = true; // enable math latex blocks
    commonmark.math_text = true; // enable inline math latex

    let mut parse_options = md::ParseOptions::default();
    parse_options.constructs = commonmark;

    let mut options = md::Options::default();
    options.parse = parse_options;

    options
}

/// Converts markdown strings to html strings
fn md_to_html(config: &md::Options, markdown_text: &String) -> Result<String, String> {
    md::to_html_with_options(markdown_text, config)
}

/// Given the text of a file, finds and evaluates lua macros. Returns the modified text of the file.
fn evaluate_macros(lua: &Lua, text: &str) -> String {
    let mut result = String::from(text);

    let mut macro_start_idx: usize;
    let mut macro_end_idx = 0;

    loop {
        macro_start_idx = match text[macro_end_idx..].find("{{") {
            Some(x) => x + macro_end_idx,
            None => break
        };
    
        macro_end_idx = match text[macro_start_idx..].find("}}") {
            Some(x) => x + macro_start_idx,
            None => break
        };

        let macro_text = &text[macro_start_idx..macro_end_idx+2];     // the macro itself, including {{ }}
        let macro_contents = &text[macro_start_idx+2..macro_end_idx]; // the text inside the macro

        let output = match lua.load(macro_contents).eval::<String>() {
            Ok(x) => x,
            Err(x) => {
                println!("ERROR: At line {} when executing {macro_text}", get_line_number(text, macro_start_idx)); // every error is O(n), so overall this could be O(n^2)!
                println!("\t{x}");
                String::from(macro_text)
            }
        };
        result = result.replacen(macro_text, &output, 1);
    }
    
    return result;
}

fn init_lua(lua: &Lua) {
    let globals = lua.globals();

    let md_to_html = lua.create_function(|_, markdown: String| {
        Ok(md_to_html(&md_init(), &markdown).expect("ERROR: md_to_html() failed."))
    }).expect("ERROR: Failed to create lua function.");
    globals.set("md_to_html", md_to_html)
        .expect("ERROR: Failed to add lua function.");
}

/// deletes the build directory if it exists
fn clean_build_directory(build_dir: &Path) {
    if build_dir.exists() {
        fs::remove_dir_all(build_dir)
            .expect("Failed to delete build directory.");
    }
}

/// creates the build directory if it doesn't exist, and copies the source directory's contents into it
fn init_build_directory(source_dir: &Path, build_dir: &Path) {
    assert!(source_dir.exists());

    if !build_dir.exists() {
        println!("Build directory not found. Attempting to create it...");
        fs::create_dir_all(build_dir)
            .expect("Failed to create build directory!");
        println!("Build directory created.");
    }

    assert!(build_dir.exists());

    // perform the copy
    let mut copy_options = fs_extra::dir::CopyOptions::new();
    copy_options.overwrite = true;    // overwrite existing destination files
    copy_options.content_only = true; // only copy the files inside the source directory
    fs_extra::dir::copy(source_dir, build_dir, &copy_options)
        .expect("Failed to copy source directory contents into build directory!");
}

/// creates a template file for the markdown file
fn template_md(md_path: &Path, template_path: &Path) {
    let md_name = md_path.file_stem()
        .expect("Could not get file name of markdown file.");
    let mut html_name = std::ffi::OsString::from(md_name);
    html_name.push(std::ffi::OsString::from(".html"));
    let html_path = md_path.with_file_name(&html_name);
    
    // create the html file
    fs::copy(template_path, html_path)
        .expect("Failed to create template copy.");
}

/// expands code-generating macros
fn generate_code(path: &Path) {
    
}

fn main() {
    let lua = Lua::new();
    init_lua(&lua);

    let html_filepath = String::from("template.html");
    let html_file_text = fs::read_to_string(html_filepath)
        .expect("Could not open html file.");
    let result = evaluate_macros(&lua, &html_file_text);
    println!("{result}");

    // let source_dir = Path::new("put a valid path here");
    // let build_dir = Path::new("put another valid path here");    

    // clean_build_directory(build_dir);
    // init_build_directory(source_dir, build_dir);
    // assert!(build_dir.exists());

    // let items = fs_extra::dir::get_dir_content(build_dir)
    //     .expect("Couldn't access build folder.");
    // for file in items.files {
    //     if !file.ends_with(".md") {
    //         continue;
    //     }
    //     println!("Templating file {file}...");
    //     let template_path = build_dir.join("templates").join("template.html");
    //     assert!(template_path.exists());
    //     template_md(Path::new(&file), template_path.as_path());
    // }
}
