let currentUser = null;

async function sendRequest(endpoint, method, data) {
    try {
        const response = await $.ajax({
            url: endpoint,
            type: method,
            data: data,
            dataType: 'json'
        });
        return response;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

class User {
    constructor(email, firstname, lastname, date_created, last_login, balance, total_income, total_expenses, savings) {
        this.email = email;
        this.date_created = date_created;
        this.last_login = last_login;
        this.firstname = firstname;
        this.lastname = lastname;
        this.balance = balance;
        this.total_income = total_income;
        this.total_expenses = total_expenses;
        this.savings = savings;
    }

    static async authenticate(email, password, remember_me) {

    }

    static async create_account(email, password, confirm_password) {

    }
}

function showLoginForm() {
    $('.page-content').css({
        filter: 'blur(15px)',
        pointerEvents: 'none',
        userSelect: 'none'
    });
    $('body').css('overflow', 'hidden');
    $('nav').css({
        display: 'none'
    });
    $('#scrollToTopBtn').remove();
    $("footer").css({
        display: 'none'
    });
    $('.auth-overlay').css({
        display: 'flex',
    });

    if ($('.auth-overlay').length > 0) {

        $('.auth-overlay').css({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh'
        });

        $('#loginForm.auth-form').css({
            position: 'relative',
            top: '0',
            left: '0',
            transform: 'translateY(-100vh)',
            opacity: 0,
            display: 'block'
        });

        setTimeout(() => {
            $('#loginForm.auth-form').css({
                transition: 'transform 0.5s cubic-bezier(0.4,0,0.2,1), opacity 0.5s',
                transform: 'translateY(75%)',
                opacity: 1
            });
        }, 50);

        $('.auth-overlay').on('click', function (e) {
            if (e.target === this) {
                $('#loginForm.auth-form').css({ animation: 'shake 0.3s' });
                setTimeout(() => $('#loginForm.auth-form').css({ animation: '' }), 300);
            }
        });

    }
}

async function hideLoginForm(removeOverlay = true) {
    return new Promise(function (resolve) {
        $('#loginForm.auth-form').css({
            transform: 'translateY(-100vh)',
            opacity: 0
        });

        setTimeout(() => {
            $('#loginForm.auth-form').css({
                display: 'none'
            });
            if (removeOverlay) {
                $('.auth-overlay').css({
                    display: 'none'
                });
                $('.page-content').css({
                    filter: 'none',
                    pointerEvents: 'auto',
                    userSelect: 'auto'
                });
                $('nav').css({
                    display: 'flex'
                });
                $('#scrollToTopBtn').css({
                    display: 'block'
                });
                $("footer").css({
                    display: 'block'
                });
                $('body').css('overflow', 'auto');
            }
            $('#loginForm.auth-form').css({
                display: 'none',
            });
            resolve();
        }, 500);
    });
}

function showRegisterForm() {
    $('.auth-overlay').css({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh'
    });

    const $registerForm = $('#registerForm.auth-form');
    if ($registerForm.length === 0) {
        console.error('Register form not found in the DOM.');
        return;
    }

    $registerForm.css({
        display: 'block',
        transition: 'none',
        transform: 'translateY(-100vh)',
        opacity: 0
    });

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
    return new Promise(function (resolve) {
        const $registerForm = $('#registerForm.auth-form');
        if ($registerForm.length === 0) {
            console.error('Register form not found in the DOM.');
            resolve();
            return;
        }

        $registerForm.css({
            transform: 'translateY(-100vh)',
            opacity: 0
        });

        setTimeout(() => {
            $registerForm.css({
                display: 'none'
            });
            if (removeOverlay) {
                $('.auth-overlay').css({
                    display: 'none'
                });
                $('.page-content').css({
                    filter: 'none',
                    pointerEvents: 'auto',
                    userSelect: 'auto'
                });
                $('nav').css({
                    display: 'flex'
                });
                $('#scrollToTopBtn').css({
                    display: 'block'
                });
                $("footer").css({
                    display: 'block'
                });
                $('body').css('overflow', 'auto');
            }
            resolve();
        }, 500);
    });
}

function registerEventListeners() {
    $(document).on('click', '#loginBTN', async function (e) {
        hideLoginForm();
        e.preventDefault();
    });

    $(document).on('click', '#showRegisterBTN', async function (e) {
        e.preventDefault();
        await hideLoginForm(false);
        showRegisterForm();
    });

    $(document).on('click', '#backToSignInBTN', async function (e) {
        e.preventDefault();
        await hideRegisterForm(false);
        showLoginForm();
    });
}

$(document).ready(function () {
    $("html").css("scroll-behavior", "smooth");

    const $scrollBtn = $('#scrollToTopBtn');
    let isScrolling = false;

    $(window).on('scroll', function () {
        if ($(window).scrollTop() > 100) {
            $scrollBtn.fadeIn();
        } else {
            $scrollBtn.fadeOut();
        }
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

    if (currentUser === null) {
        showLoginForm();
    }

    registerEventListeners();
});