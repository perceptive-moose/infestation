// Progress transfer plugin for miniquad.
(() => {
    "use strict";

    const importKey = "infestation_progress_import";
    const dialog = document.getElementById("progress-import");
    const form = document.getElementById("import-form");
    const code = document.getElementById("import-code");
    const error = document.getElementById("import-error");
    const submit = document.getElementById("import-submit");

    function clearError() {
        error.hidden = true;
        error.textContent = "";
        code.removeAttribute("aria-invalid");
    }

    function showError(message) {
        code.readOnly = false;
        submit.disabled = false;
        error.textContent = message;
        error.hidden = false;
        code.setAttribute("aria-invalid", "true");
        code.focus({ preventScroll: true });
    }

    function cancelImport() {
        localStorage.setItem(importKey, JSON.stringify({ action: "cancel" }));
        dialog.close("cancelled");
    }

    document.getElementById("import-cancel").addEventListener("click", cancelImport);
    dialog.addEventListener("cancel", event => {
        event.preventDefault();
        cancelImport();
    });
    code.addEventListener("input", clearError);
    // Miniquad captures clipboard events on window and cancels native paste.
    // Keep editing in this field native, including the iPhone Paste menu.
    for (const type of ["copy", "cut", "paste"]) {
        code.addEventListener(type, event => event.stopPropagation());
    }
    form.addEventListener("submit", event => {
        event.preventDefault();
        if (submit.disabled) return;
        if (!code.value.trim()) {
            showError("Paste an export code first.");
            return;
        }
        clearError();
        try {
            // The game validates the code before closing the dialog.
            localStorage.setItem(importKey, JSON.stringify({ action: "submit", code: code.value }));
            code.readOnly = true;
            submit.disabled = true;
        } catch (failure) {
            console.warn("Could not submit progress:", failure);
            showError("Couldn’t submit the code. Please try again.");
        }
    });

    miniquad_add_plugin({
        name: "progress",
        version: 1,
        register_plugin(importObject) {
            importObject.env.sapp_clipboard_write = function (buf, len) {
                navigator.clipboard.writeText(UTF8ToString(buf, len));
            };
            importObject.env.sapp_progress_import = function () {
                localStorage.removeItem(importKey);
                // Focus changes release canvas keys. Let the WASM frame return
                // before those handlers call back into the engine.
                queueMicrotask(() => {
                    code.value = "";
                    code.readOnly = false;
                    submit.disabled = false;
                    clearError();
                    dialog.returnValue = "";
                    dialog.showModal();
                    dialog.dispatchEvent(new Event("import-open"));
                });
            };
            importObject.env.sapp_progress_import_error = function (buf, len) {
                console.warn("Invalid progress code:", UTF8ToString(buf, len));
                queueMicrotask(() => {
                    showError("That export code isn’t valid. Paste the complete code and try again.");
                });
            };
            importObject.env.sapp_progress_import_finish = function () {
                queueMicrotask(() => dialog.close("imported"));
            };
        }
    });
})();
