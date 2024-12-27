/* signature_pad/static/signature_pad/js/signature_pad.js */
document.addEventListener("DOMContentLoaded", () => {
  if (typeof SignaturePad === "undefined") {
    console.error("SignaturePad is not available");
    return;
  }
  document.querySelectorAll('[id$="-pad"]').forEach((canvas) => {
    const container = canvas.closest(".signature-pad-container");
    const input = container.querySelector('input[type="hidden"]');
    const clearButton = container.querySelector(".clear-button");

    const signaturePad = new SignaturePad(canvas);

    // Load existing signature if present
    if (input.value) {
      try {
        const pointData = JSON.parse(input.value);
        signaturePad.fromData(pointData);
      } catch (e) {
        console.error("Invalid signature data:", e);
      }
    }

    canvas.closest("form").addEventListener("submit", () => {
      if (!signaturePad.isEmpty()) {
        const data = signaturePad.toData();
        input.value = JSON.stringify(data);
      }
    });

    clearButton.addEventListener("click", () => {
      signaturePad.clear();
      input.value = "";
    });
  });
});
