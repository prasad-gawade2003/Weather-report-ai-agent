"""
Curated Meteorological Knowledge Base for RAG.
Contains expert advisories, safety thresholds, outdoor activity criteria,
and travel health protocols.
"""

INITIAL_KNOWLEDGE_DOCUMENTS = [
    {
        "id": "doc-mountain-hiking-safety",
        "title": "Mountain & Alpine Hiking Weather Safety Protocols",
        "category": "outdoor_safety",
        "tags": ["hiking", "mountains", "hypothermia", "altitude", "storms", "gear"],
        "content": (
            "Mountain weather changes abruptly. For every 1,000 meters gained, temperature drops by approximately 6.5°C "
            "(environmental lapse rate) and wind speed doubles on exposed ridges. "
            "HYPOTHERMIA RISK: Hypothermia can occur even at 10°C if clothing is damp from rain or sweat combined with 25 km/h winds. "
            "LIGHTNING PROTOCOL: If thunder follows lightning in less than 30 seconds (flash-to-bang 10km rule), descend immediately. "
            "Avoid isolated trees, ridgelines, metal via ferratas, and water streams. Squat on an insulating backpack in the lightning crouch. "
            "REQUIRED GEAR: 3-layer system (moisture-wicking synthetic/merino base, fleece or down mid-layer, breathable Gore-Tex 20,000mm "
            "waterproof shell). Always carry waterproof over-trousers, emergency bivy bag, headlamp with spare batteries, and high-calorie rations."
        )
    },
    {
        "id": "doc-heat-index-uv-guidelines",
        "title": "Extreme Heat, Wet-Bulb & UV Index Health Guidelines",
        "category": "health_safety",
        "tags": ["heat", "uv", "sunstroke", "hydration", "summer"],
        "content": (
            "HEAT INDEX CATEGORIES: "
            "27°C - 32°C (Caution): Fatigue possible with prolonged exposure. Drink 500ml water per hour of light activity. "
            "32°C - 41°C (Extreme Caution): Heat cramps and heat exhaustion possible. Limit direct sun during 11:00 - 16:00. "
            "41°C - 54°C (Danger): Heat exhaustion likely, heatstroke possible. Heavy outdoor exertion must be rescheduled. "
            "Over 54°C (Extreme Danger): Imminent heatstroke; seek air conditioning. "
            "UV INDEX GUIDELINES: "
            "UV 0-2 (Low): Minimal protection required. "
            "UV 3-5 (Moderate): Wear SPF 30+ sunscreen, sunglasses, and a wide-brim hat. "
            "UV 6-7 (High): SPF 50+, seek shade midday, protective UV clothing. "
            "UV 8-10 (Very High): Skin burns in under 15 minutes without protection; avoid midday sun. "
            "UV 11+ (Extreme): Full barrier protection required, unexposed skin only."
        )
    },
    {
        "id": "doc-running-marathon-weather",
        "title": "Running, Marathon & Endurance Weather Thresholds",
        "category": "sports_athletics",
        "tags": ["running", "marathon", "cycling", "athletics", "endurance"],
        "content": (
            "Optimal performance temperatures for distance running are between 7°C and 15°C (45°F - 59°F). "
            "DEW POINT IMPACT: "
            "- Dew point under 10°C (50°F): Crisp and optimal sweat evaporation. "
            "- Dew point 15°C - 18°C (60-65°F): Noticeable drag on cooling; slow target pace by 2-3%. "
            "- Dew point 18°C - 21°C (65-70°F): Difficult conditions; cardiac drift accelerates. Increase electrolyte intake to 500mg sodium/hr. "
            "- Dew point above 21°C (70°F): Hazardous for high intensity; slow pace by 10-15% or run on treadmill. "
            "WIND RESISTANCE: Headwinds over 25 km/h increase metabolic cost by up to 12%. When running out-and-back, plan the outbound leg "
            "into the headwind and return with the tailwind when fatigued."
        )
    },
    {
        "id": "doc-severe-weather-protocols",
        "title": "Severe Weather Alerts & Emergency Action Protocols",
        "category": "emergency_response",
        "tags": ["thunderstorm", "flood", "tornado", "blizzard", "gale"],
        "content": (
            "FLASH FLOOD PROTOCOL: Never drive or walk through moving water. Just 15 cm (6 inches) of moving water can sweep a person off "
            "their feet, and 30 cm (12 inches) can float a standard vehicle. If trapped near swelling rivers or urban underpasses, move to high ground immediately. "
            "SEVERE THUNDERSTORM & TORNADO: Seek shelter in an interior room on the lowest floor without windows (e.g., bathroom, basement, reinforced closet). "
            "Protect head with a helmet or heavy cushions. "
            "WIND WARNINGS (BEAUFORT SCALE): "
            "- Force 7 (50-61 km/h / 30-38 mph): Near gale; whole trees in motion; walking against wind is inconvenient. "
            "- Force 8-9 (62-88 km/h / 39-54 mph): Gale / Strong gale; slight structural damage, tree branches break. Avoid parks and construction sites. "
            "- Force 10+ (>89 km/h / >55 mph): Storm; trees uprooted, significant infrastructure damage. Shelter in place."
        )
    },
    {
        "id": "doc-drone-aviation-weather",
        "title": "Drone (UAV) & General Aviation Meteorological Constraints",
        "category": "aviation_drone",
        "tags": ["drone", "uav", "aviation", "flight", "wind_limits"],
        "content": (
            "Commercial consumer drones (DJI Mini/Air/Mavic series) have strict meteorological operating limits: "
            "1. MAXIMUM WIND SPEED: Maximum wind resistance is typically 10.7 m/s (38 km/h / 24 mph / Level 5). Gusts above 12 m/s trigger gimbal stability loss and flyaway risks. "
            "2. PRECIPITATION: Non-IP-rated consumer drones must not be flown in drizzle, rain, or snow due to brushless motor short-circuit and optical sensor fogging. "
            "3. ICING & TEMPERATURE: Operating below 0°C rapidly cuts LiPo battery capacity by 40-50%. Pre-warm batteries to 20°C before takeoff. "
            "Avoid clouds and dense fog due to propeller icing which ruins aerodynamic lift. "
            "4. VISIBILITY & CEILING: Maintain minimum 5 km horizontal visibility and stay below cloud bases by at least 150 meters."
        )
    },
    {
        "id": "doc-wardrobe-travel-packing",
        "title": "Algorithmic Travel Wardrobe & Clothing Packing System",
        "category": "travel_wardrobe",
        "tags": ["packing", "travel", "clothing", "layers", "shoes"],
        "content": (
            "Temperature-Based Packing Matrix: "
            "Below 0°C (Freezing / Sub-Zero): Thermal long underwear base, wool/fleece mid-layer, heavy insulated down parka (650+ fill), "
            "waterproof insulated boots, windproof gloves, balaclava or fleece beanie. "
            "0°C - 10°C (Chilly): Long pants, sweater or fleece jacket, trench coat or light wool coat, water-resistant leather shoes or boots, light scarf. "
            "10°C - 18°C (Mild / Transitional): Layered outfit (t-shirt + light cardigan or denim jacket), breathable sneakers, compact umbrella for sudden showers. "
            "18°C - 25°C (Warm / Comfortable): Short sleeves, breathable cotton or linen shirts, chinos or jeans, sunglasses. Light sweater for evening breeze. "
            "Above 25°C (Hot / Tropical): Ultra-light linen or moisture-wicking fabrics, shorts, breathable sandals or canvas shoes, wide-brim sunhat, SPF 50 sunscreen. "
            "RAIN CONTINGENCY: If precipitation probability exceeds 30%, always carry a packable lightweight rain poncho or windproof Teflon-coated umbrella."
        )
    },
    {
        "id": "doc-air-quality-pollutants",
        "title": "Air Quality Index (AQI), PM2.5 & Allergen Health Guidelines",
        "category": "health_safety",
        "tags": ["aqi", "pm25", "pollution", "asthma", "allergies", "health"],
        "content": (
            "AIR QUALITY HEALTH BRACKETS (US AQI / European AQI): "
            "- AQI 0 - 50 (Good): Air quality is satisfactory. No health precautions needed. "
            "- AQI 51 - 100 (Moderate): Acceptable; unusually sensitive individuals should consider reducing prolonged outdoor heavy exertion. "
            "- AQI 101 - 150 (Unhealthy for Sensitive Groups): Children, elderly, and people with respiratory or heart conditions (asthma) should reduce strenuous outdoor activity. "
            "- AQI 151 - 200 (Unhealthy): Everyone may begin to experience health effects. Wear N95/FFP2 masks outdoors; run indoor HEPA filters. "
            "- AQI 201 - 300 (Very Unhealthy): Health alert; avoid all outdoor physical exercise. "
            "- AQI 301+ (Hazardous): Emergency conditions; stay indoors with sealed windows. "
            "POLLEN ADVISORY: Peak tree and grass pollen counts occur during dry, windy mid-mornings (10:00 - 14:00). Rain clears particulate matter and pollen from the lower atmosphere."
        )
    },
    {
        "id": "doc-coastal-marine-weather",
        "title": "Coastal, Sailing & Water Sports Meteorological Guidelines",
        "category": "marine_coastal",
        "tags": ["sailing", "beach", "surfing", "tides", "coastal", "swimming"],
        "content": (
            "Coastal weather is dominated by thermal sea breezes (onshore in afternoon, offshore at night). "
            "WATER SAFETY & SWELL: "
            "Rip currents are strongest at low tide and around sandbars or jetties. If caught in a rip current, swim parallel to the shore, never against the current. "
            "SAILING THRESHOLDS: "
            "- Beaufort 3 (12-19 km/h): Gentle breeze, ideal for novice sailors and paddle-boarders. "
            "- Beaufort 5 (29-38 km/h): Fresh breeze, whitecaps common, requires experienced skipper. "
            "- Beaufort 6+ (>39 km/h): Strong breeze; small craft advisory issued. Inexperienced recreational boaters must remain in harbor. "
            "COLD WATER SHOCK: Water temperatures below 15°C (59°F) cause involuntary gasp reflex and rapid incapacitation. Always wear an approved PFD (Personal Flotation Device)."
        )
    },
    {
        "id": "doc-mumbai-climate-dynamics",
        "title": "Mumbai Coastal Climate, October Heat & Arabian Sea Weather Norms",
        "category": "regional_climate",
        "tags": ["mumbai", "india", "october heat", "arabian sea", "humidity", "coastal", "maharashtra", "bombay", "marine drive", "juhu", "monsoon"],
        "content": (
            "MUMBAI CLIMATE PROFILE: "
            "Mumbai experiences a tropical maritime climate characterized by high relative humidity (typically 65% - 88%), "
            "maritime Arabian Sea breezes, and distinct seasonal phases: "
            "1. OCTOBER HEAT (Current Transitional Season): Following the withdrawal of the Southwest Monsoon in early October, "
            "Mumbai undergoes the notorious 'October Heat' phenomenon. Clear skies combined with intense solar insolation and residual soil moisture "
            "cause daytime temperatures to surge to 33°C - 37°C with apparent feels-like temperatures reaching 40°C - 44°C. "
            "The cooling afternoon Arabian Sea breeze usually sets in around 16:30 - 18:00 IST. "
            "2. SOUTHWEST MONSOON (June - September): Delivers over 2,200 mm of torrential rainfall. When high tides in the Arabian Sea "
            "exceed 4.5 meters concurrently with rainfall > 100 mm/24h, severe waterlogging occurs in low-lying transit corridors "
            "(Hindmata, Dadar TT, Kurla, Milan Subway, Andheri Subway, Gandhi Market). BMC issues Red Alerts and local trains "
            "(Central & Harbour lines) operate under water-level speed limits. "
            "3. WINTER & DRY SEASON (November - February): Dry, pleasant days (28°C - 32°C) and cooler evenings (17°C - 22°C). "
            "However, nighttime temperature inversions frequently trap vehicular and construction dust, spiking AQI to 160-260 (Moderate to Poor) "
            "across BKC, Deonar, Mazagon, and Navi Mumbai. "
            "4. WARDROBE & HEALTH IN MUMBAI: Wear ultra-breathable, loose-fitting cotton or linen clothing. Synthetic fabrics trap sweat and cause heat rashes. "
            "During October Heat and summer, carry hydration (coconut water, nimbu pani, electrolyte ORS) and carry a compact umbrella for sudden high-humidity squalls."
        )
    },
    {
        "id": "doc-imd-warning-color-codes",
        "title": "IMD (India Meteorological Department) Weather Warning Color Code Framework",
        "category": "emergency_response",
        "tags": ["imd", "india", "warning", "color codes", "cyclone", "monsoon", "alerts", "red alert", "orange alert", "yellow alert", "mumbai"],
        "content": (
            "The India Meteorological Department (IMD) issues standardized 4-color operational warnings for severe weather, rainfall, and cyclones: "
            "1. GREEN (All Clear / No Warning): No adverse weather expected. Normal public activities can continue. "
            "2. YELLOW (Watch / Be Updated): Weather condition is likely to deteriorate over 24-48 hours. Rainfall 64.5 - 115.5 mm (Heavy Rain) "
            "or squally winds 40-50 km/h. Citizens should monitor local weather bulletins and transit advisories. "
            "3. ORANGE (Alert / Be Prepared): Severe weather is imminent. Rainfall 115.6 - 204.4 mm (Very Heavy Rain) or wind gusts 50-65 km/h. "
            "High probability of localized road waterlogging, minor electricity disruptions, and rail delays. Keep emergency devices charged. "
            "4. RED (Warning / Take Action): Extremely severe meteorological emergency. Rainfall > 204.5 mm (Extremely Heavy Rain) or cyclone gale winds > 65 km/h. "
            "BMC and NDMA recommend complete shelter-in-place, closure of non-essential offices and schools, and avoidance of coastal promenades "
            "(Marine Drive, Worli Seaface, Carter Road, Bandra Bandstand) due to violent tidal surges. "
            "COASTAL HEATWAVE THRESHOLD: For coastal cities like Mumbai and Chennai, a maximum temperature >= 37°C with a departure of 4.5°C above normal constitutes an IMD Coastal Heatwave."
        )
    },
    {
        "id": "doc-india-monsoon-cyclone-protocols",
        "title": "Indian Monsoon Dynamics, Cyclonic Storms & Seasonal Health Guidelines",
        "category": "regional_climate",
        "tags": ["india", "monsoon", "cyclone", "arabian sea", "bay of bengal", "dengue", "floods", "delhi", "bengaluru", "chennai", "kolkata"],
        "content": (
            "INDIAN MONSOON & CYCLONE CYCLES: "
            "1. SOUTHWEST MONSOON (June - September): Advances across Kerala around June 1st and covers the entire subcontinent by July, providing 75% of annual precipitation. "
            "2. RETREATING & NORTHEAST MONSOON (October - December): Shifts southeasterly, causing heavy convective precipitation over Tamil Nadu, coastal Andhra Pradesh, and interior Karnataka. "
            "3. CYCLONE SEASONS: Tropical cyclones in the North Indian Ocean peak during pre-monsoon (April-May) and post-monsoon (October-November). "
            "Storms in the Arabian Sea (e.g. Cyclone Tauktae, Nisarga) and Bay of Bengal bring storm surges and gale winds. "
            "4. VECTOR-BORNE HEALTH HAZARDS: Post-monsoon high humidity (>75%) coupled with standing rain puddles dramatically increases vector breeding of Aedes aegypti (Dengue, Chikungunya) "
            "and Anopheles (Malaria). Ensure dry surroundings, sleep under mosquito nets, and apply DEET or Picaridin repellents during dusk and dawn."
        )
    },
    {
        "id": "doc-delhi-ncr-weather-smog",
        "title": "Delhi-NCR & North India Extreme Seasons (Winter Smog, Fog & Summer Loo)",
        "category": "regional_climate",
        "tags": ["delhi", "ncr", "india", "smog", "aqi", "fog", "loo", "heatwave", "cold wave", "north india"],
        "content": (
            "NORTH INDIA METEOROLOGICAL PROFILE: "
            "1. WINTER SMOG CRISIS (October - January): Agricultural post-harvest crop residue burning combined with low boundary-layer atmospheric inversion "
            "and firecracker emissions causes hazardous air quality. PM2.5 levels skyrocket, with US AQI consistently exceeding 350-500+ (Hazardous category). "
            "N95/FFP2 masks are essential outdoors; vulnerable individuals must remain indoors with HEPA air purifiers. "
            "2. DENSE RADIATION FOG (December - January): Morning visibility drops below 50 meters, causing widespread flight cancellations at IGI Airport and Northern Railway delays. "
            "3. SUMMER 'LOO' WINDS (April - June): Torrid, dry westerly winds pushing temperatures to 42°C - 48°C. Imminent heatstroke risk between 11:30 and 16:00."
        )
    }
]

