document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('submit', function(e) {
        
        if (e.target.matches('#ajax-register-form')) {
            e.preventDefault(); 
            
            const form = e.target;
            const btn = form.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Processing...';
            btn.disabled = true;

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url; 
                    return null;
                }
                return response.text();
            })
            .then(html => {
                if (!html) return;
                
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                const registerUrl = window.AUTH_CONFIG.registerUrl;
                const newForm = doc.querySelector(`form[action="${registerUrl}"]`);
                if (newForm) {
                    form.innerHTML = newForm.innerHTML;
                }
            })
            .catch(err => {
                console.error('Registration error:', err);
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
        }
    });
});