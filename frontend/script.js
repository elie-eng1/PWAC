
const API_URL = "http://127.0.0.1:8000";

// Get HTML elements
const websiteInput = document.getElementById("websiteInput");
const addButton = document.getElementById("addButton");
const websiteList = document.getElementById("websiteList");

// Load website rules from backend

async function loadRules() {
    try {
        const response = await fetch(`${API_URL}/rules`);

        if (!response.ok) {
            throw new Error("Failed to load website rules");
        }

        const data = await response.json();
        const rules = data.website_rules;

        // Calculate statistics
        const total = rules.length;

        const blocked = rules.filter(
            rule => Number(rule[2]) === 1
        ).length;

        const allowed = rules.filter(
            rule => Number(rule[2]) === 0
        ).length;

        // Display statistics
        document.getElementById("totalCount").textContent = total;
        document.getElementById("blockedCount").textContent = blocked;
        document.getElementById("allowedCount").textContent = allowed;

        // Clear previous website list
        websiteList.innerHTML = "";

        if (rules.length === 0) {
            websiteList.textContent = "No website rules added yet.";
            return;
        }

        // Display each website
        rules.forEach(rule => {
            const [id, domain, isBlocked] = rule;

            const item = document.createElement("div");
            item.className = "website-item";

            const name = document.createElement("span");
            name.textContent = domain;

            const status = document.createElement("span");
            status.textContent = isBlocked ? "Blocked" : "Allowed";
            status.className = isBlocked ? "blocked" : "allowed";

            const toggleButton = document.createElement("button");
            toggleButton.textContent = isBlocked ? "Allow" : "Block";

            toggleButton.addEventListener("click", () => {
                updateRule(id, !Boolean(isBlocked));
            });

            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.className = "delete-button";

            deleteButton.addEventListener("click", () => {
                deleteRule(id);
            });

            item.append(name, status, toggleButton, deleteButton);
            websiteList.appendChild(item);
        });

    } catch (error) {
        websiteList.textContent = "Cannot connect to PWAC backend.";
        console.error(error);
    }
}


// Add a website

async function addWebsite() {
    let domain = websiteInput.value.trim().toLowerCase();

    // Remove protocol if entered
    domain = domain.replace(/^https?:\/\//, "");

    // Remove path after domain
    domain = domain.split(/[/?#]/)[0];

    // Validate domain format
    const domainPattern =
        /^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$/;

    if (!domainPattern.test(domain)) {
        alert("Please enter a valid domain, such as facebook.com");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/rules`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ domain })
        });

        const result = await response.json();

        if (!response.ok) {
            alert("Could not add website.");
            return;
        }

        alert(result.message);
        websiteInput.value = "";
        loadRules();

    } catch (error) {
        alert("Cannot connect to PWAC backend.");
        console.error(error);
    }
}

// Activate or deactivate a rule
async function updateRule(id, isBlocked) {
    try {
        const response = await fetch(
            `${API_URL}/rules/${id}?is_blocked=${isBlocked}`,
            { method: "PATCH" }
        );

        if (!response.ok) {
            alert("Could not update website rule.");
            return;
        }

        loadRules();

    } catch (error) {
        alert("Cannot update website rule.");
        console.error(error);
    }
}

// Delete a rule
async function deleteRule(id) {
    if (!confirm("Are you sure you want to delete this rule?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/rules/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            alert("Could not delete website rule.");
            return;
        }

        loadRules();

    } catch (error) {
        alert("Cannot delete website rule.");
        console.error(error);
    }
}

// Connect button to function
addButton.addEventListener("click", addWebsite);

// Load rules when dashboard opens
loadRules();
