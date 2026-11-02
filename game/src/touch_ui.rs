//! The web page's touch control dock and independent room-tip presentation.
//! Native builds keep the original HUD. The browser shell opts in only once
//! its controls are ready, and opts out again when the dock is hidden.

#[cfg(target_arch = "wasm32")]
unsafe extern "C" {
    fn infestation_touch_controls_visible() -> u32;
    fn infestation_touch_tip(
        room_ptr: *const u8,
        room_len: u32,
        text_ptr: *const u8,
        text_len: u32,
        player: u32,
        shown: u32,
        visible: u32,
    );
}

/// JavaScript copies both UTF-8 strings synchronously; no pointers are retained.
/// The full text sizes the card, while `shown` preserves the dialogue typewriter.
pub(crate) fn set_tip(room: &str, text: &str, player: u32, shown: u32, visible: bool) {
    #[cfg(target_arch = "wasm32")]
    unsafe {
        infestation_touch_tip(
            room.as_ptr(),
            room.len() as u32,
            text.as_ptr(),
            text.len() as u32,
            player,
            shown,
            u32::from(visible),
        );
    }
    #[cfg(not(target_arch = "wasm32"))]
    let _ = (room, text, player, shown, visible);
}

pub(crate) fn controls_visible() -> bool {
    #[cfg(target_arch = "wasm32")]
    {
        unsafe { infestation_touch_controls_visible() != 0 }
    }
    #[cfg(not(target_arch = "wasm32"))]
    {
        false
    }
}
