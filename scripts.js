// ...existing code...

function applyDarkTheme() {
  document.body.classList.add("dark-theme");
  document.body.classList.remove("light-theme");
}

// Call the function on load
applyDarkTheme();

// Remove any event listeners for system color scheme changes
// window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyDarkTheme);

// ...existing code...
