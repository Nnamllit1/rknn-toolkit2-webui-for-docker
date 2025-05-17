function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    if (body.classList.contains('dark')) {
        body.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        icon.className = 'fas fa-moon';
    } else {
        body.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        icon.className = 'fas fa-sun';
    }
}
window.onload = function() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    // Use config default_theme if no localStorage theme is set
    let defaultTheme = 'light';
    if (window.config && window.config.default_theme) {
        defaultTheme = window.config.default_theme;
    }
    let theme = localStorage.getItem('theme') || defaultTheme;
    if(theme === 'dark') {
        body.classList.add('dark');
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}
