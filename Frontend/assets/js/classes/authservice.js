class AuthService {
    constructor() {
        this.token = localStorage.getItem('token') || null;
        this.userData = {};
    }

    getHeaderPreset() {
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': this.token ? `Bearer ${this.token}` : '',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    async sendRequest(endpoint, method, data, headers = this.getHeaderPreset()) {
        try {
            const response = await $.ajax({
                url: `${endpoint_host}${endpoint_prefix}${endpoint}`,
                type: method,
                contentType: 'application/json',
                headers: headers,
                data: JSON.stringify(data),
                dataType: 'json',
                crossDomain: true,
                xhrFields: { withCredentials: true }
            });
            return { status: 200, response };
        } catch (jqXHR) {
            return { status: jqXHR.status, response: jqXHR.responseText };
        }
    }

    async loadData() {
        AuthUI.showSpinner();
        try {
            let resp = await this.sendRequest('/users/me', 'GET');
            if (resp.status === 200) {
                this.userData = resp.response;
                AuthUI.updateUserUI(this.userData);
            } else {
                throw new Error("Failed to load user data");
            }
        } catch (e) {
            let resp = await this.sendRequest('/users/refresh', 'POST');
            if (resp.status === 200) {
                this.token = resp.response.access_token;
                localStorage.setItem('token', this.token);
                await this.loadData();
            } else {
                showAlert("Session expired or invalid token. Please log in again.", 5000, 'warning');
                this.token = null;
                localStorage.removeItem('token');
                AuthUI.showLoginForm();
            }
        }
        AuthUI.hideSpinner();
    }

    async login(email, password) {
        return await this.sendRequest('/users/login', 'POST', { email, password });
    }

    async register(firstName, lastName, email, password) {
        return await this.sendRequest('/users/register', 'POST', {
            firstname: firstName,
            lastname: lastName,
            email,
            password
        });
    }

    async logout() {
        this.token = null;
        localStorage.removeItem('token');
        await this.sendRequest('/users/logout', 'POST');
    }
}