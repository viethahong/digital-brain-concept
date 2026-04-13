// Digital Brain - Theme Management Logic
document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');
    
    // 1. Check for saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.add('light-mode');
        if (themeToggle) themeToggle.innerHTML = '🌙'; // Icon to switch to dark
    } else {
        if (themeToggle) themeToggle.innerHTML = '☀️'; // Icon to switch to light
    }

    // 2. Toggle Login
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const isLight = body.classList.toggle('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            
            // Update Icon
            themeToggle.innerHTML = isLight ? '🌙' : '☀️';
            
            // Feedback effect
            themeToggle.style.transform = 'scale(1.2) rotate(45deg)';
            setTimeout(() => {
                themeToggle.style.transform = '';
            }, 200);
        });
    }
});
