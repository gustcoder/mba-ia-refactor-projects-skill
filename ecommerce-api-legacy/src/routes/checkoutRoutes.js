const express = require('express');

function checkoutRoutes(checkoutController) {
    const router = express.Router();
    router.post('/checkout', checkoutController.checkout);
    return router;
}

module.exports = checkoutRoutes;
