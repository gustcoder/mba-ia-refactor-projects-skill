function createUserController(userModel) {
    return {
        async deleteUser(req, res) {
            try {
                await userModel.delete(req.params.id);
                res.json({ msg: 'Usuário deletado' });
            } catch (err) {
                console.error('Erro ao deletar usuário:', err);
                res.status(500).send('Erro ao deletar usuário');
            }
        },
    };
}

module.exports = createUserController;
