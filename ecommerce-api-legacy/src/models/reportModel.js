class ReportModel {
    constructor(db) {
        this.db = db;
    }

    async getFinancialReport() {
        const rows = await this.db.all(`
            SELECT c.id AS course_id, c.title AS course_title,
                   u.name AS student_name,
                   p.amount AS paid_amount, p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id
        `);

        const reportByCourse = new Map();

        for (const row of rows) {
            if (!reportByCourse.has(row.course_id)) {
                reportByCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }

            const courseData = reportByCourse.get(row.course_id);
            if (row.student_name) {
                if (row.payment_status === 'PAID') {
                    courseData.revenue += row.paid_amount;
                }
                courseData.students.push({ student: row.student_name, paid: row.paid_amount || 0 });
            }
        }

        return Array.from(reportByCourse.values());
    }
}

module.exports = ReportModel;
