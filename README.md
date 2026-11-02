# Infestation

A top-down 2D grid-based turn-based puzzle game inspired by [DROD](https://drod.caravelgames.com/).

This fork adds touchscreen controls and a mobile layout to
[David Spies's Infestation](https://github.com/davidspies/infestation). It keeps
the original game, levels, artwork and audio, with changes to the web interface
and the game's portrait HUD.

Play this version at https://perceptive-moose.github.io/infestation/.
Play the original upstream version at https://davidspies.github.io/infestation.
Build and serve this fork locally, or publish a playable copy with
[GitHub Pages](#publish-with-github-pages) using the instructions below.

AI Disclaimer: This game uses entirely AI-generated artwork, music and sound effects.

## Touchscreen support

- Prompts and tutorial notes follow the input you use: touch, keyboard or
  controller. Phones start with touch controls; using a physical keyboard,
  mouse or controller restores its instructions. Touching the game switches
  back. The Help guide follows the same input mode.
- A classic directional pad with an inactive center, beside matching Restart,
  Wait and Undo buttons. The controls expand across phone widths and move to
  a side dock on short landscape screens.
- Hero portraits and Move together appear only in two-hero rooms. Play and
  Enter room appear on the title and map screens; Continue stays on the win
  card. Settings use direct taps, without a redundant Select button. The dock
  keeps the same geometry throughout a room.
- Drag the settings sliders, scroll the settings panel on smaller screens,
  and choose which side holds the D-pad. The control-side preference is saved
  alongside the existing audio and screen-shake preferences.
- Set **On-screen controls: shown / hidden** in the game menu to show or hide
  the pad. Your choice is saved; before you choose, phones show the pad and
  desktops hide it by default.
- In portrait gameplay, the touch dock replaces the duplicate instruction
  panel, giving its space back to the puzzle. Room tips appear in a scrollable,
  dismissible overlay; opening, closing or typing a tip does not resize or
  reposition the board.
- Direct taps on the game's menus and map, audio activation on a real gesture,
  and fullscreen where the browser supports it. Keyboard
  and controller controls remain available, and native builds retain their original HUD.
- The game opens automatically when loading finishes. The first keyboard or
  pointer gesture enables audio. Help pauses game input for every device,
  and returning to play suppresses carried holds. Touch directions remain
  separate from physical keyboard input, so changing instruction mode cannot
  change which hero a held key controls.
- Undoable restarts: undo past the moves in a fresh attempt to restore the
  previous one, then keep undoing through earlier moves and restarts.

See the [touchscreen guide](docs/TOUCHSCREEN.md) for controls, input switching,
implementation details and device checks.

## Development

Install Rust through [rustup](https://rustup.rs/) and Python 3, then run these
commands from the repository root:

```sh
rustup target add wasm32-unknown-unknown
./serve.sh
```

`./serve.sh` builds the web version and serves it at http://localhost:8080.
For a phone on the same network, open port 8080 at the computer's local network
address. The first build needs network access for dependencies and any missing
fonts or JavaScript runtime files. Use an up-to-date Rust toolchain; the game
uses the Rust 2024 edition.

- `cargo run -r` runs the native version (from the repository root, where it
  finds `assets/music`). Pass a level name, e.g. `cargo run -r -- chase`, to
  start in that level (`?level=chase` on the web).
- Levels live in `levels/` (CSV grid + JSON metadata); `levels/world_map.json`
  lays out the world map: themed rooms, the level nodes and the paths between
  them. Levels unlock the way the old hub levels gated them: you can walk
  through junctions and completed levels, and play any level you can reach.
- `cargo run -r --bin editor <level>` opens the level editor.

### Tests

Run the game-state, scene and original puzzle-scenario regression tests,
including undo across restarts:

```sh
cargo test --locked -p infestation -p scenario_tests --lib
```

On Ubuntu, native tests need `libasound2-dev`, `libudev-dev` and `pkg-config`.

The JavaScript tests use Node.js's built-in test runner and require no npm
packages. Run the Rust tests above first; their build step prepares the browser
runtime used by the shell integration tests:

```sh
node --test tests/*.test.cjs
```

These cover input handling, device detection, adaptive controls, room-tip state,
and integration of the browser shell with automatic startup, Help and loading
recovery.
Also test the served game on
physical phones: the Node tests do not exercise WebGL rendering, browser audio,
fullscreen or device-specific touch behavior. The web game requires a browser
with WebAssembly and working WebGL graphics support.

### Publish with GitHub Pages

In the fork's **Settings → Pages → Build and deployment**, select **GitHub
Actions** as the source. If GitHub has disabled workflows in the new fork,
enable them from the **Actions** tab.

The **Deploy to GitHub Pages** workflow runs on pushes to `master` and can also
be started manually. It runs the game, original puzzle scenarios and browser
regression tests, builds the
current game with `Cargo.lock`, packages the matching browser files and music,
and publishes the result. Future pushes to `master` update the playable site.
The historical comparison versions remain in Git history; this workflow
publishes the current touchscreen game.

After the first successful deployment, the Pages settings and workflow's
`github-pages` environment show the live URL. For this repository, the default
address is `https://perceptive-moose.github.io/infestation/`. The URL becomes
available only after Pages has been enabled and a deployment has succeeded.

See GitHub's [publishing source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
for the one-time repository setting. The workflow uses GitHub's automatic
token once Pages is configured; no personal access token needs to be added as
a repository secret.

### Generated assets

The art and audio are generated by deterministic scripts; rerun them after
changing them:

- `python3 scripts/art/generate_art.py [--review DIR]` writes the sprite atlas
  (`assets/sprites.png` + `.json`) and tiling textures (`assets/textures/`).
  Needs pycairo, numpy, scipy and Pillow.
- `python3 scripts/audio/generate_audio.py [sfx|music]` writes the sound
  effects and music loops (`assets/sfx/`, `assets/music/`) as Ogg Vorbis for
  native builds and MP3 for the web. Needs numpy, scipy, and ffmpeg with
  libvorbis and libmp3lame.

`SHOTS_DIR=/tmp/shots cargo test -r -p infestation screenshots -- --ignored --test-threads=1`
renders scripted scenes (title, levels, effects frame by frame, the world map
and a full title-to-map-to-level flow) to PNGs for visual review. `W`/`H` set
the window size, `HINTS=pad` controller prompts, `HINTS=touch` touch prompts,
and `ONLY=` a
comma-separated list of shot name prefixes.
