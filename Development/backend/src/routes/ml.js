const router = require('express').Router();
const { predictCategory, predictForecast } = require('../controllers/mlController');
const { requireAuth } = require('../middleware/auth');

router.use(requireAuth);
router.post('/predict/category', predictCategory);
router.get('/predict/forecast', predictForecast);

module.exports = router;
