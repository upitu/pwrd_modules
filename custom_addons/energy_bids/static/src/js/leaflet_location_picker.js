odoo.define('energy_bids.leaflet_location_picker', [], function (require) {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        const openMapBtn = document.getElementById('open-map-btn');
        const mapModal = document.getElementById('mapModal');
        const mapContainer = document.getElementById('leafletMap');

        const locationField = document.getElementById('location');
        const locationIdField = document.getElementById('location_id');
        const locationLinkField = document.getElementById('location_link');
        const emirateSelect = document.getElementById('emirate_select');

        if (!openMapBtn || !mapModal || !mapContainer || !locationIdField || !locationLinkField || !emirateSelect) {
            console.warn('Map Picker: Some DOM elements are missing. Initialization skipped.');
            return;
        }

        let map, marker;

        // UAE emirates mapped to res.country.state IDs
        const EMIRATE_MAP = {
            'Abu Dhabi': 548,
            'Abu Dhabi Emirate': 548,
            'Dubai Emirate': 549,
            'Dubai': 549,
            'Sharjah': 550,
            'Sharjah Emirate': 550,
            'Ajman': 551,
            'Ajman Emirate': 551,
            'Umm Al Quwain': 552,
            'Umm al-Quwain': 552,
            'Umm al-Quwain Emirate': 552,
            'Umm Al Quwain Emirate': 552,
            'Ras Al Khaimah': 553,
            'Ras Al Khaimah Emirate': 553,
            'Ras al-Khaimah': 553,
            'Ras al-Khaimah Emirate': 553,
            'Fujairah': 554,
            'Fujairah Emirate': 554,
        };

        // 🔄 Fetch reverse geocoding data in English
        async function reverseGeocode(lat, lon) {
            const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&accept-language=en&lat=${lat}&lon=${lon}`;
            const response = await fetch(url);
            return await response.json();
        }

        // 🗺️ Initialize Leaflet map
        function setupMap() {
            if (!map) {
                map = L.map('leafletMap').setView([24.466667, 54.366669], 9);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors',
                }).addTo(map);

                map.on('click', async function (e) {
                    const { lat, lng } = e.latlng;

                    if (marker) {
                        map.removeLayer(marker);
                    }

                    marker = L.marker([lat, lng]).addTo(map);

                    try {
                        const result = await reverseGeocode(lat, lng);
                        const state = result?.address?.state ||result?.address?.city || '';
                        console.log("State: "+state);

                        locationLinkField.value = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}#map=18/${lat}/${lng}`;
                        if (locationField) {
                            locationField.value = state;
                        }

                        if (EMIRATE_MAP[state]) {
                            locationIdField.value = EMIRATE_MAP[state];
                            emirateSelect.value = EMIRATE_MAP[state];
                        } else {
                            locationIdField.value = '';
                            emirateSelect.value = '';
                        }
                    } catch (err) {
                        console.error('Reverse geocoding failed:', err);
                    }
                });
            }

            // Fix sizing after modal open
            setTimeout(() => map.invalidateSize(), 200);
        }

        // 📍 Show modal and launch map
        openMapBtn.addEventListener('click', function () {
            if (typeof bootstrap === 'undefined') {
                console.error('❌ Bootstrap is not loaded. Cannot open modal.');
                return;
            }

            const modal = new bootstrap.Modal(mapModal);
            modal.show();
            setupMap();
        });
    });
});