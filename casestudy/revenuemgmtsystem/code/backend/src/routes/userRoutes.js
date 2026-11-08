const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

router.get('/', userController.getUsers);
router.post('/invite', userController.inviteUser);
router.get('/idp', userController.getIDPConfig);
router.put('/idp', userController.updateIDPConfig);

module.exports = router;
