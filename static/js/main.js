document.addEventListener('DOMContentLoaded', () => {
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

        // Map initialization
        let map = null;
        const locationInput = document.getElementById('locationInput');
        const mapContainer = document.getElementById('mapContainer');
        const mapCloseBtn = document.getElementById('mapCloseBtn');
        const searchBtn = document.getElementById('searchBtn');

        function initializeMap() {
            if (map) return;
            
            map = L.map('map').setView([23.8103, 90.4125], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(map);
        }

        function openMap() {
            mapContainer.classList.add('show');
            setTimeout(initializeMap, 100);
        }

        function closeMap() {
            mapContainer.classList.remove('show');
        }

        locationInput.addEventListener('focus', openMap);

        mapCloseBtn.addEventListener('click', closeMap);

       
        mapContainer.addEventListener('click', (e) => {
            if (e.target === mapContainer) {
                closeMap();
            }
        });

        
        document.querySelector('.map-modal').addEventListener('click', (e) => {
            e.stopPropagation();
        });

        searchBtn.addEventListener('click', () => {
            const location = locationInput.value;
            if (location.trim() !== '') {
                openMap();
                geocodeLocation(location);
            }
        });

        locationInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const location = locationInput.value;
                if (location.trim() !== '') {
                    openMap();
                    geocodeLocation(location);
                }
            }
        });

        function geocodeLocation(location) {
            initializeMap();
            const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}&countrycodes=BD`;
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        const result = data[0];
                        const lat = parseFloat(result.lat);
                        const lon = parseFloat(result.lon);
                        
                        map.setView([lat, lon], 14);
                        L.marker([lat, lon]).addTo(map)
                            .bindPopup(`<b>${result.display_name}</b>`)
                            .openPopup();
                    } else {
                        alert('Location not found. Please try another location.');
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    });