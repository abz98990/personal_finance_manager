const router = require('express').Router();
const { list, create, update, remove, summary } = require('../controllers/transactionController');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);
router.get('/', list);
router.get('/summary', summary);
router.post('/', create);
router.put('/:id', update);
router.delete('/:id', remove);

module.exports = router;
