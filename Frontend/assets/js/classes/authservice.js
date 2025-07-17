class AuthService {
    constructor() {
        this.token = localStorage.getItem('token') || null;
        this.userData = {};
        this.logger = new Logger();
    }

    async loadData() {
        AuthUI.showSpinner();
        this.logger.log("Loading user data...");
        try {
            let resp = await sendRequest('/users/me', 'GET');
            if (resp.status === 200) {
                this.userData = resp.response;
                AuthUI.updateUserUI(this.userData);
            } else {
                throw new Error("Failed to load user data");
            }
        } catch (e) {
            let resp = await sendRequest('/users/refresh', 'POST');
            if (resp.status === 200) {
                this.logger.log(`Session refreshed successfully. New token ${resp.response.access_token}` );
                this.token = resp.response.access_token;
                localStorage.setItem('token', this.token);
                await this.loadData();
            } else {
                this.logger.log("Session expired or invalid token. Please log in again.");
                showAlert("Session expired or invalid token. Please log in again.", 5000, 'warning');
                this.token = null;
                localStorage.removeItem('token');
                AuthUI.showLoginForm();
            }
        }
        document.dispatchEvent(new CustomEvent('auth:userDataLoaded', { detail: this.userData }));
        AuthUI.hideSpinner();
    }

    async login(email, password) {
        return await sendRequest('/users/login', 'POST', { email, password });
    }

    async register(firstName, lastName, email, password) {
        return await sendRequest('/users/register', 'POST', {
            firstname: firstName,
            lastname: lastName,
            email,
            password
        });
    }

    async logout() {
        this.token = null;
        localStorage.removeItem('token');
        await sendRequest('/users/logout', 'POST');
    }
}