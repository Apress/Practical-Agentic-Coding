const express = require('express');
const router = express.Router();
const settingsController = require('../controllers/settingsController');

router.get('/general', settingsController.getGeneralSettings);
router.post('/general', settingsController.updateGeneralSettings);

module.exports = router;
