"""Configuration for the quote scraper."""

import os

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
QUOTES_RAW_DIR = os.path.join(DATA_DIR, "quotes_raw")
DEDUP_DB_PATH = os.path.join(DATA_DIR, "quotes_seen.db")
STATUS_FILE = os.path.join(DATA_DIR, "scraper_status.json")
RESUME_FILE = os.path.join(DATA_DIR, "scraper_resume.json")

# === Rate Limits ===
REDDIT_DELAY = 2.0  # seconds between requests
ANGI_DELAY = 5.0
HOMEADVISOR_DELAY = 5.0
JITTER_MIN = 0.0
JITTER_MAX = 3.0
SESSION_BREAK_EVERY = 50  # requests
SESSION_BREAK_MIN = 30  # seconds
SESSION_BREAK_MAX = 60  # seconds

# === Backoff ===
BACKOFF_INITIAL = 30  # seconds
BACKOFF_MULTIPLIER = 2
BACKOFF_MAX = 300  # 5 minutes

# === User Agents (rotate through these) ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# === Reddit Config ===
SUBREDDITS = [
    "homeimprovement",
    "HomeOwners",
    "Contractor",
    "Renovations",
    "HomeImprovement",
    "RealEstate",
    "personalfinance",
    "HVAC",
    "Plumbing",
    "Roofing",
    "Electricians",
    "solar",
    "Landscaping",
]

SEARCH_TERMS = [
    "quote",
    "estimate",
    "bid",
    "cost",
    "price",
    "how much",
    "is this fair",
    "got quoted",
    "contractor charged",
]

# === Project Types (34 types from Ungouge) ===
PROJECT_TYPES = {
    "roof_replacement": ["roof", "roofing", "shingle", "reroof", "re-roof", "metal roof", "asphalt"],
    "bathroom_remodel": ["bathroom", "bath remodel", "shower", "bathtub", "tile bathroom", "master bath"],
    "kitchen_remodel": ["kitchen", "kitchen remodel", "countertop", "cabinet", "backsplash", "kitchen renovation"],
    "hvac_install": ["hvac", "furnace", "air conditioning", "ac unit", "heat pump", "central air", "mini split", "ductwork"],
    "plumbing_repair": ["plumbing", "plumber", "pipe", "water heater", "sewer", "drain", "faucet", "toilet"],
    "electrical_work": ["electrical", "electrician", "wiring", "panel", "circuit breaker", "outlet", "rewire"],
    "painting_interior": ["interior paint", "painting inside", "paint interior", "room painting", "wall painting"],
    "painting_exterior": ["exterior paint", "house painting", "paint exterior", "paint outside"],
    "flooring_install": ["flooring", "hardwood", "laminate", "vinyl plank", "tile floor", "lvp", "carpet"],
    "window_replacement": ["window", "replacement window", "new windows", "double pane", "window install"],
    "door_replacement": ["door replacement", "front door", "entry door", "exterior door", "sliding door"],
    "siding_install": ["siding", "vinyl siding", "hardie", "james hardie", "fiber cement", "house siding"],
    "deck_build": ["deck", "deck build", "composite deck", "trex", "wood deck", "patio deck"],
    "fence_install": ["fence", "fencing", "privacy fence", "chain link", "wood fence", "vinyl fence"],
    "concrete_work": ["concrete", "driveway", "sidewalk", "patio concrete", "foundation", "slab"],
    "landscaping": ["landscaping", "landscape", "yard", "lawn", "irrigation", "sprinkler", "grading", "sod"],
    "tree_removal": ["tree removal", "tree service", "tree trimming", "stump", "arborist"],
    "garage_door": ["garage door", "overhead door", "garage opener"],
    "insulation": ["insulation", "attic insulation", "spray foam", "blown in", "fiberglass insulation"],
    "gutter_install": ["gutter", "gutters", "downspout", "gutter guard", "leaf guard"],
    "solar_install": ["solar", "solar panel", "solar install", "photovoltaic", "pv system"],
    "basement_finish": ["basement", "basement finish", "basement remodel", "finish basement"],
    "addition": ["addition", "home addition", "room addition", "house addition", "build addition"],
    "demolition": ["demolition", "demo", "tear down", "gut"],
    "drywall": ["drywall", "sheetrock", "drywall repair", "drywall install"],
    "framing": ["framing", "frame", "structural", "load bearing wall"],
    "masonry": ["masonry", "brick", "stone", "retaining wall", "block wall", "chimney"],
    "waterproofing": ["waterproofing", "basement waterproof", "foundation waterproof", "french drain"],
    "asbestos_removal": ["asbestos", "asbestos removal", "abatement"],
    "mold_remediation": ["mold", "mold remediation", "mold removal"],
    "septic": ["septic", "septic tank", "septic system", "drain field", "leach field"],
    "well_drilling": ["well", "well drilling", "water well"],
    "pool_install": ["pool", "swimming pool", "inground pool", "pool install"],
    "general_remodel": ["remodel", "renovation", "home improvement", "general contractor"],
}

# === US States (for location detection) ===
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

# Reverse lookup: state name -> abbreviation
STATE_NAME_TO_ABBR = {v.lower(): k for k, v in US_STATES.items()}

# Common large cities for location detection
MAJOR_CITIES = {
    "new york": "NY", "los angeles": "CA", "chicago": "IL", "houston": "TX",
    "phoenix": "AZ", "philadelphia": "PA", "san antonio": "TX", "san diego": "CA",
    "dallas": "TX", "san jose": "CA", "austin": "TX", "jacksonville": "FL",
    "fort worth": "TX", "columbus": "OH", "charlotte": "NC", "indianapolis": "IN",
    "san francisco": "CA", "seattle": "WA", "denver": "CO", "washington": "DC",
    "nashville": "TN", "oklahoma city": "OK", "el paso": "TX", "boston": "MA",
    "portland": "OR", "las vegas": "NV", "memphis": "TN", "louisville": "KY",
    "baltimore": "MD", "milwaukee": "WI", "albuquerque": "NM", "tucson": "AZ",
    "fresno": "CA", "mesa": "AZ", "sacramento": "CA", "atlanta": "GA",
    "kansas city": "MO", "colorado springs": "CO", "omaha": "NE", "raleigh": "NC",
    "miami": "FL", "tampa": "FL", "minneapolis": "MN", "cleveland": "OH",
    "pittsburgh": "PA", "st louis": "MO", "saint louis": "MO",
    "cincinnati": "OH", "orlando": "FL", "detroit": "MI",
    "new orleans": "LA", "salt lake city": "UT", "richmond": "VA",
    "boise": "ID", "des moines": "IA", "birmingham": "AL", "honolulu": "HI",
    "anchorage": "AK", "madison": "WI", "providence": "RI", "hartford": "CT",
    "charleston": "SC", "little rock": "AR", "burlington": "VT",
    "jersey city": "NJ", "spokane": "WA", "rochester": "NY", "buffalo": "NY",
    "durham": "NC", "norfolk": "VA", "chandler": "AZ", "lexington": "KY",
    "henderson": "NV", "st paul": "MN", "saint paul": "MN",
}

# === Angi Cost Guide URLs ===
ANGI_COST_PAGES = [
    "https://www.angi.com/articles/how-much-does-roof-replacement-cost.htm",
    "https://www.angi.com/articles/how-much-does-bathroom-remodel-cost.htm",
    "https://www.angi.com/articles/how-much-does-kitchen-remodel-cost.htm",
    "https://www.angi.com/articles/how-much-does-hvac-system-cost.htm",
    "https://www.angi.com/articles/how-much-does-plumbing-repair-cost.htm",
    "https://www.angi.com/articles/how-much-does-electrical-work-cost.htm",
    "https://www.angi.com/articles/how-much-does-house-painting-cost.htm",
    "https://www.angi.com/articles/how-much-does-flooring-installation-cost.htm",
    "https://www.angi.com/articles/how-much-does-window-replacement-cost.htm",
    "https://www.angi.com/articles/how-much-does-siding-cost.htm",
    "https://www.angi.com/articles/how-much-does-deck-cost.htm",
    "https://www.angi.com/articles/how-much-does-fence-installation-cost.htm",
    "https://www.angi.com/articles/how-much-does-concrete-work-cost.htm",
    "https://www.angi.com/articles/how-much-does-landscaping-cost.htm",
    "https://www.angi.com/articles/how-much-does-tree-removal-cost.htm",
    "https://www.angi.com/articles/how-much-does-garage-door-cost.htm",
    "https://www.angi.com/articles/how-much-does-insulation-cost.htm",
    "https://www.angi.com/articles/how-much-does-gutter-installation-cost.htm",
    "https://www.angi.com/articles/how-much-does-solar-panel-installation-cost.htm",
    "https://www.angi.com/articles/how-much-does-basement-finishing-cost.htm",
    "https://www.angi.com/articles/how-much-does-home-addition-cost.htm",
    "https://www.angi.com/articles/how-much-does-drywall-cost.htm",
    "https://www.angi.com/articles/how-much-does-water-heater-cost.htm",
    "https://www.angi.com/articles/how-much-does-septic-tank-cost.htm",
    "https://www.angi.com/articles/how-much-does-pool-cost.htm",
]

# Additional Angi cost guide path patterns to try
ANGI_COST_PATHS = [
    "/costs/roof-replacement",
    "/costs/bathroom-remodel",
    "/costs/kitchen-remodel",
    "/costs/hvac-system",
    "/costs/plumbing",
    "/costs/electrician",
    "/costs/interior-painting",
    "/costs/exterior-painting",
    "/costs/flooring",
    "/costs/window-replacement",
    "/costs/siding",
    "/costs/deck-building",
    "/costs/fence-installation",
    "/costs/concrete",
    "/costs/landscaping",
    "/costs/tree-removal",
    "/costs/garage-door",
    "/costs/insulation",
    "/costs/gutter-installation",
    "/costs/solar-panels",
    "/costs/basement-remodel",
    "/costs/home-addition",
    "/costs/drywall",
    "/costs/water-heater",
    "/costs/septic-system",
    "/costs/swimming-pool",
    "/costs/mold-removal",
    "/costs/asbestos-removal",
    "/costs/waterproofing",
]

# === HomeAdvisor Cost Guide URLs ===
HOMEADVISOR_COST_PAGES = [
    "https://www.homeadvisor.com/cost/roofing/install-a-roof/",
    "https://www.homeadvisor.com/cost/bathrooms/remodel-a-bathroom/",
    "https://www.homeadvisor.com/cost/kitchens/remodel-a-kitchen/",
    "https://www.homeadvisor.com/cost/heating-and-cooling/install-an-hvac-system/",
    "https://www.homeadvisor.com/cost/plumbing/",
    "https://www.homeadvisor.com/cost/electrical/",
    "https://www.homeadvisor.com/cost/painting/paint-the-interior-of-a-home/",
    "https://www.homeadvisor.com/cost/painting/paint-a-house/",
    "https://www.homeadvisor.com/cost/flooring/install-flooring/",
    "https://www.homeadvisor.com/cost/doors-and-windows/install-replacement-windows/",
    "https://www.homeadvisor.com/cost/siding/install-siding/",
    "https://www.homeadvisor.com/cost/outdoor-living/build-a-deck/",
    "https://www.homeadvisor.com/cost/fencing/install-a-fence/",
    "https://www.homeadvisor.com/cost/outdoor-living/concrete-installation-costs/",
    "https://www.homeadvisor.com/cost/landscape/price-to-landscape/",
    "https://www.homeadvisor.com/cost/landscape/remove-a-tree/",
    "https://www.homeadvisor.com/cost/garages/install-a-garage-door/",
    "https://www.homeadvisor.com/cost/insulation/install-insulation/",
    "https://www.homeadvisor.com/cost/roofing/install-gutters/",
    "https://www.homeadvisor.com/cost/green-energy-solutions/install-solar-panels/",
    "https://www.homeadvisor.com/cost/basements-and-foundations/finish-a-basement/",
    "https://www.homeadvisor.com/cost/additions-and-remodels/build-an-addition/",
    "https://www.homeadvisor.com/cost/walls-and-ceilings/install-drywall/",
    "https://www.homeadvisor.com/cost/plumbing/install-a-water-heater/",
    "https://www.homeadvisor.com/cost/plumbing/install-a-septic-tank/",
    "https://www.homeadvisor.com/cost/swimming-pools-hot-tubs-and-saunas/build-a-swimming-pool/",
]
