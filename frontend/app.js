// app.js: JavaScript logic for the DB-Forge frontend

// Base URL for the API
const BASE_URL = 'http://db.localhost:8081'; // This should match your Traefik setup
const HOST_HEADER = 'db.localhost';

// DOM Elements
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login');
const logoutBtn = document.getElementById('logout');
const authSection = document.getElementById('authSection');
const mainContent = document.getElementById('mainContent');
const authStatus = document.getElementById('authStatus');

const newDbNameInput = document.getElementById('newDbName');
const spawnDbBtn = document.getElementById('spawnDb');

const pruneDbNameInput = document.getElementById('pruneDbName');
const pruneDbBtn = document.getElementById('pruneDb');

const listDbsBtn = document.getElementById('listDbs');
const dbList = document.getElementById('dbList');

// New DOM Elements for Stats and Discovery
const getGatewayStatsBtn = document.getElementById('getGatewayStats');
const gatewayStatsDiv = document.getElementById('gatewayStats');

const discoverDbsBtn = document.getElementById('discoverDbs');
const discoveryListDiv = document.getElementById('discoveryList');

const dbForTableInput = document.getElementById('dbForTable');
const tableNameInput = document.getElementById('tableName');
const tableColumnsInput = document.getElementById('tableColumns');
const createTableBtn = document.getElementById('createTable');

const dbForInsertInput = document.getElementById('dbForInsert');
const tableForInsertInput = document.getElementById('tableForInsert');
const insertDataInput = document.getElementById('insertData');
const insertDataBtn = document.getElementById('insertDataBtn');

const dbForQueryInput = document.getElementById('dbForQuery');
const tableForQueryInput = document.getElementById('tableForQuery');
const queryParamsInput = document.getElementById('queryParams');
const queryDataBtn = document.getElementById('queryData');
const queryResult = document.getElementById('queryResult');

const dbManagementStatus = document.getElementById('dbManagementStatus');
const dataOpStatus = document.getElementById('dataOpStatus');
const loadingIndicator = document.getElementById('loading');

// State
let authToken = '';
let isLoggedIn = false;

// Utility function to show/hide loading indicator
function showLoading() {
    loadingIndicator.style.display = 'block';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

// Utility function to display status messages
function showStatus(element, message, isSuccess = true) {
    element.innerHTML = `<p class="${isSuccess ? 'success' : 'error'}">${message}</p>`;
    // Clear the message after 5 seconds
    setTimeout(() => {
        element.innerHTML = '';
    }, 5000);
}

// Utility function to make API requests
async function apiRequest(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
        'Host': HOST_HEADER,
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const config = {
        method: 'GET',
        headers,
        ...options
    };
    
    try {
        showLoading();
        const response = await fetch(url, config);
        hideLoading();
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        hideLoading();
        console.error('API Request failed:', error);
        throw error;
    }
}

// Utility function to make API requests with API Key
async function apiRequestWithApiKey(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
        'Host': HOST_HEADER,
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Get API key from local storage
    const apiKey = localStorage.getItem('db-forge-api-key');
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }
    
    const config = {
        method: 'GET',
        headers,
        ...options
    };
    
    try {
        showLoading();
        const response = await fetch(url, config);
        hideLoading();
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        hideLoading();
        console.error('API Request failed:', error);
        throw error;
    }
}

// Function to login
async function login() {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    
    if (!email || !password) {
        showStatus(authStatus, 'Please enter both email and password.', false);
        return;
    }
    
    try {
        const response = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Host': HOST_HEADER,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }
        
        const data = await response.json();
        authToken = data.access_token;
        isLoggedIn = true;
        
        // Hide auth section and show main content
        authSection.style.display = 'none';
        mainContent.style.display = 'block';
        
        showStatus(authStatus, 'Login successful!', true);
    } catch (error) {
        showStatus(authStatus, `Login failed: ${error.message}`, false);
    }
}

// Function to logout
function logout() {
    authToken = '';
    isLoggedIn = false;
    
    // Show auth section and hide main content
    authSection.style.display = 'block';
    mainContent.style.display = 'none';
    
    showStatus(authStatus, 'Logged out successfully!', true);
}

// --- New Functions for Stats and Discovery ---

// Function to fetch and display gateway stats
async function fetchAndDisplayGatewayStats() {
    try {
        const stats = await apiRequestWithApiKey('/admin/gateway/stats');
        let html = `<h3>Gateway Statistics</h3>`;
        html += `<p><strong>Uptime:</strong> ${stats.uptime_seconds.toFixed(2)} seconds</p>`;
        html += `<p><strong>Total Requests:</strong> ${stats.total_requests}</p>`;
        html += `<p><strong>Total Errors:</strong> ${stats.total_errors}</p>`;
        
        html += `<h4>Requests by Endpoint:</h4>`;
        html += `<ul>`;
        for (const [endpoint, count] of Object.entries(stats.requests_by_endpoint)) {
            html += `<li>${endpoint}: ${count}</li>`;
        }
        html += `</ul>`;
        
        html += `<h4>Errors by Type:</h4>`;
        html += `<ul>`;
        for (const [errorType, count] of Object.entries(stats.errors_by_type)) {
            html += `<li>${errorType}: ${count}</li>`;
        }
        html += `</ul>`;
        
        gatewayStatsDiv.innerHTML = html;
    } catch (error) {
        gatewayStatsDiv.innerHTML = `<p class="error">Failed to fetch gateway stats: ${error.message}</p>`;
    }
}

// Function to fetch and display discovered databases
async function fetchAndDisplayDiscovery() {
    try {
        const databases = await apiRequestWithApiKey('/admin/discovery');
        if (databases.length === 0) {
            discoveryListDiv.innerHTML = '<p>No database instances discovered.</p>';
        } else {
            let html = '<h3>Discovered Databases</h3>';
            html += '<ul class="list-group">';
            databases.forEach(db => {
                html += `<li class="list-group-item">
                    <strong>${db.db_name}</strong> - 
                    Status: ${db.status}
                </li>`;
            });
            html += '</ul>';
            discoveryListDiv.innerHTML = html;
        }
    } catch (error) {
        discoveryListDiv.innerHTML = `<p class="error">Failed to fetch discovery info: ${error.message}</p>`;
    }
}

// Database Management
spawnDbBtn.addEventListener('click', async () => {
    const dbName = newDbNameInput.value.trim();
    if (!dbName) {
        showStatus(dbManagementStatus, 'Please enter a database name.', false);
        return;
    }
    
    try {
        const data = await apiRequestWithApiKey(`/admin/databases/spawn/${dbName}`, {
            method: 'POST'
        });
        showStatus(dbManagementStatus, `Database '${dbName}' spawned successfully!`, true);
        newDbNameInput.value = ''; // Clear the input
    } catch (error) {
        showStatus(dbManagementStatus, `Failed to spawn database: ${error.message}`, false);
    }
});

pruneDbBtn.addEventListener('click', async () => {
    const dbName = pruneDbNameInput.value.trim();
    if (!dbName) {
        showStatus(dbManagementStatus, 'Please enter a database name.', false);
        return;
    }
    
    try {
        const data = await apiRequestWithApiKey(`/admin/databases/prune/${dbName}`, {
            method: 'POST'
        });
        showStatus(dbManagementStatus, `Database '${dbName}' pruned successfully!`, true);
        pruneDbNameInput.value = ''; // Clear the input
    } catch (error) {
        showStatus(dbManagementStatus, `Failed to prune database: ${error.message}`, false);
    }
});

listDbsBtn.addEventListener('click', async () => {
    try {
        const databases = await apiRequestWithApiKey('/admin/databases');
        if (databases.length === 0) {
            dbList.innerHTML = '<p>No active databases found.</p>';
        } else {
            let html = '<ul class="list-group">';
            databases.forEach(db => {
                html += `<li class="list-group-item">
                    <strong>${db.name}</strong> - 
                    Container ID: ${db.container_id} - 
                    Status: ${db.status}
                </li>`;
            });
            html += '</ul>';
            dbList.innerHTML = html;
        }
    } catch (error) {
        dbList.innerHTML = `<p class="error">Failed to list databases: ${error.message}</p>`;
    }
});

// Data Operations
createTableBtn.addEventListener('click', async () => {
    const dbName = dbForTableInput.value.trim();
    const tableName = tableNameInput.value.trim();
    const columnsJson = tableColumnsInput.value.trim();
    
    if (!dbName || !tableName || !columnsJson) {
        showStatus(dataOpStatus, 'Please fill in all fields for creating a table.', false);
        return;
    }
    
    try {
        const columns = JSON.parse(columnsJson);
        const data = await apiRequestWithApiKey(`/api/db/${dbName}/tables`, {
            method: 'POST',
            body: JSON.stringify({
                table_name: tableName,
                columns: columns
            })
        });
        showStatus(dataOpStatus, `Table '${tableName}' created successfully in database '${dbName}'!`, true);
        // Clear the inputs
        dbForTableInput.value = '';
        tableNameInput.value = '';
        tableColumnsInput.value = '';
    } catch (error) {
        if (error instanceof SyntaxError) {
            showStatus(dataOpStatus, 'Invalid JSON in columns field.', false);
        } else {
            showStatus(dataOpStatus, `Failed to create table: ${error.message}`, false);
        }
    }
});

insertDataBtn.addEventListener('click', async () => {
    const dbName = dbForInsertInput.value.trim();
    const tableName = tableForInsertInput.value.trim();
    const dataJson = insertDataInput.value.trim();
    
    if (!dbName || !tableName || !dataJson) {
        showStatus(dataOpStatus, 'Please fill in all fields for inserting data.', false);
        return;
    }
    
    try {
        const rows = JSON.parse(dataJson);
        const data = await apiRequestWithApiKey(`/api/db/${dbName}/tables/${tableName}/rows`, {
            method: 'POST',
            body: JSON.stringify({
                rows: rows
            })
        });
        showStatus(dataOpStatus, `Data inserted successfully into '${tableName}' in database '${dbName}'! (${data.rows_affected} rows affected)`, true);
        // Clear the inputs
        dbForInsertInput.value = '';
        tableForInsertInput.value = '';
        insertDataInput.value = '';
    } catch (error) {
        if (error instanceof SyntaxError) {
            showStatus(dataOpStatus, 'Invalid JSON in data field.', false);
        } else {
            showStatus(dataOpStatus, `Failed to insert data: ${error.message}`, false);
        }
    }
});

queryDataBtn.addEventListener('click', async () => {
    const dbName = dbForQueryInput.value.trim();
    const tableName = tableForQueryInput.value.trim();
    const queryParams = queryParamsInput.value.trim();
    
    if (!dbName || !tableName) {
        showStatus(dataOpStatus, 'Please enter database and table names for querying.', false);
        return;
    }
    
    let url = `/api/db/${dbName}/tables/${tableName}/rows`;
    
    // Add query parameters if provided
    if (queryParams) {
        const params = new URLSearchParams();
        queryParams.split('\n').forEach(param => {
            const [key, value] = param.split('=');
            if (key && value !== undefined) {
                params.append(key.trim(), value.trim());
            }
        });
        url += `?${params.toString()}`;
    }
    
    try {
        const data = await apiRequestWithApiKey(url);
        if (data.data && data.data.length > 0) {
            // Create a simple table to display the results
            let html = `<p><strong>Query returned ${data.rows_affected} rows:</strong></p>`;
            html += '<div class="table-responsive"><table class="table table-striped table-bordered">';
            
            // Table header
            html += '<thead><tr>';
            Object.keys(data.data[0]).forEach(key => {
                html += `<th>${key}</th>`;
            });
            html += '</tr></thead>';
            
            // Table body
            html += '<tbody>';
            data.data.forEach(row => {
                html += '<tr>';
                Object.values(row).forEach(value => {
                    html += `<td>${value}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody>';
            
            html += '</table></div>';
            queryResult.innerHTML = html;
        } else {
            queryResult.innerHTML = '<p>No data returned from query.</p>';
        }
    } catch (error) {
        queryResult.innerHTML = `<p class="error">Failed to query data: ${error.message}</p>`;
    }
});

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    console.log('DB-Forge Frontend Initialized');
    
    // Check if user is already logged in
    const token = localStorage.getItem('db-forge-auth-token');
    if (token) {
        authToken = token;
        isLoggedIn = true;
        authSection.style.display = 'none';
        mainContent.style.display = 'block';
    }
});

// Event Listeners
loginBtn.addEventListener('click', login);
logoutBtn.addEventListener('click', logout);

// --- New Event Listeners for Stats and Discovery ---

getGatewayStatsBtn.addEventListener('click', fetchAndDisplayGatewayStats);

discoverDbsBtn.addEventListener('click', fetchAndDisplayDiscovery);

// --- End of New Event Listeners ---