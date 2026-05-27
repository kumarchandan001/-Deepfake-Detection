// Popup interaction handler
document.addEventListener("DOMContentLoaded", () => {
  const saveBtn = document.getElementById("save-btn");
  const apiKeyInput = document.getElementById("api-key");
  
  // Restore saved API Key settings from Chrome extension storage
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(["x_api_key"], (result) => {
      if (result.x_api_key) {
        apiKeyInput.value = result.x_api_key;
      }
    });
  }

  // Handle click events
  saveBtn.addEventListener("click", () => {
    const key = apiKeyInput.value.trim();
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ x_api_key: key }, () => {
        alert("API Verification Key updated successfully.");
      });
    } else {
      // Mock alert in development contexts
      console.log(`[Extension MOCK] Preserved X-API-Key value: ${key}`);
      alert("Key saved (development environment mock mode).");
    }
  });
});
