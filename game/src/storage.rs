use std::collections::HashSet;

use base64::Engine;
use base64::engine::general_purpose::STANDARD;
use serde::Serialize;
use serde::de::DeserializeOwned;

macro_rules! warn_err {
    ($expr:expr, $($arg:tt)+) => {
        $expr.map_err(|e| log::warn!($($arg)+, e)).ok()
    };
}

const COMPLETED_LEVELS: &str = "completed_levels";

pub(crate) fn load_completed_levels() -> HashSet<String> {
    load::<HashSet<String>>(COMPLETED_LEVELS)
        .unwrap_or_default()
        .into_iter()
        .map(|s| strip_path_prefix(&s).to_string())
        .collect()
}

pub(crate) fn save_completed_levels(completed: &HashSet<String>) {
    save(COMPLETED_LEVELS, completed);
}

/// Load a saved value, if there is one (and it parses).
pub(crate) fn load<T: DeserializeOwned>(name: &str) -> Option<T> {
    let json = backend::load(name)?;
    warn_err!(
        serde_json::from_str(&json),
        "Failed to parse saved {}: {}",
        name
    )
}

pub(crate) fn save<T: Serialize>(name: &str, value: &T) {
    let json = serde_json::to_string(value).expect("saved values should serialize");
    backend::save(name, &json);
}

fn encode_progress(completed: &HashSet<String>) -> String {
    use flate2::Compression;
    use flate2::write::ZlibEncoder;
    use std::io::Write;

    let mut sorted: Vec<&str> = completed.iter().map(String::as_str).collect();
    sorted.sort();
    let json = serde_json::to_string(&sorted).expect("completed levels should serialize");

    let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
    encoder
        .write_all(json.as_bytes())
        .expect("zlib write should succeed");
    let compressed = encoder.finish().expect("zlib finish should succeed");

    STANDARD.encode(&compressed)
}

fn decode_progress(encoded: &str) -> Result<HashSet<String>, String> {
    use flate2::read::ZlibDecoder;
    use std::io::Read;

    let encoded: String = encoded.chars().filter(|c| !c.is_whitespace()).collect();
    let compressed = STANDARD
        .decode(encoded)
        .map_err(|e| format!("invalid base64: {e}"))?;
    let mut decoder = ZlibDecoder::new(&compressed[..]);
    let mut json_str = String::new();
    decoder
        .read_to_string(&mut json_str)
        .map_err(|e| format!("invalid zlib data: {e}"))?;
    let levels: Vec<String> =
        serde_json::from_str(&json_str).map_err(|e| format!("invalid JSON: {e}"))?;
    Ok(levels.into_iter().collect())
}

pub(crate) fn strip_path_prefix(s: &str) -> &str {
    s.rsplit('/').next().unwrap_or(s)
}

#[cfg(all(target_arch = "wasm32", not(test)))]
mod backend {
    fn key(name: &str) -> String {
        format!("infestation_{name}")
    }

    pub(super) fn save(name: &str, json: &str) {
        quad_storage::STORAGE.lock().unwrap().set(&key(name), json);
    }

    pub(super) fn load(name: &str) -> Option<String> {
        quad_storage::STORAGE.lock().unwrap().get(&key(name))
    }
}

#[cfg(all(not(target_arch = "wasm32"), not(test)))]
mod backend {
    use std::fs::{create_dir_all, read_to_string, write};
    use std::path::PathBuf;

    pub(super) fn save(name: &str, json: &str) {
        if let Some(path) = save_path(name) {
            if let Some(parent) = path.parent() {
                warn_err!(
                    create_dir_all(parent),
                    "Failed to create {}: {}",
                    parent.display()
                );
            }
            warn_err!(write(&path, json), "Failed to write {}: {}", path.display());
        }
    }

    pub(super) fn load(name: &str) -> Option<String> {
        let path = save_path(name)?;
        if !path.exists() {
            return None;
        }
        warn_err!(
            read_to_string(&path),
            "Failed to read {}: {}",
            path.display()
        )
    }

    fn save_path(name: &str) -> Option<PathBuf> {
        let dirs = directories::ProjectDirs::from("", "dspyz", "InfestationGame")?;
        Some(dirs.data_dir().join(format!("{name}.json")))
    }
}

/// Tests keep saves in memory, so they can never touch the player's real
/// save files.
#[cfg(test)]
mod backend {
    use std::cell::RefCell;
    use std::collections::HashMap;

    thread_local! {
        static SAVES: RefCell<HashMap<String, String>> = RefCell::new(HashMap::new());
    }

    pub(super) fn save(name: &str, json: &str) {
        SAVES.with(|saves| {
            saves
                .borrow_mut()
                .insert(name.to_string(), json.to_string())
        });
    }

    pub(super) fn load(name: &str) -> Option<String> {
        SAVES.with(|saves| saves.borrow().get(name).cloned())
    }
}

/// Copyable progress codes and platform-specific import input.
pub(crate) mod progress {
    use super::*;

    #[derive(serde::Deserialize)]
    #[serde(tag = "action", rename_all = "snake_case")]
    enum ImportInput {
        Submit { code: String },
        Cancel,
    }

    pub(crate) enum ImportOutcome {
        Imported(HashSet<String>),
        Cancelled,
    }

    pub(crate) fn encode(completed: &HashSet<String>) -> String {
        encode_progress(completed)
    }

    pub(crate) fn decode(encoded: &str) -> Result<HashSet<String>, String> {
        decode_progress(encoded)
    }

    pub(crate) fn copy_to_clipboard(text: &str) {
        platform::write(text);
    }

    pub(crate) fn start_import() {
        platform::start_import();
    }

    pub(crate) fn finish_import() {
        platform::finish_import();
    }

    #[must_use]
    pub(crate) fn poll_import() -> Option<ImportOutcome> {
        let code = match platform::poll_input()? {
            ImportInput::Submit { code } => code,
            ImportInput::Cancel => return Some(ImportOutcome::Cancelled),
        };
        match decode(&code) {
            Ok(levels) => Some(ImportOutcome::Imported(levels)),
            Err(e) => {
                log::warn!("Failed to decode imported progress: {}", e);
                #[cfg(target_arch = "wasm32")]
                {
                    platform::show_import_error(&e);
                    None
                }
                #[cfg(not(target_arch = "wasm32"))]
                Some(ImportOutcome::Cancelled)
            }
        }
    }

    #[cfg(target_arch = "wasm32")]
    mod platform {
        use super::ImportInput;

        const IMPORT_KEY: &str = "infestation_progress_import";

        unsafe extern "C" {
            fn sapp_clipboard_write(buf: *const u8, len: u32);
            fn sapp_progress_import();
            fn sapp_progress_import_error(buf: *const u8, len: u32);
            fn sapp_progress_import_finish();
        }

        pub(super) fn write(text: &str) {
            unsafe { sapp_clipboard_write(text.as_ptr(), text.len() as u32) };
        }

        pub(super) fn start_import() {
            unsafe { sapp_progress_import() };
        }

        pub(super) fn finish_import() {
            unsafe { sapp_progress_import_finish() };
        }

        pub(super) fn show_import_error(error: &str) {
            unsafe { sapp_progress_import_error(error.as_ptr(), error.len() as u32) };
        }

        #[must_use]
        pub(super) fn poll_input() -> Option<ImportInput> {
            let mut storage = quad_storage::STORAGE.lock().unwrap();
            let text = storage.get(IMPORT_KEY)?;
            storage.remove(IMPORT_KEY);
            drop(storage);
            match serde_json::from_str(&text) {
                Ok(input) => Some(input),
                Err(error) => {
                    log::warn!("Failed to read progress import: {}", error);
                    show_import_error("Invalid import request. Please try again.");
                    None
                }
            }
        }
    }

    #[cfg(not(target_arch = "wasm32"))]
    mod platform {
        use std::sync::Mutex;

        use super::ImportInput;

        static PENDING: Mutex<Option<ImportInput>> = Mutex::new(None);

        pub(super) fn write(text: &str) {
            if let Ok(mut cb) = arboard::Clipboard::new() {
                let _ = cb.set_text(text);
            }
        }

        pub(super) fn start_import() {
            let input = match arboard::Clipboard::new().and_then(|mut c| c.get_text()) {
                Ok(code) if !code.trim().is_empty() => ImportInput::Submit { code },
                Ok(_) => ImportInput::Cancel,
                Err(error) => {
                    log::warn!("Failed to read progress from clipboard: {}", error);
                    ImportInput::Cancel
                }
            };
            *PENDING.lock().unwrap() = Some(input);
        }

        pub(super) fn finish_import() {}

        #[must_use]
        pub(super) fn poll_input() -> Option<ImportInput> {
            PENDING.lock().unwrap().take()
        }

        #[cfg(test)]
        mod tests {
            use super::*;
            use crate::storage::progress::{ImportOutcome, poll_import};

            #[test]
            fn native_import_failure_finishes_instead_of_staying_pending() {
                for input in [
                    ImportInput::Cancel,
                    ImportInput::Submit {
                        code: String::new(),
                    },
                    ImportInput::Submit {
                        code: "not a code!".to_string(),
                    },
                ] {
                    *PENDING.lock().unwrap() = Some(input);
                    assert!(matches!(poll_import(), Some(ImportOutcome::Cancelled)));
                    assert!(poll_import().is_none());
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use flate2::Compression;
    use flate2::write::ZlibEncoder;
    use std::io::Write;

    fn code_for_json(json: &str) -> String {
        let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
        encoder.write_all(json.as_bytes()).unwrap();
        STANDARD.encode(encoder.finish().unwrap())
    }

    #[test]
    fn progress_codes_round_trip_with_pasted_whitespace() {
        let levels = HashSet::from(["rats".to_string(), "webs".to_string()]);
        let code = encode_progress(&levels);
        assert_eq!(decode_progress(&code).unwrap(), levels);

        let wrapped = code
            .as_bytes()
            .chunks(8)
            .map(|chunk| std::str::from_utf8(chunk).unwrap())
            .collect::<Vec<_>>()
            .join("\r\n ");
        assert_eq!(decode_progress(&format!(" \t{wrapped}\n")).unwrap(), levels);
        assert_eq!(
            decode_progress(&encode_progress(&HashSet::new())).unwrap(),
            HashSet::new()
        );
    }

    #[test]
    fn invalid_progress_codes_are_rejected_before_changing_saved_progress() {
        let mut progress = crate::progress::Progress::with_completed(["rats"]);
        progress.complete("webs");
        for (code, error) in [
            ("!not base64!".to_string(), "invalid base64"),
            (STANDARD.encode(b"not zlib"), "invalid zlib data"),
            (code_for_json("not JSON"), "invalid JSON"),
            (code_for_json(r#"{"rats":true}"#), "invalid JSON"),
        ] {
            assert!(decode_progress(&code).unwrap_err().starts_with(error));
            assert_eq!(
                load_completed_levels(),
                HashSet::from(["rats".to_string(), "webs".to_string()])
            );
        }
    }

    #[test]
    fn importing_a_code_preserves_existing_completed_levels() {
        let mut progress = crate::progress::Progress::with_completed(["rats"]);
        let imported = HashSet::from(["webs".to_string()]);
        progress.import(decode_progress(&encode_progress(&imported)).unwrap());
        assert_eq!(
            load_completed_levels(),
            HashSet::from(["rats".to_string(), "webs".to_string()])
        );
    }
}
