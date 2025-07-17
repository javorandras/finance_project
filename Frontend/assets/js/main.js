let debug = true;
let logger = new Logger();
const authService = new AuthService();
let lazyTransactions = new LazyTransactions();

function getHeaderPreset() {
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': authService.token ? `Bearer ${authService.token}` : '',
        'X-Requested-With': 'XMLHttpRequest'
    };
}

async function sendRequest(endpoint, method, data, headers = getHeaderPreset()) {
    logger.log(`Sending request to ${endpoint} with method ${method} including these headers: ${JSON.stringify(headers)} with data: ${JSON.stringify(data)}`);
    try {
        const response = await $.ajax({
            url: `${endpoint_host}${endpoint_prefix}${endpoint}`,
            type: method,
            contentType: 'application/json',
            headers: headers,
            data: method == 'GET' ? data : JSON.stringify(data),
            dataType: 'json',
            crossDomain: true,
            xhrFields: { withCredentials: true }
        });
        return { status: 200, response: response };
    } catch (jqXHR) {
        return { status: jqXHR.status, response: jqXHR.responseText };
    }
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

    App.registerEventListeners(authService);

    $(document).ready(async function () {
        if (authService.token) {
            logger.log(`Token found in localStorage (${authService.token}), loading user data...`);
            await authService.loadData();
        } else {
            logger.log("No token found in localStorage, showing login form.");
            await AuthUI.showLoginForm();
            showAlert("Welcome to the Personal Finance App! Please log in or register to continue.", 5000, 'info');
        }

        // Ensure the body is scrollable
        $('body').css({ 'overflow': 'auto' });

        let lazyLoading = false;
        $(window).on('scroll', async function () {
            const scrollTop = $(window).scrollTop();
            const windowHeight = $(window).height();
            const documentHeight = $(document).height();

            // Trigger when user is within 200px of the bottom, and not already loading
            if (!lazyLoading && scrollTop + windowHeight >= documentHeight - 200) {
            lazyLoading = true;
            try {
                await lazyTransactions.loadTransactions(lazyTransactions.transactions.length > 0 ? lazyTransactions.transactions.length - 1 : 0, 30);
                logger.log("Lazy transactions loaded successfully.");
                LazyTransactions.refreshTransactions(lazyTransactions.transactions);
            } catch (error) {
                console.log("Error loading lazy transactions:", error);
                showAlert("Failed to load more transactions. Please try again later.", 5000, 'error');
            } finally {
                lazyLoading = false;
            }
            }
        });
    });
});
