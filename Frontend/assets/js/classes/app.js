class App {
    static registerEventListeners(authService) {
        $(document)
            .on('click', '#loginBTN', async function (e) {
                let email = $('#loginEmail').val();
                let password = $('#loginPassword').val();

                if (!email || !password) {
                    showAlert('Please fill in both email and password fields.', 5000, 'warning');
                    return;
                }

                $("#loginBTN").prop('disabled', true);
                AuthUI.showSpinner();
                let resp = await authService.login(email, password);
                $("#loginBTN").prop('disabled', false);
                AuthUI.hideSpinner();

                if (resp && resp.status === 200) {
                    authService.token = resp.response.access_token;
                    localStorage.setItem('token', authService.token);
                    clearAlerts();
                    showAlert("Login successful! Welcome back!", 5000, 'success');
                    await authService.loadData();
                    await AuthUI.hideLoginForm();
                } else {
                    let parsed = resp && resp.response ? JSON.parse(resp.response) : {};
                    showAlert("Login failed: " + (parsed.detail || "No response from server."), 5000, 'error');
                }
                e.preventDefault();
            })
            .on('click', '#showRegisterBTN', async function (e) {
                e.preventDefault();
                await AuthUI.hideLoginForm(false);
                AuthUI.showRegisterForm();
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
                    return;
                }

                $("#registerBTN").prop('disabled', true);
                AuthUI.showSpinner();
                let resp = await authService.register(firstName, lastName, email, password);
                AuthUI.hideSpinner();
                $("#registerBTN").prop('disabled', false);

                if (resp.status === 200) {
                    authService.token = resp.response.access_token;
                    localStorage.setItem('token', authService.token);
                    clearAlerts();
                    showAlert("Registration successful! Welcome aboard!", 5000, 'success');
                    await authService.loadData();
                    await AuthUI.hideRegisterForm();
                    AuthUI.showPanel("welcomePanel");
                } else {
                    let parsed = resp && resp.response ? JSON.parse(resp.response) : {};
                    showAlert("Registration failed: " + (parsed.detail || "No response from server."), 5000, 'error');
                }

                e.preventDefault();
            })
            .on('click', '#backToSignInBTN', async function (e) {
                e.preventDefault();
                await AuthUI.hideRegisterForm(false);
                clearAlerts();
                AuthUI.showLoginForm();
            })
            .on('click', '#showForgottenPasswordFormBTN', async function (e) {
                e.preventDefault();
                await AuthUI.hideLoginForm(false);
                clearAlerts();
                AuthUI.showForgotPasswordForm();
            })
            .on('click', '#backToSignInFromForgottenPasswordForm', async function (e) {
                e.preventDefault();
                await AuthUI.hideForgottenPasswordForm(false);
                clearAlerts();
                AuthUI.showLoginForm();
            })
            .on('click', '#logoutBTN', async function (e) {
                e.preventDefault();
                await authService.logout();
                AuthUI.restorePageStyles();
                clearAlerts();
                showAlert("You have been logged out successfully.", 5000, 'success');
                $('.page-content h2').text('Welcome back!');
                $('#total-balance, #total-income, #total-expenses, #net-savings, #goal').text('$0.00');
                await AuthUI.showLoginForm();
            });
    }
}
