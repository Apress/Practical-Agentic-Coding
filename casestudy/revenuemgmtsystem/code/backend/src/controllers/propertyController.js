const mockDataService = require('../services/mockDataService');

const getAllProperties = (req, res) => {
    console.log(`[PropertyController] Received request to get all properties`);
    try {
        const properties = mockDataService.getProperties();
        console.log(`[PropertyController] Successfully retrieved ${properties.length} properties`);
        res.status(200).json(properties);
    } catch (error) {
        console.error(`[PropertyController] Error fetching properties:`, error);
        res.status(500).json({ message: 'Error fetching properties', error: error.message });
    }
};

const getPropertyById = (req, res) => {
    const { id } = req.params;
    console.log(`[PropertyController] Received request to get property by ID: ${id}`);
    try {
        const property = mockDataService.getPropertyById(id);
        if (!property) {
            console.warn(`[PropertyController] Property not found with ID: ${id}`);
            return res.status(404).json({ message: 'Property not found' });
        }
        console.log(`[PropertyController] Successfully retrieved property: ${property.name} (${property.id})`);
        res.status(200).json(property);
    } catch (error) {
        console.error(`[PropertyController] Error fetching property details for ID ${id}:`, error);
        res.status(500).json({ message: 'Error fetching property details', error: error.message });
    }
};

module.exports = {
    getAllProperties,
    getPropertyById
};
