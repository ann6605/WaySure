// ==================== GLOBAL VARIABLES ====================
let userLocation = { lat: null, lng: null };

// ==================== GET USER LOCATION ====================
function getLocation() {
    const statusEl = document.getElementById('locationStatus');
    statusEl.innerHTML = '🔄 Getting your location...';
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation.lat = position.coords.latitude;
                userLocation.lng = position.coords.longitude;
                statusEl.innerHTML = `✅ Location captured: ${userLocation.lat.toFixed(4)}, ${userLocation.lng.toFixed(4)}`;
                statusEl.style.color = '#4caf50';
            },
            (error) => {
                statusEl.innerHTML = '❌ Could not get location. Please enable location services.';
                statusEl.style.color = '#f44336';
                console.error(error);
            }
        );
    } else {
        statusEl.innerHTML = '❌ Geolocation not supported by your browser';
        statusEl.style.color = '#f44336';
    }
}

// ==================== FIND ROUTE ID ====================
async function findRouteId(routeNumber) {
    try {
        const response = await fetch(`/api/routes/search?origin=${routeNumber}`);
        const routes = await response.json();
        
        const route = routes.find(r => r.route_number.toLowerCase() === routeNumber.toLowerCase());
        return route ? route.route_id : null;
    } catch (error) {
        console.error(error);
        return null;
    }
}

// ==================== HANDLE FORM SUBMISSION ====================
document.getElementById('incidentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get form data
    const routeNumber = document.getElementById('routeNumber').value.trim();
    const incidentType = document.getElementById('incidentType').value;
    const severity = document.getElementById('severity').value;
    const description = document.getElementById('description').value.trim();
    
    // Validate location
    if (!userLocation.lat || !userLocation.lng) {
        alert('⚠️ Please capture your location first!');
        return;
    }
    
    // Find route ID
    const routeId = await findRouteId(routeNumber);
    
    if (!routeId) {
        alert('⚠️ Route not found. Please check the route number.');
        return;
    }
    
    // Prepare data
    const data = {
        route_id: routeId,
        incident_type: incidentType,
        severity: severity,
        description: description,
        latitude: userLocation.lat,
        longitude: userLocation.lng
    };
    
    try {
        // Submit report
        const response = await fetch('/api/incidents/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Hide form, show success
            document.getElementById('incidentForm').style.display = 'none';
            document.getElementById('successMessage').style.display = 'block';
        } else {
            alert('❌ Error submitting report. Please try again.');
        }
        
    } catch (error) {
        alert('❌ Error submitting report. Please try again.');
        console.error(error);
    }
});

// ==================== GO TO HOME ====================
function goHome() {
    window.location.href = '/';
}

// ==================== PANIC BUTTON ====================
function triggerPanic() {
    if (!confirm('🚨 Send emergency alert?')) return;
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            try {
                const response = await fetch('/api/panic', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: 1,
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    })
                });
                
                const result = await response.json();
                alert(`✅ ALERT SENT!\n\nLocation: ${result.maps_link}`);
                
            } catch (error) {
                alert('❌ Error sending alert');
            }
        },
        (error) => alert('❌ Could not get location')
    );
}

// ==================== AUTO-GET LOCATION ON LOAD ====================
window.addEventListener('load', function() {
    getLocation();
});