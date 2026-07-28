const { CheckoutError } = require('../services/checkoutService');

function createCheckoutController(checkoutService) {
    return {
        async checkout(req, res) {
            try {
                const { usr, eml, pwd, c_id, card } = req.body;
                const result = await checkoutService.checkout({
                    username: usr,
                    email: eml,
                    password: pwd,
                    courseId: c_id,
                    cardNumber: card,
                });
                res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
            } catch (err) {
                if (err instanceof CheckoutError) {
                    return res.status(err.statusCode).send(err.message);
                }
                console.error('Erro no checkout:', err);
                res.status(500).send('Erro interno');
            }
        },
    };
}

module.exports = createCheckoutController;
