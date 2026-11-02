use serde::{Deserialize, Serialize};

use crate::storage;

const SETTINGS: &str = "settings";

/// Player preferences, persisted across sessions.
#[derive(Clone, Serialize, Deserialize)]
#[serde(default)]
pub(crate) struct Settings {
    pub(crate) music_volume: f32,
    pub(crate) sfx_volume: f32,
    /// How much the screen shakes, from 0 (not at all) to 1 (fully).
    pub(crate) screen_shake: f32,
    /// Put the touch D-pad on the right and the action buttons on the left.
    pub(crate) touch_dpad_right: bool,
    /// Explicit on-screen control preference; None keeps the device default.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub(crate) touch_controls_visible: Option<bool>,
    /// The level the hero last stood at on the world map.
    pub(crate) map_level: Option<String>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            music_volume: 0.5,
            sfx_volume: 0.9,
            screen_shake: 1.0,
            touch_dpad_right: false,
            touch_controls_visible: None,
            map_level: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn older_settings_keep_their_values_and_default_to_the_left_dpad() {
        let settings: Settings = serde_json::from_str(
            r#"{"music_volume":0.2,"sfx_volume":0.7,"screen_shake":0.4,"map_level":"planks"}"#,
        )
        .unwrap();
        assert!(!settings.touch_dpad_right);
        assert_eq!(settings.touch_controls_visible, None);
        assert_eq!(settings.music_volume, 0.2);
        assert_eq!(settings.sfx_volume, 0.7);
        assert_eq!(settings.screen_shake, 0.4);
        assert_eq!(settings.map_level.as_deref(), Some("planks"));
    }

    #[test]
    fn dpad_side_round_trips_with_the_other_settings() {
        let settings = Settings {
            touch_dpad_right: true,
            music_volume: 0.3,
            ..Settings::default()
        };
        let loaded: Settings =
            serde_json::from_str(&serde_json::to_string(&settings).unwrap()).unwrap();
        assert!(loaded.touch_dpad_right);
        assert_eq!(loaded.music_volume, 0.3);
        assert_eq!(loaded.sfx_volume, settings.sfx_volume);
        assert_eq!(loaded.screen_shake, settings.screen_shake);
    }

    #[test]
    fn control_visibility_round_trips_without_losing_device_defaults() {
        for preference in [None, Some(false), Some(true)] {
            let settings = Settings {
                touch_controls_visible: preference,
                touch_dpad_right: true,
                music_volume: 0.3,
                ..Settings::default()
            };
            let saved = serde_json::to_value(&settings).unwrap();
            if preference.is_none() {
                assert!(saved.get("touch_controls_visible").is_none());
            }
            let loaded: Settings = serde_json::from_value(saved).unwrap();
            assert_eq!(loaded.touch_controls_visible, preference);
            assert!(loaded.touch_dpad_right);
            assert_eq!(loaded.music_volume, 0.3);
        }
    }
}

impl Settings {
    pub(crate) fn load() -> Self {
        storage::load(SETTINGS).unwrap_or_default()
    }

    pub(crate) fn save(&self) {
        storage::save(SETTINGS, self);
    }
}
