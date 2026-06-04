// ── 6. ANIMATED PROGRESS BARS (shimmer + smooth width) ──
window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll(".progress-bar[data-target]").forEach(bar => {
        const target = bar.getAttribute('data-target');
        setTimeout(() => { bar.style.width = target + "%"; }, 300);
    });

    // ── 8. LIVE STEP COUNTER ANIMATION ──
    const el = document.getElementById('liveSteps');
    if (el && typeof totalSteps !== 'undefined') {
        let current = 0;
        const target = totalSteps;
        const duration = 2000;
        const step = target / (duration / 16);
        const timer = setInterval(() => {
            current = Math.min(current + step, target);
            el.textContent = Math.floor(current).toLocaleString();
            if (current >= target) clearInterval(timer);
        }, 16);
    }

    // ── 10. WEEKLY STEPS CHART ──
    const stepsCanvas = document.getElementById("stepsChart");
    if (stepsCanvas && typeof weeklySteps !== "undefined") {
        new Chart(stepsCanvas, {
            type: "line",
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: "Steps",
                    data: weeklySteps,
                    borderColor: "#00ffff",
                    backgroundColor: "rgba(0,255,255,0.12)",
                    fill: true,
                    tension: 0.45,
                    pointBackgroundColor: "#00ffff",
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 9
                }]
            },
            options: {
                responsive: true,
                animation: { duration: 1500, easing: 'easeOutQuart' },
                plugins: {
                    legend: { labels: { color: "rgba(255,255,255,.8)", font: { family: 'Poppins' } } }
                },
                scales: {
                    x: { ticks: { color: "rgba(255,255,255,.7)" }, grid: { color: "rgba(255,255,255,.06)" } },
                    y: { ticks: { color: "rgba(255,255,255,.7)" }, grid: { color: "rgba(255,255,255,.06)" }, beginAtZero: true }
                }
            }
        });
    }

    // ── 10. ACTIVITY BREAKDOWN DOUGHNUT ──
    const activityCanvas = document.getElementById("activityChart");
    if (activityCanvas && typeof typeLabels !== "undefined" && typeLabels.length > 0) {
        new Chart(activityCanvas, {
            type: "doughnut",
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeCounts,
                    backgroundColor: ["#00ff88","#00bfff","#c084fc","#ffaa00","#ff5555","#aa00ff","#ffdd00"],
                    borderColor: "rgba(255,255,255,.1)",
                    borderWidth: 2,
                    hoverBorderColor: "#fff",
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                cutout: '65%',
                animation: { duration: 1500, easing: 'easeOutQuart' },
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: "rgba(255,255,255,.8)", font: { family: 'Poppins' }, padding: 16 }
                    }
                }
            }
        });
    } else if (activityCanvas) {
        activityCanvas.parentElement.innerHTML += '<p style="text-align:center;opacity:.5;margin-top:10px">No activities yet — add some to see breakdown!</p>';
        activityCanvas.remove();
    }

    // ── 7. BUTTON GLOW (extra sparkle on click) ──
    document.querySelectorAll(".btn").forEach(btn => {
        btn.addEventListener('click', (e) => {
            const ripple = document.createElement('span');
            ripple.style.cssText = `
                position:absolute;border-radius:50%;background:rgba(255,255,255,.35);
                width:10px;height:10px;transform:scale(0);
                left:${e.offsetX - 5}px;top:${e.offsetY - 5}px;
                animation:rippleBtn .5s ease forwards;pointer-events:none;
            `;
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 500);
        });
    });
});

// Ripple keyframe injection
const style = document.createElement('style');
style.textContent = '@keyframes rippleBtn{to{transform:scale(25);opacity:0;}}';
document.head.appendChild(style);
