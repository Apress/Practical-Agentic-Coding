const { v4: uuidv4 } = require('uuid');

/**
 * Mock Data Service
 * Generates realistic data based on proper domain schemas.
 */

// --- Properties ---
const properties = [
    {
        id: '1',
        name: 'ZenithStays Flagship Miami',
        brand: 'Zenith Signature',
        type: 'Resort',
        status: 'Active',
        location: {
            address: {
                street: '123 Ocean Drive',
                city: 'Miami Beach',
                state: 'FL',
                postalCode: '33139',
                country: 'US'
            },
            geo: { lat: 25.7617, lng: -80.1918 },
            timeZone: 'America/New_York'
        },
        specs: { totalUnits: 150, floors: 12 },
        integrations: { pmsId: 'PMS-MIA-001' }
    },
    {
        id: '2',
        name: 'ZenithStays City Center NYC',
        brand: 'Zenith Urban',
        type: 'Hotel',
        status: 'Active',
        location: {
            address: {
                street: '456 W 57th St',
                city: 'New York',
                state: 'NY',
                postalCode: '10019',
                country: 'US'
            },
            geo: { lat: 40.7663, lng: -73.9854 },
            timeZone: 'America/New_York'
        },
        specs: { totalUnits: 200, floors: 25 },
        integrations: { pmsId: 'PMS-NYC-002' }
    },
    {
        id: '3',
        name: 'ZenithStays Aspen Lodge',
        brand: 'Zenith Retreat',
        type: 'VacationRental',
        status: 'Active',
        location: {
            address: {
                street: '101 Alpine Road',
                city: 'Aspen',
                state: 'CO',
                postalCode: '81611',
                country: 'US'
            },
            geo: { lat: 39.1911, lng: -106.8175 },
            timeZone: 'America/Denver'
        },
        specs: { totalUnits: 45, floors: 3 },
        integrations: { pmsId: 'PMS-ASP-003' }
    },
    {
        id: '4',
        name: 'ZenithStays Resort',
        brand: 'Zenith Signature',
        type: 'Resort',
        status: 'Active',
        location: {
            address: {
                street: '789 Palm Way',
                city: 'Honolulu',
                state: 'HI',
                postalCode: '96815',
                country: 'US'
            },
            geo: { lat: 21.2760, lng: -157.8286 },
            timeZone: 'Pacific/Honolulu'
        },
        specs: { totalUnits: 320, floors: 18 },
        integrations: { pmsId: 'PMS-HNL-004' }
    }
];

// --- Events (PredictHQ Style) ---
const events = [
    {
        id: 'evt-001',
        source: 'PredictHQ',
        title: 'Art Basel Miami Beach',
        category: 'Expos',
        rank: 90,
        location: {
            geo: { lat: 25.7907, lng: -80.1300 },
            scope: 'International',
            venueName: 'Miami Beach Convention Center'
        },
        timing: {
            start: '2025-12-04T09:00:00Z',
            end: '2025-12-07T18:00:00Z'
        }
    },
    {
        id: 'evt-002',
        source: 'Ticketmaster',
        title: 'New York City Marathon',
        category: 'Sports',
        rank: 100,
        location: {
            geo: { lat: 40.7829, lng: -73.9654 },
            scope: 'International'
        },
        timing: {
            start: '2025-11-02T08:00:00Z',
            end: '2025-11-02T16:00:00Z'
        }
    }
];

// --- Reservations (Sample) ---
const generateReservations = (propId) => {
    // This is a dynamic generator placeholder
    return [
        {
            id: uuidv4(),
            propertyId: propId,
            guest: { firstName: 'John', lastName: 'Doe', segment: 'Transient' },
            stay: { checkIn: '2025-12-24', nights: 3 },
            financials: { totalAmount: 1200, status: 'Confirmed' }
        }
    ];
};


const getProperties = () => properties;
const getPropertyById = (id) => properties.find(p => p.id === id);
const getEvents = () => events;

const getDashboardStats = (propertyId) => {
    console.log(`Getting stats for propertyId: ${propertyId} (Type: ${typeof propertyId})`);

    // Basic variety based on property ID
    if (propertyId === '2') { // NYC
        return [
            { name: 'RevPAR', value: '$210.50', change: '+15.2%', icon: 'DollarSign', trend: 'up' },
            { name: 'Occupancy', value: '88%', change: '+8.1%', icon: 'Users', trend: 'up' },
            { name: 'ADR', value: '$240.00', change: '+5.5%', icon: 'Activity', trend: 'up' },
            { name: 'Demand Score', value: '9.2/10', change: '+10%', icon: 'TrendingUp', trend: 'up' },
        ];
    } else if (propertyId === '3') { // Aspen
        return [
            { name: 'RevPAR', value: '$350.00', change: '-2.5%', icon: 'DollarSign', trend: 'down' },
            { name: 'Occupancy', value: '65%', change: '-5.0%', icon: 'Users', trend: 'down' },
            { name: 'ADR', value: '$540.00', change: '+1.2%', icon: 'Activity', trend: 'up' },
            { name: 'Demand Score', value: '6.5/10', change: '-8%', icon: 'TrendingUp', trend: 'down' },
        ];
    } else if (propertyId === '4') { // Honolulu (Resort)
        return [
            { name: 'RevPAR', value: '$295.00', change: '+5.5%', icon: 'DollarSign', trend: 'up' },
            { name: 'Occupancy', value: '92%', change: '+12.0%', icon: 'Users', trend: 'up' },
            { name: 'ADR', value: '$320.00', change: '-1.5%', icon: 'Activity', trend: 'down' },
            { name: 'Demand Score', value: '8.8/10', change: '+5%', icon: 'TrendingUp', trend: 'up' },
        ];
    }

    // Default (Miami - ID 1)
    return [
        { name: 'RevPAR', value: '$142.50', change: '+12.5%', icon: 'DollarSign', trend: 'up' },
        { name: 'Occupancy', value: '78%', change: '+5.2%', icon: 'Users', trend: 'up' },
        { name: 'ADR', value: '$182.00', change: '+2.1%', icon: 'Activity', trend: 'up' },
        { name: 'Demand Score', value: '8.5/10', change: '+15%', icon: 'TrendingUp', trend: 'up' },
    ];
};



// --- Settings State (Mutable) ---
let generalSettings = {
    propertyInfo: properties[0], // Default to first property
    regional: {
        currency: 'USD ($)',
        timezone: 'America/New_York (GMT-5)',
        units: 'Imperial (sq ft)',
        language: 'English (US)'
    }
};

const getGeneralSettings = () => generalSettings;
const updateGeneralSettings = (newSettings) => {
    generalSettings = { ...generalSettings, ...newSettings };
    return generalSettings;
};

const getDashboardChart = (propertyId) => {
    if (propertyId === '2') { // NYC
        return [
            { name: 'Mon', revenue: 5500, forecast: 5800 },
            { name: 'Tue', revenue: 4800, forecast: 5100 },
            { name: 'Wed', revenue: 4200, forecast: 4500 },
            { name: 'Thu', revenue: 5100, forecast: 5400 },
            { name: 'Fri', revenue: 6200, forecast: 6500 },
            { name: 'Sat', revenue: 7500, forecast: 7800 },
            { name: 'Sun', revenue: 6800, forecast: 7000 },
        ];
    }
    return [
        { name: 'Mon', revenue: 4000, forecast: 4200 },
        { name: 'Tue', revenue: 3000, forecast: 3500 },
        { name: 'Wed', revenue: 2000, forecast: 2800 },
        { name: 'Thu', revenue: 2780, forecast: 3100 },
        { name: 'Fri', revenue: 1890, forecast: 2800 },
        { name: 'Sat', revenue: 2390, forecast: 3500 },
        { name: 'Sun', revenue: 3490, forecast: 3600 },
    ];
};

const getDashboardInsight = (propertyId) => {
    if (propertyId === '2') {
        return {
            id: 'nyc-1',
            description: 'Local event "Tech Week" drives high demand. Recommendation: Increase midweek rates by 10%.'
        };
    }
    return {
        id: '123',
        description: 'Demand surge detected for Weekend of Oct 28th. Competitor "Grand Hotel" raised rates by 15%. Recommend increasing BAR by $20 to capture yield.'
    };
};

module.exports = {
    getProperties,
    getPropertyById,
    getEvents,
    getDashboardStats,
    getDashboardChart,
    getDashboardInsight,
    getGeneralSettings,
    updateGeneralSettings
};
