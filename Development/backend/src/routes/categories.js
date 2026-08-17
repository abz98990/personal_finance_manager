const router = require('express').Router();
const { list, create, remove } = require('../controllers/categoryController');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);
router.get('/', list);
router.post('/', create);
router.delete('/:id', remove);

module.exports = router;
