#!/usr/bin/env python3
"""Generate all 50 state location pages"""

import os
import json

OUTPUT_DIR = "/home/ungouge/clawd/projects/ungouge-app/frontend/content/locations"

# State data with location factors, cities, and climate notes
STATES = {
    "Alabama": {
        "code": "AL",
        "factor": 0.85,
        "labor_rate": "$45-75",
        "cities": ["Birmingham", "Montgomery", "Mobile", "Huntsville"],
        "climate": "Hot, humid summers with high cooling costs. Hurricane risk near coast requires reinforced construction.",
        "common_projects": "HVAC replacement, roof repairs (storm damage), foundation work, termite remediation"
    },
    "Alaska": {
        "code": "AK",
        "factor": 1.28,
        "labor_rate": "$75-120",
        "cities": ["Anchorage", "Fairbanks", "Juneau"],
        "climate": "Extreme cold requires specialized insulation, heating systems, and cold-weather construction techniques. Short building season.",
        "common_projects": "Heating system upgrades, extreme insulation, foundation work (permafrost), winterization"
    },
    "Arizona": {
        "code": "AZ",
        "factor": 0.92,
        "labor_rate": "$50-85",
        "cities": ["Phoenix", "Tucson", "Mesa", "Scottsdale"],
        "climate": "Extreme heat requires efficient cooling, UV-resistant materials, and desert landscaping considerations.",
        "common_projects": "HVAC replacement, pool installation, xeriscaping, stucco repair, tile roofing"
    },
    "Arkansas": {
        "code": "AR",
        "factor": 0.79,
        "labor_rate": "$40-70",
        "cities": ["Little Rock", "Fayetteville", "Fort Smith"],
        "climate": "Hot summers, mild winters. Tornado risk requires reinforced construction in some areas.",
        "common_projects": "Roof replacement, siding, HVAC, deck building"
    },
    "California": {
        "code": "CA",
        "factor": 1.38,
        "labor_rate": "$75-140",
        "cities": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"],
        "climate": "Varied by region—coastal moderate, inland hot. Seismic codes add cost. Water restrictions affect landscaping.",
        "common_projects": "Seismic retrofitting, drought-tolerant landscaping, solar installation, ADU construction"
    },
    "Colorado": {
        "code": "CO",
        "factor": 1.05,
        "labor_rate": "$60-95",
        "cities": ["Denver", "Colorado Springs", "Aurora", "Boulder"],
        "climate": "Cold winters, intense sun, low humidity. High altitude affects HVAC sizing and materials.",
        "common_projects": "Roof replacement (snow load), HVAC, deck building, basement finishing"
    },
    "Connecticut": {
        "code": "CT",
        "factor": 1.18,
        "labor_rate": "$65-110",
        "cities": ["Hartford", "New Haven", "Stamford", "Bridgeport"],
        "climate": "Cold winters, humid summers. Coastal areas face salt damage and storm surge risk.",
        "common_projects": "Roof replacement, siding (weather damage), heating system upgrades, window replacement"
    },
    "Delaware": {
        "code": "DE",
        "factor": 1.08,
        "labor_rate": "$60-95",
        "cities": ["Wilmington", "Dover", "Newark"],
        "climate": "Humid subtropical. Coastal flooding risk. Moderate winters.",
        "common_projects": "Roof replacement, siding, HVAC, foundation waterproofing"
    },
    "Florida": {
        "code": "FL",
        "factor": 0.91,
        "labor_rate": "$50-85",
        "cities": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
        "climate": "Hurricane-prone. Requires impact-resistant windows, reinforced roofing, flood-resistant construction. High humidity.",
        "common_projects": "Hurricane-rated windows/doors, roof replacement (wind damage), pool installation, AC replacement"
    },
    "Georgia": {
        "code": "GA",
        "factor": 0.88,
        "labor_rate": "$48-80",
        "cities": ["Atlanta", "Augusta", "Savannah", "Columbus"],
        "climate": "Hot, humid summers. Termite activity high. Occasional ice storms.",
        "common_projects": "HVAC replacement, roof repairs, foundation work, termite treatment"
    },
    "Hawaii": {
        "code": "HI",
        "factor": 1.42,
        "labor_rate": "$80-150",
        "cities": ["Honolulu", "Hilo", "Kailua"],
        "climate": "Tropical. Salt air corrosion, termite activity, lava zone restrictions. High shipping costs for materials.",
        "common_projects": "Termite treatment, corrosion-resistant materials, solar installation, roofing (trade winds)"
    },
    "Idaho": {
        "code": "ID",
        "factor": 0.94,
        "labor_rate": "$52-85",
        "cities": ["Boise", "Meridian", "Nampa"],
        "climate": "Cold winters, dry climate. Growing season affects landscaping.",
        "common_projects": "Heating upgrades, insulation, roof replacement, deck building"
    },
    "Illinois": {
        "code": "IL",
        "factor": 1.12,
        "labor_rate": "$62-100",
        "cities": ["Chicago", "Aurora", "Naperville", "Rockford"],
        "climate": "Cold winters, hot summers. Chicago wind affects exterior work. Freeze-thaw cycles damage concrete.",
        "common_projects": "Roof replacement, basement waterproofing, HVAC, concrete repair"
    },
    "Indiana": {
        "code": "IN",
        "factor": 0.91,
        "labor_rate": "$50-82",
        "cities": ["Indianapolis", "Fort Wayne", "Evansville"],
        "climate": "Cold winters, hot summers. Tornado risk in some areas.",
        "common_projects": "Roof replacement, siding, HVAC, basement finishing"
    },
    "Iowa": {
        "code": "IA",
        "factor": 0.96,
        "labor_rate": "$52-85",
        "cities": ["Des Moines", "Cedar Rapids", "Davenport"],
        "climate": "Cold winters, hot summers. Tornado risk. Freeze-thaw cycles.",
        "common_projects": "Roof replacement, siding, HVAC, foundation work"
    },
    "Kansas": {
        "code": "KS",
        "factor": 0.92,
        "labor_rate": "$50-82",
        "cities": ["Wichita", "Overland Park", "Kansas City"],
        "climate": "Hot summers, cold winters. Tornado Alley—reinforced construction common.",
        "common_projects": "Storm shelters, roof replacement (hail damage), siding, HVAC"
    },
    "Kentucky": {
        "code": "KY",
        "factor": 0.87,
        "labor_rate": "$48-78",
        "cities": ["Louisville", "Lexington", "Bowling Green"],
        "climate": "Humid subtropical. Moderate seasons.",
        "common_projects": "Roof replacement, siding, HVAC, deck building"
    },
    "Louisiana": {
        "code": "LA",
        "factor": 0.89,
        "labor_rate": "$48-80",
        "cities": ["New Orleans", "Baton Rouge", "Shreveport"],
        "climate": "Hurricane risk, high humidity, flooding concerns. Elevated construction common.",
        "common_projects": "Hurricane-rated windows, roof repairs (storm damage), foundation elevation, termite treatment"
    },
    "Maine": {
        "code": "ME",
        "factor": 1.06,
        "labor_rate": "$58-95",
        "cities": ["Portland", "Lewiston", "Bangor"],
        "climate": "Cold winters, short building season. Coastal salt damage. Ice dam risk.",
        "common_projects": "Roof replacement (ice dams), heating upgrades, insulation, weatherization"
    },
    "Maryland": {
        "code": "MD",
        "factor": 1.09,
        "labor_rate": "$60-98",
        "cities": ["Baltimore", "Columbia", "Germantown", "Silver Spring"],
        "climate": "Humid subtropical. Coastal areas face salt damage and storm surge.",
        "common_projects": "Roof replacement, siding, HVAC, basement waterproofing"
    },
    "Massachusetts": {
        "code": "MA",
        "factor": 1.25,
        "labor_rate": "$70-115",
        "cities": ["Boston", "Worcester", "Springfield", "Cambridge"],
        "climate": "Cold winters, coastal storms. Old housing stock requires specialized work. Strict energy codes.",
        "common_projects": "Roof replacement, heating upgrades, window replacement, insulation (energy efficiency)"
    },
    "Michigan": {
        "code": "MI",
        "factor": 1.02,
        "labor_rate": "$56-90",
        "cities": ["Detroit", "Grand Rapids", "Ann Arbor", "Lansing"],
        "climate": "Cold winters, heavy snow. Great Lakes affect weather. Freeze-thaw cycles.",
        "common_projects": "Roof replacement (snow load), siding, basement waterproofing, HVAC"
    },
    "Minnesota": {
        "code": "MN",
        "factor": 1.15,
        "labor_rate": "$64-105",
        "cities": ["Minneapolis", "St. Paul", "Rochester", "Duluth"],
        "climate": "Extremely cold winters require specialized construction. Short building season. Heavy snow loads.",
        "common_projects": "Roof replacement (snow load), heating upgrades, insulation, window replacement"
    },
    "Mississippi": {
        "code": "MS",
        "factor": 0.82,
        "labor_rate": "$42-72",
        "cities": ["Jackson", "Gulfport", "Southaven"],
        "climate": "Hot, humid. Hurricane risk near coast. Termite activity high.",
        "common_projects": "Hurricane-rated construction (coastal), HVAC, roof repairs, foundation work"
    },
    "Missouri": {
        "code": "MO",
        "factor": 0.95,
        "labor_rate": "$52-85",
        "cities": ["Kansas City", "St. Louis", "Springfield"],
        "climate": "Hot summers, cold winters. Tornado risk. Humidity.",
        "common_projects": "Roof replacement, HVAC, basement finishing, storm shelters"
    },
    "Montana": {
        "code": "MT",
        "factor": 1.01,
        "labor_rate": "$55-90",
        "cities": ["Billings", "Missoula", "Great Falls"],
        "climate": "Cold winters, short building season. Rural areas have limited contractor availability.",
        "common_projects": "Heating upgrades, insulation, roof replacement, well/septic work"
    },
    "Nebraska": {
        "code": "NE",
        "factor": 0.95,
        "labor_rate": "$52-85",
        "cities": ["Omaha", "Lincoln", "Bellevue"],
        "climate": "Cold winters, hot summers. Tornado risk.",
        "common_projects": "Roof replacement, HVAC, basement finishing, storm protection"
    },
    "Nevada": {
        "code": "NV",
        "factor": 1.08,
        "labor_rate": "$60-95",
        "cities": ["Las Vegas", "Henderson", "Reno"],
        "climate": "Desert heat requires efficient cooling. Water restrictions. UV damage to materials.",
        "common_projects": "HVAC replacement, pool installation, desert landscaping, stucco work"
    },
    "New Hampshire": {
        "code": "NH",
        "factor": 1.09,
        "labor_rate": "$60-98",
        "cities": ["Manchester", "Nashua", "Concord"],
        "climate": "Cold winters, short building season. Ice dam risk. Energy efficiency focus.",
        "common_projects": "Roof replacement (ice dams), heating upgrades, insulation, window replacement"
    },
    "New Jersey": {
        "code": "NJ",
        "factor": 1.22,
        "labor_rate": "$68-112",
        "cities": ["Newark", "Jersey City", "Paterson", "Elizabeth"],
        "climate": "Coastal storms, high property costs. Strict building codes.",
        "common_projects": "Roof replacement, siding, HVAC, flood mitigation"
    },
    "New Mexico": {
        "code": "NM",
        "factor": 0.93,
        "labor_rate": "$51-83",
        "cities": ["Albuquerque", "Santa Fe", "Las Cruces"],
        "climate": "Desert climate, high altitude. Adobe/stucco construction common. Water conservation.",
        "common_projects": "Stucco repair, HVAC, xeriscaping, solar installation"
    },
    "New York": {
        "code": "NY",
        "factor": 1.38,
        "labor_rate": "$75-140",
        "cities": ["New York City", "Buffalo", "Rochester", "Albany", "Syracuse"],
        "climate": "Cold winters (upstate snow belt). NYC has high labor costs and strict codes. Coastal storm risk.",
        "common_projects": "Roof replacement, heating upgrades, facade work (NYC), window replacement"
    },
    "North Carolina": {
        "code": "NC",
        "factor": 0.89,
        "labor_rate": "$48-80",
        "cities": ["Charlotte", "Raleigh", "Greensboro", "Durham"],
        "climate": "Humid subtropical. Hurricane risk on coast. Moderate winters.",
        "common_projects": "Roof replacement, siding, HVAC, deck building"
    },
    "North Dakota": {
        "code": "ND",
        "factor": 1.02,
        "labor_rate": "$56-90",
        "cities": ["Fargo", "Bismarck", "Grand Forks"],
        "climate": "Extremely cold winters, short building season. Energy costs high.",
        "common_projects": "Heating upgrades, insulation, roof replacement, window replacement"
    },
    "Ohio": {
        "code": "OH",
        "factor": 0.98,
        "labor_rate": "$54-88",
        "cities": ["Columbus", "Cleveland", "Cincinnati", "Toledo"],
        "climate": "Cold winters, hot summers. Freeze-thaw cycles. Lake effect snow near Erie.",
        "common_projects": "Roof replacement, siding, basement waterproofing, HVAC"
    },
    "Oklahoma": {
        "code": "OK",
        "factor": 0.87,
        "labor_rate": "$47-77",
        "cities": ["Oklahoma City", "Tulsa", "Norman"],
        "climate": "Tornado Alley. Hot summers, variable winters. Hail damage common.",
        "common_projects": "Storm shelters, roof replacement (hail/wind damage), HVAC, foundation work"
    },
    "Oregon": {
        "code": "OR",
        "factor": 1.09,
        "labor_rate": "$60-98",
        "cities": ["Portland", "Eugene", "Salem", "Bend"],
        "climate": "Wet winters, dry summers. Seismic concerns. Mold/moisture issues west of Cascades.",
        "common_projects": "Roof replacement (moss/moisture), seismic retrofitting, moisture remediation, deck building"
    },
    "Pennsylvania": {
        "code": "PA",
        "factor": 1.05,
        "labor_rate": "$58-94",
        "cities": ["Philadelphia", "Pittsburgh", "Allentown", "Erie"],
        "climate": "Cold winters, humid summers. Old housing stock. Rust belt infrastructure.",
        "common_projects": "Roof replacement, siding, heating upgrades, foundation work"
    },
    "Rhode Island": {
        "code": "RI",
        "factor": 1.16,
        "labor_rate": "$64-105",
        "cities": ["Providence", "Warwick", "Cranston"],
        "climate": "Coastal storms, salt damage. Cold winters. Old housing stock.",
        "common_projects": "Roof replacement, siding (weather damage), window replacement, heating upgrades"
    },
    "South Carolina": {
        "code": "SC",
        "factor": 0.85,
        "labor_rate": "$46-75",
        "cities": ["Charleston", "Columbia", "Greenville"],
        "climate": "Hurricane risk on coast. Hot, humid summers. Termite activity high.",
        "common_projects": "Hurricane-rated construction (coastal), HVAC, roof repairs, pool installation"
    },
    "South Dakota": {
        "code": "SD",
        "factor": 0.96,
        "labor_rate": "$52-85",
        "cities": ["Sioux Falls", "Rapid City", "Aberdeen"],
        "climate": "Cold winters, short building season. Rural areas have limited contractors.",
        "common_projects": "Heating upgrades, insulation, roof replacement, well/septic work"
    },
    "Tennessee": {
        "code": "TN",
        "factor": 0.87,
        "labor_rate": "$47-77",
        "cities": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
        "climate": "Hot, humid summers. Tornado risk. Moderate winters.",
        "common_projects": "Roof replacement, HVAC, siding, deck building"
    },
    "Texas": {
        "code": "TX",
        "factor": 0.91,
        "labor_rate": "$50-85",
        "cities": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
        "climate": "Varied by region—coastal hurricane risk, inland extreme heat. Foundation issues (clay soil).",
        "common_projects": "Foundation repair (clay soil), HVAC, hurricane protection (coastal), pool installation"
    },
    "Utah": {
        "code": "UT",
        "factor": 0.97,
        "labor_rate": "$53-87",
        "cities": ["Salt Lake City", "Provo", "West Valley City"],
        "climate": "Cold winters, dry climate. Seismic concerns. High altitude.",
        "common_projects": "Roof replacement, HVAC, basement finishing, earthquake retrofitting"
    },
    "Vermont": {
        "code": "VT",
        "factor": 0.98,
        "labor_rate": "$54-88",
        "cities": ["Burlington", "Montpelier", "Barre", "Northfield"],
        "climate": "Very cold winters, short building season. Heavy snow loads. Ice dam risk. Old housing stock.",
        "common_projects": "Roof replacement (snow/ice dams), heating upgrades, insulation, weatherization"
    },
    "Virginia": {
        "code": "VA",
        "factor": 1.02,
        "labor_rate": "$56-90",
        "cities": ["Virginia Beach", "Norfolk", "Richmond", "Arlington"],
        "climate": "Humid subtropical. Coastal areas face storm surge. Moderate winters.",
        "common_projects": "Roof replacement, siding, HVAC, deck building"
    },
    "Washington": {
        "code": "WA",
        "factor": 1.15,
        "labor_rate": "$64-105",
        "cities": ["Seattle", "Spokane", "Tacoma", "Bellevue"],
        "climate": "Wet winters (west), dry summers. Seismic concerns. Mold/moisture issues west of Cascades.",
        "common_projects": "Roof replacement (moss/moisture), seismic retrofitting, moisture remediation, deck building"
    },
    "West Virginia": {
        "code": "WV",
        "factor": 0.88,
        "labor_rate": "$48-78",
        "cities": ["Charleston", "Huntington", "Morgantown"],
        "climate": "Cold winters, humid summers. Mountainous terrain affects access/costs.",
        "common_projects": "Roof replacement, siding, heating upgrades, foundation work"
    },
    "Wisconsin": {
        "code": "WI",
        "factor": 1.07,
        "labor_rate": "$59-96",
        "cities": ["Milwaukee", "Madison", "Green Bay"],
        "climate": "Very cold winters, heavy snow. Short building season. Freeze-thaw cycles.",
        "common_projects": "Roof replacement (snow load), heating upgrades, insulation, basement waterproofing"
    },
    "Wyoming": {
        "code": "WY",
        "factor": 1.01,
        "labor_rate": "$55-90",
        "cities": ["Cheyenne", "Casper", "Laramie"],
        "climate": "Cold, windy winters. Short building season. Rural—limited contractor availability.",
        "common_projects": "Heating upgrades, insulation, roof replacement (wind), well/septic work"
    }
}


def generate_state_page(state_name, data):
    """Generate a location page for one state"""
    
    template_path = os.path.join(OUTPUT_DIR, "TEMPLATE.md")
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Determine cost context
    factor = data['factor']
    if factor < 0.90:
        cost_context = f"run about {int((1-factor)*100)}% below the national average"
        factor_explanation = "lower than national average"
    elif factor > 1.10:
        cost_context = f"run about {int((factor-1)*100)}% above the national average"
        factor_explanation = "higher than national average"
    else:
        cost_context = "are close to the national average"
        factor_explanation = "near national average"
    
    # Format cities
    cities_formatted = ", ".join(data['cities'][:-1]) + f", and {data['cities'][-1]}"
    cities_array = json.dumps(data['cities'])
    
    # Climate section
    climate_section = f"\n- **Climate considerations:** {data['climate']}"
    
    # Project list
    project_list = f"**Most common {state_name} projects:**\n- {data['common_projects'].replace(', ', '\n- ')}"
    
    # Red flags (generic for now, could be customized)
    red_flags = f"""- **Labor rates above ${data['labor_rate'].split('-')[1]}/hour** without justification
- **Material markups exceeding 40%** over retail
- **No itemized breakdown** of costs
- **Pressure to sign immediately** ("today only" pricing)
- **Missing permits** for work that requires them in {state_name}
- **No proof of {state_name} contractor license** and insurance"""
    
    # Replace all placeholders
    content = template
    replacements = {
        "{{STATE_NAME}}": state_name,
        "{{STATE_CODE}}": data['code'],
        "{{LOCATION_FACTOR}}": str(data['factor']),
        "{{LOCATION_FACTOR_EXPLANATION}}": factor_explanation,
        "{{AVG_LABOR_RATE}}": data['labor_rate'],
        "{{AVG_LABOR_RATE_RANGE}}": data['labor_rate'],
        "{{MAJOR_CITIES}}": cities_formatted,
        "{{MAJOR_CITIES_FORMATTED}}": cities_formatted,
        "{{MAJOR_CITIES_ARRAY}}": cities_array,
        "{{COST_CONTEXT}}": cost_context,
        "{{CLIMATE_SECTION}}": climate_section,
        "{{COMMON_PROJECTS}}": data['common_projects'],
        "{{PROJECT_LIST}}": project_list,
        "{{RED_FLAGS_LIST}}": red_flags,
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Write file
    filename = f"{state_name.lower().replace(' ', '-')}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return filename


def main():
    """Generate all state pages"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Generating location pages for all 50 states...\n")
    
    generated = []
    for state_name in sorted(STATES.keys()):
        filename = generate_state_page(state_name, STATES[state_name])
        generated.append(filename)
        print(f"✅ {filename}")
    
    print(f"\n✅ Generated {len(generated)} state location pages")
    print(f"📁 Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
