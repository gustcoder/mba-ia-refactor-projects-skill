function requireAdmin(config) {
    return (req, res, next) => {
        const providedKey = req.header('x-admin-key');
        if (!providedKey || providedKey !== config.adminApiKey) {
            return res.status(401).send('Não autorizado');
        }
        next();
    };
}

module.exports = requireAdmin;
