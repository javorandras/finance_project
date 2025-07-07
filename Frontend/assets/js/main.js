let token = null;
let userData = {};

function getHeaderPreset() {
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
    };
}

async function sendRequest(endpoint, method, data, headers = getHeaderPreset()) {
    try {
        const response = await $.ajax({
            url: `${endpoint_host}${endpoint_prefix}${endpoint}`,
            type: method,
            contentType: 'application/json',
            headers: headers,
            data: JSON.stringify(data),
            dataType: 'json',
            withCredentials: true
        });
        return { status: 200, response: response };
    } catch (jqXHR) {
        return { status: jqXHR.status, response: jqXHR.responseText };
    }
}

function setAuthOverlayStyles(display = 'flex') {
    $('.auth-overlay').css({
        display,
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh'
    });
}

function setFormStyles($form, show = true, y = '-100vh', opacity = 0, transition = 'none') {
    $form.css({
        display: show ? 'block' : 'none',
        transition,
        transform: `translateY(${y})`,
        opacity
    });
}

async function showLoginForm() {
    $('.page-content').css({ filter: 'blur(15px)', pointerEvents: 'none', userSelect: 'none' });
    $('body').css('overflow', 'hidden');
    $('nav, footer').css('display', 'none');
    $('#scrollToTopBtn').css('display', 'none');
    setAuthOverlayStyles();

    const $loginForm = $('#loginForm.auth-form');
    setFormStyles($loginForm, true);

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

    // Wait for the animation to finish before resolving
    return new Promise(resolve => setTimeout(resolve, 550));
}

function restorePageStyles() {
    $('.auth-overlay').css('display', 'none');
    $('.page-content').css({ filter: 'none', pointerEvents: 'auto', userSelect: 'auto' });
    $('nav').css('display', 'flex');
    $('footer').css('display', 'block');
    // $('#scrollToTopBtn').css('display', 'block');
    $('body').css('overflow', 'auto');
}

async function hideLoginForm(removeOverlay = true) {
    const $loginForm = $('#loginForm.auth-form');
    $loginForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
    return new Promise(resolve => {
        setTimeout(() => {
            setFormStyles($loginForm, false);
            if (removeOverlay) restorePageStyles();
            resolve();
        }, 500);
    });
}

function showRegisterForm() {
    setAuthOverlayStyles();
    const $registerForm = $('#registerForm.auth-form');
    if (!$registerForm.length) return console.error('Register form not found in the DOM.');
    setFormStyles($registerForm, true);

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

function hideRegisterForm(removeOverlay = true) {
    const $registerForm = $('#registerForm.auth-form');
    if (!$registerForm.length) {
        console.error('Register form not found in the DOM.');
        return Promise.resolve();
    }
    $registerForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
    return new Promise(resolve => {
        setTimeout(() => {
            setFormStyles($registerForm, false);
            if (removeOverlay) restorePageStyles();
            resolve();
        }, 500);
    });
}

async function showForgotPasswordForm() {
    await hideLoginForm(false);
    setAuthOverlayStyles();
    const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
    if (!$forgotPasswordForm.length) return console.error('Forgot password form not found in the DOM.');
    setFormStyles($forgotPasswordForm, true);

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

function hideForgottenPasswordForm(removeOverlay = true) {
    const $forgotPasswordForm = $('#forgottenPasswordForm.auth-form');
    if (!$forgotPasswordForm.length) {
        console.error('Forgot password form not found in the DOM.');
        return Promise.resolve();
    }
    $forgotPasswordForm.css({ transform: 'translateY(-100vh)', opacity: 0 });
    return new Promise(resolve => {
        setTimeout(() => {
            setFormStyles($forgotPasswordForm, false);
            if (removeOverlay) restorePageStyles();
            resolve();
        }, 500);
    });
}

function registerEventListeners() {
    $(document)
        .on('click', '#loginBTN', async function (e) {
            let email = $('#loginEmail').val();
            let password = $('#loginPassword').val();

            if (!email || !password) {
                showAlert('Please fill in both email and password fields.', 5000, 'warning');
                return;
            }

            $("#loginBTN").prop('disabled', true);
            showSpinner();
            let resp = await sendRequest('/users/login', 'POST', {
                email: email,
                password: password
            });
            $("#loginBTN").prop('disabled', false);
            hideSpinner();
            console.log("Login response:", resp);
            if (resp != null && resp.status === 200) {
                token = resp.response.access_token;
                console.log("Login successful, token:", token);
                clearAlerts();
                showAlert("Login successful! Welcome back!", 5000, 'success');
                localStorage.setItem('token', token);
                await loadData();
                await hideLoginForm();
            } else {
                if (!resp || !resp.response) {
                    showAlert("Login failed: No response from server.", 5000, 'error');
                    return;
                }
                let parsed = JSON.parse(resp.response);
                showAlert("Login failed: " + parsed.detail, 5000, 'error');
            }
            e.preventDefault();
        })
        .on('click', '#showRegisterBTN', async function (e) {
            e.preventDefault();
            await hideLoginForm(false);
            showRegisterForm();
        })
        .on('click', '#registerBTN', async function (e) {
            let firstName = $('#registerFirstName').val();
            let lastName = $('#registerLastName').val();
            let email = $('#registerEmail').val();
            let password = $('#registerPassword').val();
            let confirmPassword = $('#registerPasswordConf').val();

            if (!firstName || !lastName || !email || !password || !confirmPassword) {
                showAlert('Please fill in all fields.', 5000, 'warning');
                return;
            }

            if (password !== confirmPassword) {
                showAlert('Passwords do not match.', 5000, 'warning');
            }

            $("#registerBTN").prop('disabled', true);
            showSpinner();
            let resp = await sendRequest('/users/register', 'POST', {
                firstname: firstName,
                lastname: lastName,
                email: email,
                password: password,
            });
            hideSpinner();
            $("#registerBTN").prop('disabled', false);

            console.log("Registration response:", resp);
            if (resp.status === 200) {
                token = resp.response.access_token;
                console.log("Registration successful, token:", token);
                localStorage.setItem('token', token);
                clearAlerts();
                showAlert("Registration successful! Welcome aboard!", 5000, 'success');
                await loadData();
                await hideRegisterForm();
                showPanel("welcomePanel");
            } else {
                if (!resp || !resp.response) {
                    showAlert("Login failed: No response from server.", 5000, 'error');
                    return;
                }
                let parsed = JSON.parse(resp.response);
                showAlert("Registration failed: " + parsed.detail, 5000, 'error');
            }

            e.preventDefault();
        })
        .on('click', '#backToSignInBTN', async function (e) {
            e.preventDefault();
            await hideRegisterForm(false);
            clearAlerts();
            showLoginForm();
        })
        .on('click', '#showForgottenPasswordFormBTN', async function (e) {
            e.preventDefault();
            await hideLoginForm(false);
            clearAlerts();
            showForgotPasswordForm();
        })
        .on('click', '#backToSignInFromForgottenPasswordForm', async function (e) {
            e.preventDefault();
            await hideForgottenPasswordForm(false);
            clearAlerts();
            showLoginForm();
        })
        .on('click', '#logoutBTN', async function (e) {
            e.preventDefault();
            token = null;
            localStorage.removeItem('token');
            restorePageStyles();
            clearAlerts();
            showAlert("You have been logged out successfully.", 5000, 'success');
            $('.page-content h2').text('Welcome back!');
            $('#total-balance, #total-income, #total-expenses, #net-savings, #goal').text('$0.00');
            await showLoginForm();
        });
}

function showSpinner() {
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

function hideSpinner() {
    $('.loading-overlay').remove();
}

async function loadData() {
    showSpinner();
    try {
        let resp = await sendRequest('/users/me', 'GET', undefined, getHeaderPreset());
        if (resp.status === 200) {
            userData = resp.response;
            $('.page-content h2').text(`Welcome back, ${userData.firstname} ${userData.lastname}!`);
            $('#total-balance').text(`$${userData.balance}`);
            $('#total-income').text(`$${userData.total_income}`);
            $('#total-expenses').text(`$${userData.total_expense}`);
            $('#net-savings').text(`$${userData.savings}`);
            $('#goal').text(`$${userData.goal}`);
        } else {
            throw new Error("Failed to load user data");
        }
    } catch (e) {
        let resp = await sendRequest('/users/refresh', 'POST', undefined, getHeaderPreset());
        if (resp.status === 200) {
            token = resp.response.access_token;
            console.log("Token refreshed successfully:", token);
            localStorage.setItem('token', token);
            await loadData();
        } else {
            showAlert("Session expired or invalid token. Please log in again.", 5000, 'warning');
            token = null;
            localStorage.removeItem('token');
            showLoginForm();
        }
    }
    hideSpinner();
}

$(async function () {

    $("html").css("scroll-behavior", "smooth");
    const $scrollBtn = $('#scrollToTopBtn');
    let isScrolling = false;

    $(window).on('scroll', function () {
        $(window).scrollTop() > 100 ? $scrollBtn.fadeIn() : $scrollBtn.fadeOut();
    });

    $scrollBtn.on('click', function () {
        if (isScrolling) return;
        isScrolling = true;
        $scrollBtn.prop('disabled', true);
        $('html, body').animate({ scrollTop: 0 }, 400, function () {
            isScrolling = false;
            $scrollBtn.prop('disabled', false);
        });
    });

    token = localStorage.getItem('token') || null;
    console.log("Token from localStorage:", token);
    registerEventListeners();

    $(document).ready(async function () {
        if (token) {
            await loadData();
        } else {
            await showLoginForm();
            showAlert("Welcome to the Personal Finance App! Please log in or register to continue.", 5000, 'info');
        }
    });


});
