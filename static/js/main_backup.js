document.addEventListener('DOMContentLoaded', () => {
    // Carousel functionality
    const items = document.querySelectorAll('#recipeCarousel .carousel-item');
    items.forEach((el) => {
        const minPerSlide = 4;
        let next = el.nextElementSibling;
        for (let i = 1; i < minPerSlide; i++) {
            if (!next) next = items[0];
            const cloneChild = next.cloneNode(true);
            el.appendChild(cloneChild.children[0]);
            next = next.nextElementSibling;
        }
    });

    // ===== LOCATION SELECTION - UBER/PATHAO STYLE =====
    let map = null;
    let marker = null;
    let selectedLocation = null;
    
    const locationInput = document.getElementById('locationInput');
    const mapContainer = document.getElementById('mapContainer');
    const mapSearchInput = document.getElementById('mapSearchInput');
    const mapSuggestions = document.getElementById('mapSuggestions');
    const confirmBtn = document.getElementById('confirmLocationBtn');
    const mapCloseBtn = document.getElementById('mapCloseBtn');
    const currentLocationBtn = document.getElementById('currentLocationBtn');
    const selectedLocationInfo = document.getElementById('selectedLocationInfo');
    const selectedLocationText = document.getElementById('selectedLocationText');

    // Open map when clicking location input
    if (locationInput) {
        locationInput.addEventListener('click', openLocationPicker);
    }

    // Open location picker
    function openLocationPicker() {
        mapContainer.classList.add('show');
        setTimeout(() => {
            initMap();
            if (map) map.invalidateSize();
        }, 100);
    }

    // Close location picker
    function closeLocationPicker() {
        mapContainer.classList.remove('show');
        mapSearchInput.value = '';
        mapSuggestions.style.display = 'none';
    }

    // Initialize map
    function initMap() {
        if (map) return;

        // Default center: Dhaka, Bangladesh
        const defaultLat = 23.8103;
        const defaultLng = 90.4125;

        map = L.map('map', {
            center: [defaultLat, defaultLng],
            zoom: 13,
            zoomControl: true
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap',
            maxZoom: 19
        }).addTo(map);

        // Add click handler
        map.on('click', onMapClick);
    }

    // Handle map click
    function onMapClick(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        
        placeMarker(lat, lng);
        reverseGeocode(lat, lng);
    }

    // Place marker on map
    function placeMarker(lat, lng) {
        // Remove existing marker
        if (marker) {
            map.removeLayer(marker);
        }

        // Custom marker icon
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="position: relative;">
                    <i class="fas fa-map-marker-alt" style="color: #E37C7C; font-size: 36px;"></i>
                   </div>`,
            iconSize: [36, 36],
            iconAnchor: [18, 36]
        });

        // Add new marker
        marker = L.marker([lat, lng], { icon: icon }).addTo(map);
        map.setView([lat, lng], 15);

        // Enable confirm button
        confirmBtn.disabled = false;
    }

    // Reverse geocode to get address
    function reverseGeocode(lat, lng) {
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data && data.display_name) {
                    selectedLocation = {
                        lat: lat,
                        lng: lng,
                        address: data.display_name
                    };

                    // Show selected location
                    selectedLocationText.textContent = data.display_name;
                    selectedLocationInfo.style.display = 'block';
                } else {
                    selectedLocation = {
                        lat: lat,
                        lng: lng,
                        address: `${lat.toFixed(4)}, ${lng.toFixed(4)}`
                    };
                    selectedLocationText.textContent = selectedLocation.address;
                    selectedLocationInfo.style.display = 'block';
                }
            })
            .catch(err => {
                console.error('Reverse geocoding failed:', err);
                selectedLocation = {
                    lat: lat,
                    lng: lng,
                    address: `${lat.toFixed(4)}, ${lng.toFixed(4)}`
                };
                selectedLocationText.textContent = selectedLocation.address;
                selectedLocationInfo.style.display = 'block';
            });
    }

    // Search as user types
    if (mapSearchInput) {
        let searchTimeout;
        mapSearchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            if (query.length < 2) {
                mapSuggestions.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                searchLocation(query);
            }, 300);
        });
    }

    // Search for location
    function searchLocation(query) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=BD&limit=5&addressdetails=1`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data && data.length > 0) {
                    showSuggestions(data);
                } else {
                    mapSuggestions.innerHTML = '<div class="map-suggestion-item">No results found</div>';
                    mapSuggestions.style.display = 'block';
                }
            })
            .catch(err => {
                console.error('Search failed:', err);
                mapSuggestions.style.display = 'none';
            });
    }

    // Show search suggestions
    function showSuggestions(places) {
        mapSuggestions.innerHTML = places.map(place => `
            <div class="map-suggestion-item" data-lat="${place.lat}" data-lng="${place.lon}">
                <i class="fas fa-map-pin map-suggestion-icon"></i>
                <div class="map-suggestion-text">
                    <div class="map-suggestion-name">${place.name || place.display_name.split(',')[0]}</div>
                    <div class="map-suggestion-address">${place.display_name}</div>
                </div>
            </div>
        `).join('');

        // Add click handlers
        mapSuggestions.querySelectorAll('.map-suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const lat = parseFloat(item.dataset.lat);
                const lng = parseFloat(item.dataset.lng);
                const address = item.querySelector('.map-suggestion-address').textContent;

                placeMarker(lat, lng);
                selectedLocation = { lat, lng, address };
                selectedLocationText.textContent = address;
                selectedLocationInfo.style.display = 'block';

                mapSuggestions.style.display = 'none';
                mapSearchInput.value = '';
            });
        });

        mapSuggestions.style.display = 'block';
    }

    // Get current location
    if (currentLocationBtn) {
        currentLocationBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                currentLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lng = position.coords.longitude;
                        placeMarker(lat, lng);
                        reverseGeocode(lat, lng);
                        currentLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                    },
                    (error) => {
                        alert('Could not get your location. Please select manually.');
                        currentLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser');
            }
        });
    }

    // Confirm location
    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            if (selectedLocation) {
                locationInput.value = selectedLocation.address;
                closeLocationPicker();
                console.log('Location confirmed:', selectedLocation);
                // Here you can trigger search or filter workers by location
            }
        });
    }

    // Close map
    if (mapCloseBtn) {
        mapCloseBtn.addEventListener('click', closeLocationPicker);
    }

    // Close when clicking outside
    if (mapContainer) {
        mapContainer.addEventListener('click', (e) => {
            if (e.target === mapContainer) {
                closeLocationPicker();
            }
        });
    }

    // Prevent closing when clicking inside modal
    const mapModal = document.querySelector('.map-modal');
    if (mapModal) {
        mapModal.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!mapSearchInput?.contains(e.target) && !mapSuggestions?.contains(e.target)) {
            if (mapSuggestions) mapSuggestions.style.display = 'none';
        }
    });
    const mapCloseBtn = document.getElementById('mapCloseBtn');
    const searchBtn = document.getElementById('searchBtn');

    // Create autocomplete suggestions container
    function createSuggestionsContainer() {
        if (document.querySelector('.location-suggestions')) return;
        
        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'location-suggestions';
        suggestionsDiv.id = 'locationSuggestions';
        locationInput.parentElement.appendChild(suggestionsDiv);
    }

    // Show autocomplete suggestions
    function showSuggestions(suggestions) {
        const suggestionsDiv = document.getElementById('locationSuggestions');
        if (!suggestionsDiv) return;

        if (suggestions.length === 0) {
            suggestionsDiv.innerHTML = '<div class="suggestion-item">No locations found</div>';
            return;
        }

        suggestionsDiv.innerHTML = suggestions
            .slice(0, 8)
            .map((place, index) => `
                <div class="suggestion-item" data-index="${index}">
                    <i class="fas fa-map-pin suggestion-icon"></i>
                    <div class="suggestion-text">
                        <div class="suggestion-name">${place.display_name.split(',')[0]}</div>
                        <div class="suggestion-address">${place.display_name.substring(place.display_name.indexOf(',') + 2)}</div>
                    </div>
                </div>
            `)
            .join('');

        // Add click handlers
        document.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                selectSuggestion(suggestions[index]);
            });
        });

        suggestionsDiv.style.display = 'block';
    }

    // Hide suggestions
    function hideSuggestions() {
        const suggestionsDiv = document.getElementById('locationSuggestions');
        if (suggestionsDiv) suggestionsDiv.style.display = 'none';
    }

    // Select a suggestion
    function selectSuggestion(place) {
        selectedPlace = {
            lat: parseFloat(place.lat),
            lng: parseFloat(place.lon),
            name: place.display_name
        };

        locationInput.value = place.display_name;
        hideSuggestions();
        openMap();

        setTimeout(() => {
            updateMapView(selectedPlace.lat, selectedPlace.lng, selectedPlace.name);
        }, 100);
    }

    // Fetch suggestions from Nominatim (FREE!)
    async function fetchLocationSuggestions(query) {
        if (query.length < 2) {
            hideSuggestions();
            return;
        }

        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=BD&limit=8`
            );
            const data = await response.json();
            
            if (data.length > 0) {
                showSuggestions(data);
            } else {
                const suggestionsDiv = document.getElementById('locationSuggestions');
                if (suggestionsDiv) {
                    suggestionsDiv.innerHTML = '<div class="suggestion-item">No locations found in Bangladesh</div>';
                    suggestionsDiv.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            hideSuggestions();
        }
    }

    // Location input event listeners
    createSuggestionsContainer();

    locationInput.addEventListener('focus', () => {
        openMap();
        if (locationInput.value.length >= 2) {
            fetchLocationSuggestions(locationInput.value);
        }
    });

    locationInput.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length >= 2) {
            fetchLocationSuggestions(query);
        } else {
            hideSuggestions();
        }
    });

    // Close suggestions when clicking elsewhere
    document.addEventListener('click', (e) => {
        if (e.target !== locationInput && !e.target.closest('.location-suggestions')) {
            hideSuggestions();
        }
    });

    // Initialize Leaflet map
    let hoverMarker = null;
    let tempLat = null;
    let tempLng = null;

    function initializeMap() {
        if (map) return;

        try {
            map = L.map('map').setView([23.8103, 90.4125], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);

            // Add mousemove event to show temporary marker
            map.on('mousemove', function(e) {
                tempLat = e.latlng.lat;
                tempLng = e.latlng.lng;
                
                // Remove existing hover marker
                if (hoverMarker) {
                    map.removeLayer(hoverMarker);
                }
                
                // Create custom icon for hover marker (semi-transparent)
                const hoverIcon = L.divIcon({
                    className: 'hover-marker-icon',
                    html: '<i class="fas fa-map-marker-alt" style="color: #E37C7C; font-size: 30px; opacity: 0.6;"></i>',
                    iconSize: [30, 30],
                    iconAnchor: [15, 30]
                });
                
                // Add hover marker
                hoverMarker = L.marker([tempLat, tempLng], { icon: hoverIcon }).addTo(map);
            });

            // Click on map to select location
            map.on('click', function(e) {
                const lat = e.latlng.lat;
                const lng = e.latlng.lng;
                console.log('Map clicked at:', lat, lng);
                selectLocation(lat, lng);
            });

            console.log('Map initialized with click handler');

            // Remove hover marker when mouse leaves map
            map.on('mouseout', function() {
                if (hoverMarker) {
                    map.removeLayer(hoverMarker);
                    hoverMarker = null;
                }
            });

        } catch (error) {
            console.error('Error initializing map:', error);
        }
    }

    // Select location when map is clicked
    function selectLocation(lat, lng) {
        console.log('selectLocation called with:', lat, lng);
        
        // Remove hover marker
        if (hoverMarker && map) {
            map.removeLayer(hoverMarker);
            hoverMarker = null;
        }
        
        // Reverse geocode to get location name
        reverseGeocode(lat, lng);
    }

    // Reverse geocode coordinates to location name
    function reverseGeocode(lat, lng) {
        console.log('Reverse geocoding:', lat, lng);
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&countrycodes=BD`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Reverse geocode response:', data);
                if (data && data.display_name) {
                    selectedPlace = {
                        lat: lat,
                        lng: lng,
                        name: data.display_name
                    };
                    
                    locationInput.value = data.display_name;
                    updateMapView(lat, lng, data.display_name);
                    console.log('Location selected:', selectedPlace);
                } else {
                    // If outside Bangladesh or no result, still show marker
                    selectedPlace = {
                        lat: lat,
                        lng: lng,
                        name: `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`
                    };
                    
                    locationInput.value = selectedPlace.name;
                    updateMapView(lat, lng, selectedPlace.name);
                    console.log('Location selected (no geocode):', selectedPlace);
                }
            })
            .catch(error => {
                console.error('Reverse geocoding error:', error);
                // Still place marker even if geocoding fails
                selectedPlace = {
                    lat: lat,
                    lng: lng,
                    name: `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`
                };
                
                locationInput.value = selectedPlace.name;
                updateMapView(lat, lng, selectedPlace.name);
            });
    }

    // Update map with location marker
    function updateMapView(lat, lng, locationName) {
        initializeMap();
        
        if (!map) return;

        map.setView([lat, lng], 14);

        // Remove existing markers
        map.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });

        // Add new marker
        L.marker([lat, lng]).addTo(map)
            .bindPopup(`<b>${locationName}</b>`)
            .openPopup();
    }

    // Open map modal
    function openMap() {
        mapContainer.classList.add('show');
        setTimeout(() => {
            initializeMap();
            if (map) map.invalidateSize();
        }, 100);
    }

    // Close map modal
    function closeMap() {
        mapContainer.classList.remove('show');
        hideSuggestions();
        // Reset temporary selection
        if (hoverMarker && map) {
            map.removeLayer(hoverMarker);
            hoverMarker = null;
        }
    }

    // Apply location selection
    function applyLocation() {
        if (selectedPlace) {
            // Location is already set in the input field
            console.log('Applied location:', selectedPlace);
            closeMap();
            // Here you can trigger any additional actions like filtering workers
        } else {
            alert('Please select a location on the map first');
        }
    }

    // Cancel location selection
    function cancelLocation() {
        console.log('Cancel location');
        // Reset to previous state
        locationInput.value = '';
        selectedPlace = null;
        
        // Remove all markers
        if (map) {
            map.eachLayer(layer => {
                if (layer instanceof L.Marker) {
                    map.removeLayer(layer);
                }
            });
        }
        
        closeMap();
    }

    // Map action buttons
    const applyLocationBtn = document.getElementById('applyLocationBtn');
    const cancelLocationBtn = document.getElementById('cancelLocationBtn');

    if (applyLocationBtn) {
        applyLocationBtn.addEventListener('click', applyLocation);
    }

    if (cancelLocationBtn) {
        cancelLocationBtn.addEventListener('click', cancelLocation);
    }

    // Map close button
    if (mapCloseBtn) {
        mapCloseBtn.addEventListener('click', closeMap);
    }

    // Close when clicking outside map
    if (mapContainer) {
        mapContainer.addEventListener('click', (e) => {
            if (e.target === mapContainer) {
                closeMap();
            }
        });
    }

    // Prevent closing when clicking inside map
    const mapModal = document.querySelector('.map-modal');
    if (mapModal) {
        mapModal.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    // Search button click
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const location = locationInput.value.trim();
            if (location) {
                searchLocation(location);
            }
        });
    }

    // Search on Enter key
    locationInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const location = locationInput.value.trim();
            if (location) {
                searchLocation(location);
                hideSuggestions();
            }
        }
    });

    // Search by location
    function searchLocation(location) {
        console.log('Searching for location:', location);
        openMap();

        if (selectedPlace && selectedPlace.name === location) {
            updateMapView(selectedPlace.lat, selectedPlace.lng, selectedPlace.name);
            return;
        }

        // Use Nominatim geocoding (FREE!)
        geocodeLocation(location);
    }

    // Geocode location using Nominatim
    function geocodeLocation(location) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}&countrycodes=BD`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const result = data[0];
                    const lat = parseFloat(result.lat);
                    const lon = parseFloat(result.lon);
                    
                    selectedPlace = {
                        lat: lat,
                        lng: lon,
                        name: result.display_name
                    };
                    
                    locationInput.value = result.display_name;
                    updateMapView(lat, lon, result.display_name);
                } else {
                    alert('Location not found in Bangladesh. Please try another location.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error searching for location. Please check your internet connection.');
            });
    }

    // ===== WORKER CARD ANIMATION ON SCROLL =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                cardObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.worker-card').forEach((card) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        card.style.transition = 'all 0.6s ease';
        cardObserver.observe(card);
    });
});

    // ===== WORKER CARD ANIMATION ON SCROLL =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
                cardObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.worker-card').forEach((card) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px)';
        card.style.transition = 'all 0.6s ease';
        cardObserver.observe(card);
    });
});
