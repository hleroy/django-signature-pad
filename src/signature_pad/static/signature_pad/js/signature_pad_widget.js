/* signature_pad/static/signature_pad/js/signature_pad_widget.js */
document.addEventListener("DOMContentLoaded", () => {
  if (typeof SignaturePad === "undefined") {
    console.error("SignaturePad is not available");
    return;
  }

  // redraw() was added in signature_pad 5.1.0
  if (typeof SignaturePad.prototype.redraw !== "function") {
    console.error("django-signature-pad requires signature_pad 5.1.0 or later");
    return;
  }

  // Define allowed options with their correct casing
  const allowedOptions = {
    signaturePadDotsize: "dotSize",
    signaturePadMinwidth: "minWidth",
    signaturePadMaxwidth: "maxWidth",
    signaturePadBackgroundcolor: "backgroundColor",
    signaturePadPencolor: "penColor",
  };

  document.querySelectorAll('.signature-pad-wrapper canvas[id$="-pad"]').forEach((canvas) => {
    const container = canvas.closest(".signature-pad-container");
    const wrapper = canvas.closest(".signature-pad-wrapper");
    const input = container.querySelector('input[type="hidden"]');
    const clearButton = container.querySelector(".signature-pad-clear-button");

    // Get signature pad options from data attributes
    const options = {};

    // Check only for our allowed options
    Object.keys(allowedOptions).forEach((datasetKey) => {
      if (datasetKey in canvas.dataset) {
        const optionName = allowedOptions[datasetKey];
        let value = canvas.dataset[datasetKey];

        // Parse values appropriately
        if (!isNaN(value) && value.trim() !== "") {
          value = parseFloat(value);
        } else if (value === "true") {
          value = true;
        } else if (value === "false") {
          value = false;
        }

        options[optionName] = value;
      }
    });

    const signaturePad = new SignaturePad(canvas, options);

    // Resizing a canvas wipes it, so size it to its wrapper (scaled for
    // high-DPI screens) and let signature_pad repaint the strokes it holds.
    function resizeCanvas() {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = wrapper.clientWidth * dpr;
      canvas.height = wrapper.clientHeight * dpr;
      canvas.getContext("2d").scale(dpr, dpr);
      signaturePad.redraw();
    }

    // Initial resize and setup
    resizeCanvas();

    // Add resize event listener with debounce
    let resizeTimer;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resizeCanvas, 250);
    });

    // Handle orientation change on mobile
    window.addEventListener("orientationchange", () => {
      setTimeout(resizeCanvas, 500);
    });

    // Handle form submission. An empty pad leaves the input untouched, so a
    // signature saved earlier survives edits to other fields; the clear
    // button is the only way to remove it.
    canvas.closest("form").addEventListener("submit", () => {
      if (!signaturePad.isEmpty()) {
        input.value = signaturePad.toDataURL("image/png");
      }
    });

    // Handle clear button
    clearButton.addEventListener("click", () => {
      signaturePad.clear();
      input.value = "";
    });

    // Prevent scrolling on mobile when signing
    canvas.addEventListener(
      "touchstart",
      (e) => {
        if (e.cancelable) {
          e.preventDefault();
        }
      },
      { passive: false }
    );
  });
});
