/* Lahore Transit Simulation - Fixed Node Clustering Issue */

// ===================== REACT DEVTOOLS FIX =====================
// Fix for React DevTools "initSimulation function not found" error
if (typeof window !== 'undefined') {
    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__ && window.__REACT_DEVTOOLS_GLOBAL_HOOK__.overrideMethod) {
        const originalOverrideMethod = window.__REACT_DEVTOOLS_GLOBAL_HOOK__.overrideMethod;
        window.__REACT_DEVTOOLS_GLOBAL_HOOK__.overrideMethod = function(obj, methodName, fn) {
            try {
                return originalOverrideMethod.call(this, obj, methodName, fn);
            } catch (error) {
                console.warn('React DevTools overrideMethod error caught:', error.message);
                return function() {};
            }
        };
    }
    
    if (!window.initSimulation) {
        window.initSimulation = function() {
            console.log('initSimulation called by React DevTools - Simulation is ready');
            return Promise.resolve();
        };
    }
}

console.log('Simulation script loaded - Fixed Node Clustering');

// Global variables
let map;
let tileLayer;
let satelliteLayer;
let currentTileLayer;

const LAHORE_CENTER = [31.5204, 74.3587];
const LAHORE_BOUNDS = L.latLngBounds([31.30, 74.10], [31.70, 74.55]);

// Simulation state
let ROUTES = [];
let GRAPH = { nodes: [], edges: [] };
let coordsBase = new Map();
let coords = new Map();
let stopMarkers = new Map();
let edgeLines = new Map();
let weightMarkers = new Map();
let hasInitialized = false;
let edgeLayer = null;
let weightLayer = null;
let busTrail = null;

// Dijkstra state
let settledOrder = [];
let path = [];
let totalDistance = null;

// Animation state
let animToken = 0;
let isPaused = false;
let isAnimating = false;
let busMarker = null;
let busAnimationInterval = null;

// DOM Elements
let startSelect, endSelect, computeBtn, stopBtn, pauseBtn, playBtn, swapBtn;
let simMsg, searchStop;
let tGrid, tWeights, tLabels, tExplored, tSatellite, tAutoConnect;
let resetLayoutBtn, saveLayoutBtn, autoConnectBtn, clearRouteBtn;
let kpiDistance, kpiStops, kpiConnections, kpiStatus, netPill, routePill, stopCount;
let speedSlider, speedValue;
let zoomInBtn, zoomOutBtn, fitBoundsBtn, zoomLevel;

// ===================== INITIALIZATION =====================
function initializeDOMReferences() {
    console.log('Initializing DOM references...');
    
    // Control elements
    startSelect = document.getElementById("startSelect");
    endSelect = document.getElementById("endSelect");
    computeBtn = document.getElementById("computeBtn");
    stopBtn = document.getElementById("stopBtn");
    pauseBtn = document.getElementById("pauseBtn");
    playBtn = document.getElementById("playBtn");
    swapBtn = document.getElementById("swapBtn");
    simMsg = document.getElementById("simMsg");
    searchStop = document.getElementById("searchStop");
    
    // Toggle elements
    tGrid = document.getElementById("tGrid");
    tWeights = document.getElementById("tWeights");
    tLabels = document.getElementById("tLabels");
    tExplored = document.getElementById("tExplored");
    tSatellite = document.getElementById("tSatellite");
    tAutoConnect = document.getElementById("tAutoConnect");
    
    // Layout buttons
    resetLayoutBtn = document.getElementById("resetLayoutBtn");
    saveLayoutBtn = document.getElementById("saveLayoutBtn");
    autoConnectBtn = document.getElementById("autoConnectBtn");
    clearRouteBtn = document.getElementById("clearRouteBtn");
    
    // KPI elements
    kpiDistance = document.getElementById("kpiDistance");
    kpiStops = document.getElementById("kpiStops");
    kpiConnections = document.getElementById("kpiConnections");
    kpiStatus = document.getElementById("kpiStatus");
    netPill = document.getElementById("netPill");
    routePill = document.getElementById("routePill");
    stopCount = document.getElementById("stopCount");
    
    // Speed control
    speedSlider = document.getElementById("speed");
    speedValue = document.getElementById("speedValue");
    
    // Map controls
    zoomInBtn = document.getElementById("zoomInBtn");
    zoomOutBtn = document.getElementById("zoomOutBtn");
    fitBoundsBtn = document.getElementById("fitBoundsBtn");
    zoomLevel = document.getElementById("zoomLevel");
    
    console.log('DOM references initialized');
}

function setMsg(el, text, isErr = false) {
    el.textContent = text;
    el.style.color = isErr ? "#fecaca" : "#94a3b8";
}

function setKpis({ distance, stops, connections, status }) {
    kpiDistance.textContent = distance == null ? "—" : `${(Math.round(distance * 100) / 100).toFixed(2)} km`;
    kpiStops.textContent = stops == null ? "0" : String(stops);
    kpiConnections.textContent = connections == null ? "0" : String(connections);
    kpiStatus.textContent = status || "🟢 Idle";
    stopCount.textContent = stops || "0";
}

// ===================== LEAFLET MAP SETUP =====================
function initMap() {
    console.log('Initializing Leaflet map...');

    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('Map container not found!');
        return;
    }
    
    map = L.map('map', {
        center: LAHORE_CENTER,
        zoom: 12,
        zoomControl: true,
        preferCanvas: true,
        maxZoom: 18,
        minZoom: 10,
        maxBounds: LAHORE_BOUNDS,
        maxBoundsViscosity: 0.9
    });

    tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        minZoom: 10
    });
    
    satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri',
        maxZoom: 19,
        minZoom: 10
    });

    currentTileLayer = tileLayer;
    tileLayer.addTo(map);

    map.fitBounds(LAHORE_BOUNDS.pad(0.08));

    edgeLayer = L.layerGroup().addTo(map);
    weightLayer = L.layerGroup().addTo(map);

    map.on('zoom', function() {
        zoomLevel.textContent = map.getZoom();
    });
    
    console.log('Map initialized successfully');
}

// ===================== STOP MANAGEMENT =====================
function createStopIcon(type = 'normal') {
    const className = `stop-icon ${type}`;
    const size = type === 'start' || type === 'end' ? 56 : 48;
    const buildingSvg = `
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M4 20V7.5L12 4l8 3.5V20" stroke="white" stroke-width="1.6" fill="rgba(255,255,255,0.15)"/>
            <rect x="7" y="9" width="2" height="2" fill="white"/>
            <rect x="11" y="9" width="2" height="2" fill="white"/>
            <rect x="15" y="9" width="2" height="2" fill="white"/>
            <rect x="7" y="13" width="2" height="2" fill="white"/>
            <rect x="11" y="13" width="2" height="2" fill="white"/>
            <rect x="15" y="13" width="2" height="2" fill="white"/>
            <rect x="10" y="17" width="4" height="3" fill="white"/>
        </svg>
    `;
    const emoji = type === 'start' ? '📍' : type === 'end' ? '🎯' : buildingSvg;
    
    return L.divIcon({
        className: className,
        iconSize: [size, size],
        iconAnchor: [size/2, size/2],
        html: `
            <div style="
                width:${size}px;
                height:${size}px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:${type === 'start' || type === 'end' ? '20px' : '16px'};
            ">
                ${emoji}
            </div>
        `
    });
}

function createBusIcon() {
    return L.divIcon({
        className: 'bus-icon',
        iconSize: [62, 62],
        iconAnchor: [31, 31],
        html: '<div style="width:62px;height:62px;display:flex;align-items:center;justify-content:center;font-size:28px">🚌</div>'
    });
}

function renderStops() {
    console.log('Rendering stops...');
    
    stopMarkers.forEach(marker => {
        if (marker && marker.remove) marker.remove();
    });
    stopMarkers.clear();
    
    if (!GRAPH.nodes || GRAPH.nodes.length === 0) {
        console.log('No stops to render');
        return;
    }
    
    console.log('Rendering stops:', GRAPH.nodes);
    
    GRAPH.nodes.forEach((stopName, index) => {
        const coord = coords.get(stopName);
        if (!coord || !coord.lat || !coord.lng) {
            console.error(`Missing coordinates for stop: ${stopName}`);
            return;
        }
        
        let type = 'normal';
        if (stopName === startSelect.value) type = 'start';
        else if (stopName === endSelect.value) type = 'end';
        else if (path.includes(stopName)) type = 'path';
        else if (settledOrder.includes(stopName) && tExplored.checked) type = 'explored';
        
        const marker = L.marker([coord.lat, coord.lng], {
            icon: createStopIcon(type),
            draggable: true,
            title: stopName
        }).addTo(map);
        
        const connections = GRAPH.edges.filter(e => e.from === stopName || e.to === stopName).length;
        marker.bindTooltip(`
            <strong>${stopName}</strong><br>
            📍 Lat: ${coord.lat.toFixed(4)}<br>
            📍 Lng: ${coord.lng.toFixed(4)}<br>
            🔗 Connections: ${connections}
        `, {
            permanent: tLabels.checked,
            direction: 'top',
            opacity: 0.9,
            className: 'stop-tooltip'
        });
        
        stopMarkers.set(stopName, marker);
        
        marker.on('dragend', function(e) {
            const newPos = e.target.getLatLng();
            const oldCoord = coords.get(stopName);
            
            const distanceMoved = calculateDistance(
                oldCoord.lat, oldCoord.lng,
                newPos.lat, newPos.lng
            ) * 1000;
            
            if (distanceMoved > 10) {
                coords.set(stopName, { lat: newPos.lat, lng: newPos.lng });
                setMsg(simMsg, `Moved ${stopName} to new location`, false);
                renderEdges();
                updateStopIcons();
            }
        });
        
        marker.on('click', function() {
            if (!startSelect.value) {
                startSelect.value = stopName;
            } else if (!endSelect.value) {
                endSelect.value = stopName;
            } else {
                startSelect.value = endSelect.value;
                endSelect.value = stopName;
            }
            updateStopIcons();
            setMsg(simMsg, `Selected ${stopName}`, false);
        });
    });
    
    console.log(`Rendered ${stopMarkers.size} stops`);
}

function updateStopIcons() {
    stopMarkers.forEach((marker, stopName) => {
        if (!marker) return;
        
        let type = 'normal';
        if (stopName === startSelect.value) type = 'start';
        else if (stopName === endSelect.value) type = 'end';
        else if (path.includes(stopName)) type = 'path';
        else if (settledOrder.includes(stopName) && tExplored.checked) type = 'explored';
        
        marker.setIcon(createStopIcon(type));
        
        const tooltip = marker.getTooltip();
        if (tooltip) {
            tooltip.setOpacity(tLabels.checked ? 0.9 : 0);
        }
    });
}

// ===================== EDGE MANAGEMENT =====================
function renderEdges() {
    console.log('Rendering edges...');
    
    edgeLines.forEach(lines => {
        if (Array.isArray(lines)) {
            lines.forEach(line => line && line.remove && line.remove());
        } else if (lines && lines.remove) {
            lines.remove();
        }
    });
    weightMarkers.forEach(marker => marker && marker.remove && marker.remove());
    edgeLines.clear();
    weightMarkers.clear();

    if (edgeLayer) edgeLayer.clearLayers();
    if (weightLayer) weightLayer.clearLayers();
    
    if (!tGrid.checked || !GRAPH.edges || GRAPH.edges.length === 0) {
        console.log('Edges disabled or no edges to render');
        return;
    }
    
    console.log('Drawing edges:', GRAPH.edges);
    
    GRAPH.edges.forEach(edge => {
        const fromCoord = coords.get(edge.from);
        const toCoord = coords.get(edge.to);
        
        if (!fromCoord || !toCoord) {
            console.warn(`Missing coordinates for edge: ${edge.from} -> ${edge.to}`);
            return;
        }
        
        if (isNaN(fromCoord.lat) || isNaN(fromCoord.lng) || isNaN(toCoord.lat) || isNaN(toCoord.lng)) {
            console.warn(`Invalid coordinates for edge: ${edge.from} -> ${edge.to}`);
            return;
        }
        
        const isPathEdge = path.some((stop, index) => {
            if (index === path.length - 1) return false;
            return (stop === edge.from && path[index + 1] === edge.to) ||
                   (stop === edge.to && path[index + 1] === edge.from);
        });
        
        const distance = typeof edge.w === 'number' ? edge.w : calculateDistance(fromCoord.lat, fromCoord.lng, toCoord.lat, toCoord.lng);
        
        const lineBase = L.polyline([
            [fromCoord.lat, fromCoord.lng],
            [toCoord.lat, toCoord.lng]
        ], {
            color: isPathEdge ? '#0f766e' : '#0f172a',
            weight: isPathEdge ? 18 : 14,
            opacity: isPathEdge ? 0.5 : 0.55,
            lineCap: 'round',
            lineJoin: 'round',
            className: `${isPathEdge ? 'road-line path casing' : 'road-line casing'}`
        });

        const line = L.polyline([
            [fromCoord.lat, fromCoord.lng],
            [toCoord.lat, toCoord.lng]
        ], {
            color: isPathEdge ? '#10b981' : '#2563eb',
            weight: isPathEdge ? 12 : 9,
            opacity: isPathEdge ? 0.95 : 0.85,
            lineCap: 'round',
            lineJoin: 'round',
            className: `${isPathEdge ? 'road-line path glow' : 'road-line glow'}`
        });

        lineBase.addTo(edgeLayer);
        line.addTo(edgeLayer);

        edgeLines.set(`${edge.from}-${edge.to}`, [lineBase, line]);
        
        if (tWeights.checked) {
            const midLat = (fromCoord.lat + toCoord.lat) / 2;
            const midLng = (fromCoord.lng + toCoord.lng) / 2;
            
            const weightDiv = L.divIcon({
                className: 'weight-label',
                iconSize: [1, 1],
                iconAnchor: [0, 0],
                html: `<div>${distance.toFixed(2)} km</div>`
            });
            
            const weightMarker = L.marker([midLat, midLng], {
                icon: weightDiv,
                interactive: false
            }).addTo(weightLayer);
            
            weightMarkers.set(`${edge.from}-${edge.to}`, weightMarker);
        }
    });
    
    console.log(`Rendered ${edgeLines.size} edges`);
}

function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function computePathDistance(pathStops) {
    if (!Array.isArray(pathStops) || pathStops.length < 2) return 0;
    let distance = 0;
    for (let i = 0; i < pathStops.length - 1; i++) {
        const from = pathStops[i];
        const to = pathStops[i + 1];
        const edge = GRAPH.edges.find(e =>
            (e.from === from && e.to === to) || (e.from === to && e.to === from)
        );
        if (edge && typeof edge.w === 'number') {
            distance += edge.w;
        } else {
            const fromCoord = coords.get(from);
            const toCoord = coords.get(to);
            if (fromCoord && toCoord) {
                distance += calculateDistance(fromCoord.lat, fromCoord.lng, toCoord.lat, toCoord.lng);
            }
        }
    }
    return distance;
}

function computePathDistance(pathStops) {
    if (!Array.isArray(pathStops) || pathStops.length < 2) return 0;
    let distance = 0;
    for (let i = 0; i < pathStops.length - 1; i++) {
        const from = pathStops[i];
        const to = pathStops[i + 1];
        const edge = GRAPH.edges.find(e =>
            (e.from === from && e.to === to) || (e.from === to && e.to === from)
        );
        if (edge && typeof edge.w === 'number') {
            distance += edge.w;
        } else {
            const fromCoord = coords.get(from);
            const toCoord = coords.get(to);
            if (fromCoord && toCoord) {
                distance += calculateDistance(fromCoord.lat, fromCoord.lng, toCoord.lat, toCoord.lng);
            }
        }
    }
    return distance;
}

// ===================== DATA LOADING =====================
async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

async function loadSimulationData() {
    console.log('Loading simulation data...');
    setMsg(simMsg, 'Loading simulation data...');
    
    try {
        const routesData = await fetchJSON('/api/sim/routes');
        ROUTES = routesData.routes || [];
        console.log('Routes loaded:', ROUTES);
        
        const graphData = await fetchJSON('/api/sim/graph');
        console.log('Graph data loaded:', graphData);
        
        await processData(routesData, graphData);
        
        netPill.textContent = `Network: ${GRAPH.nodes.length} stops · ${GRAPH.edges.length} routes`;
        
        populateDropdowns();
        
        renderStops();
        renderEdges();
        
        setTimeout(() => {
            fitBoundsToStops();
            setMsg(simMsg, `Loaded ${GRAPH.nodes.length} stops and ${GRAPH.edges.length} routes`);
            setKpis({
                distance: null,
                stops: GRAPH.nodes.length,
                connections: GRAPH.edges.length,
                status: "🟢 Ready"
            });
        }, 100);
        
        console.log('Data loaded successfully');
        
    } catch (error) {
        console.error('Failed to load simulation data:', error);
        setMsg(simMsg, `Error loading data: ${error.message}`, true);
        setKpis({
            distance: null,
            stops: null,
            connections: null,
            status: "🔴 Error"
        });
        
        createStableTestData();
    }
}

async function processData(routesData, graphData) {
    console.log('Processing data...');
    
    GRAPH = { nodes: [], edges: [] };
    coordsBase.clear();
    coords.clear();
    
    const nodesFromRoutes = extractNodesFromRoutes();
    if (graphData.nodes && graphData.nodes.length > 0) {
        console.log('Using node coordinates from graph data');
        processGraphNodes(graphData.nodes);
    }

    GRAPH.nodes = nodesFromRoutes.filter((name) => coords.has(name));
    if (GRAPH.nodes.length === 0 && nodesFromRoutes.length > 0) {
        GRAPH.nodes = nodesFromRoutes;
    }

    GRAPH.edges = buildEdgesFromRoutes(routesData);
    if (GRAPH.edges.length === 0 && graphData.edges && graphData.edges.length > 0) {
        console.log('Fallback to graph edges');
        processGraphEdges(graphData.edges);
    }
    
    console.log('Final graph:', GRAPH);
    console.log('Final coordinates:', coords);
}

function processGraphNodes(nodes) {
    nodes.forEach((node, index) => {
        let nodeName;
        let lat = null;
        let lng = null;
        
        if (typeof node === 'string') {
            nodeName = node.trim();
        } else if (typeof node === 'object') {
            nodeName = (node.name || node.id || `Stop_${index + 1}`).toString().trim();
            lat = typeof node.lat === 'number' ? node.lat : null;
            lng = typeof node.lng === 'number' ? node.lng : null;
        }
        
        if (!nodeName) return;

        if (lat !== null && lng !== null) {
            coords.set(nodeName, { lat, lng });
            coordsBase.set(nodeName, { lat, lng });
        }
    });
}

function extractNodesFromRoutes() {
    const nodeSet = new Set();
    
    ROUTES.forEach(route => {
        if (route.stops && Array.isArray(route.stops)) {
            route.stops.forEach(stop => {
                if (stop && typeof stop === 'string') {
                    nodeSet.add(stop.trim());
                }
            });
        }
    });
    
    const nodes = Array.from(nodeSet);
    console.log('Extracted nodes:', nodes);
    return nodes;
}

function processGraphEdges(edges) {
    edges.forEach(edge => {
        if (edge.from && edge.to && 
            GRAPH.nodes.includes(edge.from) && 
            GRAPH.nodes.includes(edge.to)) {
            
            const edgeExists = GRAPH.edges.some(e => 
                (e.from === edge.from && e.to === edge.to) ||
                (e.from === edge.to && e.to === edge.from)
            );
            
            if (!edgeExists) {
                const fromCoord = coords.get(edge.from);
                const toCoord = coords.get(edge.to);
                
                if (fromCoord && toCoord) {
                    const distance = typeof edge.w === 'number'
                        ? edge.w
                        : calculateDistance(
                            fromCoord.lat, fromCoord.lng,
                            toCoord.lat, toCoord.lng
                        );
                    
                    GRAPH.edges.push({
                        from: edge.from,
                        to: edge.to,
                        w: distance
                    });
                }
            }
        }
    });
}

function createStableEdgesFromRoutes() {
    const edgeSet = new Set();
    
    ROUTES.forEach(route => {
        if (!route.stops || !Array.isArray(route.stops)) return;
        
        const stops = route.stops;
        
        for (let i = 0; i < stops.length - 1; i++) {
            const fromStop = stops[i]?.toString().trim();
            const toStop = stops[i + 1]?.toString().trim();
            
            if (!fromStop || !toStop || fromStop === toStop) continue;
            
            if (!GRAPH.nodes.includes(fromStop) || !GRAPH.nodes.includes(toStop)) continue;
            
            const edgeKey = `${fromStop}-${toStop}`;
            const reverseEdgeKey = `${toStop}-${fromStop}`;
            
            if (!edgeSet.has(edgeKey) && !edgeSet.has(reverseEdgeKey)) {
                const fromCoord = coords.get(fromStop);
                const toCoord = coords.get(toStop);
                
                if (fromCoord && toCoord) {
                    const distance = calculateDistance(
                        fromCoord.lat, fromCoord.lng,
                        toCoord.lat, toCoord.lng
                    );
                    
                    GRAPH.edges.push({
                        from: fromStop,
                        to: toStop,
                        w: distance
                    });
                    
                    edgeSet.add(edgeKey);
                }
            }
        }
    });
}

function buildEdgesFromRoutes(routesData) {
    const edges = [];
    const edgeSet = new Set();
    const routes = routesData?.routes || [];

    routes.forEach((route) => {
        const stops = Array.isArray(route.stops) ? route.stops : [];
        const distances = Array.isArray(route.distances) ? route.distances : [];

        for (let i = 0; i < stops.length - 1; i++) {
            const fromStop = stops[i]?.toString().trim();
            const toStop = stops[i + 1]?.toString().trim();
            if (!fromStop || !toStop) continue;
            if (!GRAPH.nodes.includes(fromStop) || !GRAPH.nodes.includes(toStop)) continue;

            const edgeKey = `${fromStop}-${toStop}`;
            const reverseKey = `${toStop}-${fromStop}`;
            if (edgeSet.has(edgeKey) || edgeSet.has(reverseKey)) continue;

            let distance = distances[i];
            if (typeof distance !== 'number' || Number.isNaN(distance)) {
                const fromCoord = coords.get(fromStop);
                const toCoord = coords.get(toStop);
                if (fromCoord && toCoord) {
                    distance = calculateDistance(fromCoord.lat, fromCoord.lng, toCoord.lat, toCoord.lng);
                } else {
                    distance = 1;
                }
            }

            edges.push({ from: fromStop, to: toStop, w: distance });
            edgeSet.add(edgeKey);
        }
    });

    return edges;
}

// ===================== ROUTE COMPUTATION =====================
async function computeRoute() {
    const start = startSelect.value;
    const end = endSelect.value;
    
    if (!start || !end) {
        setMsg(simMsg, "Please select both start and destination stops", true);
        return;
    }
    
    if (start === end) {
        setMsg(simMsg, "Start and destination cannot be the same", true);
        return;
    }
    
    setMsg(simMsg, "Computing shortest path...");
    setKpis({
        distance: null,
        stops: GRAPH.nodes.length,
        connections: GRAPH.edges.length,
        status: "🟡 Computing"
    });
    
    try {
        const result = await fetchJSON('/api/sim/path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start, end })
        });
        
        settledOrder = result.settled_order || [];
        path = result.path || [];
        totalDistance = result.distance || null;
        
        if (path.length === 0) {
            setMsg(simMsg, "No path found between selected stops", true);
            setKpis({
                distance: null,
                stops: GRAPH.nodes.length,
                connections: GRAPH.edges.length,
                status: "🔴 No route"
            });
            return;
        }
        
        if (totalDistance == null) {
            totalDistance = computePathDistance(path);
        }

        routePill.textContent = `Path: ${path[0]} → ${path[path.length - 1]}`;
        setMsg(simMsg, `Found path: ${path.join(' → ')} | Distance: ${totalDistance?.toFixed(2)} km`);
        
        setKpis({
            distance: totalDistance,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🟢 Path found"
        });
        
        updateStopIcons();
        renderEdges();
        
        animateBusAlongPath();
        
    } catch (error) {
        console.error('Route computation error:', error);
        setMsg(simMsg, `Error computing route: ${error.message}`, true);
        setKpis({
            distance: null,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🔴 Error"
        });
        
        computeClientSideRoute(start, end);
    }
}

function computeClientSideRoute(start, end) {
    console.log('Computing route client-side...');
    
    const distances = {};
    const previous = {};
    const unvisited = new Set(GRAPH.nodes);
    
    GRAPH.nodes.forEach(node => {
        distances[node] = Infinity;
        previous[node] = null;
    });
    distances[start] = 0;
    
    settledOrder = [];
    
    while (unvisited.size > 0) {
        let current = null;
        let minDist = Infinity;
        
        unvisited.forEach(node => {
            if (distances[node] < minDist) {
                minDist = distances[node];
                current = node;
            }
        });
        
        if (current === null || current === end) break;
        
        unvisited.delete(current);
        settledOrder.push(current);
        
        const neighbors = GRAPH.edges.filter(edge => 
            edge.from === current || edge.to === current
        );
        
        neighbors.forEach(edge => {
            const neighbor = edge.from === current ? edge.to : edge.from;
            if (!unvisited.has(neighbor)) return;
            
            const alt = distances[current] + edge.w;
            if (alt < distances[neighbor]) {
                distances[neighbor] = alt;
                previous[neighbor] = current;
            }
        });
    }
    
    path = [];
    totalDistance = distances[end];
    
    if (distances[end] !== Infinity) {
        let current = end;
        while (current !== null) {
            path.unshift(current);
            current = previous[current];
        }
    }
    
    if (path.length > 0) {
        if (totalDistance === Infinity) {
            totalDistance = computePathDistance(path);
        }

        routePill.textContent = `Path: ${path[0]} → ${path[path.length - 1]}`;
        setMsg(simMsg, `Found path: ${path.join(' → ')} | Distance: ${totalDistance?.toFixed(2) || 0} km`);
        
        setKpis({
            distance: totalDistance,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🟢 Path found"
        });
        
        updateStopIcons();
        renderEdges();
        animateBusAlongPath();
    } else {
        setMsg(simMsg, "No path found between selected stops", true);
        setKpis({
            distance: null,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🔴 No route"
        });
    }
}

function animateBusAlongPath() {
    if (busAnimationInterval) {
        cancelAnimationFrame(busAnimationInterval);
        busAnimationInterval = null;
    }
    
    if (busMarker) {
        busMarker.remove();
        busMarker = null;
    }

    if (busTrail) {
        busTrail.remove();
        busTrail = null;
    }
    
    if (path.length < 2) return;
    
    const startCoord = coords.get(path[0]);
    if (!startCoord) return;
    
    busMarker = L.marker([startCoord.lat, startCoord.lng], {
        icon: createBusIcon()
    }).addTo(map);

    busTrail = L.polyline([[startCoord.lat, startCoord.lng]], {
        color: '#f59e0b',
        weight: 6,
        opacity: 0.6,
        lineCap: 'round',
        lineJoin: 'round',
        dashArray: '8 12'
    }).addTo(map);
    
    const speed = parseFloat(speedSlider.value) || 1;
    let currentSegment = 0;
    let progress = 0;
    let lastTimestamp = null;

    const step = (timestamp) => {
        if (isPaused) {
            busAnimationInterval = requestAnimationFrame(step);
            return;
        }
        
        if (currentSegment >= path.length - 1) {
            cancelAnimationFrame(busAnimationInterval);
            busAnimationInterval = null;
            setMsg(simMsg, `Bus reached destination: ${path[path.length - 1]}`);
            setKpis({
                distance: totalDistance,
                stops: GRAPH.nodes.length,
                connections: GRAPH.edges.length,
                status: "🟢 Complete"
            });
            return;
        }

        if (!lastTimestamp) lastTimestamp = timestamp;
        const delta = timestamp - lastTimestamp;
        lastTimestamp = timestamp;
        
        const fromStop = path[currentSegment];
        const toStop = path[currentSegment + 1];
        const fromCoord = coords.get(fromStop);
        const toCoord = coords.get(toStop);
        
        if (!fromCoord || !toCoord) {
            currentSegment++;
            progress = 0;
            return;
        }
        
        progress += (delta / 2000) * speed;
        if (progress >= 1) {
            progress = 0;
            currentSegment++;
            busAnimationInterval = requestAnimationFrame(step);
            return;
        }
        
        const currentLat = fromCoord.lat + (toCoord.lat - fromCoord.lat) * progress;
        const currentLng = fromCoord.lng + (toCoord.lng - fromCoord.lng) * progress;
        
        busMarker.setLatLng([currentLat, currentLng]);

        if (busTrail) {
            const trail = busTrail.getLatLngs();
            trail.push([currentLat, currentLng]);
            if (trail.length > 200) trail.shift();
            busTrail.setLatLngs(trail);
        }
        
        const overallProgress = ((currentSegment + progress) / (path.length - 1)) * 100;
        setMsg(simMsg, `Bus: ${fromStop} → ${toStop} (${overallProgress.toFixed(0)}%)`);
        
        busAnimationInterval = requestAnimationFrame(step);
    };

    busAnimationInterval = requestAnimationFrame(step);
}

function clearRoute() {
    if (busAnimationInterval) {
        cancelAnimationFrame(busAnimationInterval);
        busAnimationInterval = null;
    }
    
    if (busMarker) {
        busMarker.remove();
        busMarker = null;
    }

    if (busTrail) {
        busTrail.remove();
        busTrail = null;
    }
    
    path = [];
    settledOrder = [];
    totalDistance = null;
    
    updateStopIcons();
    renderEdges();
    routePill.textContent = "Path: Not Selected";
    
    setMsg(simMsg, "Route cleared");
    setKpis({
        distance: null,
        stops: GRAPH.nodes.length,
        connections: GRAPH.edges.length,
        status: "🟢 Idle"
    });
}

// ===================== MAP CONTROLS =====================
function fitBoundsToStops() {
    if (!map || !GRAPH.nodes || GRAPH.nodes.length === 0) return;
    
    const coordsArray = [];
    GRAPH.nodes.forEach(stopName => {
        const coord = coords.get(stopName);
        if (coord && coord.lat && coord.lng) {
            coordsArray.push([coord.lat, coord.lng]);
        }
    });
    
    if (coordsArray.length > 0) {
        const bounds = L.latLngBounds(coordsArray);
        map.fitBounds(bounds.pad(0.3));
        console.log('Fitted bounds to stops');
    }
}

// ===================== EVENT HANDLERS =====================
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    computeBtn.addEventListener('click', computeRoute);
    
    swapBtn.addEventListener('click', () => {
        const temp = startSelect.value;
        startSelect.value = endSelect.value;
        endSelect.value = temp;
        updateStopIcons();
        setMsg(simMsg, "Swapped start and destination");
    });
    
    playBtn.addEventListener('click', () => {
        isPaused = false;
        pauseBtn.textContent = "⏸️ Pause";
        setMsg(simMsg, "Resumed animation");
        setKpis({
            distance: totalDistance,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🟢 Running"
        });
    });
    
    pauseBtn.addEventListener('click', () => {
        isPaused = !isPaused;
        pauseBtn.textContent = isPaused ? "▶️ Resume" : "⏸️ Pause";
        setMsg(simMsg, isPaused ? "Paused animation" : "Resumed animation");
    });
    
    stopBtn.addEventListener('click', () => {
        isPaused = false;
        clearRoute();
        setMsg(simMsg, "Stopped animation");
    });
    
    clearRouteBtn.addEventListener('click', clearRoute);
    
    // Toggle handlers
    tGrid.addEventListener('change', renderEdges);
    tWeights.addEventListener('change', renderEdges);
    tLabels.addEventListener('change', updateStopIcons);
    tExplored.addEventListener('change', updateStopIcons);
    
    tSatellite.addEventListener('change', function() {
        if (this.checked) {
            map.removeLayer(currentTileLayer);
            currentTileLayer = satelliteLayer;
            satelliteLayer.addTo(map);
        } else {
            map.removeLayer(currentTileLayer);
            currentTileLayer = tileLayer;
            tileLayer.addTo(map);
        }
    });
    
    // Speed control
    speedSlider.addEventListener('input', function() {
        speedValue.textContent = `${this.value}x`;
    });
    
    // Search functionality
    searchStop.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        let firstMatch = null;

        if (!query) {
            stopMarkers.forEach(marker => {
                if (marker) {
                    marker.setOpacity(1);
                    const tooltip = marker.getTooltip();
                    if (tooltip && tLabels.checked) {
                        tooltip.setOpacity(0.9);
                    }
                }
            });
            return;
        }
        
        stopMarkers.forEach((marker, stopName) => {
            if (!marker) return;
            
            if (stopName.toLowerCase().includes(query)) {
                if (!firstMatch) firstMatch = stopName;
                marker.setOpacity(1);
                marker.bringToFront();
                
                const tooltip = marker.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0.9);
                }
            } else {
                marker.setOpacity(0.3);
                const tooltip = marker.getTooltip();
                if (tooltip) {
                    tooltip.setOpacity(0);
                }
            }
        });

        if (firstMatch) {
            const coord = coords.get(firstMatch);
            if (coord) {
                map.setView([coord.lat, coord.lng], Math.max(map.getZoom(), 14), { animate: true });
            }
        }
    });

    searchStop.addEventListener('keydown', function(event) {
        if (event.key !== 'Enter') return;
        const query = this.value.toLowerCase().trim();
        if (!query) return;
        const match = GRAPH.nodes.find((name) => name.toLowerCase().includes(query));
        if (match) {
            if (!startSelect.value) {
                startSelect.value = match;
            } else if (!endSelect.value) {
                endSelect.value = match;
            } else {
                endSelect.value = match;
            }
            updateStopIcons();
        }
    });
    
    // Map zoom controls
    zoomInBtn.addEventListener('click', () => {
        map.zoomIn();
    });
    
    zoomOutBtn.addEventListener('click', () => {
        map.zoomOut();
    });
    
    fitBoundsBtn.addEventListener('click', () => {
        fitBoundsToStops();
    });
    
    // Layout management
    resetLayoutBtn.addEventListener('click', () => {
        coordsBase.forEach((coord, stopName) => {
            coords.set(stopName, { ...coord });
        });
        
        renderStops();
        renderEdges();
        setMsg(simMsg, "Reset all stops to original positions");
    });
    
    saveLayoutBtn.addEventListener('click', () => {
        coords.forEach((coord, stopName) => {
            coordsBase.set(stopName, { ...coord });
        });
        
        setMsg(simMsg, "Saved current layout as default");
    });
    
    // FIXED AUTO-CONNECT BUTTON
    autoConnectBtn.addEventListener('click', function() {
        setMsg(simMsg, "Auto-connecting nearby stops...");
        
        const newEdges = [];
        const edgeSet = new Set();
        
        GRAPH.edges.forEach(edge => {
            const key = `${edge.from}-${edge.to}`;
            edgeSet.add(key);
        });
        
        GRAPH.nodes.forEach(fromStop => {
            GRAPH.nodes.forEach(toStop => {
                if (fromStop === toStop) return;
                
                const edgeKey = `${fromStop}-${toStop}`;
                const reverseKey = `${toStop}-${fromStop}`;
                
                if (edgeSet.has(edgeKey) || edgeSet.has(reverseKey)) return;
                
                const fromCoord = coords.get(fromStop);
                const toCoord = coords.get(toStop);
                
                if (!fromCoord || !toCoord) return;
                
                const distance = calculateDistance(
                    fromCoord.lat, fromCoord.lng,
                    toCoord.lat, toCoord.lng
                );
                
                if (distance < 0.8) {
                    newEdges.push({
                        from: fromStop,
                        to: toStop,
                        w: distance
                    });
                    
                    edgeSet.add(edgeKey);
                    console.log(`Auto-connected: ${fromStop} ↔ ${toStop} (${distance.toFixed(2)} km)`);
                }
            });
        });
        
        GRAPH.edges.push(...newEdges);
        
        netPill.textContent = `Network: ${GRAPH.nodes.length} stops · ${GRAPH.edges.length} routes`;
        renderEdges();
        
        setMsg(simMsg, `Added ${newEdges.length} new connections`);
        setKpis({
            distance: totalDistance,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🟢 Updated"
        });
    });
    
    
    document.addEventListener('keydown', function(event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            computeRoute();
        }
        
        if (event.key === ' ' && !event.target.matches('input, textarea, select')) {
            event.preventDefault();
            if (busAnimationInterval) {
                isPaused = !isPaused;
                pauseBtn.textContent = isPaused ? "▶️ Resume" : "⏸️ Pause";
                setMsg(simMsg, isPaused ? "Paused animation" : "Resumed animation");
            }
        }
    });
    
    console.log('Event listeners setup complete');
}

// ===================== INITIALIZATION =====================
async function initializeSimulation() {
    console.log('Initializing simulation...');
    
    try {
        if (hasInitialized) {
            console.warn('Simulation already initialized');
            return;
        }
        hasInitialized = true;
        initializeDOMReferences();
        initMap();
        setupEventListeners();
        await loadSimulationData();
        
        speedValue.textContent = `${speedSlider.value}x`;
        zoomLevel.textContent = map.getZoom();
        
        setKpis({
            distance: null,
            stops: GRAPH.nodes.length,
            connections: GRAPH.edges.length,
            status: "🟢 Ready"
        });
        
        setMsg(simMsg, "Simulation ready. Select stops and compute route.");
        
        console.log('Simulation initialized successfully');
        
    } catch (error) {
        console.error('Initialization error:', error);
        setMsg(simMsg, `Initialization error: ${error.message}`, true);
        
        createStableTestData();
        setMsg(simMsg, "Using test data. Add your own stops or wait for server.");
    }
}

// ===================== START SIMULATION =====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, starting simulation...');
    setTimeout(initializeSimulation, 100);
});

window.initSimulation = initializeSimulation;

window.initSimulation = initializeSimulation;

// Export for debugging
window.simulation = {
    GRAPH,
    coords,
    coordsBase,
    ROUTES,
    stopMarkers,
    edgeLines,
    weightMarkers,
    path,
    settledOrder,
    totalDistance,
    renderStops,
    renderEdges,
    updateStopIcons,
    clearRoute,
    computeRoute,
    calculateDistance,
    fitBoundsToStops,
    initializeSimulation
};

console.log('Lahore Transit Simulation script loaded - Fixed Node Clustering Issue');
