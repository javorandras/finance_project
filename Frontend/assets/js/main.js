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

    const authService = new AuthService();
    App.registerEventListeners(authService);

    $(document).ready(async function () {
        if (authService.token) {
            await authService.loadData();
        } else {
            await AuthUI.showLoginForm();
            showAlert("Welcome to the Personal Finance App! Please log in or register to continue.", 5000, 'info');
        }
    });
});
