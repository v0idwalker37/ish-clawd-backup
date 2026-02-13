#!/usr/bin/env python3
"""
Cost Model Enrichment Script
Integrates scraped data from BLS, HomeAdvisor, Cost vs Value Report,
and Prevailing Wage data into existing cost models.

Rules:
- DO NOT delete existing data — only add/update
- Keep existing structure intact
- Add new fields alongside existing ones
"""

import json
import os
import copy
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COST_DATA_DIR = os.path.join(BASE_DIR, 'cost-data')
MODELS_FILE = os.path.join(BASE_DIR, 'backend', 'data', 'project_cost_models.json')

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Load all data
bls = load_json(os.path.join(COST_DATA_DIR, 'bls-labor-rates.json'))
census = load_json(os.path.join(COST_DATA_DIR, 'census-construction-data.json'))
homeadvisor = load_json(os.path.join(COST_DATA_DIR, 'homeadvisor-cost-guides.json'))
prevailing = load_json(os.path.join(COST_DATA_DIR, 'prevailing-wage-rates.json'))
roi_data = load_json(os.path.join(COST_DATA_DIR, 'remodeling-cost-vs-value.json'))
models = load_json(MODELS_FILE)

# Backup original
original = copy.deepcopy(models)

changes_log = []

def log_change(project_type, field, description):
    changes_log.append({
        'project_type': project_type,
        'field': field,
        'description': description
    })

# ============================================================
# HELPER: Build BLS labor rate lookup
# ============================================================
bls_trades = {}
for trade_key, trade_data in bls['occupations'].items():
    if trade_key == 'additional_may_2024_construction_trades':
        # These are flat entries
        for sub_key, sub_data in trade_data.items():
            if isinstance(sub_data, dict) and 'mean_hourly_wage' in sub_data:
                bls_trades[sub_key] = sub_data
    else:
        bls_trades[trade_key] = trade_data

# ============================================================
# HELPER: Build prevailing wage regional multipliers
# ============================================================
# Calculate multipliers relative to national BLS averages
# Using carpenter as the baseline trade
def calc_prevailing_wage_multipliers():
    """Calculate regional wage multipliers from prevailing wage data relative to BLS national average."""
    pw_rates = prevailing['representative_prevailing_wage_rates']
    
    # National BLS averages for key trades (May 2024)
    national_avg = {
        'carpenter': 30.79,  # from BLS May 2024
        'electrician': 33.47,
        'plumber': 33.63,
        'roofer': 27.45,
    }
    
    regional_multipliers = {}
    for state_key, state_data in pw_rates.items():
        if state_key == 'note':
            continue
        if not isinstance(state_data, dict):
            continue
        # Find the area data (first key that contains rates)
        for area_key, area_data in state_data.items():
            if isinstance(area_data, dict) and 'carpenter' in area_data:
                multipliers = {}
                for trade in ['carpenter', 'electrician', 'plumber', 'roofer']:
                    if trade in area_data and trade in national_avg:
                        pw_hourly = area_data[trade].get('hourly', 0)
                        if pw_hourly > 0 and national_avg[trade] > 0:
                            multipliers[trade] = round(pw_hourly / national_avg[trade], 2)
                if multipliers:
                    regional_multipliers[f"{state_key}_{area_key}"] = {
                        'multipliers': multipliers,
                        'avg_multiplier': round(sum(multipliers.values()) / len(multipliers), 2),
                        'source': state_data.get('source', 'Prevailing wage data'),
                        'note': state_data.get('note', '')
                    }
    return regional_multipliers

prevailing_multipliers = calc_prevailing_wage_multipliers()

# ============================================================
# HELPER: Build HomeAdvisor lookup by project type
# ============================================================
ha_guides = homeadvisor['cost_guides']

# ============================================================
# HELPER: Build ROI lookup
# ============================================================
roi_top = {item['project'].lower(): item for item in roi_data.get('top_projects_by_roi', [])}
roi_additional = roi_data.get('additional_projects', {})

# ============================================================
# MAPPING: Project type -> relevant BLS trades
# ============================================================
project_bls_mapping = {
    'roof_replacement': {
        'primary': 'roofers',
        'supplemental': ['construction_laborers']
    },
    'kitchen_remodel': {
        'primary': 'carpenters',
        'supplemental': ['electricians', 'plumbers_pipefitters_steamfitters', 'painters_construction_maintenance',
                         'carpet_floor_tile_installers']
    },
    'bathroom_remodel': {
        'primary': 'plumbers_pipefitters_steamfitters',
        'supplemental': ['carpenters', 'electricians', 'carpet_floor_tile_installers',
                         'painters_construction_maintenance']
    },
    'hvac_replacement': {
        'primary': 'hvac_mechanics_installers',  # from additional trades
        'supplemental': ['electricians', 'sheet_metal_workers']
    },
    'plumbing_repair': {
        'primary': 'plumbers_pipefitters_steamfitters',
        'supplemental': ['pipelayers']
    },
    'electrical_work': {
        'primary': 'electricians',
        'supplemental': []
    },
    'deck_building': {
        'primary': 'carpenters',
        'supplemental': ['construction_laborers']
    },
    'painting_interior': {
        'primary': 'painters_construction_maintenance',  # from additional trades
        'supplemental': ['drywall_ceiling_tile_installers_tapers']
    },
    'siding_replacement': {
        'primary': 'carpenters',
        'supplemental': ['construction_laborers', 'insulation_workers']
    },
    'window_replacement': {
        'primary': 'carpenters',
        'supplemental': ['glaziers']
    },
    'flooring_installation': {
        'primary': 'carpet_floor_tile_installers',  # from additional trades
        'supplemental': ['carpenters', 'cement_masons_concrete_finishers']
    },
    'fence_installation': {
        'primary': 'fence_erectors',  # from additional trades
        'supplemental': ['construction_laborers']
    },
    'concrete_work': {
        'primary': 'cement_masons_concrete_finishers',  # from additional trades
        'supplemental': ['construction_laborers', 'construction_equipment_operators']
    },
    'gutter_installation': {
        'primary': 'roofers',
        'supplemental': ['sheet_metal_workers']
    }
}

# ============================================================
# MAPPING: Project type -> HomeAdvisor guide key
# ============================================================
project_ha_mapping = {
    'roof_replacement': 'roofing',
    'kitchen_remodel': 'kitchen_remodel',
    'bathroom_remodel': 'bathroom_remodel',
    'hvac_replacement': 'hvac',
    'plumbing_repair': 'plumbing',
    'electrical_work': 'electrical',
    'deck_building': 'deck_building',
    'painting_interior': 'painting',
    'siding_replacement': 'siding',
    'window_replacement': 'windows',
    'flooring_installation': 'flooring',
    'fence_installation': 'fencing',
    'concrete_work': 'concrete',
    'gutter_installation': 'gutters'
}

# ============================================================
# MAPPING: Project type -> ROI data
# ============================================================
project_roi_mapping = {
    'roof_replacement': None,  # Not in report (no direct ROI data for roof replacement)
    'kitchen_remodel': {
        'top_projects': ['minor kitchen remodel (midrange)'],
        'additional': ['minor_kitchen_remodel_midrange', 'major_kitchen_remodel_midrange', 'major_kitchen_remodel_upscale']
    },
    'bathroom_remodel': {
        'top_projects': [],
        'additional': ['bathroom_remodel_midrange', 'bathroom_remodel_universal_design', 'bathroom_remodel_upscale']
    },
    'hvac_replacement': None,
    'plumbing_repair': None,
    'electrical_work': None,
    'deck_building': {
        'top_projects': ['wood deck addition', 'composite deck addition'],
        'additional': []
    },
    'painting_interior': None,
    'siding_replacement': {
        'top_projects': ['fiber-cement siding replacement', 'vinyl siding replacement'],
        'additional': []
    },
    'window_replacement': {
        'top_projects': [],
        'additional': ['window_replacement_vinyl']
    },
    'flooring_installation': None,
    'fence_installation': None,
    'concrete_work': None,
    'gutter_installation': None
}

# ============================================================
# ENRICH EACH MODEL
# ============================================================
for project_type, project_data in models['project_types'].items():
    print(f"\n--- Enriching: {project_type} ---")
    
    # --------------------------------------------------------
    # 1. BLS Labor Rate Data
    # --------------------------------------------------------
    bls_mapping = project_bls_mapping.get(project_type, {})
    primary_trade = bls_mapping.get('primary')
    supplemental_trades = bls_mapping.get('supplemental', [])
    
    bls_enrichment = {
        'source': 'Bureau of Labor Statistics - OEWS',
        'data_period': bls['data_period'],
        'scraped_date': bls['scraped_date'],
        'primary_trade': {},
        'supplemental_trades': {},
        'notes': [
            'BLS wages do not include self-employed workers',
            'Loaded rates (with overhead, insurance, WC) are typically 1.4-1.6x base wage',
            'These are individual worker wages, not crew rates'
        ]
    }
    
    # Primary trade
    if primary_trade:
        trade_data = None
        if primary_trade in bls['occupations'] and primary_trade != 'additional_may_2024_construction_trades':
            td = bls['occupations'][primary_trade]
            trade_data = {
                'occupation': primary_trade,
                'soc_code': td.get('soc_code', ''),
                'national_mean_hourly': td.get('national', {}).get('mean_hourly_wage') or td.get('may_2024_national', {}).get('mean_hourly_wage'),
                'national_median_hourly': td.get('national', {}).get('percentiles', {}).get('50th_median') or td.get('may_2024_national', {}).get('median_hourly_wage'),
                'employment': td.get('national', {}).get('employment') or td.get('may_2024_national', {}).get('employment'),
            }
            # Add May 2024 data if available
            if 'may_2024_national' in td:
                trade_data['may_2024_update'] = {
                    'mean_hourly_wage': td['may_2024_national'].get('mean_hourly_wage'),
                    'median_hourly_wage': td['may_2024_national'].get('median_hourly_wage'),
                    'employment': td['may_2024_national'].get('employment')
                }
            # Add top paying states
            if 'top_states_by_pay' in td:
                trade_data['top_paying_states'] = td['top_states_by_pay'][:5]
            # Add state data for BLS comparison
            if 'top_states_by_employment' in td:
                trade_data['top_employment_states'] = td['top_states_by_employment'][:5]
            # Vermont data if available
            if 'vermont_data' in td:
                trade_data['vermont_data'] = td['vermont_data']
        elif primary_trade in bls_trades:
            # From additional_may_2024_construction_trades
            td = bls_trades[primary_trade]
            trade_data = {
                'occupation': primary_trade,
                'national_mean_hourly': td.get('mean_hourly_wage'),
                'national_median_hourly': td.get('median_hourly_wage'),
                'employment': td.get('employment'),
                'data_period': 'May 2024'
            }
        
        if trade_data:
            bls_enrichment['primary_trade'] = trade_data
            log_change(project_type, 'bls_labor_rates.primary_trade', 
                       f"Added BLS data for {primary_trade}: ${trade_data.get('national_mean_hourly', 'N/A')}/hr mean")
    
    # Supplemental trades
    for supp_trade in supplemental_trades:
        supp_data = None
        if supp_trade in bls['occupations'] and supp_trade != 'additional_may_2024_construction_trades':
            td = bls['occupations'][supp_trade]
            supp_data = {
                'occupation': supp_trade,
                'national_mean_hourly': td.get('national', {}).get('mean_hourly_wage') or td.get('may_2024_national', {}).get('mean_hourly_wage'),
                'national_median_hourly': td.get('national', {}).get('percentiles', {}).get('50th_median') or td.get('may_2024_national', {}).get('median_hourly_wage'),
                'employment': td.get('national', {}).get('employment') or td.get('may_2024_national', {}).get('employment'),
            }
            if 'may_2024_national' in td:
                supp_data['may_2024_update'] = {
                    'mean_hourly_wage': td['may_2024_national'].get('mean_hourly_wage'),
                    'median_hourly_wage': td['may_2024_national'].get('median_hourly_wage')
                }
        elif supp_trade in bls_trades:
            td = bls_trades[supp_trade]
            supp_data = {
                'occupation': supp_trade,
                'national_mean_hourly': td.get('mean_hourly_wage'),
                'national_median_hourly': td.get('median_hourly_wage'),
                'employment': td.get('employment'),
                'data_period': 'May 2024'
            }
        
        if supp_data:
            bls_enrichment['supplemental_trades'][supp_trade] = supp_data
            log_change(project_type, f'bls_labor_rates.supplemental_trades.{supp_trade}',
                       f"Added BLS data for {supp_trade}: ${supp_data.get('national_mean_hourly', 'N/A')}/hr mean")
    
    project_data['bls_labor_rates'] = bls_enrichment
    
    # --------------------------------------------------------
    # 2. HomeAdvisor Market Benchmarks
    # --------------------------------------------------------
    ha_key = project_ha_mapping.get(project_type)
    if ha_key and ha_key in ha_guides:
        ha_data = ha_guides[ha_key]
        market_benchmarks = {
            'source': 'HomeAdvisor / Angi Cost Guides',
            'scraped_date': homeadvisor['scraped_date'],
            'data_period': homeadvisor['data_period'],
            'source_url': ha_data.get('source_url', ''),
            'data': {}
        }
        
        # Copy all HomeAdvisor data for this category
        for key, value in ha_data.items():
            if key != 'source_url':
                market_benchmarks['data'][key] = value
        
        # Add average cost and range if available
        if 'average_cost' in ha_data:
            market_benchmarks['average_cost'] = ha_data['average_cost']
        if 'typical_range' in ha_data:
            market_benchmarks['typical_range'] = ha_data['typical_range']
        
        project_data['market_benchmarks'] = market_benchmarks
        
        desc_parts = []
        if 'average_cost' in ha_data:
            desc_parts.append(f"avg=${ha_data['average_cost']:,}")
        if 'typical_range' in ha_data:
            r = ha_data['typical_range']
            desc_parts.append(f"range=${r.get('low', 'N/A'):,}-${r.get('high', 'N/A'):,}")
        log_change(project_type, 'market_benchmarks', 
                   f"Added HomeAdvisor benchmarks: {', '.join(desc_parts) if desc_parts else 'detailed cost data'}")
    
    # --------------------------------------------------------
    # 3. Cost vs. Value ROI Data
    # --------------------------------------------------------
    roi_mapping = project_roi_mapping.get(project_type)
    if roi_mapping:
        roi_enrichment = {
            'source': 'Remodeling Magazine / Zonda 2025 Cost vs. Value Report',
            'scraped_date': roi_data['scraped_date'],
            'data_period': roi_data['data_period'],
            'projects': []
        }
        
        # Top projects
        for proj_name in roi_mapping.get('top_projects', []):
            proj_name_lower = proj_name.lower()
            if proj_name_lower in roi_top:
                item = roi_top[proj_name_lower]
                roi_enrichment['projects'].append({
                    'project': item['project'],
                    'average_cost': item.get('average_cost'),
                    'resale_value': item.get('resale_value'),
                    'roi_pct': item.get('roi_pct'),
                    'rank': item.get('rank'),
                    'note': item.get('note', '')
                })
        
        # Additional projects
        for add_key in roi_mapping.get('additional', []):
            if add_key in roi_additional:
                item = roi_additional[add_key]
                roi_enrichment['projects'].append({
                    'project': add_key.replace('_', ' ').title(),
                    'cost': item.get('cost'),
                    'resale_value': item.get('resale_value'),
                    'roi_pct': item.get('roi_pct'),
                    'note': item.get('note', '')
                })
        
        # Add regional ROI ranges
        if roi_data.get('regional_roi_ranges'):
            roi_enrichment['regional_roi_ranges'] = roi_data['regional_roi_ranges']
        
        # Add key insights relevant to this project type
        roi_enrichment['key_insights'] = roi_data.get('key_insights', [])
        
        if roi_enrichment['projects']:
            project_data['roi_data'] = roi_enrichment
            proj_summaries = [f"{p['project']} ({p.get('roi_pct', 'N/A')}% ROI)" for p in roi_enrichment['projects']]
            log_change(project_type, 'roi_data', 
                       f"Added ROI data for: {'; '.join(proj_summaries)}")
    
    # --------------------------------------------------------
    # 4. Regional Wage Multipliers from Prevailing Wage Data
    # --------------------------------------------------------
    # Build trade-specific prevailing wage context
    pw_enrichment = {
        'source': prevailing['source'],
        'scraped_date': prevailing['scraped_date'],
        'data_period': prevailing['data_period'],
        'key_insight': prevailing['key_insight_for_ungouge'],
        'states_with_prevailing_wage_laws': prevailing['states_with_prevailing_wage_laws'],
        'states_without_prevailing_wage_laws': prevailing['states_without_prevailing_wage_laws'],
        'data_limitations': prevailing['data_limitations'],
        'regional_rates': {}
    }
    
    # Get relevant trade rates from prevailing wage data
    pw_rates = prevailing['representative_prevailing_wage_rates']
    relevant_trades = set()
    if primary_trade:
        # Map BLS trade names to prevailing wage trade names
        trade_name_map = {
            'carpenters': 'carpenter',
            'electricians': 'electrician',
            'plumbers_pipefitters_steamfitters': 'plumber',
            'roofers': 'roofer',
            'hvac_mechanics_installers': 'electrician',  # closest proxy
            'painters_construction_maintenance': 'laborer',  # closest proxy
            'carpet_floor_tile_installers': 'laborer',
            'fence_erectors': 'laborer',
            'cement_masons_concrete_finishers': 'laborer',
            'glaziers': 'laborer',
            'sheet_metal_workers': 'electrician',  # closest proxy
            'construction_laborers': 'laborer',
            'insulation_workers': 'laborer',
            'construction_equipment_operators': 'laborer',
            'drywall_ceiling_tile_installers_tapers': 'carpenter',
        }
        
        primary_pw_trade = trade_name_map.get(primary_trade, 'laborer')
        relevant_trades.add(primary_pw_trade)
        
        for state_key, state_data in pw_rates.items():
            if state_key == 'note' or not isinstance(state_data, dict):
                continue
            for area_key, area_data in state_data.items():
                if isinstance(area_data, dict) and primary_pw_trade in area_data:
                    trade_rates = area_data[primary_pw_trade]
                    pw_enrichment['regional_rates'][f"{state_key}_{area_key}"] = {
                        'trade': primary_pw_trade,
                        'hourly': trade_rates.get('hourly'),
                        'fringe': trade_rates.get('fringe'),
                        'total_package': trade_rates.get('total_package'),
                        'note': state_data.get('note', '')
                    }
    
    # Add computed multipliers
    pw_enrichment['computed_multipliers'] = {}
    for region_key, mult_data in prevailing_multipliers.items():
        pw_enrichment['computed_multipliers'][region_key] = {
            'avg_multiplier': mult_data['avg_multiplier'],
            'trade_multipliers': mult_data['multipliers'],
            'source': mult_data['source'],
            'note': mult_data['note']
        }
    
    project_data['prevailing_wage_context'] = pw_enrichment
    log_change(project_type, 'prevailing_wage_context',
               f"Added prevailing wage data for {len(pw_enrichment['regional_rates'])} metro areas")

# ============================================================
# 5. Update metadata
# ============================================================
models['metadata']['enrichment_date'] = datetime.now().strftime('%Y-%m-%d')
models['metadata']['enrichment_sources'] = [
    {
        'name': 'BLS Occupational Employment and Wage Statistics',
        'file': 'bls-labor-rates.json',
        'data_period': bls['data_period'],
        'scraped_date': bls['scraped_date']
    },
    {
        'name': 'U.S. Census Bureau Construction Spending (C30)',
        'file': 'census-construction-data.json',
        'data_period': census['data_period'],
        'scraped_date': census['scraped_date']
    },
    {
        'name': 'HomeAdvisor / Angi Cost Guides',
        'file': 'homeadvisor-cost-guides.json',
        'data_period': homeadvisor['data_period'],
        'scraped_date': homeadvisor['scraped_date']
    },
    {
        'name': 'Prevailing Wage Rates (eBacon, DOL Davis-Bacon)',
        'file': 'prevailing-wage-rates.json',
        'data_period': prevailing['data_period'],
        'scraped_date': prevailing['scraped_date']
    },
    {
        'name': 'Remodeling Magazine 2025 Cost vs. Value Report',
        'file': 'remodeling-cost-vs-value.json',
        'data_period': roi_data['data_period'],
        'scraped_date': roi_data['scraped_date']
    }
]

# Add census market context at the top level
models['metadata']['market_context'] = {
    'source': 'U.S. Census Bureau C30 Report',
    'data_period': census['data_period'],
    'total_construction_saar_billions': census['construction_spending_october_2025']['total_construction']['saar_billions'],
    'private_residential_saar_billions': census['construction_spending_october_2025']['private_construction']['residential']['saar_billions'],
    'home_improvement_estimated_billions': '365-410',
    'trend': census['market_context']['trend'],
    'relevance': census['market_context']['relevance_to_ungouge']
}

# ============================================================
# Save enriched models
# ============================================================
save_json(MODELS_FILE, models)
print(f"\n\n=== ENRICHMENT COMPLETE ===")
print(f"Total changes: {len(changes_log)}")
print(f"Models file updated: {MODELS_FILE}")

# ============================================================
# Generate summary
# ============================================================
summary = {
    'enrichment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'total_changes': len(changes_log),
    'project_types_enriched': len(models['project_types']),
    'data_sources_integrated': 5,
    'changes_by_project': {},
    'changes_detail': changes_log
}

for change in changes_log:
    pt = change['project_type']
    if pt not in summary['changes_by_project']:
        summary['changes_by_project'][pt] = []
    summary['changes_by_project'][pt].append({
        'field': change['field'],
        'description': change['description']
    })

# Summary of what was added per model
print("\n--- Changes by Project Type ---")
for pt, changes in summary['changes_by_project'].items():
    print(f"\n{pt}: {len(changes)} changes")
    for c in changes:
        print(f"  - {c['description']}")

save_json(os.path.join(BASE_DIR, 'cost-data', 'enrichment-summary.json'), summary)
print(f"\nSummary saved to: cost-data/enrichment-summary.json")
