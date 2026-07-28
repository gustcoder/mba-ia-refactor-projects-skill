const { hashPassword } = require('../security/password');

const VISA_TEST_CARD_PREFIX = '4';
const DEFAULT_PASSWORD = '123456';

class CheckoutError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
    }
}

class CheckoutService {
    constructor({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
    }

    async checkout({ username, email, password, courseId, cardNumber }) {
        if (!username || !email || !courseId || !cardNumber) {
            throw new CheckoutError('Bad Request', 400);
        }

        const course = await this.courseModel.findActiveById(courseId);
        if (!course) {
            throw new CheckoutError('Curso não encontrado', 404);
        }

        const user = await this._resolveUser({ username, email, password });

        const paymentStatus = this._authorizePayment(cardNumber);
        if (paymentStatus === 'DENIED') {
            throw new CheckoutError('Pagamento recusado', 400);
        }

        const { lastID: enrollmentId } = await this.enrollmentModel.create(user.id, courseId);
        await this.paymentModel.create(enrollmentId, course.price, paymentStatus);
        await this.auditLogModel.create(`Checkout curso ${courseId} por ${user.id}`);

        return { enrollmentId, courseTitle: course.title };
    }

    async _resolveUser({ username, email, password }) {
        const existingUser = await this.userModel.findByEmail(email);
        if (existingUser) return existingUser;

        const passwordHash = await hashPassword(password || DEFAULT_PASSWORD);
        const { lastID } = await this.userModel.create({ name: username, email, passwordHash });
        return { id: lastID };
    }

    _authorizePayment(cardNumber) {
        return cardNumber.startsWith(VISA_TEST_CARD_PREFIX) ? 'PAID' : 'DENIED';
    }
}

module.exports = { CheckoutService, CheckoutError };
