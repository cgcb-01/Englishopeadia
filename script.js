// Sidebar toggle + search only.
// Chapters are now pre-built static pages with real URLs (see build.py),
// so there is no more fetch-and-swap content logic here — that's what was
// stopping Google from indexing anything beyond the homepage.

function openSidebar() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebarOverlay').classList.add('active');
}
function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('active');
}

document.getElementById('hamburgerBtn').addEventListener('click', openSidebar);
document.getElementById('closeSidebar').addEventListener('click', closeSidebar);
document.getElementById('sidebarOverlay').addEventListener('click', closeSidebar);

document.getElementById('sidebarSearch').addEventListener('input', function (e) {
    const val = e.target.value.toLowerCase().trim();
    document.querySelectorAll('.nav-item').forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(val) ? 'flex' : 'none';
    });
});
