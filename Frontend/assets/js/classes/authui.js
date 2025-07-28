class AuthUI {
    // Consistent animation configuration
    static ANIMATION_CONFIG = {
        duration: 500,
        easing: 'cubic-bezier(0.4,0,0.2,1)',
        delay: 50
    };

    static setAuthOverlayStyles(display = 'flex') {
        $('.auth-overlay').css({
            display,
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh'
        });
    }

    static setFormStyles($form, show = true, opacity = 0, transform = 'translateY(-50px) scale(0.95)') {
        $form.css({
            display: show ? 'block' : 'none',
            opacity,
            transform
        });
    }

    static applyFormAnimation($form) {
        setTimeout(() => {
            $form.css({
                transition: `transform ${this.ANIMATION_CONFIG.duration}ms ${this.ANIMATION_CONFIG.easing}, opacity ${this.ANIMATION_CONFIG.duration}ms`,
                transform: 'translateY(0) scale(1)',
                opacity: 1
            });
        }, this.ANIMATION_CONFIG.delay);

        $('.auth-overlay').off('click').on('click', function (e) {
            if (e.target === this) {
                $form.css({ animation: 'shake 0.3s' });
                setTimeout(() => $form.css({ animation: '' }), 300);
            }
        });
    }

    static async hideForm($form, removeOverlay = true) {
        if (!$form.length) {
            console.error('Form not found in the DOM.');
            return Promise.resolve();
        }
        
        $form.css({ 
            transform: 'translateY(-50px) scale(0.95)', 
            opacity: 0 
        });
        
        return new Promise(resolve => {
            setTimeout(() => {
                this.setFormStyles($form, false);
                if (removeOverlay) this.restorePageStyles();
                resolve();
            }, this.ANIMATION_CONFIG.duration);
        });
    }

    static async showLoginForm() {
        $('.page-content').css({ filter: 'blur(15px)', pointerEvents: 'none', userSelect: 'none' });
        $('body').css('overflow', 'hidden');
        $('nav, footer').css('display', 'none');
        $('#scrollToTopBtn').css('display', 'none');
        this.setAuthOverlayStyles();

        const $loginForm = $('#loginForm.auth-form');
        this.setFormStyles($loginForm, true);
        this.applyFormAnimation($loginForm);

        return new Promise(resolve => setTimeout(resolve, this.ANIMATION_CONFIG.duration + 50));
    }

    static restorePageStyles() {
        $('.auth-overlay').css('display', 'none');
        $('.page-content').css({ filter: 'none', pointerEvents: 'auto', userSelect: 'auto' });
        $('nav').css('display', 'flex');
        $('footer').css('display', 'block');
        $('body').css('overflow', 'auto');
    }

    static async hideLoginForm(removeOverlay = true) {
        const $loginForm = $('#loginForm.auth-form');
        return this.hideForm($loginForm, removeOverlay);
    }

    static showRegisterForm() {
        this.setAuthOverlayStyles();
        const $registerForm = $('#registerForm.auth-form');
        if (!$registerForm.length) return console.error('Register form not found in the DOM.');
        
        this.setFormStyles($registerForm, true);
        this.applyFormAnimation($registerForm);
    }

    static async hideRegisterForm(removeOverlay = true) {
        const $registerForm = $('#registerForm.auth-form');
        return this.hideForm($registerForm, removeOverlay);
    }

    static async showForgotPasswordForm() {
        this.setAuthOverlayStyles();
        const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
        if (!$forgotPasswordForm.length) return console.error('Forgot password form not found in the DOM.');
        
        // Hide login form immediately without waiting
        const $loginForm = $('#loginForm.auth-form');
        $loginForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
        this.setFormStyles($loginForm, false);
        
        // Show forgot password form immediately
        this.setFormStyles($forgotPasswordForm, true);
        this.applyFormAnimation($forgotPasswordForm);
    }

    static async hideForgottenPasswordForm(removeOverlay = true) {
        const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
        return this.hideForm($forgotPasswordForm, removeOverlay);
    }

    static showSpinner() {
        if (!$('.loading-overlay').length) {
            $('body').append(`
            <div class="loading-overlay" style="
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(20px);
            ">
                <div class="spinner" style="
                border: 8px solid filter(blur(10px));
                border-top: 8px solid #3498db;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                animation: spin 1s linear infinite;
                "></div>
            </div>
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg);}
                100% { transform: rotate(360deg);}
            }
            </style>
            `);
        }
    }

    static hideSpinner() {
        $('.loading-overlay').remove();
    }

    static updateUserUI(userData) {
        $('.page-content h2').text(`Welcome back, ${userData.firstname} ${userData.lastname}!`);
        $('#total-balance').text(`$${userData.balance}`);
        $('#total-income').text(`$${userData.total_income}`);
        $('#total-expenses').text(`$${userData.total_expense}`);
        $('#net-savings').text(`$${userData.savings}`);
        $('#goal').text(`$${userData.goal}`);
    }

    static showPanel(panelId) {
        // Implement your panel logic here
        $(`#${panelId}`).show();
    }
}