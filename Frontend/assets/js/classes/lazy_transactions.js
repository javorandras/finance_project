class Transaction {
    constructor(id, amount, type, description, date) {
        this.loaded = false;

        this.id = id;
        this.amount = amount;
        this.type = type; // 'income' or 'expense'
        this.description = description;
        this.date = new Date(date);
    }

    load() {
        if (this.loaded) return;
        $('#transactions-body').append(`
            <tr id="transaction-${this.id}">
                <td id="transaction-date">${this.date.toLocaleDateString()}</td>
                <td id="transaction-description">${this.description}</td>
                <td id="transaction-amount">$${this.amount}</td>
                <td id="transaction-type">${this.type.charAt(0).toUpperCase() + this.type.slice(1)}</td>
            </tr>
        `);
        const amountCell = $(`#transaction-${this.id} #transaction-amount`);
        if (this.type === 'income') {
            amountCell.css('color', 'green');
        } else if (this.type === 'expense') {
            amountCell.css('color', 'red');
        }
        this.loaded = true;
    }
}

class LazyTransactions {
    constructor() {
        this.transactions = [];
    }

    async loadTransactions(skip = 0, limit = 30) {
        if (this.loaded) return;
        if (!authService.token || authService.token === 'null' || authService.token === 'undefined' || authService.token === '' || authService.token === undefined || authService.token === null) return;

        logger.log("Loading transactions...");
        try {
            const resp = await sendRequest('/transactions/transactions', 'GET', {
                "skip": skip,
                "limit": limit
            });
            if (resp.status == 200) {
                for (const item of resp.response) {
                    const transaction = new Transaction(
                        item.id,
                        item.amount,
                        item.type,
                        item.description,
                        item.date
                    );
                    transaction.load();
                    this.transactions.push(transaction);
                }
                logger.log("Transactions loaded successfully.");
            } else {
                console.log("Failed to load transactions:", resp.status, resp.response);
                showAlert("Failed to load transactions. Please try again later.", 5000, 'error');
            }
        } catch (error) {
            console.log("Failed to load transactions:", error);
            showAlert("Failed to load transactions. Please try again later.", 5000, 'error');
        }
    }

    getTransactions() {
        return this.transactions;
    }

    static reloadTransactions(transactions) {
        for (const transaction of transactions) {
            transaction.loaded = false; // Reset loaded state
            $('#transaction-' + transaction.id).remove(); // Remove from DOM
            transaction.load();
        }
        logger.log("Transactions reloaded.");
    }

    static refreshTransactions(transactions) {
        for (const transaction of transactions) transaction.load();
        logger.log("Transactions refreshed.");
    }
}