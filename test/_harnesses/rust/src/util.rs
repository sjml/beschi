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

    pub fn check(&self) {
        if !self.ok {
            eprintln!("Failed assertions.");
            std::process::exit(1);
        }
    }
}

pub fn arg_parse() -> HashMap<String, String> {
    let mut args = HashMap::new();

    let mut current_keyword: Option<String> = None;
    for a in env::args() {
        if let Some(keyword) = a.strip_prefix("--") {
            current_keyword = Some(keyword.to_string());
            continue;
        }
        if let Some(kw) = current_keyword {
            args.insert(kw, a);
            current_keyword = None;
            continue;
        }
    }

    args
}
