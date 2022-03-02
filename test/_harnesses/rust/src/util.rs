use std::env;
use std::collections::HashMap;

pub struct Checker {
    pub ok: bool,
}
impl Checker {
    pub fn soft_assert(&mut self, condition: bool, label: &str) {
        if !condition {
            eprintln!("FAILED! Rust: {}", label);
            self.ok = false;
        }
    }
}

pub fn arg_parse() -> HashMap<String, String> {
    let mut args = HashMap::new();

    let mut current_keyword: Option<String> = None;
    for a in env::args() {
        if a.starts_with("--") {
            current_keyword = Some(a[2..].to_string());
            continue;
        }
        match current_keyword {
            Some(kw) => {
                args.insert(kw, a);
                current_keyword = None;
                continue;
            },
            None => (),
        }
    }

    return args;
}
