const sqlite3 = require('sqlite3').verbose();

function createConnection(databaseUrl) {
    const raw = new sqlite3.Database(databaseUrl);

    return {
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.run(sql, params, function callback(err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
    };
}

module.exports = { createConnection };
