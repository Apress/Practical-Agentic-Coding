/**
 * @fileoverview Domain Data Models / Schemas for ZenithStays Backend.
 * Designed to align with Industry Standards (OTA/HTNG patterns, PredictHQ event models).
 */

/**
 * @typedef {Object} GeoLocation
 * @property {number} lat - Latitude
 * @property {number} lng - Longitude
 */

/**
 * @typedef {Object} Address
 * @property {string} street - Street address
 * @property {string} city - City
 * @property {string} state - State/Province code
 * @property {string} postalCode - Postal/Zip code
 * @property {string} country - Country code (ISO 3166-1 alpha-2)
 */

/**
 * Property Model
 * Aligns with PMS/OTA standards for property description.
 */
const PropertySchema = {
    id: 'string (UUID)',
    name: 'string',
    brand: 'string (optional)',
    type: 'string (Hotel | Resort | VacationRental)',
    status: 'string (Active | Inactive | Maintenance)',
    location: {
        address: 'Address Obect',
        geo: 'GeoLocation Object',
        timeZone: 'string (IANA zone, e.g., America/New_York)'
    },
    specs: {
        totalUnits: 'number',
        floors: 'number (optional)',
        yearBuilt: 'number (optional)'
    },
    // Configuration for connected external systems
    integrations: {
        pmsId: 'string (External PMS ID)',
        channelManagerId: 'string (optional)',
        revenueManagementSystemId: 'string (optional)'
    }
};

/**
 * Room Type Model
 * Inventory definitions.
 */
const RoomTypeSchema = {
    id: 'string (UUID)',
    propertyId: 'string',
    code: 'string (PMS Code, e.g., KNG)',
    name: 'string (e.g., Deluxe King Ocean View)',
    description: 'string',
    maxOccupancy: 'number',
    baseRate: 'number (Decimal)',
    inventoryCount: 'number'
};

/**
 * Booking / Reservation Model
 * Standard PMS Reservation record.
 */
const ReservationSchema = {
    id: 'string (UUID)',
    externalId: 'string (PMS Confirmation Number)',
    propertyId: 'string',
    guest: {
        firstName: 'string',
        lastName: 'string',
        email: 'string',
        phone: 'string',
        segment: 'string (Transient | Group | Corporate)'
    },
    stay: {
        checkIn: 'string (ISO 8601 Date)',
        checkOut: 'string (ISO 8601 Date)',
        nights: 'number'
    },
    rooms: [
        {
            roomTypeId: 'string',
            adults: 'number',
            children: 'number',
            ratePlanId: 'string' // e.g., 'BAR', 'AAA'
        }
    ],
    financials: {
        currency: 'string (USD, EUR)',
        totalAmount: 'number',
        taxAmount: 'number',
        avgDailyRate: 'number',
        status: 'string (Confirmed | Cancelled | CheckedIn | CheckedOut)'
    },
    meta: {
        bookedAt: 'string (ISO 8601 Timestamp)',
        channel: 'string (Direct | OTA | GDS)'
    }
};

/**
 * Market Event Model
 * Aligned with PredictHQ / Google Events API.
 */
const MarketEventSchema = {
    id: 'string',
    source: 'string (PredictHQ | Ticketmaster | Google)',
    title: 'string',
    description: 'string',
    category: 'string (Concerts | Sports | Conferences | Expos | Festivals)',
    labels: 'string[]',
    rank: 'number (0-100 Impact Score)',
    location: {
        geo: 'GeoLocation Object',
        venueName: 'string (optional)',
        scope: 'string (Local | Regional | National | International)'
    },
    timing: {
        start: 'string (ISO 8601 Timestamp)',
        end: 'string (ISO 8601 Timestamp)',
        predictedAttendance: 'number (optional)'
    }
};

/**
 * Market Data / Competitor Rate
 * For rate shopping and parity checks.
 */
const CompetitorRateSchema = {
    id: 'string',
    propertyId: 'string (Our Property)',
    competitorId: 'string (Competitor Property)',
    competitorName: 'string',
    date: 'string (ISO 8601 Date)',
    lengthOfStay: 'number',
    rate: 'number',
    currency: 'string',
    source: 'string (OTA Name | Direct)'
};

module.exports = {
    PropertySchema,
    RoomTypeSchema,
    ReservationSchema,
    MarketEventSchema,
    CompetitorRateSchema
};
