/* signature_pad/static/signature_pad/js/signature_pad_widget.js */
document.addEventListener("DOMContentLoaded", () => {
  if (typeof SignaturePad === "undefined") {
    console.error("SignaturePad is not available");
    return;
  }

  const signaturePads = {};

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

    // Function to resize the canvas
    function resizeCanvas() {
      // Save current signature as data
      let signatureData = null;
      if (signaturePads[canvas.id] && !signaturePads[canvas.id].isEmpty()) {
        signatureData = signaturePads[canvas.id].toData();
      }

      // Get the display size of the canvas from its parent wrapper
      const containerWidth = wrapper.clientWidth;
      const containerHeight = wrapper.clientHeight;

      // For high-DPI displays, adjust the canvas size
      const dpr = window.devicePixelRatio || 1;

      // Set canvas internal dimensions scaled for DPI
      canvas.width = containerWidth * dpr;
      canvas.height = containerHeight * dpr;

      // Scale the context for retina displays
      const ctx = canvas.getContext("2d");
      ctx.scale(dpr, dpr);

      // If we have an existing signature pad instance, clear it
      if (signaturePads[canvas.id]) {
        signaturePads[canvas.id].clear();
      } else {
        // Initialize a new signature pad with options
        signaturePads[canvas.id] = new SignaturePad(canvas, options);
      }

      // Restore the saved signature data if there was any
      if (signatureData && signatureData.length > 0) {
        signaturePads[canvas.id].fromData(signatureData);
      }
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

    // Handle form submission
    canvas.closest("form").addEventListener("submit", () => {
      if (!signaturePads[canvas.id].isEmpty()) {
        const dataURL = signaturePads[canvas.id].toDataURL("image/png");
        input.value = dataURL;
      } else {
        input.value = "";
      }
    });

    // Handle clear button
    clearButton.addEventListener("click", () => {
      signaturePads[canvas.id].clear();
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
