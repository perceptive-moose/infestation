/* Touch page and explicit visibility bridge to the game's adaptive HUD. */
(() => {
  "use strict";
  const canvas = document.getElementById("glcanvas");
  const app = document.getElementById("app");
  const welcome = document.getElementById("welcome");
  const start = document.getElementById("start-game");
  const help = document.getElementById("help");
  const toast = document.getElementById("toast");
  const menuButton = document.querySelector('.topbar [data-code="Escape"]');
  const controlsToggle = document.getElementById("toggle-controls");
  const tipRoot = document.getElementById("level-tip");
  const inputMode = InfestationInputMode.create({
    touchDefault: InfestationInputMode.prefersTouch({
      coarsePointer: window.matchMedia("(pointer: coarse)").matches,
      finePointer: window.matchMedia("(any-pointer: fine)").matches,
      maxTouchPoints: navigator.maxTouchPoints || 0
    }),
    onChange() {
      // Release the dock's synthetic keys before physical input takes over.
      // Prompt changes alone must not reset a fresh key/stick action, discard
      // synchronized moves, or resize the puzzle.
      if (presentedMode === "touch" && inputMode.mode() !== "touch") controls.releaseAll();
      syncInputPresentation();
      syncPresentation();
    }
  });
  let controlsVisible = inputMode.controlsVisible();
  let presentedMode = inputMode.mode();
  let toastTimer;
  let ready = false;
  let loadFailed = false;
  let engineTipVisible = false;

  function showToast(message, duration = 2600) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, duration);
  }
  function resumeAudio() {
    // Called by real gestures; synthetic key events alone do not activate audio.
    if (typeof audio_context !== "undefined" && audio_context?.state === "suspended") {
      audio_context.resume().catch(error => {
        console.warn("Audio could not resume:", error);
        showToast("Sound is paused. Tap the game to enable it.");
      });
    }
  }
  const controls = InfestationTouch.create({
    canvas,
    root: document.body,
    onInterrupt() { dock.interrupt(); },
    onAction(action) {
      resumeAudio();
      if (ready) welcome.hidden = true;
      syncTipVisibility();
      if (action.code === "KeyR") {
        showToast("Restart uses two taps within 2 seconds to confirm.", 2000);
      }
    }
  });
  const dock = InfestationDock.create({
    root: document.getElementById("controller"),
    controls,
    onPlayerChange() {
      resumeAudio();
      focusGame();
    },
    onSyncChange(enabled) {
      resumeAudio();
      if (enabled) showToast("Choose a direction for each hero to move together.", 3600);
      focusGame();
    }
  });
  const tips = InfestationTips.create({
    root: tipRoot,
    onToggle(open) {
      dock.interrupt();
      if (open) tipRoot.querySelector("[data-tip-card]").focus({ preventScroll: true });
      else focusGame();
    }
  });
  // Reading or scrolling a tip must not leave a held direction running.
  tipRoot.addEventListener("pointerdown", () => dock.interrupt());
  function syncTipVisibility() {
    tips.setSuppressed(!engineTipVisible || help.open || !welcome.hidden
      || !controlsVisible || !ready || loadFailed);
  }
  function syncPresentation() {
    const interactive = ready && !loadFailed && !help.open && welcome.hidden
      && document.visibilityState !== "hidden";
    dock.setAvailable(interactive && controlsVisible);
    menuButton.disabled = !interactive;
    syncTipVisibility();
  }
  function syncInputPresentation() {
    controlsVisible = inputMode.controlsVisible();
    const mode = inputMode.mode();
    presentedMode = mode;
    document.body.dataset.inputMode = mode;
    app.classList.toggle("controls-hidden", !controlsVisible);
    controlsToggle.setAttribute("aria-expanded", String(controlsVisible));
    controlsToggle.setAttribute("aria-label", controlsVisible ? "Hide touch controls" : "Show touch controls");
    canvas.setAttribute("aria-label", mode === "touch"
      ? "Game board. Use the direction buttons to move, Wait to pass a turn, and Undo to take back a move."
      : mode === "controller" ? "Game board. Use your controller. Matching button prompts appear in the game."
        : "Game board. Use the arrow keys or WASD to move, Space to wait, and U to undo.");
    if (ready && !loadFailed) {
      document.getElementById("start-label").textContent = "Play";
      document.getElementById("load-note").textContent = mode === "touch"
        ? "Sound starts when you tap Play."
        : "Sound starts when you choose Play.";
    }
  }
  // Capture identifies the real input before the dock emits synthetic keys.
  document.addEventListener("pointerdown", event => {
    // Toggling the dock must act on the visibility the button was displaying,
    // without an automatic device change reversing that action first.
    if (event.target.closest?.("#toggle-controls")) return;
    if (event.pointerType === "mouse" && event.target.closest?.(".topbar")) return;
    inputMode.pointer(event, Boolean(event.target.closest?.("#controller")));
  }, { capture: true, passive: true });
  document.addEventListener("keydown", event => inputMode.keyboard(event), { capture: true });
  function focusGame() { canvas.focus({ preventScroll: true }); }
  function closeHelp() { help.close(); syncPresentation(); focusGame(); }
  start.addEventListener("click", () => {
    resumeAudio();
    welcome.hidden = true;
    syncPresentation();
    focusGame();
  });
  document.getElementById("show-help").addEventListener("click", () => {
    help.showModal();
    syncPresentation();
  });
  document.getElementById("close-help").addEventListener("click", closeHelp);
  document.getElementById("help-done").addEventListener("click", closeHelp);
  help.addEventListener("cancel", () => { dock.interrupt(); });
  help.addEventListener("close", syncPresentation);
  document.addEventListener("visibilitychange", syncPresentation);
  controlsToggle.addEventListener("click", () => {
    inputMode.toggleControls();
    focusGame();
  });
  const fullscreen = document.getElementById("fullscreen");
  if (!document.documentElement.requestFullscreen) fullscreen.hidden = true;
  fullscreen.addEventListener("click", async () => {
    dock.interrupt();
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
      focusGame();
    } catch (error) {
      console.warn("Fullscreen was unavailable:", error);
      showToast("Fullscreen isn’t available in this browser.");
    }
  });
  document.addEventListener("fullscreenchange", () => {
    fullscreen.setAttribute("aria-label", document.fullscreenElement ? "Exit fullscreen" : "Enter fullscreen");
  });
  canvas.addEventListener("pointerdown", event => {
    focusGame();
    resumeAudio();
    // Mouse/pen releases outside the canvas must still finish a slider drag.
    // Touch events already remain associated with their original target.
    if (event.isPrimary && event.button === 0
      && (event.pointerType === "mouse" || event.pointerType === "pen")) {
      canvas.setPointerCapture(event.pointerId);
    }
  });
  // These gestures belong to the canvas rather than a dock button. Notify the
  // engine too, so an interrupted slider drag cannot resume with a later touch.
  for (const event of ["pointercancel", "touchcancel"]) {
    canvas.addEventListener(event, () => dock.interrupt());
  }
  new ResizeObserver(() => {
    dock.interrupt();
    window.dispatchEvent(new Event("resize"));
  }).observe(canvas.parentElement);
  function showLoadFailure(message) {
    loadFailed = true;
    engineTipVisible = false;
    tips.clear();
    syncPresentation();
    if (welcome.hidden) { showToast(message, 12000); return; }
    document.getElementById("start-label").textContent = "Game couldn’t start";
    document.getElementById("load-note").textContent = message;
    start.disabled = true;
  }
  canvas.addEventListener("webglcontextlost", () => {
    dock.interrupt();
    showLoadFailure("The graphics context was lost. Reload the page to continue.");
  });
  canvas.addEventListener("webglcontextcreationerror", event => {
    console.warn("WebGL initialization failed:", event.statusMessage);
    showLoadFailure("WebGL isn’t available in this browser. Open the game in a browser with hardware graphics enabled.");
  });
  window.addEventListener("error", event => {
    console.error("Infestation error:", event.message);
    if (!ready) showLoadFailure("The game couldn’t initialize. Try reloading in Chrome or Safari.");
  });
  // First poll happens once App has loaded sprites/audio and starts running.
  miniquad_add_plugin({
    name: "infestation_touch_page",
    version: 1,
    register_plugin(importObject) {
      importObject.env.infestation_input_mode = () => inputMode.code();
      // The game reclaims its generic instruction panel only while a usable
      // replacement is visible. Hide/show and readiness take effect next frame.
      importObject.env.infestation_touch_controls_visible = () =>
        Number(controlsVisible && ready && !loadFailed);
      importObject.env.infestation_touch_state = (roomPtr, roomLen, screen, players, actions) => {
        dock.update({ room: UTF8ToString(roomPtr, roomLen), screen, players, actions });
      };
      importObject.env.infestation_touch_layout = dpadRight => {
        dock.setDpadRight(Boolean(dpadRight));
      };
      importObject.env.infestation_touch_selected_player = () => dock.selectedPlayer();
      importObject.env.infestation_touch_input_epoch = () => dock.inputEpoch();
      importObject.env.infestation_touch_tip = (roomPtr, roomLen, textPtr, textLen, player, shown, visible) => {
        engineTipVisible = Boolean(visible);
        syncTipVisibility();
        tips.update({
          id: UTF8ToString(roomPtr, roomLen),
          text: UTF8ToString(textPtr, textLen),
          player,
          shown
        });
      };
      const count = importObject.env.sapp_gamepad_count;
      importObject.env.sapp_gamepad_count = function () {
        inputMode.gamepads(navigator.getGamepads?.() || []);
        if (!ready) {
          ready = true;
          start.disabled = false;
          syncInputPresentation();
          syncPresentation();
        }
        return count();
      };
    }
  });
  setTimeout(() => {
    if (!ready && !loadFailed) showLoadFailure("Loading is taking longer than expected. Reload if it doesn’t finish.");
  }, 45000);
  syncInputPresentation();
  syncPresentation();
  load(document.body.dataset.wasmPath);
})();
