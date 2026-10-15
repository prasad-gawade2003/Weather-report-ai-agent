/**
 * WeatherAI Agent - Interactive Client
 * Orchestrates FastMCP, FastAPI, LLM, and RAG UI
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Kolkata";
    const isIndiaTz = /kolkata|calcutta|india|ist/i.test(detectedTz);

    const state = {
        userLocation: isIndiaTz ? "Mumbai, India" : "Mumbai, India",
        userCity: "Mumbai",
        userCountry: "India",
        userTimezone: detectedTz,
        activeCity: "Mumbai", // Default localized to Mumbai
        llmProvider: localStorage.getItem("weather_llm_provider") || "auto",
        apiKey: localStorage.getItem("weather_api_key") || "",
        currentWeather: null,
        mcpTools: []
    };

    // DOM Elements - Main View
    const chatForm = document.getElementById("chatForm");
    const chatInput = document.getElementById("chatInput");
    const chatMessages = document.getElementById("chatMessages");
    const sendBtn = document.getElementById("sendBtn");
    const thoughtStreamContainer = document.getElementById("thoughtStreamContainer");
    const thoughtStreamSteps = document.getElementById("thoughtStreamSteps");
    
    // Quick search & Chips
    const quickCityInput = document.getElementById("quickCityInput");
    const quickCityBtn = document.getElementById("quickCityBtn");
    const cityChips = document.querySelectorAll(".chip");
    const scenarioBtns = document.querySelectorAll(".scenario-btn");

    // Floating POP Chatbot Elements
    const chatLauncherBtn = document.getElementById("chatLauncherBtn");
    const floatingChatWindow = document.getElementById("floatingChatWindow");
    const minimizeChatBtn = document.getElementById("minimizeChatBtn");
    const closeChatBtn = document.getElementById("closeChatBtn");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const changeLocBtn = document.getElementById("changeLocBtn");
    const floatLocBadge = document.getElementById("floatLocBadge");
    const floatLocText = document.getElementById("floatLocText");
    const launcherLocText = document.getElementById("launcherLocText");
    const detectedLocSpan = document.getElementById("detectedLocSpan");
    const floatChatForm = document.getElementById("floatChatForm");
    const floatChatInput = document.getElementById("floatChatInput");
    const floatSendBtn = document.getElementById("floatSendBtn");
    const floatChatMessages = document.getElementById("floatChatMessages");
    const floatThoughtStream = document.getElementById("floatThoughtStream");
    const floatThoughtSteps = document.getElementById("floatThoughtSteps");
    const floatQuickChips = document.querySelectorAll(".float-chip");

    // Weather Display Elements
    const displayCity = document.getElementById("displayCity");
    const displayCountry = document.getElementById("displayCountry");
    const displayTemp = document.getElementById("displayTemp");
    const displayFeels = document.getElementById("displayFeels");
    const displayWeatherIcon = document.getElementById("displayWeatherIcon");
    const displayCondition = document.getElementById("displayCondition");
    const displaySeverity = document.getElementById("displaySeverity");
    const displayWind = document.getElementById("displayWind");
    const displayHumidity = document.getElementById("displayHumidity");
    const displayUV = document.getElementById("displayUV");
    const displayAQI = document.getElementById("displayAQI");
    const forecastMiniList = document.getElementById("forecastMiniList");
    const weatherTimeLabel = document.getElementById("weatherTimeLabel");

    // Tabs
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    // RAG Explorer
    const ragSearchInput = document.getElementById("ragSearchInput");
    const ragSearchBtn = document.getElementById("ragSearchBtn");
    const ragSearchResults = document.getElementById("ragSearchResults");
    const ragDocumentsGrid = document.getElementById("ragDocumentsGrid");
    const ragDocCountBadge = document.getElementById("ragDocCountBadge");

    // MCP Sandbox
    const mcpToolSelect = document.getElementById("mcpToolSelect");
    const mcpToolArgsContainer = document.getElementById("mcpToolArgsContainer");
    const runMcpToolBtn = document.getElementById("runMcpToolBtn");
    const mcpOutputPre = document.getElementById("mcpOutputPre");
    const mcpLatencyTag = document.getElementById("mcpLatencyTag");

    // Modals
    const settingsModal = document.getElementById("settingsModal");
    const openSettingsBtn = document.getElementById("openSettingsBtn");
    const closeSettingsBtn = document.getElementById("closeSettingsBtn");
    const saveSettingsBtn = document.getElementById("saveSettingsBtn");
    const providerSelect = document.getElementById("providerSelect");
    const apiKeyInput = document.getElementById("apiKeyInput");

    const addDocModal = document.getElementById("addDocModal");
    const openAddDocBtn = document.getElementById("openAddDocBtn");
    const closeAddDocBtn = document.getElementById("closeAddDocBtn");
    const addDocForm = document.getElementById("addDocForm");

    // 1. Initial Load & Setup
    init();

    async function init() {
        providerSelect.value = state.llmProvider;
        apiKeyInput.value = state.apiKey;
        
        await detectUserLocation();
        await checkSystemStatus();
        await updateQuickWeather(state.activeCity);
        await loadRAGDocuments();
        setupMcpToolForm();
        setupFloatingChatbot();
    }

    // --- Tab Switching ---
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(targetTab)?.classList.add("active");
        });
    });

    // --- Quick Weather Lookup ---
    async function updateQuickWeather(city) {
        try {
            weatherTimeLabel.textContent = "Updating...";
            const resp = await fetch(`/api/weather/quick?city=${encodeURIComponent(city)}`);
            if (!resp.ok) throw new Error("Could not fetch city weather");
            const data = await resp.json();
            
            state.activeCity = data.city;
            displayCity.textContent = data.city;
            displayCountry.textContent = data.country || "";
            displayTemp.textContent = data.temperature?.toFixed(1) || "--";
            displayFeels.textContent = data.apparent_temperature?.toFixed(1) || "--";
            displayWeatherIcon.textContent = data.icon || "🌤️";
            displayCondition.textContent = data.condition || "Unknown";
            displayWind.textContent = `${data.wind_speed} km/h`;
            displayHumidity.textContent = `${data.humidity}%`;
            
            // Severity styling
            displaySeverity.textContent = data.severity || "normal";
            displaySeverity.className = `severity-pill ${data.severity || "normal"}`;
            
            weatherTimeLabel.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Fetch forecast & air quality to fill metrics
            loadForecastAndAirQuality(data.city);
        } catch (err) {
            weatherTimeLabel.textContent = "Offline/Error";
            console.error(err);
        }
    }

    async function loadForecastAndAirQuality(city) {
        try {
            // Forecast
            const fResp = await fetch(`/api/mcp/call`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tool_name: "get_weather_forecast", arguments: { city, days: 5 } })
            });
            if (fResp.ok) {
                const fData = await fResp.json();
                const forecast = fData.result?.forecast || [];
                renderForecastList(forecast);
            }

            // Air Quality
            const aResp = await fetch(`/api/mcp/call`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tool_name: "get_air_quality", arguments: { city } })
            });
            if (aResp.ok) {
                const aData = await aResp.json();
                const air = aData.result || {};
                displayAQI.textContent = `${air.us_aqi ?? '--'} (${air.health_level ?? 'Normal'})`;
                displayUV.textContent = `${air.uv_index ?? '--'} (${air.uv_category ?? 'Low'})`;
            }
        } catch (e) {
            console.error(e);
        }
    }

    function renderForecastList(forecast) {
        if (!forecast || forecast.length === 0) return;
        forecastMiniList.innerHTML = forecast.slice(0, 5).map(f => {
            const dateStr = new Date(f.date).toLocaleDateString([], { weekday: 'short', month: 'numeric', day: 'numeric' });
            return `
                <div class="forecast-item">
                    <span class="f-day">${dateStr}</span>
                    <span class="f-icon">${f.icon}</span>
                    <span class="f-temp">${Math.round(f.max_temp)}° / ${Math.round(f.min_temp)}°</span>
                </div>
            `;
        }).join("");
    }

    // Quick City Search Actions
    quickCityBtn.addEventListener("click", () => {
        const c = quickCityInput.value.trim();
        if (c) updateQuickWeather(c);
    });

    quickCityInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            const c = quickCityInput.value.trim();
            if (c) updateQuickWeather(c);
        }
    });

    cityChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const c = chip.getAttribute("data-city");
            if (c) {
                quickCityInput.value = c;
                updateQuickWeather(c);
            }
        });
    });

    // Scenario Template Buttons
    scenarioBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const p = btn.getAttribute("data-prompt");
            if (p) {
                chatInput.value = p;
                chatInput.focus();
                handleAgentChat(p);
            }
        });
    });

    // --- Location Auto-Detection ---
    async function detectUserLocation() {
        try {
            const resp = await fetch("/api/location/detect");
            if (resp.ok) {
                const data = await resp.json();
                if (data.city) {
                    state.userCity = data.city;
                    state.userLocation = `${data.city}, ${data.country || 'India'}`;
                    state.userTimezone = data.timezone || state.userTimezone;
                    state.activeCity = data.city;
                }
            }
        } catch (e) {
            console.log("Using default localized sector: Mumbai, India");
        }

        // Update UI badges
        if (launcherLocText) launcherLocText.textContent = `📍 ${state.userCity}`;
        if (floatLocText) floatLocText.textContent = `📍 ${state.userLocation} (Auto)`;
        if (detectedLocSpan) detectedLocSpan.textContent = state.userLocation;
    }

    // --- Floating POP Chatbot Controller ---
    function setupFloatingChatbot() {
        if (!chatLauncherBtn) return;

        // Toggle Floating Chat Window
        chatLauncherBtn.addEventListener("click", () => {
            const isHidden = floatingChatWindow.style.display === "none" || !floatingChatWindow.style.display;
            floatingChatWindow.style.display = isHidden ? "flex" : "none";
            if (isHidden) {
                floatChatInput.focus();
            }
        });

        // Close & Minimize
        minimizeChatBtn?.addEventListener("click", () => {
            floatingChatWindow.style.display = "none";
        });
        closeChatBtn?.addEventListener("click", () => {
            floatingChatWindow.style.display = "none";
        });

        // Clear Chat
        clearChatBtn?.addEventListener("click", () => {
            floatChatMessages.innerHTML = `
                <div class="chat-message bot-message">
                    <div class="message-avatar">🌪️</div>
                    <div class="message-content">
                        <p>Namaste! I'm your WeatherAI Agent. I've automatically resolved your sector to <strong>${escapeHtml(state.userLocation)}</strong>.</p>
                        <p>Ask me <em>"what is todays weather"</em> or tap any quick prompt chip above!</p>
                    </div>
                </div>
            `;
        });

        // Change Location Modal/Prompt
        function triggerChangeLocation() {
            const newLoc = prompt("Enter your city name (e.g. Mumbai, Delhi, Bengaluru, Pune, London):", state.userCity);
            if (newLoc && newLoc.trim()) {
                const city = newLoc.trim();
                state.userCity = city;
                state.userLocation = `${city}, India`;
                state.activeCity = city;

                if (launcherLocText) launcherLocText.textContent = `📍 ${city}`;
                if (floatLocText) floatLocText.textContent = `📍 ${city} (Custom)`;
                if (detectedLocSpan) detectedLocSpan.textContent = `${city}, India`;

                updateQuickWeather(city);
                appendChatMessage("bot", `📍 Your active location has been switched to **${city}**. Inquiring about "today's weather" will now analyze **${city}**!`, [], "WeatherAI Agent", "float");
            }
        }

        changeLocBtn?.addEventListener("click", triggerChangeLocation);
        floatLocBadge?.addEventListener("click", triggerChangeLocation);

        // Floating Chat Quick Chips
        floatQuickChips.forEach(chip => {
            chip.addEventListener("click", () => {
                const promptText = chip.getAttribute("data-prompt");
                if (promptText) {
                    floatChatInput.value = promptText;
                    handleAgentChat(promptText, "float");
                }
            });
        });

        // Floating Form Submit
        floatChatForm?.addEventListener("submit", (e) => {
            e.preventDefault();
            const msg = floatChatInput.value.trim();
            if (!msg) return;
            handleAgentChat(msg, "float");
        });
    }

    // --- 2. AGENT CHAT & SSE STREAMING (Dual Mode: Main & Floating) ---
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;
        handleAgentChat(msg, "main");
    });

    async function handleAgentChat(message, target = "main") {
        const isFloat = target === "float";
        
        // Append User Message to UI
        appendChatMessage("user", message, [], "", target);
        
        if (isFloat) {
            floatChatInput.value = "";
            floatSendBtn.disabled = true;
            floatThoughtStream.style.display = "block";
            floatThoughtSteps.innerHTML = "";
            addThoughtStep("thought", "Analyzing Query", "Detecting localized entities & weather intent...", target);
        } else {
            chatInput.value = "";
            sendBtn.disabled = true;
            thoughtStreamContainer.style.display = "block";
            thoughtStreamSteps.innerHTML = "";
            addThoughtStep("thought", "Initializing Agent", "Parsing intent and extracting meteorological entities...", target);
        }

        try {
            // Initiate Server-Sent Events (SSE) Stream
            const response = await fetch("/api/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: message,
                    user_location: state.userLocation,
                    user_timezone: state.userTimezone,
                    llm_provider: state.llmProvider,
                    api_key: state.apiKey
                })
            });

            if (!response.ok) throw new Error("Agent stream request failed");

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n\n");
                buffer = lines.pop(); // keep last unfinished piece

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const raw = line.slice(6).trim();
                        if (!raw) continue;
                        try {
                            const payload = JSON.parse(raw);
                            handleStreamEvent(payload, target);
                        } catch (err) {
                            console.error("Parse SSE error:", err, raw);
                        }
                    }
                }
            }
        } catch (err) {
            console.error("Chat error:", err);
            addThoughtStep("error", "Error", err.message, target);
            appendChatMessage("bot", `⚠️ **Agent Error**: Failed to complete weather intelligence query (${err.message}).`, [], "", target);
        } finally {
            if (isFloat) {
                floatSendBtn.disabled = false;
            } else {
                sendBtn.disabled = false;
            }
        }
    }

    function handleStreamEvent(payload, target = "main") {
        const isFloat = target === "float";
        if (payload.event === "trace") {
            const icons = {
                thought: "🧠",
                rag_retrieval: "📚",
                tool_call: "⚡",
                tool_result: "📊",
                summary: "✨"
            };
            const icon = icons[payload.step_type] || "🔹";
            addThoughtStep(payload.step_type, `${icon} ${payload.title}`, payload.detail, target);
        } else if (payload.event === "complete") {
            const data = payload.data;
            // Update sidebar live weather if agent detected city
            if (data.city_detected && data.city_detected !== state.activeCity) {
                updateQuickWeather(data.city_detected);
            }
            // Append formatted markdown response
            appendChatMessage("bot", data.response, data.rag_sources, data.model_used, target);
            
            // Hide thought stream after a few seconds
            setTimeout(() => {
                if (isFloat) {
                    floatThoughtStream.style.display = "none";
                } else {
                    thoughtStreamContainer.style.display = "none";
                }
            }, 3000);
        } else if (payload.event === "error") {
            appendChatMessage("bot", `⚠️ **Execution Error**: ${payload.message}`, [], "", target);
        }
    }

    function addThoughtStep(type, title, desc, target = "main") {
        const item = document.createElement("div");
        item.className = "thought-step-item";
        item.innerHTML = `
            <span class="thought-step-title">${escapeHtml(title)}:</span>
            <span class="thought-step-desc">${escapeHtml(desc)}</span>
        `;
        
        if (target === "float") {
            floatThoughtSteps.appendChild(item);
            floatThoughtSteps.scrollTop = floatThoughtSteps.scrollHeight;
        } else {
            thoughtStreamSteps.appendChild(item);
            thoughtStreamSteps.scrollTop = thoughtStreamSteps.scrollHeight;
        }
    }

    function appendChatMessage(sender, content, ragSources = [], modelUsed = "", target = "main") {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${sender}-message`;

        const avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = sender === "user" ? "👤" : "🌪️";

        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";

        if (sender === "user") {
            contentDiv.textContent = content;
        } else {
            // Render markdown
            const renderedHtml = marked.parse(content);
            contentDiv.innerHTML = renderedHtml;

            // Sources footer badge if RAG was used
            if (ragSources && ragSources.length > 0) {
                const footer = document.createElement("div");
                footer.style.marginTop = "0.85rem";
                footer.style.paddingTop = "0.6rem";
                footer.style.borderTop = "1px solid var(--border-glass)";
                footer.style.fontSize = "0.75rem";
                footer.style.color = "var(--text-muted)";
                
                const sourcesBadges = ragSources.map(s => 
                    `<span class="chip" style="margin-right: 0.3rem;">📖 ${escapeHtml(s.title)} (${Math.round(s.score*100)}%)</span>`
                ).join("");

                footer.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                        <div>${sourcesBadges}</div>
                        <span>⚡ ${escapeHtml(modelUsed || "WeatherAI Engine")}</span>
                    </div>
                `;
                contentDiv.appendChild(footer);
            }
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(contentDiv);

        if (target === "float") {
            floatChatMessages.appendChild(msgDiv);
            floatChatMessages.scrollTop = floatChatMessages.scrollHeight;
        } else {
            chatMessages.appendChild(msgDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // --- 3. RAG EXPLORER ---
    async function loadRAGDocuments() {
        try {
            const resp = await fetch("/api/rag/documents");
            if (!resp.ok) return;
            const docs = await resp.json();
            
            ragDocCountBadge.textContent = `${docs.length} Rules`;
            renderRAGDocuments(docs);
        } catch (e) {
            console.error("Error loading RAG documents:", e);
        }
    }

    function renderRAGDocuments(docs) {
        ragDocumentsGrid.innerHTML = docs.map(doc => `
            <div class="glass-card doc-card">
                <div class="doc-card-header">
                    <h3 class="doc-title">${escapeHtml(doc.title)}</h3>
                    <span class="doc-category-tag">${escapeHtml(doc.category)}</span>
                </div>
                <p class="doc-content">${escapeHtml(doc.content)}</p>
                <div class="doc-tags">
                    ${(doc.tags || []).map(t => `<span class="doc-tag">#${escapeHtml(t)}</span>`).join("")}
                </div>
            </div>
        `).join("");
    }

    ragSearchBtn.addEventListener("click", async () => {
        const query = ragSearchInput.value.trim();
        if (!query) return;
        
        try {
            ragSearchResults.style.display = "flex";
            ragSearchResults.innerHTML = "<p style='color: var(--text-muted)'>Searching vector index...</p>";
            
            const resp = await fetch("/api/rag/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, top_k: 4 })
            });
            const data = await resp.json();
            
            if (!data.results || data.results.length === 0) {
                ragSearchResults.innerHTML = "<p style='color: var(--accent-storm)'>No matching meteorological advisories found above threshold.</p>";
                return;
            }

            ragSearchResults.innerHTML = data.results.map(r => `
                <div class="rag-res-item">
                    <div class="rag-res-header">
                        <span class="rag-res-title">${escapeHtml(r.title)}</span>
                        <span class="rag-res-score">Match Score: ${Math.round(r.score * 100)}%</span>
                    </div>
                    <p class="rag-res-snippet">${escapeHtml(r.snippet)}</p>
                </div>
            `).join("");
        } catch (err) {
            ragSearchResults.innerHTML = `<p style='color: var(--accent-storm)'>Search failed: ${err.message}</p>`;
        }
    });

    // Ingest custom RAG doc
    openAddDocBtn.addEventListener("click", () => addDocModal.style.display = "flex");
    closeAddDocBtn.addEventListener("click", () => addDocModal.style.display = "none");
    addDocForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const title = document.getElementById("docTitleInput").value.trim();
        const category = document.getElementById("docCategorySelect").value;
        const tags = document.getElementById("docTagsInput").value.split(",").map(t => t.trim()).filter(Boolean);
        const content = document.getElementById("docContentInput").value.trim();

        try {
            const resp = await fetch("/api/rag/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: `doc-${Date.now()}`, title, category, tags, content })
            });
            if (resp.ok) {
                addDocModal.style.display = "none";
                addDocForm.reset();
                await loadRAGDocuments();
                alert("Meteorological document successfully indexed into RAG store!");
            }
        } catch (err) {
            alert(`Failed to add document: ${err.message}`);
        }
    });

    // --- 4. MCP TOOL SANDBOX ---
    function setupMcpToolForm() {
        renderToolArguments(mcpToolSelect.value);
        mcpToolSelect.addEventListener("change", () => {
            renderToolArguments(mcpToolSelect.value);
        });

        runMcpToolBtn.addEventListener("click", async () => {
            const toolName = mcpToolSelect.value;
            const args = extractToolArguments(toolName);

            mcpOutputPre.innerHTML = `<code>Executing MCP tool '${toolName}' via JSON-RPC...</code>`;
            mcpLatencyTag.textContent = "...";

            const t0 = performance.now();
            try {
                const resp = await fetch("/api/mcp/call", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tool_name: toolName, arguments: args })
                });
                const latency = Math.round(performance.now() - t0);
                const data = await resp.json();

                mcpLatencyTag.textContent = `${latency} ms`;
                mcpOutputPre.textContent = JSON.stringify(data, null, 2);
            } catch (err) {
                mcpOutputPre.textContent = `Error: ${err.message}`;
                mcpLatencyTag.textContent = "Error";
            }
        });
    }

    function renderToolArguments(toolName) {
        let html = "";
        if (toolName === "get_live_weather") {
            html = `
                <div class="form-group">
                    <label>City Name (required):</label>
                    <input type="text" id="mcpArgCity" value="${state.activeCity}" />
                </div>
                <div class="form-group">
                    <label>Country Code (optional):</label>
                    <input type="text" id="mcpArgCountry" placeholder="e.g. JP, US, GB" />
                </div>
            `;
        } else if (toolName === "get_weather_forecast") {
            html = `
                <div class="form-group">
                    <label>City Name (required):</label>
                    <input type="text" id="mcpArgCity" value="${state.activeCity}" />
                </div>
                <div class="form-group">
                    <label>Days Count (1 to 7):</label>
                    <input type="number" id="mcpArgDays" min="1" max="7" value="5" />
                </div>
            `;
        } else if (toolName === "get_air_quality" || toolName === "get_severe_weather_alerts") {
            html = `
                <div class="form-group">
                    <label>City Name (required):</label>
                    <input type="text" id="mcpArgCity" value="${state.activeCity}" />
                </div>
            `;
        } else if (toolName === "compare_weather") {
            html = `
                <div class="form-group">
                    <label>City A (required):</label>
                    <input type="text" id="mcpArgCityA" value="Paris" />
                </div>
                <div class="form-group">
                    <label>City B (required):</label>
                    <input type="text" id="mcpArgCityB" value="Dubai" />
                </div>
            `;
        }
        mcpToolArgsContainer.innerHTML = html;
    }

    function extractToolArguments(toolName) {
        if (toolName === "compare_weather") {
            return {
                city_a: document.getElementById("mcpArgCityA")?.value.trim() || "Paris",
                city_b: document.getElementById("mcpArgCityB")?.value.trim() || "Dubai"
            };
        }
        const city = document.getElementById("mcpArgCity")?.value.trim() || state.activeCity;
        if (toolName === "get_live_weather") {
            const country = document.getElementById("mcpArgCountry")?.value.trim();
            return country ? { city, country } : { city };
        } else if (toolName === "get_weather_forecast") {
            const days = parseInt(document.getElementById("mcpArgDays")?.value || "5", 10);
            return { city, days };
        }
        return { city };
    }

    // --- 5. SETTINGS MODAL ---
    openSettingsBtn.addEventListener("click", () => settingsModal.style.display = "flex");
    closeSettingsBtn.addEventListener("click", () => settingsModal.style.display = "none");
    saveSettingsBtn.addEventListener("click", () => {
        state.llmProvider = providerSelect.value;
        state.apiKey = apiKeyInput.value.trim();

        localStorage.setItem("weather_llm_provider", state.llmProvider);
        localStorage.setItem("weather_api_key", state.apiKey);

        settingsModal.style.display = "none";
        alert("Configuration saved! Subsequent queries will use this engine.");
    });

    // System Status check
    async function checkSystemStatus() {
        try {
            const resp = await fetch("/api/status");
            const data = await resp.json();
            const badge = document.getElementById("systemStatusBadge");
            if (badge) {
                badge.innerHTML = `<span class="pulse-dot"></span><span class="status-text">${data.status === "healthy" ? "FastMCP Ready (" + data.mcp_tools_count + " tools)" : "Connecting..."}</span>`;
            }
        } catch (e) {
            console.error("Status check failed", e);
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
