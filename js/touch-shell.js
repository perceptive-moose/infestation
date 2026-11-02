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
  const tipRoot = document.getElementById("level-tip");
  let controlsVisible = true;
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
      if (navigator.getGamepads?.()[0]?.connected) {
        showToast("For touch control of both heroes, disconnect your controller.", 4500);
      }
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
  document.getElementById("toggle-controls").addEventListener("click", event => {
    controlsVisible = !controlsVisible;
    app.classList.toggle("controls-hidden", !controlsVisible);
    event.currentTarget.setAttribute("aria-expanded", String(controlsVisible));
    event.currentTarget.setAttribute("aria-label", controlsVisible ? "Hide touch controls" : "Show touch controls");
    syncPresentation();
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
  canvas.addEventListener("pointerdown", () => { focusGame(); resumeAudio(); });
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
    showLoadFailure("WebGL isn’t available in this browser. Open the demo in a browser with hardware graphics enabled.");
  });
  window.addEventListener("error", event => {
    console.error("Touch demo error:", event.message);
    if (!ready) showLoadFailure("The game couldn’t initialize. Try reloading in Chrome or Safari.");
  });
  // First poll happens once App has loaded sprites/audio and starts running.
  miniquad_add_plugin({
    name: "infestation_touch_page",
    version: 1,
    register_plugin(importObject) {
      // The game reclaims its generic instruction panel only while a usable
      // replacement is visible. Hide/show and readiness take effect next frame.
      importObject.env.infestation_touch_controls_visible = () =>
        Number(controlsVisible && ready && !loadFailed);
      importObject.env.infestation_touch_state = (roomPtr, roomLen, screen, players, actions) => {
        dock.update({ room: UTF8ToString(roomPtr, roomLen), screen, players, actions });
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
        if (!ready) {
          ready = true;
          start.disabled = false;
          document.getElementById("start-label").textContent = "Tap to play";
          document.getElementById("load-note").textContent = "Sound starts with your tap. Then choose Play to begin.";
          syncPresentation();
        }
        return count();
      };
    }
  });
  setTimeout(() => {
    if (!ready && !loadFailed) showLoadFailure("Loading is taking longer than expected. Reload if it doesn’t finish.");
  }, 45000);
  syncPresentation();
  load(document.body.dataset.wasmPath);
})();
