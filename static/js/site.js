const navButton = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
if (navButton && nav) {
  navButton.addEventListener("click", () => nav.classList.toggle("open"));
}
