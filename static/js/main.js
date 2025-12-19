document.addEventListener('DOMContentLoaded', () => {
    // Bootstrap carousel auto-initialized via data-bs-ride="carousel"
    
    // ===== LOCATION SELECTION - UBER/PATHAO STYLE =====
    // ===== SIMPLE LOCATION TYPEAHEAD (NO MAP) =====
    const locationInput = document.getElementById('locationInput');
    const suggestionBox = document.getElementById('simpleLocationSuggestions');
    let typingTimer;

    function renderSuggestions(list) {
        if (!suggestionBox) return;
        if (!list?.length) {
            suggestionBox.innerHTML = '<div class="suggestion-item">No locations found</div>';
            suggestionBox.style.display = 'block';
            return;
        }
        suggestionBox.innerHTML = list
            .slice(0, 8)
            .map(item => `
                <div class="suggestion-item" data-name="${item.display_name}">
                    <i class="fas fa-map-pin suggestion-icon"></i>
                    <div class="suggestion-text">
                        <div class="suggestion-name">${item.display_name.split(',')[0]}</div>
                        <div class="suggestion-address">${item.display_name}</div>
                    </div>
                </div>
            `).join('');
        suggestionBox.style.display = 'block';
        suggestionBox.querySelectorAll('.suggestion-item').forEach(el => {
            el.addEventListener('click', () => {
                const name = el.dataset.name;
                locationInput.value = name;
                suggestionBox.style.display = 'none';
            });
        });
    }

    async function fetchSuggestions(query) {
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=8`);
            const data = await res.json();
            renderSuggestions(data);
        } catch (e) {
            renderSuggestions([]);
        }
    }

    if (locationInput) {
        locationInput.addEventListener('input', (e) => {
            clearTimeout(typingTimer);
            const q = e.target.value.trim();
            if (q.length < 2) {
                if (suggestionBox) suggestionBox.style.display = 'none';
                return;
            }
            typingTimer = setTimeout(() => fetchSuggestions(q), 250);
        });
        document.addEventListener('click', (e) => {
            if (!suggestionBox?.contains(e.target) && e.target !== locationInput) {
                if (suggestionBox) suggestionBox.style.display = 'none';
            }
        });
    }

    // ===== SEARCH FORM HANDLING =====
    const searchForm = document.getElementById('searchForm');
    const categorySelect = document.getElementById('categorySelect');
    const categoryHidden = document.getElementById('categoryHidden');
    const locationHidden = document.getElementById('locationHidden');
    const searchBtn = document.getElementById('searchBtn');

    if (searchBtn) {
        searchBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (categorySelect) categoryHidden.value = categorySelect.value;
            if (locationInput) locationHidden.value = locationInput.value;
            if (searchForm) searchForm.submit();
        });
    }
                        }

                        function initMap() {
                            if (map) return;
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

                            map.on('click', (e) => {
                                const lat = e.latlng.lat;
                                const lng = e.latlng.lng;
                                placeMarker(lat, lng);
                                reverseGeocode(lat, lng);
                            });
                        }

                        function placeMarker(lat, lng) {
                            // If a marker exists, move it instead of removing to avoid flicker
                            if (marker) {
                                marker.setLatLng([lat, lng]);
                            } else {
                                const icon = L.divIcon({
                                    className: 'custom-marker',
                                    html: '<i class="fas fa-map-marker-alt" style="color: #E37C7C; font-size: 36px;"></i>',
                                    iconSize: [36, 36],
                                    iconAnchor: [18, 36]
                                });
                                marker = L.marker([lat, lng], { icon }).addTo(map);
                            }
                            map.setView([lat, lng], 15);
                            if (confirmBtn) confirmBtn.disabled = false;
                        }

                        function reverseGeocode(lat, lng) {
                            const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1`;
                            fetch(url)
                                .then((res) => res.json())
                                .then((data) => {
                                    const address = data?.display_name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                                    selectedLocation = { lat, lng, address };
                                    if (selectedLocationText) selectedLocationText.textContent = address;
                                    if (selectedLocationInfo) selectedLocationInfo.style.display = 'block';
                                })
                                .catch(() => {
                                    const address = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                                    selectedLocation = { lat, lng, address };
                                    if (selectedLocationText) selectedLocationText.textContent = address;
                                    if (selectedLocationInfo) selectedLocationInfo.style.display = 'block';
                                });
                        }

                        if (mapSearchInput) {
                            let searchTimeout;
                            mapSearchInput.addEventListener('input', (e) => {
                                clearTimeout(searchTimeout);
                                const query = e.target.value.trim();
                                if (query.length < 2) {
                                    if (mapSuggestions) mapSuggestions.style.display = 'none';
                                    return;
                                }
                                searchTimeout = setTimeout(() => searchLocation(query), 300);
                            });
                        }

                        function searchLocation(query) {
                            const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=BD&limit=5&addressdetails=1`;
                            fetch(url)
                                .then((res) => res.json())
                                .then((data) => {
                                    if (data?.length) {
                                        showSuggestions(data);
                                    } else if (mapSuggestions) {
                                        mapSuggestions.innerHTML = '<div class="map-suggestion-item">No results found</div>';
                                        mapSuggestions.style.display = 'block';
                                    }
                                })
                                .catch(() => {
                                    if (mapSuggestions) mapSuggestions.style.display = 'none';
                                });
                        }

                        function showSuggestions(places) {
                            if (!mapSuggestions) return;
                            mapSuggestions.innerHTML = places
                                .map(
                                    (place) => `
                                <div class="map-suggestion-item" data-lat="${place.lat}" data-lng="${place.lon}">
                                    <i class="fas fa-map-pin map-suggestion-icon"></i>
                                    <div class="map-suggestion-text">
                                        <div class="map-suggestion-name">${place.name || place.display_name.split(',')[0]}</div>
                                        <div class="map-suggestion-address">${place.display_name}</div>
                                    </div>
                                </div>`
                                )
                                .join('');
                            mapSuggestions.querySelectorAll('.map-suggestion-item').forEach((item) => {
                                item.addEventListener('click', () => {
                                    const lat = parseFloat(item.dataset.lat);
                                    const lng = parseFloat(item.dataset.lng);
                                    const address = item.querySelector('.map-suggestion-address').textContent;
                                    placeMarker(lat, lng);
                                    selectedLocation = { lat, lng, address };
                                    if (selectedLocationText) selectedLocationText.textContent = address;
                                    if (selectedLocationInfo) selectedLocationInfo.style.display = 'block';
                                    mapSuggestions.style.display = 'none';
                                    mapSearchInput.value = '';
                                });
                            });
                            mapSuggestions.style.display = 'block';
                        }

                        if (currentLocationBtn) {
                            currentLocationBtn.addEventListener('click', () => {
                                if (!navigator.geolocation) {
                                    alert('Geolocation is not supported by your browser');
                                    return;
                                }
                                currentLocationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                                navigator.geolocation.getCurrentPosition(
                                    (pos) => {
                                        const lat = pos.coords.latitude;
                                        const lng = pos.coords.longitude;
                                        placeMarker(lat, lng);
                                        reverseGeocode(lat, lng);
                                        currentLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                                    },
                                    () => {
                                        alert('Could not get your location. Please select manually.');
                                        currentLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                                    }
                                );
                            });
                        }

                        if (confirmBtn) {
                            confirmBtn.addEventListener('click', () => {
                                if (selectedLocation) {
                                    locationInput.value = selectedLocation.address;
                                    closeLocationPicker();
                                }
                            });
                        }

                        if (mapCloseBtn) {
                            mapCloseBtn.addEventListener('click', closeLocationPicker);
                        }

                        if (mapContainer) {
                            mapContainer.addEventListener('click', (e) => {
                                if (e.target === mapContainer) closeLocationPicker();
                            });
                        }

                        const mapModal = document.querySelector('.map-modal');
                        if (mapModal) {
                            mapModal.addEventListener('click', (e) => e.stopPropagation());
                        }

                        document.addEventListener('click', (e) => {
                            if (!mapSearchInput?.contains(e.target) && !mapSuggestions?.contains(e.target)) {
                                if (mapSuggestions) mapSuggestions.style.display = 'none';
                            }
                        });
                    });
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

    // Cancel location selection (keep previously selected value intact)
    function cancelLocation() {
        console.log('Cancel location');
        // Do not clear input or selection; just close the map
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