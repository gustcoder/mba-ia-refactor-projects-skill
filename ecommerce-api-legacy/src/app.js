const express = require('express');

const config = require('./config/settings');
const { createConnection } = require('./database/connection');
const { initSchema } = require('./database/schema');
const { seed } = require('./database/seed');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const { CheckoutService } = require('./services/checkoutService');

const requireAdmin = require('./middlewares/requireAdmin');

const createCheckoutController = require('./controllers/checkoutController');
const createAdminController = require('./controllers/adminController');
const createUserController = require('./controllers/userController');

const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');

async function createApp() {
    const db = createConnection(config.databaseUrl);
    await initSchema(db);
    await seed(db);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);
    const reportModel = new ReportModel(db);

    const checkoutService = new CheckoutService({
        userModel,
        courseModel,
        enrollmentModel,
        paymentModel,
        auditLogModel,
    });

    const checkoutController = createCheckoutController(checkoutService);
    const adminController = createAdminController(reportModel);
    const userController = createUserController(userModel);

    const requireAdminMiddleware = requireAdmin(config);

    const app = express();
    app.use(express.json());

    app.use('/api', checkoutRoutes(checkoutController));
    app.use('/api', adminRoutes(adminController, requireAdminMiddleware));
    app.use('/api', userRoutes(userController, requireAdminMiddleware));

    return app;
}

if (require.main === module) {
    createApp()
        .then((app) => {
            app.listen(config.port, () => {
                console.log(`E-commerce API rodando na porta ${config.port}...`);
            });
        })
        .catch((err) => {
            console.error('Falha ao iniciar aplicação:', err);
            process.exit(1);
        });
}

module.exports = { createApp };
