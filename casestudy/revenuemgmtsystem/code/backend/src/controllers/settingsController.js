const mockDataService = require('../services/mockDataService');

const getGeneralSettings = (req, res) => {
    console.log(`[SettingsController] Fetching general settings`);
    res.json(mockDataService.getGeneralSettings());
};

const updateGeneralSettings = (req, res) => {
    console.log(`[SettingsController] Updating general settings`, req.body);
    const updated = mockDataService.updateGeneralSettings(req.body);
    console.log(`[SettingsController] Settings updated successfully`);
    res.json({ success: true, data: updated });
};

module.exports = {
    getGeneralSettings,
    updateGeneralSettings
};
