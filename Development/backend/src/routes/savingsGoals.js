const router = require('express').Router();
const { list, create, update, remove } = require('../controllers/savingsGoalController');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);
router.get('/', list);
router.post('/', create);
router.put('/:id', update);
router.delete('/:id', remove);

module.exports = router;
