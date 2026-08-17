const router = require('express').Router();
const { list, upsert, remove } = require('../controllers/budgetController');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);
router.get('/', list);
router.post('/', upsert);
router.delete('/:id', remove);

module.exports = router;
