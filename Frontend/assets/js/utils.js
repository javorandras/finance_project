function parseBool(val) {
    return val === 1 || val === '1' || val === true;
}

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

async function loadAuthOverlay() {
    await fetch('auth-overlay.html')
        .then(res => res.text())
        .then(html => {
            $('body').append(html);
        });
}

async function loadTransactionElement() {
    await fetch('transactions.html')
        .then(res => res.text())
        .then(html => {
            $('.transactions').append(html);
        });
}

async function loadElements() {
    if (!authService.token || authService.token === 'null' || authService.token === 'undefined' || authService.token === '' || authService.token === undefined || authService.token === null) {
        logger.log("No valid token found, loading auth overlay.");
        await loadAuthOverlay();
    } else {
        logger.log(`Token found: No need for auth overlay.`);
    }

    await fetch('navbar.html')
        .then(res => res.text())
        .then(html => {
            $('body').append(html);
        });

    await loadTransactionElement();

    await fetch('panel-overlay.html')
        .then(res => res.text())
        .then(html => {
            $('body').append(html);
        });
}

async function loadUserRelatedElements() {
    if (authService.isAdmin()) {
        $('.nav-items li:last').before('<li><a href="#">Admin</a></li>');
    }
}