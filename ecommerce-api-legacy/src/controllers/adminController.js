function createAdminController(reportModel) {
    return {
        async financialReport(req, res) {
            try {
                const report = await reportModel.getFinancialReport();
                res.json(report);
            } catch (err) {
                console.error('Erro ao gerar relatório financeiro:', err);
                res.status(500).send('Erro DB');
            }
        },
    };
}

module.exports = createAdminController;
