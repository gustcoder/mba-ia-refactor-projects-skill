const express = require('express');

function adminRoutes(adminController, requireAdminMiddleware) {
    const router = express.Router();
    router.get('/admin/financial-report', requireAdminMiddleware, adminController.financialReport);
    return router;
}

module.exports = adminRoutes;
