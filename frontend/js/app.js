/**
 * QuoteMaster application main JavaScript file.
 * Handles user interactions and UI updates.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

/**
 * Initialize the application by setting up event listeners and loading initial data.
 */
async function initializeApp() {
    try {
        // Load all dropdown options from the API
        await Promise.all([
            loadVehicleYears(),
            loadVehicleCategories(),
            loadVehicleCoverages(),
            loadMaritalStatuses(),
            loadHomeOwnershipOptions(),
            loadCarOwnershipOptions(),
            loadVehicleValueRanges(),
            loadDrivingFrequencyOptions()
        ]);
        
        // Set up form submission handler
        const quoteForm = document.getElementById('quote-form');
        quoteForm.addEventListener('submit', handleFormSubmit);
        
        // Set up radio button styling
        setupRadioStyling();
        
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Error initializing app:', error);
        showError(`Failed to initialize application: ${error.message}`);
    }
}

/**
 * Loads available vehicle years from the API and populates the select dropdown.
 */
async function loadVehicleYears() {
    const yearSelect = document.getElementById('vehicle-year');
    await loadDropdownOptions(yearSelect, 'vehicle-years');
}

/**
 * Loads available vehicle categories from the API and populates the select dropdown.
 */
async function loadVehicleCategories() {
    const categorySelect = document.getElementById('vehicle-category');
    await loadDropdownOptions(categorySelect, 'vehicle-categories');
}

/**
 * Loads available coverage levels from the API. The radio buttons are static in the HTML.
 */
async function loadVehicleCoverages() {
    // Radio buttons are already in the HTML, nothing to load
    // But we could validate them against the API if needed
    try {
        const coverageLevels = await api.fetchCoverageLevels();
        console.log('Available coverage levels:', coverageLevels);
    } catch (error) {
        console.error('Error loading coverage levels:', error);
    }
}

/**
 * Loads available marital statuses from the API and populates the select dropdown.
 */
async function loadMaritalStatuses() {
    const maritalSelect = document.getElementById('marital-status');
    await loadDropdownOptions(maritalSelect, 'marital-statuses');
}

/**
 * Loads available home ownership options from the API and populates the select dropdown.
 */
async function loadHomeOwnershipOptions() {
    const homeOwnershipSelect = document.getElementById('home-ownership');
    await loadDropdownOptions(homeOwnershipSelect, 'home-ownership-options');
}

/**
 * Loads available car ownership options from the API and populates the select dropdown.
 */
async function loadCarOwnershipOptions() {
    const carOwnershipSelect = document.getElementById('car-ownership');
    await loadDropdownOptions(carOwnershipSelect, 'car-ownership-options');
}

/**
 * Loads available vehicle value ranges from the API and populates the select dropdown.
 */
async function loadVehicleValueRanges() {
    const vehicleValueSelect = document.getElementById('vehicle-value');
    await loadDropdownOptions(vehicleValueSelect, 'vehicle-value-ranges');
}

/**
 * Loads available driving frequency options from the API and populates the select dropdown.
 */
async function loadDrivingFrequencyOptions() {
    const drivingFrequencySelect = document.getElementById('driving-frequency');
    await loadDropdownOptions(drivingFrequencySelect, 'driving-frequency-options');
}

/**
 * Generic function to load options for a select dropdown from the API.
 * 
 * @param {HTMLSelectElement} selectElement - The select element to populate
 * @param {string} endpointPath - The API endpoint path to fetch options from
 */
async function loadDropdownOptions(selectElement, endpointPath) {
    try {
        // Show loading state
        selectElement.disabled = true;
        
        // Fetch options from API
        const options = await api.fetchOptions(endpointPath);
        
        // Clear current options (except the first one if it's a placeholder)
        const placeholderOption = selectElement.querySelector('option[value=""]');
        selectElement.innerHTML = '';
        if (placeholderOption) {
            selectElement.appendChild(placeholderOption);
        }
        
        // Add options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            selectElement.appendChild(optionElement);
        });
    } catch (error) {
        console.error(`Failed to load options for ${endpointPath}:`, error);
        showError(`Failed to load options: ${error.message}`);
    } finally {
        // Enable select regardless of success/failure
        selectElement.disabled = false;
    }
}

/**
 * Handles the form submission to calculate a quote.
 * 
 * @param {Event} event - The form submission event
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    try {
        // Get form values
        const quoteData = {
            vehicle_category: document.getElementById('vehicle-category').value,
            vehicle_year: parseInt(document.getElementById('vehicle-year').value),
            coverage_level: document.querySelector('input[name="coverage-level"]:checked').value,
            marital_status: document.getElementById('marital-status').value,
            age: parseInt(document.getElementById('driver-age').value),
            home_ownership: document.getElementById('home-ownership').value,
            car_ownership: document.getElementById('car-ownership').value,
            vehicle_value: document.getElementById('vehicle-value').value,
            driving_frequency: document.getElementById('driving-frequency').value,
            zip_code: document.getElementById('zip-code').value
        };
        
        // Validate form data
        if (!validateQuoteData(quoteData)) {
            return;
        }
        
        // Hide any previous results
        const resultElement = document.getElementById('quote-result');
        resultElement.classList.add('hidden');
        
        // Show loading spinner
        const spinner = document.getElementById('loading-spinner');
        spinner.classList.remove('hidden');
        
        // Call API to calculate the quote
        const quoteResult = await api.calculateQuote(quoteData);
        
        // Display the quote result
        displayQuoteResult(quoteResult);
    } catch (error) {
        console.error('Error calculating quote:', error);
        showError(`Failed to calculate quote: ${error.message}`);
    } finally {
        // Hide loading spinner
        document.getElementById('loading-spinner').classList.add('hidden');
    }
}

/**
 * Validates the quote request data before submission.
 * 
 * @param {Object} data - The quote data to validate
 * @returns {boolean} True if valid, false otherwise
 */
function validateQuoteData(data) {
    // Check for any empty required fields
    for (const [key, value] of Object.entries(data)) {
        if (value === "" || value === null || value === undefined) {
            showError(`Please provide a value for ${key.replace(/[_-]/g, ' ')}`);
            return false;
        }
    }
    
    // Age validation
    if (data.age < 16 || data.age > 120) {
        showError("Driver age must be between 16 and 120");
        return false;
    }
    
    // ZIP code validation
    if (!/^\d{5}$/.test(data.zip_code)) {
        showError("ZIP code must be a 5-digit number");
        return false;
    }
    
    return true;
}

/**
 * Displays the quote result in the UI.
 * 
 * @param {Object} quoteResult - The quote calculation result from the API
 */
function displayQuoteResult(quoteResult) {
    const resultElement = document.getElementById('quote-result');
    
    // Create sections for the result display
    let html = `
        <h3>Your Insurance Quote</h3>
        
        <div class="quote-summary">
            <p class="quote-reference">Quote ID: ${quoteResult.quote_id} | Valid until: ${quoteResult.expiration_date}</p>
            
            <div class="summary-section">
                <h4>Coverage Details</h4>
                <div class="coverage-list">
    `;
    
    // Add each coverage
    quoteResult.coverages.forEach(coverage => {
        html += `
            <div class="coverage-item">
                <div class="coverage-header">
                    <span class="coverage-name">${coverage.name}</span>
                    <span class="coverage-amount">${coverage.amount}</span>
                </div>
                <p class="coverage-description">${coverage.description}</p>
                <span class="coverage-premium">${coverage.premium.toFixed(2)}</span>
            </div>
        `;
    });
    
    // Add pricing factors section
    html += `
                </div>
            </div>
            
            <div class="summary-section">
                <h4>Pricing Factors</h4>
                <div class="pricing-factors">
                    <div class="factor"><span>Age Factor:</span> <strong>${quoteResult.age_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Location Factor:</span> <strong>${quoteResult.location_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Marital Status Factor:</span> <strong>${quoteResult.marital_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Vehicle Factor:</span> <strong>${quoteResult.vehicle_factor.toFixed(2)}x</strong></div>
                    <div class="factor"><span>Driving Frequency Factor:</span> <strong>${quoteResult.driving_factor.toFixed(2)}x</strong></div>
                </div>
            </div>
    `;
    
    // Add discounts section if there are any
    if (quoteResult.discounts && quoteResult.discounts.length > 0) {
        html += `
            <div class="summary-section">
                <h4>Your Discounts</h4>
                <div class="discounts-list">
        `;
        
        quoteResult.discounts.forEach(discount => {
            html += `
                <div class="discount-item">
                    <span class="discount-name">${discount.name}</span>
                    <span class="discount-amount">-${discount.amount.toFixed(2)}</span>
                    <p class="discount-description">${discount.description}</p>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    // Add final pricing section
    html += `
            <div class="summary-section price-summary">
                <div class="price-line"><span>Base Premium:</span> <span>${quoteResult.base_premium.toFixed(2)}</span></div>
                <div class="price-line"><span>Subtotal:</span> <span>${quoteResult.subtotal.toFixed(2)}</span></div>
                <div class="price-line discount-line"><span>Discounts:</span> <span>-${quoteResult.total_discounts.toFixed(2)}</span></div>
                <div class="price-line total-line"><span>Total Premium:</span> <span>${quoteResult.final_premium.toFixed(2)}</span></div>
            </div>
        </div>
        
        <div class="quote-actions">
            <button class="btn btn-primary">Purchase This Policy</button>
            <button class="btn btn-secondary" id="btn-modify-quote">Modify Quote</button>
            <button class="btn btn-secondary">Email Quote</button>
        </div>
    `;
    
    // Set the HTML content
    resultElement.innerHTML = html;
    
    // Show the result
    resultElement.classList.remove('hidden');
    
    // Add event listener to the "Modify Quote" button
    const modifyButton = document.getElementById('btn-modify-quote');
    if (modifyButton) {
        modifyButton.addEventListener('click', () => {
            resultElement.classList.add('hidden');
        });
    }
    
    // Scroll to the result
    resultElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Shows an error message to the user.
 * 
 * @param {string} message - The error message to display
 */
function showError(message) {
    alert(`Error: ${message}`);
    console.error(message);
}

/**
 * Setup styling for radio button selections to enhance usability.
 */
function setupRadioStyling() {
    const radioOptions = document.querySelectorAll('.radio-option');
    
    radioOptions.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        
        // Set initial state
        if (radio.checked) {
            option.style.borderColor = 'var(--color-primary)';
            option.style.backgroundColor = 'rgba(52, 152, 219, 0.05)';
        }
        
        // When radio is clicked, update styling
        radio.addEventListener('change', () => {
            // Reset all options
            radioOptions.forEach(opt => {
                opt.style.borderColor = 'var(--color-border)';
                opt.style.backgroundColor = '';
            });
            
            // Style the selected option
            if (radio.checked) {
                option.style.borderColor = 'var(--color-primary)';
                option.style.backgroundColor = 'rgba(52, 152, 219, 0.05)';
            }
        });
        
        // Make entire option clickable
        option.addEventListener('click', (e) => {
            if (e.target !== radio) {
                radio.checked = true;
                
                // Trigger change event to update styling
                const changeEvent = new Event('change');
                radio.dispatchEvent(changeEvent);
            }
        });
    });
}
