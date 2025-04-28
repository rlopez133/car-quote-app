/**
 * API client for the QuoteMaster backend.
 * Handles all communication with the API endpoints.
 */

// Configuration
const API_CONFIG = {
    // Set the API base URL to your podman host access point
    //baseUrl: 'http://localhost:8000',
    baseUrl: 'http://car-quote-app-backend:8000',
    endpoints: {
        years: '/vehicle-years',
        categories: '/vehicle-categories',
        coverages: '/coverage-levels',
        maritalStatuses: '/marital-statuses',
        homeOwnership: '/home-ownership-options',
        carOwnership: '/car-ownership-options',
        vehicleValues: '/vehicle-value-ranges',
        drivingFrequency: '/driving-frequency-options',
        quote: '/calculate-quote'
    }
};

/**
 * API client object
 */
const api = {
    /**
     * Fetch options for a dropdown from the API.
     * 
     * @param {string} endpoint - The endpoint path to fetch from
     * @returns {Promise<Array>} Promise resolving to an array of options
     */
    fetchOptions: async function(endpoint) {
        try {
            console.log(`Fetching options from: ${API_CONFIG.baseUrl}/${endpoint}`);
            const response = await fetch(`${API_CONFIG.baseUrl}/${endpoint}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors'
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response not OK:', errorText);
                throw new Error(`Failed to fetch options: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log(`Received options for ${endpoint}:`, data);
            return data;
        } catch (error) {
            console.error(`Error fetching options from ${endpoint}:`, error);
            throw error;
        }
    },
    
    /**
     * Get available vehicle years from the API.
     * 
     * @returns {Promise<number[]>} Promise resolving to an array of years
     */
    fetchVehicleYears: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.years);
    },
    
    /**
     * Get available vehicle categories from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of categories
     */
    fetchVehicleCategories: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.categories);
    },
    
    /**
     * Get available coverage levels from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of coverage levels
     */
    fetchCoverageLevels: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.coverages);
    },
    
    /**
     * Get available marital statuses from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of marital statuses
     */
    fetchMaritalStatuses: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.maritalStatuses);
    },
    
    /**
     * Get available home ownership options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of home ownership options
     */
    fetchHomeOwnershipOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.homeOwnership);
    },
    
    /**
     * Get available car ownership options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of car ownership options
     */
    fetchCarOwnershipOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.carOwnership);
    },
    
    /**
     * Get available vehicle value ranges from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of vehicle value ranges
     */
    fetchVehicleValueRanges: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.vehicleValues);
    },
    
    /**
     * Get available driving frequency options from the API.
     * 
     * @returns {Promise<string[]>} Promise resolving to an array of driving frequency options
     */
    fetchDrivingFrequencyOptions: async function() {
        return this.fetchOptions(API_CONFIG.endpoints.drivingFrequency);
    },
    
    /**
     * Calculate an insurance quote based on provided parameters.
     * 
     * @param {Object} quoteParams - The quote parameters
     * @returns {Promise<Object>} Promise resolving to the quote result
     */
    calculateQuote: async function(quoteParams) {
        try {
            console.log('Sending quote request to:', `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.quote}`);
            console.log('Quote parameters:', quoteParams);
            
            const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.quote}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                mode: 'cors',
                body: JSON.stringify(quoteParams)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                throw new Error(errorData.detail || `Failed to calculate quote: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Quote result:', result);
            return result;
        } catch (error) {
            console.error('Error calculating quote:', error);
            throw error;
        }
    }
};
