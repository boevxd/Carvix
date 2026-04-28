/**
 * Carvix — Role-Based Access Control middleware.
 *
 * Использование:
 *   router.get('/budgets', authRequired, requireRole('Директор', 'Аналитик'), handler);
 *
 * Роль берётся из JWT-payload (поле rol_nazvanie). Если в токене нет роли
 * (старые токены) — возвращаем 403.
 */

function requireRole(...allowedRoles) {
  return (req, res, next) => {
    const role = req.user?.rol_nazvanie;

    if (!role) {
      return res
        .status(403)
        .json({ error: 'Роль не определена. Выполните вход заново.' });
    }

    if (!allowedRoles.includes(role)) {
      return res.status(403).json({
        error: `Недостаточно прав. Требуется одна из ролей: ${allowedRoles.join(', ')}`,
      });
    }

    next();
  };
}

// Сахар: чаще всего нужны эти 2 группы
const requireFinanceRead = requireRole(
  'Директор',
  'Аналитик',
  'Главный механик'
);
const requireFinanceWrite = requireRole('Директор', 'Главный механик');

module.exports = { requireRole, requireFinanceRead, requireFinanceWrite };
