const express = require('express');

function userRoutes(userController, requireAdminMiddleware) {
    const router = express.Router();
    router.delete('/users/:id', requireAdminMiddleware, userController.deleteUser);
    return router;
}

module.exports = userRoutes;
