// RevDynamics - Main Controller (API Integration)
document.addEventListener("DOMContentLoaded", function() {
    initCharts();
    startLiveDataUpdates();
    initChatAssistant();
    animateStats();
    initDynoPage();
    // initPartsCatalog() called by page-specific script if needed
    // initVehicleSelect() called by vehicle-select.html after loadVehicles()
});

let realtimeChart, liveChart, dynoCurveChart;
let realtimeData = [];
let dynoRunning = false;
let dynoInterval = null;
let maxDataPoints = 30;
let currentVehicle = 'bmw-m3';

// Keep in sync with vehicleManager
window.addEventListener('vehicleChanged', function(e) {
    currentVehicle = e.detail.vehicleId;
});

function initCharts() {
    const ctx1 = document.getElementById("realtimeChart");
    if (ctx1) {
        realtimeChart = new Chart(ctx1.getContext("2d"), {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "RPM x1000",
                        data: [],
                        borderColor: "#2D89BA",
                        backgroundColor: "rgba(45, 137, 186, 0.1)",
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    },
                    {
                        label: "Speed (km/h)",
                        data: [],
                        borderColor: "#38BDF8",
                        backgroundColor: "rgba(56, 189, 248, 0.1)",
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: "#0F172A" } } },
                scales: {
                    x: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { color: "#64748B" } },
                    y: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { color: "#64748B" }, beginAtZero: true }
                }
            }
        });
    }

    const ctxLive = document.getElementById("liveChart");
    if (ctxLive) {
        window.liveChart = new Chart(ctxLive.getContext("2d"), {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    { label: "RPM (x1000)", data: [], borderColor: "#2D89BA", backgroundColor: "rgba(45, 137, 186, 0.2)", fill: true, tension: 0.4, pointRadius: 2 },
                    { label: "HP", data: [], borderColor: "#10B981", backgroundColor: "rgba(16, 185, 129, 0.2)", fill: true, tension: 0.4, pointRadius: 2 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { labels: { color: "#0F172A" } },
                    title: { display: true, text: "Live Metrics", color: "#0F172A" }
                },
                scales: {
                    x: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { color: "#64748B" } },
                    y: { 
                        grid: { color: "rgba(0,0,0,0.05)" }, 
                        ticks: { color: "#64748B" },
                        title: { display: true, text: "Value", color: "#64748B" }
                    }
                }
            }
        });
    }

    const ctxDynoCurve = document.getElementById("dynoCurveChart");
    if (ctxDynoCurve) {
        fetch(`/api/dyno-curve/${currentVehicle}`).then(r => r.json()).then(dynoData => {
            window.dynoCurveChart = new Chart(ctxDynoCurve.getContext("2d"), {
                type: "line",
                data: {
                    labels: dynoData.map(d => d.rpm),
                    datasets: [
                        { label: "Torque (Nm)", data: dynoData.map(d => d.torque), borderColor: "#10B981", backgroundColor: "rgba(16, 185, 129, 0.1)", fill: true, tension: 0.4, yAxisID: "y" },
                        { label: "Power (HP)", data: dynoData.map(d => d.horsepower), borderColor: "#2D89BA", backgroundColor: "rgba(45, 137, 186, 0.1)", fill: true, tension: 0.4, yAxisID: "y1" }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: "index", intersect: false },
                    plugins: { legend: { labels: { color: "#0F172A" } } },
                    scales: {
                        x: { title: { display: true, text: "RPM", color: "#64748B" }, grid: { color: "rgba(0,0,0,0.05)" }, ticks: { color: "#64748B" } },
                        y: { type: "linear", display: true, position: "left", title: { display: true, text: "Torque (Nm)", color: "#10B981" }, grid: { color: "rgba(0,0,0,0.05)" }, ticks: { color: "#10B981" } },
                        y1: { type: "linear", display: true, position: "right", title: { display: true, text: "Power (HP)", color: "#2D89BA" }, grid: { drawOnChartArea: false }, ticks: { color: "#2D89BA" } }
                    }
                }
            });
        });
    }
}

function startLiveDataUpdates() {
    setInterval(() => {
        fetch(`/api/obd-data/${currentVehicle}`).then(r => r.json()).then(data => {
            updateDashboard(data);
            if (dynoRunning) updateDynoChart(data);
        });
    }, 1000);
}

function updateDashboard(data) {
    const rpmVal = document.getElementById("rpm-value");
    const speedVal = document.getElementById("speed-value");
    const tempVal = document.getElementById("temp-value");
    
    if (rpmVal) rpmVal.textContent = (data.rpm / 1000).toFixed(1);
    if (speedVal) speedVal.textContent = Math.round(data.speed);
    if (tempVal) tempVal.textContent = Math.round(data.coolantTemp);

    const rpmDisplay = document.getElementById("rpm-display");
    const speedDisplay = document.getElementById("speed-display");
    const hpDisplay = document.getElementById("hp-display");
    const torqueDisplay = document.getElementById("torque-display");
    const tempDisplay = document.getElementById("temp-display");
    
    if (rpmDisplay) rpmDisplay.textContent = Math.round(data.rpm);
    if (speedDisplay) speedDisplay.textContent = Math.round(data.speed);
    if (hpDisplay) hpDisplay.textContent = Math.round(data.horsepower);
    if (torqueDisplay) torqueDisplay.textContent = Math.round(data.torque);
    if (tempDisplay) tempDisplay.textContent = Math.round(data.coolantTemp) + "°";

    const rpmBar = document.getElementById("rpm-bar");
    const speedBar = document.getElementById("speed-bar");
    const tempBar = document.getElementById("temp-bar");
    
    if (rpmBar) rpmBar.style.width = Math.min((data.rpm / 8000) * 100, 100) + "%";
    if (speedBar) speedBar.style.width = Math.min((data.speed / 200) * 100, 100) + "%";
    if (tempBar) tempBar.style.width = Math.min(((data.coolantTemp - 60) / 140) * 100, 100) + "%";
    if (tempBar) tempBar.className = "progress-bar " + (data.coolantTemp > 100 ? "bg-danger" : data.coolantTemp > 90 ? "bg-warning" : "bg-info");

    if (realtimeChart && realtimeChart.data) {
        const now = new Date().toLocaleTimeString();
        if (realtimeData.length >= maxDataPoints) {
            realtimeData.shift();
            realtimeChart.data.labels.shift();
            realtimeChart.data.datasets[0].data.shift();
            realtimeChart.data.datasets[1].data.shift();
        }
        realtimeData.push({ rpm: data.rpm / 1000, speed: data.speed });
        realtimeChart.data.labels.push(now);
        realtimeChart.data.datasets[0].data.push(data.rpm / 1000);
        realtimeChart.data.datasets[1].data.push(data.speed);
        realtimeChart.update("none");
    }

    if (window.liveChart && dynoRunning) {
        const now = new Date().toLocaleTimeString();
        if (window.liveChart.data.labels.length >= 50) {
            window.liveChart.data.labels.shift();
            window.liveChart.data.datasets[0].data.shift();
            window.liveChart.data.datasets[1].data.shift();
        }
        window.liveChart.data.labels.push(now);
        window.liveChart.data.datasets[0].data.push(data.horsepower);
        window.liveChart.data.datasets[1].data.push(data.torque);
        window.liveChart.update("none");
    }
}

function initDynoPage() {
    const startBtn = document.getElementById("start-dyno");
    const stopBtn = document.getElementById("stop-dyno");
    const simulateAccelBtn = document.getElementById("simulate-accel");
    
    if (startBtn) {
        startBtn.addEventListener("click", function() {
            startDynoRun();
            window.apiClient.startDyno(currentVehicle);
            if (document.getElementById("dyno-status")) {
                document.getElementById("dyno-status").textContent = "Running";
                document.getElementById("dyno-status").className = "badge bg-danger";
            }
            startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener("click", function() {
            stopDynoRun();
            window.apiClient.stopDyno(currentVehicle);
            if (document.getElementById("dyno-status")) {
                document.getElementById("dyno-status").textContent = "Ready";
                document.getElementById("dyno-status").className = "badge bg-success";
            }
            stopBtn.disabled = true;
            if (startBtn) startBtn.disabled = false;
        });
    }
    
    if (simulateAccelBtn) {
        simulateAccelBtn.addEventListener("click", function() {
            simulateAcceleration();
        });
    }
    
    const applyTuneBtn = document.getElementById("apply-tune");
    if (applyTuneBtn) {
        applyTuneBtn.addEventListener("click", function() {
            const tuneData = {
                vehicleId: currentVehicle,
                afr: parseFloat(document.getElementById("afr-slider")?.value || 12.5),
                timing: parseFloat(document.getElementById("timing-slider")?.value || 24),
                boost: parseFloat(document.getElementById("boost-slider")?.value || 14.5),
                knock: document.getElementById("knock-select")?.value || "standard"
            };
            window.apiClient.applyTune(tuneData).then(result => {
                if (result.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById("tuningModal"));
                    if (modal) modal.hide();
                    loadDynoCurve();
                    const badge = document.getElementById("dyno-status");
                    if (badge) {
                        badge.textContent = "Tune Applied";
                        badge.className = "badge bg-success";
                    }
                }
            }).catch(() => {
                const badge = document.getElementById("dyno-status");
                if (badge) badge.textContent = "Tune Failed";
            });
        });
    }
    
    const afrSlider = document.getElementById("fuel-trim");
    const timingSlider = document.getElementById("timing");
    const boostSlider = document.getElementById("boost");
    
    if (afrSlider) {
        afrSlider.addEventListener("input", () => {
            document.getElementById("fuel-trim-value").textContent = afrSlider.value + ":1";
            updateEstimatedGains();
        });
    }
    if (timingSlider) {
        timingSlider.addEventListener("input", () => {
            document.getElementById("timing-value").textContent = timingSlider.value + "°";
            updateEstimatedGains();
        });
    }
    if (boostSlider) {
        boostSlider.addEventListener("input", () => {
            document.getElementById("boost-value").textContent = boostSlider.value + " psi";
            updateEstimatedGains();
        });
    }
    
    // Hold RPM and Record Peak functionality for dyno controls
    let rpmLimit = 8000;
    let heldRpm = null;

    const holdRpmBtn = document.getElementById("hold-rpm");
    if (holdRpmBtn) {
        holdRpmBtn.addEventListener("click", function() {
            const currentRpm = parseInt(document.getElementById("rpm-display")?.textContent || "0");
            if (heldRpm === null) {
                heldRpm = currentRpm;
                this.innerHTML = "<i class='fas fa-play me-1'></i>Resume";
                this.className = "btn btn-outline-warning w-100 rounded-pill";
            } else {
                heldRpm = null;
                this.innerHTML = "<i class='fas fa-pause me-1'></i>Hold RPM";
                this.className = "btn btn-outline-success w-100 rounded-pill";
            }
        });
    }

    const recordPeakBtn = document.getElementById("record-peak");
    if (recordPeakBtn) {
        recordPeakBtn.addEventListener("click", function() {
            this.innerHTML = "<i class='fas fa-check me-1'></i>Peak Recorded";
            setTimeout(() => {
                recordPeakBtn.innerHTML = "<i class='fas fa-flag-checkered me-1'></i>Record Peak";
            }, 1500);
        });
    }

    const rpmLimitSlider = document.getElementById("rpm-limit");
    if (rpmLimitSlider) {
        rpmLimitSlider.addEventListener("input", function() {
            rpmLimit = parseInt(this.value);
            document.getElementById("rpm-limit-value").textContent = rpmLimit;
        });
    }
    
    document.querySelectorAll(".tune-preset").forEach(btn => {
        btn.addEventListener("click", function() {
            document.querySelectorAll(".tune-preset").forEach(b => b.classList.remove("active"));
            this.classList.add("active");
            const preset = this.dataset.preset;
            const presets = {
                daily: {afr: 14.7, timing: 15, boost: 8},
                street: {afr: 13.0, timing: 18, boost: 10},
                sport: {afr: 12.5, timing: 24, boost: 14.5},
                track: {afr: 12.0, timing: 32, boost: 18},
                race: {afr: 11.5, timing: 38, boost: 25}
            };
            const p = presets[preset];
            if (p) {
                if (afrSlider) afrSlider.value = p.afr;
                if (timingSlider) timingSlider.value = p.timing;
                if (boostSlider) boostSlider.value = p.boost;
                document.getElementById("fuel-trim-value").textContent = p.afr + ":1";
                document.getElementById("timing-value").textContent = p.timing + "°";
                document.getElementById("boost-value").textContent = p.boost + " psi";
                document.getElementById("preset-desc").textContent = getPresetDesc(preset);
            }
            updateEstimatedGains();
        });
    });
    
    // Load initial performance stats after a short delay
    setTimeout(loadDynoCurve, 500);
}

function loadDynoCurve() {
    window.apiClient.getDynoCurve(currentVehicle).then(curve => {
        const peakHp = Math.max(...curve.map(p => p.horsepower));
        const peakTq = Math.max(...curve.map(p => p.torque));
        const peakHpRpm = curve.find(p => p.horsepower === peakHp)?.rpm || 0;
        
        const peakHpEl = document.getElementById("peak-hp");
        const peakTqEl = document.getElementById("peak-torque");
        const peakRpmEl = document.getElementById("peak-rpm");
        const zero100El = document.getElementById("zero100");
        
        if (peakHpEl) peakHpEl.textContent = peakHp;
        if (peakTqEl) peakTqEl.textContent = peakTq;
        if (peakRpmEl) peakRpmEl.textContent = peakHpRpm;
        if (zero100El) zero100El.textContent = Math.max(2.5, 4.2 - peakHp / 100).toFixed(1);
        
        // Update chart with new curve
        if (window.dynoCurveChart) {
            window.dynoCurveChart.data = {
                labels: curve.map(p => p.rpm),
                datasets: [
                    { label: "Torque (Nm)", data: curve.map(p => p.torque), borderColor: "#10B981", backgroundColor: "rgba(16, 185, 129, 0.1)", fill: true, tension: 0.4, yAxisID: "y" },
                    { label: "Power (HP)", data: curve.map(p => p.horsepower), borderColor: "#2D89BA", backgroundColor: "rgba(45, 137, 186, 0.1)", fill: true, tension: 0.4, yAxisID: "y1" }
                ]
            };
            window.dynoCurveChart.update();
        }
    }).catch(() => {});
}

function updateEstimatedGains() {
    const afrSlider = document.getElementById("fuel-trim") || document.getElementById("afr-slider");
    const afr = parseFloat(afrSlider?.value || 12.5);
    const timingSlider = document.getElementById("timing") || document.getElementById("timing-slider");
    const timing = parseFloat(timingSlider?.value || 24);
    const boostSlider = document.getElementById("boost") || document.getElementById("boost-slider");
    const boost = parseFloat(boostSlider?.value || 14.5);
    
    const hpGain = Math.max(0, Math.round((boost - 10) * 3 + (12.5 - afr) * 2 + (timing - 20) * 0.5));
    const tqGain = Math.max(0, Math.round((boost - 10) * 5 + (12.5 - afr) * 3 + (timing - 20)));
    
    const hpEl = document.getElementById("est-hp-gain");
    const tqEl = document.getElementById("est-tq-gain");
    const boostEl = document.getElementById("est-boost");
    
    if (hpEl) hpEl.textContent = "+" + hpGain;
    if (tqEl) tqEl.textContent = "+" + tqGain;
    if (boostEl) boostEl.textContent = "+" + Math.round(boost - 10);
}

function getPresetDesc(preset) {
    const descriptions = {
        daily: "Conservative tune for optimal fuel economy and daily driving",
        street: "Mild performance increase with good reliability",
        sport: "Balanced power and fuel economy for spirited driving",
        track: "Aggressive tune for track use with increased cooling",
        race: "Maximum power tune - requires supporting modifications"
    };
    return descriptions[preset] || "";
}

function startDynoRun() {
    dynoRunning = true;
    if (window.dynoCurveChart) {
        window.dynoCurveChart.data.labels = [];
        window.dynoCurveChart.data.datasets[0].data = [];
        window.dynoCurveChart.data.datasets[1].data = [];
        window.dynoCurveChart.update();
    }
}

function stopDynoRun() {
    dynoRunning = false;
}

function simulateAcceleration() {
    window.apiClient.startDyno(currentVehicle);
    if (document.getElementById("dyno-status")) {
        document.getElementById("dyno-status").textContent = "Simulating";
        document.getElementById("dyno-status").className = "badge bg-info";
    }
    
    let simRpm = 1000;
    const interval = setInterval(() => {
        if (simRpm > 8000) {
            clearInterval(interval);
            window.apiClient.stopDyno(currentVehicle);
            if (document.getElementById("dyno-status")) {
                document.getElementById("dyno-status").textContent = "Ready";
                document.getElementById("dyno-status").className = "badge bg-success";
            }
            return;
        }
        
        const rpmRatio = simRpm / 8000;
        const boost = 25;
        const basePower = 503;
        const baseTorque = 550;
        
        const hp = Math.round(basePower * rpmRatio * 0.85 + boost * 5);
        const tq = simRpm > 4000 ? Math.round(baseTorque * (1 - (simRpm - 4000) / 8000 * 0.3)) : Math.round(baseTorque * (simRpm / 4000) * 0.7);
        
        if (window.dynoCurveChart) {
            window.dynoCurveChart.data.labels.push(simRpm);
            window.dynoCurveChart.data.datasets[0].data.push(tq);
            window.dynoCurveChart.data.datasets[1].data.push(hp);
            window.dynoCurveChart.update("none");
            
            const peakHpEl = document.getElementById("peak-hp");
            const peakTqEl = document.getElementById("peak-torque");
            if (peakHpEl && hp > parseInt(peakHpEl.textContent || "0")) {
                peakHpEl.textContent = hp;
            }
            if (peakTqEl && tq > parseInt(peakTqEl.textContent || "0")) {
                peakTqEl.textContent = tq;
            }
        }
        simRpm += 300;
    }, 100);
}

function updateDynoChart(data) {
    if (window.dynoCurveChart) {
        const rpm = data.rpm;
        if (rpm >= 1000 && rpm <= 8000) {
            window.dynoCurveChart.data.labels.push(rpm);
            window.dynoCurveChart.data.datasets[0].data.push(data.torque);
            window.dynoCurveChart.data.datasets[1].data.push(data.horsepower);
            window.dynoCurveChart.update("none");
            const peakHpEl = document.getElementById("peak-hp");
            const peakTqEl = document.getElementById("peak-torque");
            if (peakHpEl && data.horsepower > parseInt(peakHpEl.textContent || "0")) {
                peakHpEl.textContent = Math.round(data.horsepower);
            }
            if (peakTqEl && data.torque > parseInt(peakTqEl.textContent || "0")) {
                peakTqEl.textContent = Math.round(data.torque);
            }
        }
    }
}

function animateStats() {
    const stats = [
        { id: "accuracy-stat", target: 98.2, suffix: "%" },
        { id: "time-stat", target: -65, suffix: "%" },
        { id: "power-stat", target: 22, suffix: "%" }
    ];
    
    stats.forEach(stat => {
        const element = document.getElementById(stat.id);
        if (element) animateNumber(element, 0, stat.target, 2000, stat.suffix);
    });
}

function animateNumber(element, start, end, duration, suffix = "") {
    const startTime = performance.now();
    const isNegative = end < 0;
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeOut;
        element.textContent = (isNegative ? "-" : "+") + Math.abs(current).toFixed(1) + suffix;
        if (progress < 1) requestAnimationFrame(update);
    }
    
    requestAnimationFrame(update);
}

function initChatAssistant() {
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.querySelector(".scrollable-chat");
    
    if (chatInput && chatMessages) {
        chatInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter" && this.value.trim()) {
                const userMessage = this.value.trim();
                addChatMessage(userMessage, "user");
                this.value = "";
                
                addChatMessage("Thinking...", "bot");
                window.apiClient.chat(userMessage).then(result => {
                    const botMessages = document.querySelectorAll(".chat-message.bot");
                    if (botMessages.length > 0) botMessages[botMessages.length - 1].remove();
                    addChatMessage(result.response, "bot");
                }).catch(() => {
                    const botMessages = document.querySelectorAll(".chat-message.bot");
                    if (botMessages.length > 0) botMessages[botMessages.length - 1].remove();
                    addChatMessage("Sorry, I couldn't process that request.", "bot");
                });
            }
        });
    }
}

function addChatMessage(message, sender) {
    const chatMessages = document.querySelector(".scrollable-chat");
    if (!chatMessages) return;
    
    const messageDiv = document.createElement("div");
    messageDiv.className = "chat-message " + sender;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv;
}

function initVehicleSelect() {
    const vehicleSearch = document.getElementById("vehicle-search");
    if (!vehicleSearch) return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const returnPage = urlParams.get('return') || 'dyno-tune.html';
    const returnTab = urlParams.get('tab') || '';

    document.querySelectorAll(".vehicle-card").forEach(card => {
        card.addEventListener("click", function() {
            const vehicle = this.dataset.vehicle;
            if (window.vehicleManager) window.vehicleManager.setVehicle(vehicle);
            let targetUrl = returnPage + "?vehicle=" + vehicle;
            if (returnTab) {
                targetUrl += "&tab=" + returnTab;
            }
            window.location.href = targetUrl;
        });
    });

    const searchInput = document.getElementById("vehicle-search");
    const searchButton = document.getElementById("vehicle-search-btn");

    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const searchTerm = this.value.toLowerCase().trim();
            document.querySelectorAll(".vehicle-card").forEach(card => {
                const vehicleId = card.dataset.vehicle;
                const vehicleName = card.querySelector("h6")?.textContent.toLowerCase() || "";
                const vehicleDetails = card.querySelector("small")?.textContent.toLowerCase() || "";
                const match = vehicleId.includes(searchTerm) || vehicleName.includes(searchTerm) || vehicleDetails.includes(searchTerm);
                const col = card.closest(".col-lg-3");
                if (col) col.style.display = match ? "block" : "none";
            });
        });
    }

    if (searchButton) {
        searchButton.addEventListener("click", function() {
            const searchInput = document.getElementById("vehicle-search");
            if (searchInput) searchInput.dispatchEvent(new Event("input"));
        });
    }
}

window.generateAIPlan = function() {
    const goal = document.querySelector('input[name="goal"]:checked')?.value || "daily";
    const maxBudget = parseInt(document.getElementById("budget-slider")?.value) || 5000;
    
    window.apiClient.getRecommendations({
        vehicleId: currentVehicle,
        goal: goal,
        maxBudget: maxBudget
    }).then(renderAIPlan);
};

function renderAIPlan(analysis) {
    const container = document.getElementById("ai-recommendations");
    if (!container) return;
    
    container.innerHTML = `
        <div class="border rounded-3 p-3 bg-light">
            <div class="d-flex justify-content-between mb-2">
                <strong>Build Summary</strong>
                <span class="text-primary">+${analysis.totalPowerGain || 0} HP</span>
            </div>
            <p class="small text-muted mb-2">Estimated cost: $${analysis.totalCost?.toLocaleString() || 0}</p>
            <p class="small text-muted">0-60: ${analysis.estimated0_60 || "N/A"}s</p>
            <hr>
            <strong>Recommended Parts:</strong>
            ${(analysis.recommendations || []).map(p => `<div class="small mt-1">• ${p.name} (+${p.powerGain} HP)</div>`).join("")}
        </div>
    `;
}

window.runDynoTest = function() {};