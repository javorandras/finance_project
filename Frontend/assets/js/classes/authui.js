class AuthUI {
    static setAuthOverlayStyles(display = 'flex') {
        $('.auth-overlay').css({
            display,
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh'
        });
    }

    static setFormStyles($form, show = true, y = '-100vh', opacity = 0, transition = 'none') {
        $form.css({
            display: show ? 'block' : 'none',
            transition,
            transform: `translateY(${y})`,
            opacity
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

        setTimeout(() => {
            $loginForm.css({
                transition: 'transform 0.5s cubic-bezier(0.4,0,0.2,1), opacity 0.5s',
                transform: 'translateY(75%)',
                opacity: 1
            });
        }, 50);

        $('.auth-overlay').off('click').on('click', function (e) {
            if (e.target === this) {
                $loginForm.css({ animation: 'shake 0.3s' });
                setTimeout(() => $loginForm.css({ animation: '' }), 300);
            }
        });

        return new Promise(resolve => setTimeout(resolve, 550));
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
        $loginForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
        return new Promise(resolve => {
            setTimeout(() => {
                this.setFormStyles($loginForm, false);
                if (removeOverlay) this.restorePageStyles();
                resolve();
            }, 500);
        });
    }

    static showRegisterForm() {
        this.setAuthOverlayStyles();
        const $registerForm = $('#registerForm.auth-form');
        if (!$registerForm.length) return console.error('Register form not found in the DOM.');
        this.setFormStyles($registerForm, true);

        setTimeout(() => {
            $registerForm.css({
                transition: 'transform 0.5s cubic-bezier(0.4,0,0.2,1), opacity 0.5s',
                transform: 'translateY(60%)',
                opacity: 1
            });
        }, 50);

        $('.auth-overlay').off('click').on('click', function (e) {
            if (e.target === this) {
                $registerForm.css({ animation: 'shake 0.3s' });
                setTimeout(() => $registerForm.css({ animation: '' }), 300);
            }
        });
    }

    static async hideRegisterForm(removeOverlay = true) {
        const $registerForm = $('#registerForm.auth-form');
        if (!$registerForm.length) {
            console.error('Register form not found in the DOM.');
            return Promise.resolve();
        }
        $registerForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
        return new Promise(resolve => {
            setTimeout(() => {
                this.setFormStyles($registerForm, false);
                if (removeOverlay) this.restorePageStyles();
                resolve();
            }, 500);
        });
    }

    static async showForgotPasswordForm() {
        await this.hideLoginForm(false);
        this.setAuthOverlayStyles();
        const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
        if (!$forgotPasswordForm.length) return console.error('Forgot password form not found in the DOM.');
        this.setFormStyles($forgotPasswordForm, true);

        setTimeout(() => {
            $forgotPasswordForm.css({
                transition: 'transform 0.5s cubic-bezier(0.4,0,0.2,1), opacity 0.5s',
                transform: 'translateY(70%)',
                opacity: 1
            });
        }, 50);

        $('.auth-overlay').off('click').on('click', function (e) {
            if (e.target === this) {
                $forgotPasswordForm.css({ animation: 'shake 0.3s' });
                setTimeout(() => $forgotPasswordForm.css({ animation: '' }), 300);
            }
        });
    }

    static async hideForgottenPasswordForm(removeOverlay = true) {
        const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
        if (!$forgotPasswordForm.length) {
            console.error('Forgot password form not found in the DOM.');
            return Promise.resolve();
        }
        $forgotPasswordForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
        return new Promise(resolve => {
            setTimeout(() => {
                this.setFormStyles($forgotPasswordForm, false);
                if (removeOverlay) this.restorePageStyles();
                resolve();
            }, 500);
        });
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