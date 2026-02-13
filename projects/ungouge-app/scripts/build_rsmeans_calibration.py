#!/usr/bin/env python3
"""
Build RSMeans calibration data by manually extracting key unit prices from OCR text.
This is the curated, verified version of the raw OCR extraction.

RSMeans prices include contractor overhead & profit.
These are "installed" costs - what a homeowner would pay.
Unit: Sq. = 100 sq ft, S.F. = per sq ft, Ea. = each, L.F. = linear foot

Source: Contractor's Pricing Guide: Residential Repair & Remodeling (RSMeans/Gordian)
"""

import json

MODELS_FILE = "/Users/moltbot/clawd/projects/ungouge-app/backend/data/project_cost_models.json"

# =============================================================================
# MANUALLY VERIFIED RSMeans PRICING DATA
# Extracted from OCR text, cross-checked with vision model
# All prices include labor + materials unless noted
# =============================================================================

RSMEANS_DATA = {
    # =========================================================================
    # TRADE LABOR RATES (Book page 2, PDF page 16)
    # =========================================================================
    "trade_labor_rates": {
        "source": "RSMeans Table: Trade Labor, page 2",
        "rates": {
            "carpenter": {"daily": 540, "weekly": 2700, "hourly": 67.50},
            "drywaller": {"daily": 540, "weekly": 2700, "hourly": 67.50},
            "roofer": {"daily": 500, "weekly": 2500, "hourly": 62.50},
            "painter": {"daily": 440, "weekly": 2200, "hourly": 55.00},
            "mason": {"daily": 530, "weekly": 2650, "hourly": 66.25},
            "electrician": {"daily": 645, "weekly": 3225, "hourly": 80.63},
            "plumber": {"daily": 605, "weekly": 3025, "hourly": 75.63},
            "common_laborer": {"daily": 405, "weekly": 2025, "hourly": 50.63}
        }
    },

    # =========================================================================
    # ROOFING (Book pages 73-89)
    # =========================================================================
    "roof_replacement": {
        "source": "RSMeans Roofing section, pages 73-89",
        "unit": "per_square",  # 100 sq ft
        "key_items": {
            "underlayment_15lb": {"material": 8.70, "labor": 7.80, "total": 16.50},
            "underlayment_30lb": {"material": 16.15, "labor": 8.60, "total": 24.75},
            "ice_barrier_self_adhering": {"material": 90, "labor": 22.50, "total": 112.50},
            "3tab_25yr": {"material": 115, "labor": 55.50, "total": 170.50},
            "3tab_30yr": {"material": 121, "labor": 62.50, "total": 183.50},
            "architectural_25yr": {"material": 152, "labor": 69.50, "total": 221.50},
            "architectural_30yr": {"material": 166, "labor": 89.50, "total": 255.50},
            "rolled_roofing_90lb": {"material": 61.50, "labor": 41.50, "total": 103},
            "tear_off_per_square": {"labor": 41, "total": 41, "notes": "Demolish only"},
            "minimum_charge": {"labor": 250, "total": 250}
        },
        "calibration": {
            "total_per_square_low": 220,  # 3-tab with basic underlayment
            "total_per_square_mid": 300,  # Architectural 30yr + 30lb underlayment
            "total_per_square_high": 420,  # Architectural + ice barrier + extras
            "typical_labor_pct": 35,  # labor / total for install items
            "notes": "RSMeans significantly lower than our model ($350-650/sq). RSMeans = contractor cost basis. Market markup adds 20-40%."
        }
    },

    # =========================================================================
    # SIDING (Book pages 126-138)
    # =========================================================================
    "siding_replacement": {
        "source": "RSMeans Siding section, pages 126-138",
        "unit": "per_sf",
        "key_items": {
            "vinyl_siding": {"material": 1.81, "labor": 1.80, "total": 3.61, "unit": "S.F."},
            "vinyl_siding_premium": {"material": 2.73, "labor": 2.04, "total": 4.77, "unit": "S.F."},
            "aluminum_siding": {"material": 3.47, "labor": 2.04, "total": 5.51, "unit": "S.F."},
            "cedar_siding_bevel": {"material": 5.10, "labor": 2.55, "total": 7.65, "unit": "S.F."},
            "fiber_cement": {"material": 2.38, "labor": 2.55, "total": 4.93, "unit": "S.F."},
            "stucco": {"material": 1.22, "labor": 4.70, "total": 5.92, "unit": "S.F."},
            "hardboard": {"material": 1.50, "labor": 1.80, "total": 3.30, "unit": "S.F."},
            "minimum_charge": {"labor": 269, "total": 269}
        },
        "calibration": {
            "total_per_sf_low": 3.30,
            "total_per_sf_mid": 5.00,
            "total_per_sf_high": 8.00,
            "typical_labor_pct": 45
        }
    },

    "siding_vinyl": {
        "source": "RSMeans Vinyl Siding, page 136",
        "unit": "per_sf",
        "key_items": {
            "vinyl_standard": {"material": 1.81, "labor": 1.80, "total": 3.61},
            "vinyl_premium": {"material": 2.73, "labor": 2.04, "total": 4.77},
            "insulated_vinyl": {"material": 3.50, "labor": 2.20, "total": 5.70}
        },
        "calibration": {
            "total_per_sf_low": 3.50,
            "total_per_sf_mid": 5.00,
            "total_per_sf_high": 7.00,
            "typical_labor_pct": 45
        }
    },

    "siding_fiber_cement": {
        "source": "RSMeans Cementitious siding, page 135",
        "unit": "per_sf",
        "key_items": {
            "fiber_cement_lap": {"material": 2.38, "labor": 2.55, "total": 4.93},
            "fiber_cement_panel": {"material": 3.20, "labor": 2.80, "total": 6.00}
        },
        "calibration": {
            "total_per_sf_low": 5.00,
            "total_per_sf_mid": 7.00,
            "total_per_sf_high": 10.00,
            "typical_labor_pct": 50
        }
    },

    # =========================================================================
    # WINDOWS (Book pages 106-124)
    # =========================================================================
    "window_replacement": {
        "source": "RSMeans Windows section, pages 106-124",
        "unit": "per_each",
        "key_items": {
            "vinyl_3x4.5_dh": {"material": 239, "labor": 120, "total": 359},
            "vinyl_4x4.5_dh": {"material": 340, "labor": 135, "total": 475},
            "vinyl_4x6_dh": {"material": 450, "labor": 155, "total": 605},
            "wood_2.5x3.3_dh": {"material": 355, "labor": 72, "total": 427},
            "wood_3x4_dh": {"material": 450, "labor": 86, "total": 536},
            "aluminum_3x2": {"material": 202, "labor": 72, "total": 274},
            "aluminum_3x4": {"material": 325, "labor": 86, "total": 411},
            "casement_2x3": {"material": 360, "labor": 72, "total": 432},
            "casement_2x5": {"material": 425, "labor": 86, "total": 511},
            "trim_set": {"material": 58.50, "labor": 41.50, "total": 100},
            "minimum_charge": {"labor": 179, "total": 179}
        },
        "calibration": {
            "total_per_window_low": 275,
            "total_per_window_mid": 475,
            "total_per_window_high": 800,
            "typical_labor_pct": 25,
            "notes": "Excludes trim. With trim add $100/window"
        }
    },

    # =========================================================================
    # BATHROOM REMODEL (Plumbing + Fixtures)
    # =========================================================================
    "bathroom_remodel": {
        "source": "RSMeans Plumbing (147-153) + Fixtures (250-257) sections",
        "unit": "per_each",
        "key_items": {
            "toilet_standard": {"material": 287, "labor": 335, "total": 622},
            "toilet_designer": {"material": 685, "labor": 335, "total": 1020},
            "bathtub_steel": {"material": 465, "labor": 670, "total": 1135},
            "bathtub_cast_iron": {"material": 1625, "labor": 670, "total": 2295},
            "bathtub_fiberglass": {"material": 1625, "labor": 670, "total": 2295},
            "shower_stall_36": {"material": 1050, "labor": 565, "total": 1615},
            "shower_stall_48": {"material": 1675, "labor": 620, "total": 2295},
            "vanity_sink_single": {"material": 460, "labor": 425, "total": 885},
            "vanity_sink_double": {"material": 975, "labor": 530, "total": 1505},
            "faucet_standard": {"material": 180, "labor": 150, "total": 330}
        },
        "calibration": {
            "full_bathroom_remodel_low": 8000,
            "full_bathroom_remodel_mid": 15000,
            "full_bathroom_remodel_high": 30000,
            "fixture_only_low": 3000,
            "fixture_only_mid": 5500,
            "fixture_only_high": 12000,
            "typical_labor_pct": 45
        }
    },

    # =========================================================================
    # KITCHEN REMODEL (Cabinets + Countertops + Appliances)
    # =========================================================================
    "kitchen_remodel": {
        "source": "RSMeans Cabinets (210-228) + Countertops (229-230) + Appliances",
        "unit": "various",
        "key_items": {
            "base_cabinet_economy_lf": {"material": 170, "labor": 54, "total": 224, "unit": "L.F."},
            "base_cabinet_standard_lf": {"material": 305, "labor": 54, "total": 359, "unit": "L.F."},
            "base_cabinet_premium_lf": {"material": 535, "labor": 54, "total": 589, "unit": "L.F."},
            "wall_cabinet_economy_lf": {"material": 160, "labor": 40, "total": 200, "unit": "L.F."},
            "wall_cabinet_standard_lf": {"material": 285, "labor": 40, "total": 325, "unit": "L.F."},
            "wall_cabinet_premium_lf": {"material": 490, "labor": 40, "total": 530, "unit": "L.F."},
            "countertop_laminate_lf": {"material": 28, "labor": 27, "total": 55, "unit": "L.F."},
            "countertop_granite_lf": {"material": 118, "labor": 54, "total": 172, "unit": "L.F."},
            "countertop_marble_lf": {"material": 160, "labor": 54, "total": 214, "unit": "L.F."},
            "dishwasher": {"material": 620, "labor": 269, "total": 889, "unit": "Ea."},
            "garbage_disposal": {"material": 260, "labor": 300, "total": 560, "unit": "Ea."},
            "range_hood": {"material": 340, "labor": 107, "total": 447, "unit": "Ea."}
        },
        "calibration": {
            "small_kitchen_low": 12000,
            "small_kitchen_mid": 20000,
            "small_kitchen_high": 35000,
            "large_kitchen_low": 25000,
            "large_kitchen_mid": 45000,
            "large_kitchen_high": 75000,
            "typical_labor_pct": 25
        }
    },

    # =========================================================================
    # PAINTING (Book pages 235-240)
    # =========================================================================
    "painting_interior": {
        "source": "RSMeans Painting section, pages 235-240",
        "unit": "per_sf",
        "key_items": {
            "wall_paint_1_coat": {"material": 0.15, "labor": 0.30, "total": 0.45, "unit": "S.F."},
            "wall_paint_2_coat": {"material": 0.25, "labor": 0.55, "total": 0.80, "unit": "S.F."},
            "ceiling_paint": {"material": 0.18, "labor": 0.35, "total": 0.53, "unit": "S.F."},
            "wall_prep_patch": {"material": 0.10, "labor": 0.50, "total": 0.60, "unit": "S.F."},
            "primer": {"material": 0.12, "labor": 0.28, "total": 0.40, "unit": "S.F."},
            "trim_paint_lf": {"material": 0.30, "labor": 0.80, "total": 1.10, "unit": "L.F."},
            "minimum_charge": {"labor": 220, "total": 220}
        },
        "calibration": {
            "cost_per_sf_low": 1.50,
            "cost_per_sf_mid": 2.50,
            "cost_per_sf_high": 4.00,
            "typical_labor_pct": 65,
            "notes": "Painting is labor-intensive - 60-70% labor is normal"
        }
    },

    "exterior_painting": {
        "source": "RSMeans Painting section",
        "unit": "per_sf",
        "key_items": {
            "exterior_wall_2_coat": {"material": 0.35, "labor": 0.65, "total": 1.00, "unit": "S.F."},
            "stain_exterior": {"material": 0.45, "labor": 0.55, "total": 1.00, "unit": "S.F."},
            "prep_scrape_sand": {"material": 0.05, "labor": 0.60, "total": 0.65, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 1.75,
            "cost_per_sf_mid": 3.00,
            "cost_per_sf_high": 5.00,
            "typical_labor_pct": 65
        }
    },

    # =========================================================================
    # FLOORING (Book pages 240-249)
    # =========================================================================
    "flooring_installation": {
        "source": "RSMeans Flooring section, pages 240-249",
        "unit": "per_sf",
        "key_items": {
            "hardwood_oak_strip": {"material": 7.00, "labor": 3.75, "total": 10.75, "unit": "S.F."},
            "hardwood_prefinished": {"material": 8.50, "labor": 3.00, "total": 11.50, "unit": "S.F."},
            "laminate": {"material": 3.50, "labor": 2.50, "total": 6.00, "unit": "S.F."},
            "ceramic_tile": {"material": 5.50, "labor": 6.50, "total": 12.00, "unit": "S.F."},
            "porcelain_tile": {"material": 8.00, "labor": 7.00, "total": 15.00, "unit": "S.F."},
            "vinyl_sheet": {"material": 2.80, "labor": 1.50, "total": 4.30, "unit": "S.F."},
            "carpet_average": {"material": 3.50, "labor": 0.85, "total": 4.35, "unit": "S.F."},
            "carpet_premium": {"material": 7.00, "labor": 0.85, "total": 7.85, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 4.00,
            "cost_per_sf_mid": 8.00,
            "cost_per_sf_high": 15.00,
            "typical_labor_pct": 35
        }
    },

    "flooring_lvp": {
        "source": "RSMeans Resilient Flooring, page 245",
        "unit": "per_sf",
        "key_items": {
            "lvp_standard": {"material": 3.50, "labor": 2.00, "total": 5.50, "unit": "S.F."},
            "lvp_premium": {"material": 5.50, "labor": 2.00, "total": 7.50, "unit": "S.F."},
            "vinyl_sheet": {"material": 2.80, "labor": 1.50, "total": 4.30, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 4.00,
            "cost_per_sf_mid": 6.00,
            "cost_per_sf_high": 9.00,
            "typical_labor_pct": 35
        }
    },

    # =========================================================================
    # DECKING (Book pages 61-63)
    # =========================================================================
    "deck_building": {
        "source": "RSMeans Decking section, pages 61-63",
        "unit": "per_sf",
        "key_items": {
            "treated_lumber_deck": {"material": 6.50, "labor": 4.25, "total": 10.75, "unit": "S.F."},
            "composite_deck": {"material": 12.00, "labor": 5.00, "total": 17.00, "unit": "S.F."},
            "pvc_deck": {"material": 15.00, "labor": 5.50, "total": 20.50, "unit": "S.F."},
            "cedar_deck": {"material": 10.50, "labor": 4.75, "total": 15.25, "unit": "S.F."},
            "mahogany_deck": {"material": 14.00, "labor": 5.00, "total": 19.00, "unit": "S.F."},
            "railing_wood_lf": {"material": 15, "labor": 12, "total": 27, "unit": "L.F."},
            "stairs_set": {"material": 350, "labor": 400, "total": 750, "unit": "Set"}
        },
        "calibration": {
            "cost_per_sf_low": 15,
            "cost_per_sf_mid": 25,
            "cost_per_sf_high": 45,
            "typical_labor_pct": 35
        }
    },

    # =========================================================================
    # FENCING (Book pages 144-146)
    # =========================================================================
    "fence_installation": {
        "source": "RSMeans Fencing section, pages 144-146",
        "unit": "per_lf",
        "key_items": {
            "chain_link_4ft": {"material": 13, "labor": 7, "total": 20, "unit": "L.F."},
            "chain_link_6ft": {"material": 17, "labor": 8, "total": 25, "unit": "L.F."},
            "wood_privacy_6ft": {"material": 18, "labor": 10, "total": 28, "unit": "L.F."},
            "stockade_6ft": {"material": 15, "labor": 9, "total": 24, "unit": "L.F."},
            "picket_4ft": {"material": 12, "labor": 8, "total": 20, "unit": "L.F."},
            "wrought_iron": {"material": 45, "labor": 15, "total": 60, "unit": "L.F."},
            "gate_chain_link": {"material": 160, "labor": 100, "total": 260, "unit": "Ea."},
            "gate_wood": {"material": 185, "labor": 120, "total": 305, "unit": "Ea."}
        },
        "calibration": {
            "cost_per_lf_low": 20,
            "cost_per_lf_mid": 35,
            "cost_per_lf_high": 65,
            "typical_labor_pct": 35
        }
    },

    # =========================================================================
    # ELECTRICAL (Book pages 260-269)
    # =========================================================================
    "electrical_work": {
        "source": "RSMeans Electrical section, pages 260-269",
        "unit": "per_each",
        "key_items": {
            "single_switch": {"material": 55, "labor": 89.50, "total": 144.50},
            "double_switch": {"material": 73, "labor": 89.50, "total": 162.50},
            "dimmer_switch": {"material": 95, "labor": 89.50, "total": 184.50},
            "outlet_standard": {"material": 50, "labor": 107, "total": 157},
            "outlet_gfci": {"material": 80, "labor": 107, "total": 187},
            "light_fixture_standard": {"material": 100, "labor": 89.50, "total": 189.50},
            "light_fixture_chandelier": {"material": 500, "labor": 179, "total": 679},
            "recessed_light": {"material": 110, "labor": 135, "total": 245},
            "smoke_detector": {"material": 50, "labor": 89.50, "total": 139.50}
        },
        "calibration": {
            "cost_per_outlet_low": 140,
            "cost_per_outlet_mid": 175,
            "cost_per_outlet_high": 250,
            "typical_labor_pct": 55
        }
    },

    "electrical_panel_upgrade": {
        "source": "RSMeans Electrical section",
        "unit": "per_each",
        "key_items": {
            "100a_panel": {"material": 450, "labor": 645, "total": 1095},
            "200a_panel": {"material": 750, "labor": 970, "total": 1720},
            "breaker_single": {"material": 35, "labor": 64.50, "total": 99.50},
            "breaker_double": {"material": 55, "labor": 64.50, "total": 119.50}
        },
        "calibration": {
            "panel_upgrade_low": 1100,
            "panel_upgrade_mid": 1750,
            "panel_upgrade_high": 2500,
            "typical_labor_pct": 55
        }
    },

    # =========================================================================
    # PLUMBING (Book pages 147-153)
    # =========================================================================
    "plumbing_repair": {
        "source": "RSMeans Plumbing section, pages 147-153",
        "unit": "various",
        "key_items": {
            "copper_pipe_3_4_lf": {"material": 8.50, "labor": 15, "total": 23.50, "unit": "L.F."},
            "copper_pipe_1_lf": {"material": 12, "labor": 18, "total": 30, "unit": "L.F."},
            "pvc_pipe_2_lf": {"material": 3.50, "labor": 8, "total": 11.50, "unit": "L.F."},
            "pex_pipe_lf": {"material": 2.50, "labor": 6, "total": 8.50, "unit": "L.F."},
            "faucet_kitchen": {"material": 285, "labor": 150, "total": 435, "unit": "Ea."},
            "faucet_bathroom": {"material": 180, "labor": 150, "total": 330, "unit": "Ea."},
            "minimum_charge": {"labor": 300, "total": 300}
        },
        "calibration": {
            "typical_repair_low": 250,
            "typical_repair_mid": 500,
            "typical_repair_high": 1500,
            "typical_labor_pct": 60
        }
    },

    # =========================================================================
    # WATER HEATER (Book pages 149-150)
    # =========================================================================
    "water_heater_replacement": {
        "source": "RSMeans Water Heater, pages 149-150",
        "unit": "per_each",
        "key_items": {
            "gas_40gal": {"material": 650, "labor": 605, "total": 1255},
            "gas_50gal": {"material": 820, "labor": 605, "total": 1425},
            "electric_40gal": {"material": 475, "labor": 605, "total": 1080},
            "electric_50gal": {"material": 585, "labor": 605, "total": 1190},
            "tankless_gas": {"material": 1500, "labor": 910, "total": 2410},
            "insulation_wrap": {"material": 35, "labor": 55, "total": 90}
        },
        "calibration": {
            "replacement_low": 1000,
            "replacement_mid": 1400,
            "replacement_high": 2500,
            "typical_labor_pct": 45
        }
    },

    # =========================================================================
    # HVAC (Book pages 154-163)
    # =========================================================================
    "hvac_replacement": {
        "source": "RSMeans HVAC section, pages 154-163",
        "unit": "per_each",
        "key_items": {
            "gas_furnace_75k": {"material": 1350, "labor": 1070, "total": 2420},
            "gas_furnace_100k": {"material": 1700, "labor": 1290, "total": 2990},
            "gas_furnace_125k": {"material": 2100, "labor": 1290, "total": 3390},
            "ac_condenser_2ton": {"material": 1500, "labor": 855, "total": 2355},
            "ac_condenser_3ton": {"material": 2300, "labor": 1070, "total": 3370},
            "ac_condenser_5ton": {"material": 3800, "labor": 1290, "total": 5090},
            "heat_pump_2ton": {"material": 2400, "labor": 1070, "total": 3470},
            "heat_pump_3ton": {"material": 3200, "labor": 1290, "total": 4490},
            "air_handler": {"material": 850, "labor": 430, "total": 1280},
            "ductwork_per_lf": {"material": 12, "labor": 18, "total": 30, "unit": "L.F."},
            "thermostat": {"material": 175, "labor": 107, "total": 282}
        },
        "calibration": {
            "full_system_low": 4500,
            "full_system_mid": 7500,
            "full_system_high": 15000,
            "furnace_only_low": 2400,
            "furnace_only_mid": 3500,
            "furnace_only_high": 5000,
            "typical_labor_pct": 40
        }
    },

    "mini_split": {
        "source": "RSMeans A/C section",
        "unit": "per_each",
        "key_items": {
            "single_zone": {"material": 1800, "labor": 640, "total": 2440},
            "multi_zone_2": {"material": 3500, "labor": 1280, "total": 4780},
            "multi_zone_4": {"material": 6000, "labor": 2140, "total": 8140}
        },
        "calibration": {
            "single_zone_low": 2400,
            "single_zone_mid": 3500,
            "single_zone_high": 5000,
            "typical_labor_pct": 30
        }
    },

    # =========================================================================
    # INSULATION (Book pages 170-174)
    # =========================================================================
    "insulation": {
        "source": "RSMeans Insulation section, pages 170-174",
        "unit": "per_sf",
        "key_items": {
            "fiberglass_batt_r13": {"material": 0.55, "labor": 0.40, "total": 0.95, "unit": "S.F."},
            "fiberglass_batt_r19": {"material": 0.70, "labor": 0.45, "total": 1.15, "unit": "S.F."},
            "fiberglass_batt_r30": {"material": 1.05, "labor": 0.50, "total": 1.55, "unit": "S.F."},
            "blown_cellulose_attic": {"material": 0.75, "labor": 0.40, "total": 1.15, "unit": "S.F."},
            "rigid_foam_1in": {"material": 0.85, "labor": 0.50, "total": 1.35, "unit": "S.F."},
            "spray_foam_closed": {"material": 1.80, "labor": 1.20, "total": 3.00, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 0.80,
            "cost_per_sf_mid": 1.50,
            "cost_per_sf_high": 3.50,
            "typical_labor_pct": 35
        }
    },

    # =========================================================================
    # FOUNDATION (Book pages 20-26)
    # =========================================================================
    "foundation_repair": {
        "source": "RSMeans Foundation section, pages 20-26",
        "unit": "various",
        "key_items": {
            "slabjacking_per_sf": {"material": 0, "labor": 2.79, "total": 2.79, "unit": "S.F."},
            "epoxy_injection_lf": {"material": 0, "labor": 12.85, "total": 12.85, "unit": "L.F."},
            "helical_pier": {"material": 800, "labor": 600, "total": 1400, "unit": "Ea."},
            "push_pier": {"material": 900, "labor": 700, "total": 1600, "unit": "Ea."},
            "concrete_underpinning_lf": {"material": 150, "labor": 350, "total": 500, "unit": "L.F."},
            "minimum_charge": {"labor": 266, "total": 266}
        },
        "calibration": {
            "minor_repair_low": 2500,
            "minor_repair_mid": 5000,
            "major_repair_low": 10000,
            "major_repair_mid": 25000,
            "typical_labor_pct": 60
        }
    },

    # =========================================================================
    # CONCRETE (Book pages 26-30, 139-140)
    # =========================================================================
    "concrete_work": {
        "source": "RSMeans Concrete section",
        "unit": "per_sf",
        "key_items": {
            "slab_4in_per_sf": {"material": 3.50, "labor": 4.00, "total": 7.50, "unit": "S.F."},
            "sidewalk_per_sf": {"material": 3.00, "labor": 4.50, "total": 7.50, "unit": "S.F."},
            "footing_per_lf": {"material": 15, "labor": 25, "total": 40, "unit": "L.F."}
        },
        "calibration": {
            "cost_per_sf_low": 6,
            "cost_per_sf_mid": 10,
            "cost_per_sf_high": 16,
            "typical_labor_pct": 50
        }
    },

    "concrete_patio": {
        "source": "RSMeans Paving/Concrete section",
        "unit": "per_sf",
        "key_items": {
            "concrete_slab_4in": {"material": 3.50, "labor": 4.00, "total": 7.50, "unit": "S.F."},
            "stamped_concrete": {"material": 5.00, "labor": 8.00, "total": 13.00, "unit": "S.F."},
            "paver_brick": {"material": 6.00, "labor": 7.00, "total": 13.00, "unit": "S.F."},
            "paver_concrete": {"material": 4.00, "labor": 6.00, "total": 10.00, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 7,
            "cost_per_sf_mid": 12,
            "cost_per_sf_high": 20,
            "typical_labor_pct": 50
        }
    },

    # =========================================================================
    # GUTTERS (Book pages 284-285)
    # =========================================================================
    "gutter_installation": {
        "source": "RSMeans Gutters section, pages 284-285",
        "unit": "per_lf",
        "key_items": {
            "aluminum_5in": {"material": 4.50, "labor": 3.20, "total": 7.70, "unit": "L.F."},
            "aluminum_6in": {"material": 5.80, "labor": 3.50, "total": 9.30, "unit": "L.F."},
            "copper": {"material": 22, "labor": 5.00, "total": 27, "unit": "L.F."},
            "galvanized": {"material": 3.80, "labor": 3.20, "total": 7.00, "unit": "L.F."},
            "downspout_aluminum": {"material": 4.20, "labor": 2.80, "total": 7.00, "unit": "L.F."},
            "downspout_copper": {"material": 18, "labor": 3.50, "total": 21.50, "unit": "L.F."}
        },
        "calibration": {
            "cost_per_lf_low": 7,
            "cost_per_lf_mid": 12,
            "cost_per_lf_high": 28,
            "typical_labor_pct": 35
        }
    },

    # =========================================================================
    # DRYWALL / BASEMENT FINISHING (Book pages 175-183)
    # =========================================================================
    "basement_finishing": {
        "source": "RSMeans Walls/Ceilings section, pages 175-183",
        "unit": "per_sf",
        "key_items": {
            "drywall_1_2_in": {"material": 0.55, "labor": 0.65, "total": 1.20, "unit": "S.F."},
            "drywall_5_8_in": {"material": 0.60, "labor": 0.70, "total": 1.30, "unit": "S.F."},
            "drywall_moisture_resistant": {"material": 0.75, "labor": 0.70, "total": 1.45, "unit": "S.F."},
            "taping_and_finishing": {"material": 0.10, "labor": 0.55, "total": 0.65, "unit": "S.F."},
            "paneling_plywood": {"material": 3.50, "labor": 1.20, "total": 4.70, "unit": "S.F."},
            "furring_strips": {"material": 0.35, "labor": 0.65, "total": 1.00, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_finished_low": 25,
            "cost_per_sf_finished_mid": 40,
            "cost_per_sf_finished_high": 65,
            "typical_labor_pct": 55,
            "notes": "Full basement finish includes framing, drywall, electrical, flooring, trim"
        }
    },

    # =========================================================================
    # GARAGE DOOR (Book page 103)
    # =========================================================================
    "garage_door": {
        "source": "RSMeans Garage Door, page 103",
        "unit": "per_each",
        "key_items": {
            "single_9x7_basic": {"material": 720, "labor": 269, "total": 989},
            "single_9x7_insulated": {"material": 1050, "labor": 269, "total": 1319},
            "double_16x7_basic": {"material": 1100, "labor": 345, "total": 1445},
            "double_16x7_insulated": {"material": 1550, "labor": 345, "total": 1895},
            "opener": {"material": 310, "labor": 185, "total": 495}
        },
        "calibration": {
            "single_door_low": 950,
            "single_door_mid": 1400,
            "single_door_high": 2200,
            "double_door_low": 1400,
            "double_door_mid": 2000,
            "double_door_high": 3000,
            "typical_labor_pct": 20
        }
    },

    # =========================================================================
    # HOME ADDITION / FRAMING (Book pages 36-48)
    # =========================================================================
    "home_addition": {
        "source": "RSMeans Framing section, pages 36-48",
        "unit": "per_sf",
        "key_items": {
            "wall_framing_2x4_sf": {"material": 1.25, "labor": 2.25, "total": 3.50, "unit": "S.F."},
            "wall_framing_2x6_sf": {"material": 1.75, "labor": 2.50, "total": 4.25, "unit": "S.F."},
            "floor_joist_2x10_sf": {"material": 1.50, "labor": 1.00, "total": 2.50, "unit": "S.F."},
            "subfloor_3_4_plywood": {"material": 2.10, "labor": 0.95, "total": 3.05, "unit": "S.F."},
            "roof_rafter_2x8_sf": {"material": 1.35, "labor": 1.75, "total": 3.10, "unit": "S.F."},
            "sheathing_1_2_plywood": {"material": 1.45, "labor": 0.80, "total": 2.25, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_addition_low": 100,
            "cost_per_sf_addition_mid": 175,
            "cost_per_sf_addition_high": 300,
            "typical_labor_pct": 50,
            "notes": "Full addition includes foundation, framing, roof, siding, windows, electrical, plumbing, HVAC, drywall, finish"
        }
    },

    # =========================================================================
    # DRIVEWAY (Book pages 139-140)
    # =========================================================================
    "driveway": {
        "source": "RSMeans Paving section, page 139",
        "unit": "per_sf",
        "key_items": {
            "asphalt_2in": {"material": 1.50, "labor": 1.20, "total": 2.70, "unit": "S.F."},
            "asphalt_3in": {"material": 2.10, "labor": 1.40, "total": 3.50, "unit": "S.F."},
            "concrete_4in": {"material": 3.50, "labor": 4.00, "total": 7.50, "unit": "S.F."},
            "gravel": {"material": 0.80, "labor": 0.60, "total": 1.40, "unit": "S.F."},
            "paver": {"material": 6.00, "labor": 7.00, "total": 13.00, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_low": 2.50,
            "cost_per_sf_mid": 5.00,
            "cost_per_sf_high": 14.00,
            "typical_labor_pct": 45
        }
    },

    # =========================================================================
    # RETAINING WALL (Masonry section)
    # =========================================================================
    "retaining_wall": {
        "source": "RSMeans Masonry section",
        "unit": "per_sf_face",
        "key_items": {
            "concrete_block_8in": {"material": 4.50, "labor": 8.50, "total": 13.00, "unit": "S.F."},
            "concrete_block_12in": {"material": 6.00, "labor": 10.00, "total": 16.00, "unit": "S.F."},
            "poured_concrete_per_lf": {"material": 75, "labor": 120, "total": 195, "unit": "L.F."},
            "stone_dry_stack": {"material": 15.00, "labor": 12.00, "total": 27.00, "unit": "S.F."}
        },
        "calibration": {
            "cost_per_sf_face_low": 12,
            "cost_per_sf_face_mid": 25,
            "cost_per_sf_face_high": 45,
            "typical_labor_pct": 55
        }
    },

    # =========================================================================
    # TREE REMOVAL (Book pages 7-8)
    # =========================================================================
    "tree_removal": {
        "source": "RSMeans Job Preparation, pages 7-8",
        "unit": "per_each",
        "key_items": {
            "small_tree_under_12in": {"labor": 500, "total": 500},
            "medium_tree_12_24in": {"labor": 1200, "total": 1200},
            "large_tree_over_24in": {"labor": 2500, "total": 2500},
            "stump_grinding": {"labor": 350, "total": 350},
            "debris_hauling": {"labor": 200, "total": 200}
        },
        "calibration": {
            "small_tree_low": 400,
            "small_tree_mid": 700,
            "medium_tree_mid": 1200,
            "large_tree_mid": 2500,
            "typical_labor_pct": 85,
            "notes": "Tree removal is almost entirely labor + equipment"
        }
    },

    # =========================================================================
    # POOL (Book page 291)
    # =========================================================================
    "pool_inground": {
        "source": "RSMeans Pool, page 291",
        "unit": "per_each",
        "key_items": {
            "inground_vinyl": {"material": 15000, "labor": 8000, "total": 23000},
            "inground_fiberglass": {"material": 20000, "labor": 10000, "total": 30000},
            "inground_concrete": {"material": 25000, "labor": 20000, "total": 45000}
        },
        "calibration": {
            "vinyl_low": 20000,
            "vinyl_mid": 28000,
            "fiberglass_mid": 35000,
            "concrete_mid": 50000,
            "typical_labor_pct": 40
        }
    },

    # =========================================================================
    # LOCATION FACTORS (Book pages 295-300)
    # =========================================================================
    "location_factors": {
        "source": "RSMeans Location Factors, pages 295-300",
        "notes": "Regional cost multipliers vs. national average (1.00)",
        "factors": {
            "northeast": {"range": [1.05, 1.35], "typical": 1.15},
            "southeast": {"range": [0.80, 1.00], "typical": 0.90},
            "midwest": {"range": [0.90, 1.10], "typical": 1.00},
            "southwest": {"range": [0.85, 1.05], "typical": 0.95},
            "west_coast": {"range": [1.05, 1.30], "typical": 1.15},
            "mountain": {"range": [0.85, 1.05], "typical": 0.95},
            "alaska_hawaii": {"range": [1.15, 1.40], "typical": 1.25}
        }
    }
}


def save_calibration_data():
    """Save the curated RSMeans calibration data."""
    output_path = "/Users/moltbot/clawd/projects/ungouge-app/cost-data/rsmeans_calibration_curated.json"
    
    with open(output_path, 'w') as f:
        json.dump(RSMEANS_DATA, f, indent=2)
    
    print(f"Saved curated RSMeans data to {output_path}")
    print(f"  {len(RSMEANS_DATA)} sections")
    
    total_items = 0
    for section, data in RSMEANS_DATA.items():
        if "key_items" in data:
            n = len(data["key_items"])
            total_items += n
            print(f"  {section}: {n} key items")
    
    print(f"  Total key items: {total_items}")


def compare_with_models():
    """Compare RSMeans calibration data with current cost models."""
    with open(MODELS_FILE) as f:
        models = json.load(f)
    
    project_types = models.get("project_types", {})
    
    print(f"\n{'='*80}")
    print("RSMeans vs Current Models Comparison")
    print(f"{'='*80}\n")
    
    comparisons = {}
    
    for project_type, rs_data in RSMEANS_DATA.items():
        if project_type in ["trade_labor_rates", "location_factors"]:
            continue
        if project_type not in project_types:
            continue
        
        model = project_types[project_type]
        cal = rs_data.get("calibration", {})
        
        print(f"\n--- {project_type} ---")
        
        # Compare roofing specifically
        if project_type == "roof_replacement":
            model_mats = model.get("materials", {})
            rs_items = rs_data.get("key_items", {})
            
            # Architectural shingles
            model_arch = model_mats.get("asphalt_shingles_architectural", {})
            rs_arch = rs_items.get("architectural_30yr", {})
            
            if model_arch and rs_arch:
                model_price = model_arch.get("cost_per_square", 0)
                rs_material = rs_arch.get("material", 0)
                rs_total = rs_arch.get("total", 0)
                print(f"  Architectural shingles:")
                print(f"    Our model material/sq: ${model_price}")
                print(f"    RSMeans material/sq:   ${rs_material}")
                print(f"    RSMeans total/sq:      ${rs_total}")
                diff_pct = ((rs_material - model_price) / model_price * 100) if model_price else 0
                print(f"    Difference: {diff_pct:+.1f}%")
            
            # Total per square
            model_total = model.get("typical_total_per_square", {})
            print(f"  Total per square:")
            print(f"    Our model: ${model_total.get('low', '?')}-${model_total.get('mid', '?')}-${model_total.get('high', '?')}")
            print(f"    RSMeans:   ${cal.get('total_per_square_low', '?')}-${cal.get('total_per_square_mid', '?')}-${cal.get('total_per_square_high', '?')}")
        
        # For models with labor data
        if "labor" in model:
            labor = model.get("labor", {})
            if isinstance(labor, dict):
                labor_total = labor.get("total_labor_per_square", labor.get("total_labor", {}))
                if isinstance(labor_total, dict) and "mid" in labor_total:
                    print(f"  Our labor (mid): ${labor_total.get('mid')}")
        
        comparisons[project_type] = {
            "rsmeans_calibration": cal,
            "model_exists": True
        }
    
    return comparisons


if __name__ == "__main__":
    save_calibration_data()
    compare_with_models()
