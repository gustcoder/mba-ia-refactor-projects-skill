const { hashPassword } = require('../security/password');

async function seed(db) {
    const passwordHash = await hashPassword('123');
    await db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', passwordHash]
    );
    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
        ['Clean Architecture', 997.0, 1, 'Docker', 497.0, 1]
    );
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [1, 997.0, 'PAID']
    );
}

module.exports = { seed };
