//! The web page's touch control dock and independent room-tip presentation.
//! Native builds keep the original HUD. The browser shell opts in only once
//! its controls are ready, and opts out again when the dock is hidden.

use crate::grid::Player;

/// Stable values shared with the browser's touch-dock state adapter.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u32)]
pub(crate) enum Screen {
    Title = 1,
    Map = 2,
    Playing = 3,
    Won = 4,
    Lost = 5,
    Menu = 6,
    Code = 7,
    Transition = 8,
}

pub(crate) const DIRECTION: u32 = 1;
pub(crate) const WAIT: u32 = 2;
pub(crate) const UNDO: u32 = 4;
pub(crate) const RESTART: u32 = 8;
pub(crate) const CONFIRM: u32 = 16;

/// Room identity and initial hero count stay attached to an obscured level,
/// keeping the dock's geometry stable through menus and outcome cards.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct State<'a> {
    pub(crate) room: &'a str,
    pub(crate) screen: Screen,
    pub(crate) players: usize,
    pub(crate) actions: u32,
}

#[cfg(target_arch = "wasm32")]
unsafe extern "C" {
    fn infestation_touch_controls_visible() -> u32;
    fn infestation_touch_selected_player() -> u32;
    fn infestation_touch_input_epoch() -> u32;
    fn infestation_touch_state(
        room_ptr: *const u8,
        room_len: u32,
        screen: u32,
        players: u32,
        actions: u32,
    );
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

/// The page copies the room name synchronously; it never keeps a WASM pointer.
pub(crate) fn set_state(state: State<'_>) {
    #[cfg(target_arch = "wasm32")]
    unsafe {
        infestation_touch_state(
            state.room.as_ptr(),
            state.room.len() as u32,
            state.screen as u32,
            state.players as u32,
            state.actions,
        );
    }
    #[cfg(not(target_arch = "wasm32"))]
    let _ = state;
}

/// A browser interruption invalidates buffered input without rewinding a turn.
pub(crate) fn input_epoch() -> u32 {
    #[cfg(target_arch = "wasm32")]
    {
        unsafe { infestation_touch_input_epoch() }
    }
    #[cfg(not(target_arch = "wasm32"))]
    {
        0
    }
}

pub(crate) fn selected_player() -> Option<Player> {
    #[cfg(target_arch = "wasm32")]
    {
        match unsafe { infestation_touch_selected_player() } {
            1 => Some(Player::Player1),
            2 => Some(Player::Player2),
            _ => None,
        }
    }
    #[cfg(not(target_arch = "wasm32"))]
    {
        None
    }
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
