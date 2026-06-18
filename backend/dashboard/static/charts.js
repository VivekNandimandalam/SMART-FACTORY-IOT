const SENSOR_CONFIG = {
    VIB_001: { label: "Vibration", valueId: "vib-value", metaId: "vib-meta", chartId: "vib-chart", color: "#56d4ff" },
    TEMP_001: { label: "Temperature", valueId: "temp-value", metaId: "temp-meta", chartId: "temp-chart", color: "#ff8fab" },
    PRES_001: { label: "Pressure", valueId: "pres-value", metaId: "pres-meta", chartId: "pres-chart", color: "#49e58d" },
    HUM_001: { label: "Humidity", valueId: "hum-value", metaId: "hum-meta", chartId: "hum-chart", color: "#9bdbff" },
    PWR_001: { label: "Power", valueId: "pwr-value", metaId: "pwr-meta", chartId: "pwr-chart", color: "#ffd166" },
};

const histories = {};
const charts = {};

function createChart(canvasId, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    return new Chart(canvas, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label,
                data: [],
                borderColor: color,
                backgroundColor: `${color}22`,
                fill: true,
                tension: 0.35,
                pointRadius: 0,
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 400 },
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8", maxTicksLimit: 4 }, grid: { color: "rgba(148, 163, 184, 0.1)" } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148, 163, 184, 0.1)" } },
            },
        },
    });
}

function createOverviewChart() {
    const canvas = document.getElementById("overview-chart");
    if (!canvas) return null;

    return new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["Vibration", "Temperature", "Pressure", "Humidity", "Power"],
            datasets: [{
                label: "Latest readings",
                data: [0, 0, 0, 0, 0],
                borderWidth: 0,
                backgroundColor: ["#56d4ff", "#ff8fab", "#49e58d", "#9bdbff", "#ffd166"],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148, 163, 184, 0.1)" } },
            },
        },
    });
}

function ensureChart(sensorId) {
    if (!charts[sensorId]) {
        const config = SENSOR_CONFIG[sensorId];
        charts[sensorId] = createChart(config.chartId, config.label, config.color);
        histories[sensorId] = [];
    }
    return charts[sensorId];
}

function updateSensorCard(sensorId, reading) {
    const config = SENSOR_CONFIG[sensorId];
    const valueElement = document.getElementById(config.valueId);
    const metaElement = document.getElementById(config.metaId);
    if (!valueElement || !metaElement || !reading) return;

    valueElement.textContent = `${reading.value} ${reading.unit}`;
    valueElement.className = `metric ${reading.anomaly ? "warn" : "neutral"}`;
    metaElement.textContent = reading.timestamp ? `Updated ${new Date(reading.timestamp).toLocaleTimeString()}` : "Updated recently";

    const chart = ensureChart(sensorId);
    if (!chart) return;

    histories[sensorId].push(reading);
    histories[sensorId] = histories[sensorId].slice(-20);

    chart.data.labels = histories[sensorId].map((_, index) => index + 1);
    chart.data.datasets[0].data = histories[sensorId].map((item) => item.value);
    chart.update("none");
}

function updateOverviewChart(latestBySensor) {
    if (!window.overviewChart) {
        window.overviewChart = createOverviewChart();
    }
    if (!window.overviewChart) return;

    const values = ["VIB_001", "TEMP_001", "PRES_001", "HUM_001", "PWR_001"].map((sensorId) => {
        const reading = latestBySensor[sensorId];
        return reading ? reading.value : 0;
    });

    window.overviewChart.data.datasets[0].data = values;
    window.overviewChart.update("none");
}

function renderAlerts(alerts) {
    const container = document.getElementById("alerts-list");
    if (!container) return;

    if (!alerts || !alerts.length) {
        container.innerHTML = '<div class="meta">No active alerts.</div>';
        return;
    }

    container.innerHTML = alerts.slice(0, 8).map((alert) => `
        <div class="alert">
            <strong>${alert.sensor_id || "Unknown sensor"}</strong> - ${alert.alert || "Alert"}
            <small>${alert.timestamp || "Recent event"}</small>
        </div>
    `).join("");
}

async function refreshDashboard() {
    try {
        const latestResponse = await fetch("/api/latest");
        const latestData = await latestResponse.json();
        updateOverviewChart(latestData);

        Object.entries(SENSOR_CONFIG).forEach(([sensorId]) => {
            if (latestData[sensorId]) {
                updateSensorCard(sensorId, latestData[sensorId]);
            }
        });

        const alertsResponse = await fetch("/api/alerts");
        const alertsData = await alertsResponse.json();
        renderAlerts(Array.isArray(alertsData) ? alertsData : []);
    } catch (error) {
        console.error("Dashboard refresh failed", error);
    }
}

Object.entries(SENSOR_CONFIG).forEach(([sensorId, config]) => {
    charts[sensorId] = createChart(config.chartId, config.label, config.color);
    histories[sensorId] = [];
});
window.overviewChart = createOverviewChart();

refreshDashboard();
setInterval(refreshDashboard, 5000);
