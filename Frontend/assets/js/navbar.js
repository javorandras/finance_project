$(document).ready(function () {
    const $menuToggle = $('.menu-toggle');
    const $navMenu = $('.nav-items');
    const $navbar = $('nav');

    if ($menuToggle.length && $navMenu.length) {
        $menuToggle.on('click', function () {
            $navMenu.toggleClass('active');
        });
    }

    $(window).on('scroll', function () {
        if ($(window).scrollTop() > 10) {
            $navbar.addClass('navbar-transparent');
        } else {
            $navbar.removeClass('navbar-transparent');
        }
    });
});