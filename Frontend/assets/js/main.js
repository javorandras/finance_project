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

async function authenticate(email, password, remember_me) {

}

async function create_account(email, password, confirm_password) {
    // try {
    //     const response = await sendRequest('/api/create_account', 'POST', {
    //         email: email,
    //         password: password,
    //         confirm_password: confirm_password
    //     });
    //     return response;
    // } catch (error) {
    //     console.error('Error creating account:', error);
    //     throw error;
    // }

}