// Create right-click context menu options on extension install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "verify-media",
    title: "Verify media with Antigravity AI",
    contexts: ["image", "video", "audio"]
  });
  console.log("Antigravity context verification triggers successfully initialized.");
});

// Listener for context menu triggers
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "verify-media") {
    const srcUrl = info.srcUrl;
    console.log(`Analyzing target media resource: ${srcUrl}`);

    // Notify user of analysis initiation
    chrome.notifications.create("verifying-notice", {
      type: "basic",
      iconUrl: "popup/icon.png",
      title: "Analyzing Media...",
      message: "Submitting target image to Antigravity Forensics Engine...",
      priority: 1
    });

    try {
      // Simulate verification API response
      // In production this executes a fetch request to: /api/v1/public/verify/image
      setTimeout(() => {
        const mockVerdict = Math.random() > 0.3 ? "REAL" : "FAKE";
        const confidence = mockVerdict === "REAL" ? 98.2 : 94.7;

        chrome.notifications.create("verdict-notice", {
          type: "basic",
          iconUrl: "popup/icon.png",
          title: `Verification Result: ${mockVerdict}`,
          message: `The media is analyzed as ${mockVerdict} with ${confidence}% confidence.`,
          priority: 2
        });
      }, 2000);

    } catch (err) {
      console.error("Verification processing failed:", err);
      chrome.notifications.create("error-notice", {
        type: "basic",
        iconUrl: "popup/icon.png",
        title: "Analysis Failure",
        message: "Failed to connect to verification API.",
        priority: 2
      });
    }
  }
});
