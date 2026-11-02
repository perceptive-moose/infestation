# Infestation history reconstruction

This administrative branch records the authorized history rewrite. Do not merge it into `master`.

Original head: `292f459b3a11a5ec0fa23f388f11d1e0800a9413`  
Reconstructed head: `48e5832d2f130646427159149bff3b22a74f304d`  
Unchanged upstream boundary: `a6ef414767b61977056df2b033e55334d4ff7180`  
Identical final file tree: `5dcd4c2cfc990ce52ca8071dbfce4b2800af10fe`

The original main history is retained at [the archive branch](https://github.com/perceptive-moose/infestation/tree/archive/pre-history-rewrite-2026-11-02). The original PR feature branches are retained unchanged so their historical records remain available.

The reconstruction contains 18 coherent feature commits and eight normal merge commits. Every reconstructed commit retains the human author and records ChatGPT assistance. Original author dates are retained; committer dates identify the reconstruction. Original GitHub signatures are preserved on archived originals; new commits are not represented as carrying those signatures.

The original PRs remain records of the initial squash merges. Each replacement merge links its original PR and squash. The JSON map lists the original upload commits alongside each replacement sequence, because the curation is not a one-to-one mapping.

## Replacement merges

| PR | Original squash | Replacement merge | Feature commits |
|---|---|---|---:|
| [#1](https://github.com/perceptive-moose/infestation/pull/1) | `683f65c43f0aa84a18de5c4edaf076afe6fae297` | `10d1343c6f5fce7275ad50fcb3b240bef9beb2d6` | 3 |
| [#2](https://github.com/perceptive-moose/infestation/pull/2) | `68df37681254408859ecf3bf97e75b6f060c8047` | `d120841de4b316399866892854378c41178055a0` | 2 |
| [#3](https://github.com/perceptive-moose/infestation/pull/3) | `00ba80857bc332a6c7bfd50361b35d0b7580e84f` | `7bf8590d8814fccf5a7464e3a10e07138a4edb47` | 3 |
| [#4](https://github.com/perceptive-moose/infestation/pull/4) | `341cd76430f7cc6c2f7dfac49d8bbcc46297b092` | `059931fe0040abb2f63ee2389b960d7af60db14f` | 3 |
| [#5](https://github.com/perceptive-moose/infestation/pull/5) | `2c05f78c4ea88d95f042a1294dbd862cc6edb03c` | `d619b6af7abc49cdce428fc3d0c9392de67c7e4e` | 2 |
| [#6](https://github.com/perceptive-moose/infestation/pull/6) | `7d2df58d1f6a9f468b83f1f8a853008e1703e9e1` | `fed42057b2560a12b424ebc37eb7d5573605f7fa` | 1 |
| [#7](https://github.com/perceptive-moose/infestation/pull/7) | `3db28275a7315ec553a011b4c41210cf0445559a` | `416e250a9cdcc18f4db9b604a79d5f5d873d1210` | 3 |
| [#8](https://github.com/perceptive-moose/infestation/pull/8) | `292f459b3a11a5ec0fa23f388f11d1e0800a9413` | `48e5832d2f130646427159149bff3b22a74f304d` | 1 |

## Curated changes and validation

### PR #1: Add touchscreen controls and GitHub Pages deployment

- [`c0c11bff`](https://github.com/perceptive-moose/infestation/commit/c0c11bff579f2bb3604691d7ea9371ac3439242b): Add a touch input adapter with pointer and key ownership tests
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-1-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-1-javascript.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-1-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}]
- [`1f8a08fe`](https://github.com/perceptive-moose/infestation/commit/1f8a08fe01d5ca6099f75dd6a96b2629c422b166): Add the mobile browser shell and publish its complete assets
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-2-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-2-javascript.log"}, {"command": "node --check js/touch-shell.js", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-2-shell-syntax.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-2-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-2-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]
- [`49fac1a1`](https://github.com/perceptive-moose/infestation/commit/49fac1a1dc66cb717831586025fbbebba8642da2): Keep the portrait puzzle stationary while displaying room tips
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-javascript.log"}, {"command": "node --check js/touch-shell.js", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-shell-syntax.log"}, {"command": "cargo test --locked --offline -p infestation --lib", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-native.log"}, {"command": "cargo check --locked --offline --target wasm32-unknown-unknown -p infestation --bin infestation", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-wasm-check.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr1-3-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]

Verified merge tree: `a79bb0b09c7a58198d0c61470e609838a6aaa8f3` (identical to the original squash).

### PR #2: Make restarts undoable

- [`ae9558fa`](https://github.com/perceptive-moose/infestation/commit/ae9558fa887cbe16fe7576c44fd95fd01008fa94): Preserve previous attempts when restarting a puzzle
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-1-diff-check.log"}, {"command": "cargo test --locked --offline -p infestation --lib", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-1-native.log"}, {"command": "cargo check --locked --offline --target wasm32-unknown-unknown -p infestation --bin infestation", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-1-wasm-check.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-1-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-1-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]
- [`58d603df`](https://github.com/perceptive-moose/infestation/commit/58d603df6f318bcc8661f47232bd7e55aabd7108): Expose undoable restarts through level actions and presentation
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-javascript.log"}, {"command": "node --check js/touch-shell.js", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-shell-syntax.log"}, {"command": "cargo test --locked --offline -p infestation --lib", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-native.log"}, {"command": "cargo check --locked --offline --target wasm32-unknown-unknown -p infestation --bin infestation", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-wasm-check.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr2-2-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]

Verified merge tree: `77fc1e833bc95e0b9eb0b9350ad9f5034bce9944` (identical to the original squash).

### PR #3: Redesign touch controls around movement, wait and undo

- [`62039102`](https://github.com/perceptive-moose/infestation/commit/62039102a5352af68f061abe50aadb5f355972fd): Accept a fresh input press after clearing an interrupted hold
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-1-diff-check.log"}, {"command": "cargo test --locked --offline -p infestation --lib", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-1-native.log"}, {"command": "cargo check --locked --offline --target wasm32-unknown-unknown -p infestation --bin infestation", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-1-wasm-check.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-1-touch-controls.test-direct.log", "summary": "ℹ tests 24, ℹ pass 24, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-1-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]
- [`e0925f98`](https://github.com/perceptive-moose/infestation/commit/e0925f98ec34b9d6afe006afdfcf4a88fae87001): Release touch holds safely when switching heroes or actions
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-2-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-2-javascript.log"}, {"command": "node --check js/touch-shell.js", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-2-shell-syntax.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-2-touch-controls.test-direct.log", "summary": "ℹ tests 29, ℹ pass 29, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-2-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]
- [`f8cacbd3`](https://github.com/perceptive-moose/infestation/commit/f8cacbd378a690b6a29ce23592e082f8f15754e0): Adapt the D-pad and action column to the current game state
  Validation: [{"command": "git diff --cached --check", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-diff-check.log"}, {"command": "node --test tests/touch-controls.test.cjs tests/touch-state.test.cjs tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-javascript.log"}, {"command": "node --check js/touch-shell.js", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-shell-syntax.log"}, {"command": "cargo test --locked --offline -p infestation --lib", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-native.log"}, {"command": "cargo check --locked --offline --target wasm32-unknown-unknown -p infestation --bin infestation", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-wasm-check.log"}, {"command": "node tests/touch-controls.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-touch-controls.test-direct.log", "summary": "ℹ tests 29, ℹ pass 29, ℹ fail 0"}, {"command": "node tests/touch-state.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-touch-state.test-direct.log", "summary": "ℹ tests 17, ℹ pass 17, ℹ fail 0"}, {"command": "node tests/touch-tips.test.cjs", "result": "passed", "log": "/workspace/scratch/2cbdb5cc172c/history-rewrite/pr1-3-logs/pr3-3-touch-tips.test-direct.log", "summary": "ℹ tests 18, ℹ pass 18, ℹ fail 0"}]

Verified merge tree: `56c4d6f96e443a48c0515499ffc9b30447bde65c` (identical to the original squash).

### PR #4: Make settings draggable and allow swapping touch controls

- [`5a19f754`](https://github.com/perceptive-moose/infestation/commit/5a19f754944545af55390e9648fbd5ecdb1b7f20): Make settings sliders draggable and the menu scrollable
  Validation: ["cargo test --locked --offline -p infestation --lib: 53 passed, 1 ignored", "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs: all passed", "node --check js/touch-shell.js: passed"]
- [`c33f7178`](https://github.com/perceptive-moose/infestation/commit/c33f7178d326a40001effe2d704fde1515e3bfd6): Save and apply the preferred side of the touch D-pad
  Validation: ["cargo test --locked --offline -p infestation --lib: 55 passed, 1 ignored", "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs: all passed", "node --check js/touch-shell.js: passed"]
- [`27d5586a`](https://github.com/perceptive-moose/infestation/commit/27d5586a480b45326c898d80fa535dc8a9c7a3e5): Remove redundant Select from the touch settings dock
  Validation: ["cargo test --locked --offline -p infestation --lib: 55 passed, 1 ignored", "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs: all passed", "node --check js/touch-shell.js: passed"]

Verified merge tree: `8345d7868711c7b8ecbac4d3978d31d59883a38d` (identical to the original squash).

### PR #5: Adapt instructions to touch, keyboard and controller input

- [`2addceff`](https://github.com/perceptive-moose/infestation/commit/2addceffc3ff1a4440d0e0edcd0982c98b06288a): Remove touch-demo branding from the game shell
  Validation: ["node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs: all passed", "node --check js/touch-shell.js: passed", "Rust source tree unchanged from verified PR4 endpoint"]
- [`416b3695`](https://github.com/perceptive-moose/infestation/commit/416b369597def44ae230aa3ff4c422d879134c1c): Match instructions and hero routing to the active input device
  Validation: ["cargo test --locked --offline -p infestation --lib: 63 passed, 1 ignored", "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs tests/input-mode.test.cjs: all passed", "node --check js/touch-shell.js: passed"]

Verified merge tree: `ba3ea1b150f62e0dc0ac8daa9676779441a90e14` (identical to the original squash).

### PR #6: Move on-screen controls visibility into saved settings

- [`8513f0ee`](https://github.com/perceptive-moose/infestation/commit/8513f0ee48a0099bc57eace51ef1cdfec7508e5f): Persist on-screen control visibility in game settings
  Validation: ["cargo test --locked --offline -p infestation --lib: 64 passed, 1 ignored", "node --test tests/touch-controls.test.cjs tests/touch-tips.test.cjs tests/touch-state.test.cjs tests/input-mode.test.cjs: all passed", "node --check js/touch-shell.js: passed"]

Verified merge tree: `4eaa7ec0a11260b9103b46508dd38cf6cbbdb69e` (identical to the original squash).

### PR #7: Fix browser input isolation and preserve keyboard/controller behavior

- [`e0677256`](https://github.com/perceptive-moose/infestation/commit/e06772560e3e5726684b9d26cd8d6efda6ed2955): Keep touch input independent of physical keyboard and controllers
  Validation: {"javascript": "All four existing suites passed; shell syntax passed.", "rust": "66 passed, 1 existing ignored; 130 scenario tests passed.", "logs": ["pr7-1-js.log", "pr7-1-rust.log"]}
- [`1b06efac`](https://github.com/perceptive-moose/infestation/commit/1b06efac9c9871ece8a43cee20f3c0353060a10b): Isolate browser overlays from game input and recover slow loading
  Validation: {"javascript": "All five suites passed including browser shell integration; shell syntax passed.", "rust": "66 passed, 1 existing ignored; 130 scenario tests passed.", "logs": ["pr7-2-js.log", "pr7-2-rust.log"]}
- [`b6920f48`](https://github.com/perceptive-moose/infestation/commit/b6920f4801c50c7b0c3c706e8394487bec38e6e3): Clear pending synchronized moves when restarting before turn one
  Validation: {"rust": "67 passed, 1 existing ignored; 130 scenario tests passed.", "javascript": "Unchanged from immediately preceding validated commit.", "logs": ["pr7-3-rust.log"]}

Verified merge tree: `c2991001f579bbd7f1bde7326783b23dc39d0e8a` (identical to the original squash).

### PR #8: Open the original title screen automatically after loading

- [`05fe4930`](https://github.com/perceptive-moose/infestation/commit/05fe49303bbb40916d78883b56266d6005f4bb3b): Enter the original title screen automatically after loading
  Validation: {"javascript": "All five suites passed, including 26 direct shell checks; shell syntax passed.", "rust": "Rust sources unchanged from validated PR7 endpoint.", "logs": ["pr8-1-js.log", "pr8-shell.log"]}

Verified merge tree: `5dcd4c2cfc990ce52ca8071dbfce4b2800af10fe` (identical to the original squash).

## Existing clones

Save any uncommitted work and create a local backup branch before realigning a clone. For a clone with no work to preserve, fetching the new remote history and resetting local master to origin/master is sufficient. Local feature work should be transplanted onto the new history rather than merged with the archived mainline.

## Attribution

```text
Developed with assistance from ChatGPT (OpenAI).

Co-authored-by: ChatGPT (OpenAI) <noreply@openai.com>
```

## Publication checks

The publication script checks bundle integrity, all eight merge trees and parent relationships, the complete candidate commit set, the unchanged upstream boundary, coauthor trailers, the final file tree, the old master SHA and the archive SHA. It uses an explicit force-with-lease for master. GitHub Pages validation/deployment is started separately after publication.
