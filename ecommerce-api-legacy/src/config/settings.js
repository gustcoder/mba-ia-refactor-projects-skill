require('dotenv').config({ quiet: true });

function required(name, devFallback) {
    const value = process.env[name];
    if (value) return value;
    if (process.env.NODE_ENV === 'production') {
        throw new Error(`Variável de ambiente obrigatória ausente: ${name}`);
    }
    return devFallback;
}

const config = {
    port: Number(process.env.PORT) || 3000,
    dbUser: process.env.DB_USER || '',
    dbPass: process.env.DB_PASS || '',
    smtpUser: process.env.SMTP_USER || '',
    paymentGatewayKey: required('PAYMENT_GATEWAY_KEY', 'pk_test_dev_placeholder'),
    adminApiKey: required('ADMIN_API_KEY', 'dev-admin-key'),
    databaseUrl: process.env.DATABASE_URL || ':memory:',
};

module.exports = config;
