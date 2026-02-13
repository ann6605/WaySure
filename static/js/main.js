// ==================== GLOBAL VARIABLES ====================
let currentLocation = { lat: null, lng: null };

// ==================== SEARCH ROUTES ====================
async function searchRoutes() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    
    if (!searchTerm) {
        alert('⚠️ Please enter a route number or location to search');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';
    
    try {
        // Call API
        const response = await fetch(`/api/routes/search?origin=${searchTerm}&destination=${searchTerm}`);
        const routes = await response.json();
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Display results
        displayResults(routes);
        
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        alert('❌ Error searching routes. Please try again.');
        console.error(error);
    }
}

// ==================== DISPLAY RESULTS ====================
function displayResults(routes) {
    const resultsDiv = document.getElementById('results');
    
    if (routes.length === 0) {
        resultsDiv.innerHTML = `
            <div class="results-header">
                <h3>😕 No routes found</h3>
                <p>Try searching with different keywords</p>
            </div>
        `;
        return;
    }
    
    // Header
    resultsDiv.innerHTML = `
        <div class="results-header">
            <h3>🚍 Found ${routes.length} route${routes.length > 1 ? 's' : ''}</h3>
            <p>Sorted by safety score (safest first)</p>
        </div>
    `;
    
    // Create cards for each route
    routes.forEach(route => {
        const card = createRouteCard(route);
        resultsDiv.appendChild(card);
    });
}

// ==================== CREATE ROUTE CARD ====================
function createRouteCard(route) {
    const card = document.createElement('div');
    card.className = `route-card ${route.status}`;
    
    const scoreColor = getScoreColor(route.safety_score);
    
    card.innerHTML = `
        <div class="route-header">
            <div>
                <div class="route-number">Route ${route.route_number}</div>
                <div class="route-name">${route.route_name}</div>
            </div>
            <div class="safety-score">
                <div class="score-value" style="color: ${scoreColor}">${route.safety_score}</div>
                <div class="score-label">Safety Score</div>
            </div>
        </div>
        
        <div class="route-details">
            <span>📍 ${route.start} → ${route.end}</span>
            <span>📏 ${route.distance} km</span>
            <span>⏱️ ${route.duration} mins</span>
        </div>
        
        <span class="status-badge ${route.status}">
            ${route.status === 'safe' ? '✅ Safe' : route.status === 'caution' ? '⚠️ Caution' : '🚨 High Risk'}
        </span>
        
        <button onclick="viewRouteDetails(${route.route_id})" class="btn-primary" style="margin-top: 15px;">
            View Details & Incidents
        </button>
    `;
    
    return card;
}

// ==================== GET SCORE COLOR ====================
function getScoreColor(score) {
    if (score >= 70) return '#4caf50'; // Green
    if (score >= 50) return '#ff9800'; // Orange
    return '#f44336'; // Red
}

// ==================== VIEW ROUTE DETAILS ====================
async function viewRouteDetails(routeId) {
    try {
        const response = await fetch(`/api/routes/${routeId}/details`);
        const data = await response.json();
        
        // Create modal or alert with details
        let message = `🚍 Route: ${data.route.route_number}\n`;
        message += `🛡️ Safety Score: ${data.safety_score}\n\n`;
        message += `📊 Recent Incidents (Last 7 Days):\n`;
        
        if (data.recent_incidents.length === 0) {
            message += '✅ No incidents reported recently!';
        } else {
            data.recent_incidents.forEach((inc, index) => {
                message += `\n${index + 1}. ${inc.type.toUpperCase()} (${inc.severity})\n`;
                message += `   ${inc.description}\n`;
            });
        }
        
        alert(message);
        
    } catch (error) {
        alert('❌ Error loading route details');
        console.error(error);
    }
}

// ==================== SHOW STATISTICS ====================
async function showStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        const statsSection = document.getElementById('statsSection');
        statsSection.style.display = 'block';
        
        statsSection.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${stats.total_routes}</div>
                    <div class="stat-label">Total Routes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.total_incidents}</div>
                    <div class="stat-label">Incidents (30 Days)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.most_dangerous_route}</div>
                    <div class="stat-label">Most Dangerous</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${stats.lowest_safety_score}</div>
                    <div class="stat-label">Lowest Score</div>
                </div>
            </div>
        `;
        
        // Scroll to stats
        statsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('❌ Error loading statistics');
        console.error(error);
    }
}

// ==================== SHOW REPORT FORM ====================
function showReportForm() {
    window.location.href = '/report';
}

// ==================== PANIC BUTTON ====================
function triggerPanic() {
    if (!confirm('🚨 Are you sure you want to send an emergency alert?\n\nThis will notify your emergency contacts with your location.')) {
        return;
    }
    
    // Get current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                try {
                    const response = await fetch('/api/panic', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user_id: 1, // Demo user
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(`✅ EMERGENCY ALERT SENT!\n\n📍 Your location has been shared with emergency contacts.\n\nMap Link: ${result.maps_link}\n\n🆘 Police: 100\n🚑 Ambulance: 108`);
                    }
                    
                } catch (error) {
                    alert('❌ Error sending alert. Please call emergency services directly!');
                    console.error(error);
                }
            },
            (error) => {
                alert('❌ Could not get your location. Please enable location services.');
                console.error(error);
            }
        );
    } else {
        alert('❌ Geolocation is not supported by your browser');
    }
}

//  SEARCH ON ENTER KEY 
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchRoutes();
            }
        });
    }
});