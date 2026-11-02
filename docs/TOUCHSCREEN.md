# Touchscreen guide

This fork adapts [David Spies's Infestation](https://github.com/davidspies/infestation)
for touch while retaining the original game rules, levels and assets. Build and
serve it from source using the [README instructions](../README.md).

## Playing

Tap **Tap to play** after loading, then **OK** to begin. The initial tap also
allows the browser to start audio. The game is turn based, so there is no need
to rush between moves.

| Control | Action |
| --- | --- |
| Directional pad | Move the selected hero. Tap for a step or hold to repeat. You can slide between directions. |
| Wait | Pass a turn without moving. In two-hero rooms, it supplies a wait for both heroes. |
| OK | Start, enter a selected room, choose a menu item or continue after winning. |
| Undo | Take back a move. |
| Restart | Tap twice within two seconds to confirm a restart. |
| 1 / 2 | Choose the hero controlled by the directional pad. In solo rooms, either selection controls the same hero. |
| Sync | Queue directions for a simultaneous two-hero turn. |
| Menu (☰) | Open the game's menu. |
| Controls (▤) | Hide or show the touch dock. |
| Fullscreen (⛶) | Enter or leave fullscreen when supported by the browser. |
| Help (?) | Open the touch-control guide. |

The game's own menu buttons and map rooms also accept direct taps. Drag the
map to explore it. The pad and OK provide another way to navigate menus.

### Two heroes and Sync

For an ordinary move, leave Sync off and select the hero to move. For a
simultaneous turn, turn Sync on, select hero 1 and tap a direction, then select
hero 2 and tap their direction. Both heroes can then take their queued turns
together. Release the direction button before switching heroes.

Sync uses the game's existing synchronized-input behavior. Turning it off
changes subsequent input; it **does not clear a direction already queued in
the game**. Choose another direction to replace that hero's queued input. With
the direction buttons released, Wait supplies waiting inputs for both heroes.

Disconnect physical gamepads when using the touch buttons for both heroes.
The original input system changes keyboard-to-hero routing when a gamepad is
connected, and the touch pad sends those same keyboard inputs. Hero 1 uses the
arrow keys and right Shift for Sync; hero 2 uses WASD and left Shift. The
adapter intentionally preserves this existing game input model.

## Layout and room tips

The bottom dock is about 151 CSS pixels high in its standard layout, with
44-pixel-high primary controls. At widths up to 700 pixels, it uses the
available phone width. On landscape screens up to 600 pixels high, the dock
moves to a 160-pixel-wide side column. The surrounding page also accounts for
device safe areas.

When the game uses its portrait layout and the touch controls are ready and
visible, level scenes reclaim the space used by the original lower instruction
panel. The level's title and status header stay visible. The removed panel's
buttons also stop accepting clicks, so they cannot intercept touches on the
enlarged board.

Room tips appear as an independent overlay near the bottom of the game area.
They can cover part of the puzzle, but they do not consume board layout space.
Scroll a long tip, tap **−** to minimize it, and tap **Room tip** to reopen it.
The full text determines the card's size before the typewriter effect finishes.
Showing, hiding, changing or revealing tip text never changes the board's
position or scale at a fixed viewport and controls state.

A tip retains its dismissal and scroll position while temporarily suppressed,
such as behind a menu. A different room, text or speaker starts a new tip.
Tips are suppressed during transitions, outcome cards, the welcome screen and
help. Touching or scrolling a tip releases held movement.

Hiding the touch controls restores the game's own portrait panel. Rotating the
device or toggling the dock can therefore change the board layout. In the
game's landscape layout, its existing status and field-guide panel remains.
The game's layout follows the available canvas size, which can differ from
the device's orientation after the dock takes its share of the screen. Native
builds keep the original HUD and tutorial presentation.

## Source map

| File | Responsibility |
| --- | --- |
| `index.html` | Web page, control buttons, welcome/help UI and room-tip markup. |
| `touch.css` | Compact responsive dock, safe areas and independent tip overlay. |
| `js/touch-controls.js` | Pointer input, hero selection, Sync modifiers and keyboard-event dispatch to the canvas. |
| `js/touch-shell.js` | Loading, audio activation, visibility, fullscreen, help and the JavaScript side of the game bridge. |
| `js/touch-tips.js` | Tip identity, typewriter text, dismissal, suppression and scroll restoration. |
| `game/src/touch_ui.rs` | WebAssembly imports for control visibility and authored tip text, with native fallbacks. |
| `game/src/scenes/level.rs` | Level layout adjustment and publication of the current room tip. |
| `game/src/render/ui.rs` | Reclaims the portrait instruction panel's space for the board. |
| `game/src/scenes/level/hud.rs` | Omits the replaced panel and its pointer targets. |
| `game/src/app.rs` | Coordinates tip visibility with scenes, menus and transitions. |
| `tests/touch-controls.test.cjs` | Input lifecycle and queue regression tests. |
| `tests/touch-tips.test.cjs` | Tip content, visibility, identity and scroll regression tests. |

The pointer adapter keeps short taps active for at least 80 milliseconds and
two animation frames so the game's polling loop can see them. It separates
rapid taps, tracks ownership when several fingers share a button, and
serializes directions per hero to avoid unintended direction chords. Undo,
Restart, Menu and OK cancel buffered movement. Cancellation, focus loss,
backgrounding and resizing release held input.

The web page and WebAssembly binary should be built and served from the same
revision. The updated game imports the visibility and tip callbacks registered
by the page. `./serve.sh` builds the binary at the path used by `index.html`.

## Validation and browser limits

Run the JavaScript regression tests from the repository root:

```sh
node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs
```

Build and run the web game with the normal source workflow:

```sh
rustup target add wasm32-unknown-unknown
./serve.sh
```

For a device check, exercise quick taps, held movement, direction changes,
Undo, the two-tap restart, hero switching and Sync. In portrait gameplay, open
and minimize a long tip and step onto or away from a tutorial trigger: the
board should stay at the same position and scale. Check rotating, hiding and
showing controls, opening menus, and returning after the browser has been
backgrounded. Check the native version with `cargo run -r` when changing the
shared Rust HUD code.

The game still needs WebAssembly and a working WebGL context. Browsers without
usable hardware graphics support may be unable to start it; reload after a
lost graphics context. Fullscreen depends on browser support, and audio needs
a real user gesture. Automated DOM/input tests do not establish rendering
performance or compatibility on a physical phone.

Some original tutorial wording still names keyboard keys. Very short screens
can leave menus cramped; try portrait, hide the controls, or navigate with the
pad and OK. Progress uses this site's browser storage and is separate from
progress on the original upstream site or another hosting origin.
