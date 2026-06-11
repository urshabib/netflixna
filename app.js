// Point this to your live Cloudflare API deployment
const WORKER_URL = "https://portal-api.urshabib.workers.dev/";

let activeUser = "";
let activePass = "";
let countdownInterval = null;

// AUTO-LOGIN PATTERN (Runs on startup)
window.addEventListener('DOMContentLoaded', () => {
    const savedUser = localStorage.getItem('portal_user');
    const savedPass = localStorage.getItem('portal_pass');
    
    if (savedUser && savedPass) {
        document.getElementById('username').value = savedUser;
        document.getElementById('password').value = savedPass;
        handleLogin(true); // Silent bypass login
    }
});

async function handleLogin(isAuto = false) {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const btn = document.getElementById('loginBtn');

    if (!isAuto) {
        btn.innerText = "Signing In...";
        btn.disabled = true;
    }

    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: "login", username: user, password: pass })
        });

        const result = await response.json();

        if (result.success) {
            activeUser = user;
            activePass = pass;

            // Handle Local Session Cache Persistence
            if (document.getElementById('rememberMe').checked) {
                localStorage.setItem('portal_user', user);
                localStorage.setItem('portal_pass', pass);
            }

            // UI Interface Transitions
            document.getElementById('loginView').classList.add('hidden');
            document.getElementById('mainHeader').classList.remove('hidden');
            document.getElementById('userDashboard').classList.remove('hidden');
            document.getElementById('portalUser').innerText = activeUser;

            if (result.is_admin) {
                document.getElementById('adminPortalBtn').classList.remove('hidden');
            }

            // Evaluate if user is currently locked by a 24-Hour Cooldown restriction
            if (result.last_claimed_at && result.has_limit) {
                evaluateCooldown(result.last_claimed_at);
            }
        } else {
            if (!isAuto) alert("Sign In Failed: " + result.message);
            handleLogout();
        }
    } catch (error) {
        if (!isAuto) alert("Network failure connecting to remote security array.");
        handleLogout();
    } finally {
        btn.innerText = "Sign In";
        btn.disabled = false;
    }
}

function handleLogout() {
    localStorage.removeItem('portal_user');
    localStorage.removeItem('portal_pass');
    activeUser = "";
    activePass = "";
    clearInterval(countdownInterval);
    
    document.getElementById('mainHeader').classList.add('hidden');
    document.getElementById('userDashboard').classList.add('hidden');
    document.getElementById('adminDashboard').classList.add('hidden');
    document.getElementById('loginView').classList.remove('hidden');
    document.getElementById('password').value = "";
}

function evaluateCooldown(lastClaimedIso) {
    const claimBtn = document.getElementById('claimBtn');
    const countdownBox = document.getElementById('countdownBox');
    const clock = document.getElementById('timerClock');

    clearInterval(countdownInterval);

    const lastClaimTime = new Date(lastClaimedIso).getTime();
    const lockDuration = 24 * 60 * 60 * 1000; // 24 Hours in Milliseconds

    countdownInterval = setInterval(() => {
        const now = new Date().getTime();
        const timeElapsed = now - lastClaimTime;
        const timeRemaining = lockDuration - timeElapsed;

        if (timeRemaining <= 0) {
            clearInterval(countdownInterval);
            claimBtn.disabled = false;
            countdownBox.classList.add('hidden');
        } else {
            claimBtn.disabled = true;
            countdownBox.classList.remove('hidden');
            
            // Format time delta to 00:00:00 structural display
            const hrs = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            clock.innerText = `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
    }, 1000);
}

async function claimLink() {
    const btn = document.getElementById('claimBtn');
    const loader = document.getElementById('loader');
    const resultBox = document.getElementById('linkResult');

    btn.classList.add('hidden');
    loader.classList.remove('hidden');
    resultBox.classList.add('hidden');

    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: "claim_link", username: activeUser, password: activePass })
        });

        const result = await response.json();

        if (result.success) {
            // Build the beautiful Success Card UI
            resultBox.innerHTML = `
                <span class="success-badge">✓ Account Provisioned</span>
                <div class="link-display" id="generatedLinkText">${result.url}</div>
                <div class="action-row">
                    <button class="btn-copy" onclick="copyToClipboard()">Copy Link</button>
                    <button class="btn-primary" onclick="window.open('${result.url}', '_blank')">Open Account</button>
                </div>
            `;
            
            resultBox.classList.remove('hidden');
            
            // If the user profile returned contains limitation tracking constraints, trigger lock
            if (result.last_claimed_at && result.has_limit) {
                evaluateCooldown(result.last_claimed_at);
            }
        } else {
            alert("Provision Error: " + result.message);
        }
    } catch (error) {
        alert("System request timed out.");
    } finally {
        loader.classList.add('hidden');
        if (!btn.disabled) btn.classList.remove('hidden');
    }
}

// --- ADMINISTRATIVE ROUTINES ---

async function switchView(viewId) {
    const uDash = document.getElementById('userDashboard');
    const aDash = document.getElementById('adminDashboard');

    if (viewId === 'adminDashboard') {
        uDash.classList.add('hidden');
        aDash.classList.remove('hidden');
        await loadAdminMetrics();
    } else {
        aDash.classList.add('hidden');
        uDash.classList.remove('hidden');
    }
}

async function loadAdminMetrics() {
    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: "admin_get_stats", username: activeUser, password: activePass })
        });
        const result = await response.json();

        if (result.success) {
            document.getElementById('rawCount').innerText = result.db2_count;
            
            const tbody = document.getElementById('userTableBody');
            tbody.innerHTML = "";

            result.users.forEach(user => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${user.username}</td>
                    <td>${user.is_admin ? 'Admin' : 'Standard User'}</td>
                    <td>${user.links_claimed || 0}</td>
                    <td>
                        ${user.is_admin ? 'Disabled' : `
                        <label class="switch">
                            <input type="checkbox" ${user.has_limit ? 'checked' : ''} onchange="toggleUserLimit('${user.username}', this.checked)">
                            <span class="slider"></span>
                        </label>
                        `}
                    </td>
                    <td>
                        ${user.is_admin ? '' : `
                        <button class="btn-secondary" style="padding: 6px 10px; font-size: 12px; margin-right: 5px;" onclick="resetUserTimer('${user.username}')">Reset Timer</button>
                        <button style="background-color: #dc2626; padding: 6px 10px; font-size: 12px;" onclick="deleteUser('${user.username}')">Delete</button>
                        `}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        alert("Failed to synchronize metric arrays.");
    }
}

async function toggleUserLimit(targetUser, limitStatus) {
    try {
        await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: "admin_toggle_limit",
                username: activeUser,
                password: activePass,
                target_user: targetUser,
                has_limit: limitStatus
            })
        });
    } catch (e) {
        alert("Failed to push configuration switch update to server.");
    }
}

function toggleModal(show) {
    const modal = document.getElementById('userModal');
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
}

async function submitNewUser() {
    const newUser = document.getElementById('newUsername').value;
    const newPass = document.getElementById('newPassword').value;
    const hasLimit = document.getElementById('newHasLimit').checked;

    if (!newUser || !newPass) return alert("Please fill out all user profile inputs.");

    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: "admin_create_user",
                username: activeUser,
                password: activePass,
                new_username: newUser,
                new_password: newPass,
                new_has_limit: hasLimit
            })
        });
        const result = await response.json();

        if (result.success) {
            toggleModal(false);
            await loadAdminMetrics(); // Refresh panel lists
            document.getElementById('newUsername').value = "";
            document.getElementById('newPassword').value = "";
        } else {
            alert("Creation Error: " + result.message);
        }
    } catch (e) {
        alert("Failed to commit new system user structure.");
    }
}

async function resetUserTimer(targetUser) {
    if (!confirm(`Clear the 24-hour waiting period for ${targetUser}?`)) return;
    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: "admin_reset_limit", username: activeUser, password: activePass, target_user: targetUser })
        });
        const result = await response.json();
        if (result.success) {
            alert(`Timer reset for ${targetUser}. They can claim a link immediately.`);
            await loadAdminMetrics(); // Refresh table
        } else alert("Error: " + result.message);
    } catch (e) { alert("Failed to contact server."); }
}

async function deleteUser(targetUser) {
    if (!confirm(`CRITICAL WARNING: Are you absolutely sure you want to completely delete ${targetUser}? This cannot be undone.`)) return;
    try {
        const response = await fetch(WORKER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: "admin_delete_user", username: activeUser, password: activePass, target_user: targetUser })
        });
        const result = await response.json();
        if (result.success) {
            await loadAdminMetrics(); // Refresh table
        } else alert("Error: " + result.message);
    } catch (e) { alert("Failed to contact server."); }
}

// --- UTILITY FUNCTIONS ---
function copyToClipboard() {
    const linkText = document.getElementById('generatedLinkText').innerText;
    navigator.clipboard.writeText(linkText).then(() => {
        // Change button text temporarily to show success
        const copyBtn = document.querySelector('.btn-copy');
        const originalText = copyBtn.innerText;
        copyBtn.innerText = "Copied! ✓";
        copyBtn.style.background = "#22c55e";
        copyBtn.style.borderColor = "#22c55e";
        
        setTimeout(() => {
            copyBtn.innerText = originalText;
            copyBtn.style.background = "#333";
            copyBtn.style.borderColor = "#555";
        }, 2000);
    }).catch(err => {
        alert("Failed to copy. Please select the text manually.");
    });
}
