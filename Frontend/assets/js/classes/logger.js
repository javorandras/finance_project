class Logger {
    constructor() {
        this.logs = [];
    }

    log(message) {
        if(debug) {
            const timestamp = new Date().toISOString();
            this.logs.push({ timestamp, message });
            console.log(`[${timestamp}] ${message}`);
        }
    }

    getLogs() {
        return this.logs;
    }

    getLogsAsString() {
        return this.logs.map(log => `[${log.timestamp}] ${log.message}`).join('\n');
    }

    clearLogs() {
        this.logs = [];
    }
}