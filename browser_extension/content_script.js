/**
 * Webpage Media Scanner & Overlay Injector.
 */

// Scans elements and appends visual badges
function scanPageMedia() {
  const images = document.querySelectorAll("img:not([data-antigravity-checked])");
  
  images.forEach(img => {
    // Flag to prevent redundant check loops
    img.setAttribute("data-antigravity-checked", "pending");
    
    // Simulate classification scanning (images larger than 100px)
    if (img.clientWidth > 100 && img.clientHeight > 100) {
      // Append visual hover overlays
      const overlay = document.createElement("div");
      overlay.style.position = "absolute";
      overlay.style.padding = "4px 8px";
      overlay.style.fontSize = "10px";
      overlay.style.fontWeight = "bold";
      overlay.style.borderRadius = "4px";
      overlay.style.color = "#FFFFFF";
      overlay.style.zIndex = "9999";
      overlay.style.pointerEvents = "none";
      overlay.style.transition = "opacity 0.2s";

      // Align relative positioning wrapper
      const rect = img.getBoundingClientRect();
      overlay.style.top = `${window.scrollY + rect.top + 8}px`;
      overlay.style.left = `${window.scrollX + rect.left + 8}px`;

      // Mock status assignment: 85% Real, 15% Fake
      const isFake = Math.random() < 0.15;
      if (isFake) {
        overlay.style.backgroundColor = "rgba(220, 38, 38, 0.9)"; // Red
        overlay.innerText = "⚠️ AI-GENERATED (FAKE)";
      } else {
        overlay.style.backgroundColor = "rgba(22, 163, 74, 0.9)"; // Green
        overlay.innerText = "🛡️ VERIFIED AUTHENTIC";
      }

      // Append overlay on body
      document.body.appendChild(overlay);
      
      // Bind positioning updates on window resize
      window.addEventListener("resize", () => {
        const r = img.getBoundingClientRect();
        overlay.style.top = `${window.scrollY + r.top + 8}px`;
        overlay.style.left = `${window.scrollX + r.left + 8}px`;
      });
    }
  });
}

// Initial sweep and poll loop for SPA pagination changes
scanPageMedia();
setInterval(scanPageMedia, 3000);
console.log("Antigravity Page Media Scanner activated.");
