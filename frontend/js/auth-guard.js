// Auth Guard - Redirects unauthenticated users to welcome page
(function() {
    if (window.location.pathname === '/welcome.html' || window.location.pathname === '/login-choice.html' || 
        window.location.pathname === '/registration.html' || window.location.pathname === '/owner-login.html' ||
        window.location.pathname === '/tuner-login.html' || window.location.pathname === '/verify-email.html' ||
        window.location.pathname === '/forgot-password.html' || window.location.pathname === '/recover-password.html' ||
        window.location.pathname === '/profile.html') {
        return;
    }
    
    setTimeout(function() {
        fetch('/api/check-auth', { credentials: 'include', signal: AbortSignal.timeout(5000) })
            .then(r => r.json())
            .then(data => {
                if (!data.authenticated) {
                    window.location.href = 'welcome.html';
                }
            })
            .catch(() => {
                // On network error, allow page to load (backend may not be running)
                // The page has its own fallback data for this case
            });
    }, 0);
})();