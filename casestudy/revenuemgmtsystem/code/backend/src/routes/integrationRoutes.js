const express = require('express');
const router = express.Router();
const integrationController = require('../controllers/integrationController');

router.get('/', integrationController.getIntegrations);
router.post('/:id/connect', integrationController.connectIntegration);
router.post('/:id/disconnect', integrationController.disconnectIntegration);
router.post('/:id/sync', integrationController.syncIntegration);

module.exports = router;
