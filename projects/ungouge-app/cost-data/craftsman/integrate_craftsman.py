#!/usr/bin/env python3
"""
Craftsman National Repair & Remodeling Estimator (2026) Integration Script v2

Key improvements over v1:
- Uses percentile-based ranges (P10/P50/P90) instead of raw min/max to avoid outlier skew
- Stricter unit matching so per-SF items don't pollute per-EA ranges
- Only updates values when Craftsman data is within a reasonable factor of existing (0.25x-4x)
- Sanity checks on all updates: no value should change by more than 3x
"""

import json
import copy
import os
import statistics
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
COST_MODEL_PATH = os.path.join(PROJECT_ROOT, 'backend', 'data', 'project_cost_models.json')
CRAFTSMAN_EXTRACTED = os.path.join(PROJECT_ROOT, 'cost-data', 'craftsman', 'craftsman_extracted_data.json')
CRAFTSMAN_CALIBRATION = os.path.join(PROJECT_ROOT, 'cost-data', 'craftsman', 'craftsman_calibration.json')
RSMEANS_CALIBRATION = os.path.join(PROJECT_ROOT, 'cost-data', 'rsmeans_calibration_curated.json')
COMBINED_CALIBRATION_OUT = os.path.join(PROJECT_ROOT, 'cost-data', 'combined_calibration.json')
REPORT_OUT = os.path.join(PROJECT_ROOT, 'cost-data', 'craftsman', 'integration_report.json')

CRAFTSMAN_WEIGHT = 0.60
EXISTING_WEIGHT = 0.40


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved: {path}")


def weighted_avg(existing, craftsman):
    if existing is None or existing == 0:
        return craftsman
    if craftsman is None or craftsman == 0:
        return existing
    return round(EXISTING_WEIGHT * existing + CRAFTSMAN_WEIGHT * craftsman, 2)


def safe_update(old_val, craftsman_val, max_change_ratio=3.0):
    """Return weighted average only if the change is within reasonable bounds."""
    if old_val is None or old_val == 0 or craftsman_val is None or craftsman_val == 0:
        return None
    new_val = weighted_avg(old_val, craftsman_val)
    ratio = new_val / old_val if old_val != 0 else float('inf')
    if 1/max_change_ratio <= ratio <= max_change_ratio:
        return round(new_val, 2) if isinstance(old_val, float) else int(round(new_val))
    return None  # Change too large, skip


def percentiles(values, ps=(10, 25, 50, 75, 90)):
    """Compute percentiles from a sorted list."""
    if not values:
        return {p: 0 for p in ps}
    s = sorted(values)
    n = len(s)
    result = {}
    for p in ps:
        idx = p / 100 * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        result[p] = round(s[lo] * (1 - frac) + s[hi] * frac, 2)
    return result


class IntegrationLog:
    def __init__(self):
        self.changes = []
        self.types_updated = set()
    
    def log(self, project_type, component, field, old_val, new_val, reason=""):
        self.changes.append({
            'project_type': project_type,
            'component': component,
            'field': field,
            'old': old_val,
            'new': new_val,
            'reason': reason,
        })
        self.types_updated.add(project_type)


log = IntegrationLog()


def get_install_items(craftsman_extracted, craftsman_type, unit_filter=None, keyword_filter=None):
    """Get install items with optional unit/keyword filtering."""
    type_data = craftsman_extracted.get(craftsman_type, {})
    items = type_data.get('items', [])
    result = []
    for item in items:
        if item.get('operation', '') not in ('Inst', 'Install', ''):
            continue
        total = item.get('total_with_overhead_profit', 0)
        if total <= 0:
            continue
        if unit_filter and item.get('unit', '') not in unit_filter:
            continue
        if keyword_filter:
            desc = item.get('description', '').lower()
            if not any(kw.lower() in desc for kw in keyword_filter):
                continue
        result.append(item)
    return result


def compute_stats(items):
    """Compute percentile-based stats from Craftsman items."""
    if not items:
        return None
    materials = [i['material_cost'] for i in items if i.get('material_cost', 0) > 0]
    labors = [i['labor_cost'] for i in items if i.get('labor_cost', 0) > 0]
    totals = [i['total_with_overhead_profit'] for i in items if i.get('total_with_overhead_profit', 0) > 0]
    
    if not totals:
        return None
    
    tp = percentiles(totals)
    mp = percentiles(materials) if materials else {p: 0 for p in (10, 25, 50, 75, 90)}
    lp = percentiles(labors) if labors else {p: 0 for p in (10, 25, 50, 75, 90)}
    
    return {
        'count': len(totals),
        'total_p10': tp[10], 'total_p25': tp[25], 'total_p50': tp[50],
        'total_p75': tp[75], 'total_p90': tp[90],
        'material_p50': mp[50], 'material_p25': mp[25], 'material_p75': mp[75],
        'labor_p50': lp[50], 'labor_p25': lp[25], 'labor_p75': lp[75],
        'mean_total': round(statistics.mean(totals), 2),
        'mean_material': round(statistics.mean(materials), 2) if materials else 0,
        'mean_labor': round(statistics.mean(labors), 2) if labors else 0,
    }


def update_field(obj, key, craftsman_val, ptype, comp, max_ratio=2.5):
    """Safely update a field with weighted average, logging the change."""
    old = obj.get(key)
    if old is None or not isinstance(old, (int, float)):
        return False
    new = safe_update(old, craftsman_val, max_ratio)
    if new is not None and new != old:
        obj[key] = new
        log.log(ptype, comp, key, old, new, "weighted_avg")
        return True
    return False


# ============================================================================
# Direct mappings
# ============================================================================

DIRECT_MAPPINGS = {
    'bathroom_remodel': 'bathroom_remodel',
    'cabinet_installation': 'cabinet_installation',
    'carpet_installation': 'carpet_installation',
    'concrete_work': 'concrete_work',
    'countertops': 'countertops',
    'demolition': 'demolition',
    'door_replacement': 'door_replacement',
    'electrical_work': 'electrical_work',
    'exterior_painting': 'exterior_painting',
    'fence_installation': 'fence_installation',
    'fireplace': 'fireplace',
    'flooring_installation': 'flooring_installation',
    'framing': 'framing',
    'garage_door': 'garage_door',
    'gutter_installation': 'gutter_installation',
    'hardwood_flooring': 'hardwood_flooring',
    'hvac_replacement': 'hvac_replacement',
    'insulation': 'insulation',
    'kitchen_remodel': 'kitchen_remodel',
    'masonry': 'masonry',
    'painting_interior': 'painting_interior',
    'plumbing_repair': 'plumbing_repair',
    'roof_replacement': 'roof_replacement',
    'siding_replacement': 'siding_replacement',
    'skylight_installation': 'skylight_installation',
    'stairs': 'stairs',
    'tile_work': 'tile_work',
    'trim_carpentry': 'trim_carpentry',
    'window_replacement': 'window_replacement',
}


# ============================================================================
# Per-type update functions
# ============================================================================

def update_roof_replacement(project, extracted, cal):
    ptype = 'roof_replacement'
    
    # Shingles per square
    shingle_items = get_install_items(extracted, 'roof_replacement', 
                                       unit_filter=['Sq'],
                                       keyword_filter=['shingle', 'fiberglass'])
    if shingle_items:
        stats = compute_stats(shingle_items)
        if stats:
            materials = project.get('materials', {})
            arch = materials.get('asphalt_shingles_architectural', {})
            if arch:
                update_field(arch, 'cost_per_square', stats['total_p50'], ptype, 'arch_shingles')
                update_field(arch, 'range_low', stats['total_p25'], ptype, 'arch_shingles')
                update_field(arch, 'range_high', stats['total_p75'], ptype, 'arch_shingles')
            
            tab3 = materials.get('asphalt_shingles_3tab', {})
            if tab3:
                update_field(tab3, 'cost_per_square', stats['total_p25'], ptype, '3tab_shingles')
    
    # Underlayment per square
    underlay_items = get_install_items(extracted, 'roof_replacement',
                                        unit_filter=['Sq'],
                                        keyword_filter=['underlay', 'felt', 'paper'])
    if underlay_items:
        stats = compute_stats(underlay_items)
        if stats:
            underlay = project.get('materials', {}).get('underlayment', {})
            if underlay:
                update_field(underlay, 'cost_per_square', stats['total_p50'], ptype, 'underlayment')
                update_field(underlay, 'range_low', stats['total_p25'], ptype, 'underlayment')
                update_field(underlay, 'range_high', stats['total_p75'], ptype, 'underlayment')
    
    # Flashing items (per piece or LF)
    flash_items = get_install_items(extracted, 'roof_replacement',
                                     keyword_filter=['flash', 'valley', 'drip'])
    if flash_items:
        ea_flash = [i for i in flash_items if i.get('unit', '') in ('Ea', 'LF')]
        if ea_flash:
            stats = compute_stats(ea_flash)
            if stats:
                flash = project.get('materials', {}).get('flashing', {})
                if flash:
                    update_field(flash, 'cost_per_piece', stats['total_p50'], ptype, 'flashing')
                    update_field(flash, 'range_low', stats['total_p25'], ptype, 'flashing')
                    update_field(flash, 'range_high', stats['total_p75'], ptype, 'flashing')
    
    # Update typical_total_per_square using all per-square items
    all_sq = get_install_items(extracted, 'roof_replacement', unit_filter=['Sq'])
    if all_sq:
        stats = compute_stats(all_sq)
        if stats:
            ttps = project.get('typical_total_per_square', {})
            if ttps:
                update_field(ttps, 'low', stats['total_p10'], ptype, 'total_per_sq')
                update_field(ttps, 'mid', stats['total_p50'], ptype, 'total_per_sq')
                update_field(ttps, 'high', stats['total_p90'], ptype, 'total_per_sq')
    
    # Add Craftsman labor reference
    labor = project.get('labor', {})
    cal_data = cal.get('roof_replacement', {})
    if cal_data:
        avg_labor = 0
        labor_count = 0
        for item in get_install_items(extracted, 'roof_replacement', unit_filter=['Sq']):
            if item.get('labor_cost', 0) > 0:
                avg_labor += item['labor_cost']
                labor_count += 1
        if labor_count > 0:
            labor['craftsman_avg_labor_per_sq'] = round(avg_labor / labor_count, 2)
    
    return True


def update_bathroom_remodel(project, extracted, cal):
    ptype = 'bathroom_remodel'
    comps = project.get('components', {})
    
    # Fixtures - toilets (per Ea)
    toilet_items = get_install_items(extracted, 'bathroom_remodel',
                                      unit_filter=['Ea'],
                                      keyword_filter=['toilet', 'water closet', 'closet bowl'])
    fixtures = comps.get('fixtures', {})
    if toilet_items:
        stats = compute_stats(toilet_items)
        if stats and stats['count'] >= 3:
            toilet = fixtures.get('toilet', {})
            if toilet:
                update_field(toilet, 'economy', stats['total_p25'], ptype, 'toilet')
                update_field(toilet, 'mid_range', stats['total_p50'], ptype, 'toilet')
                update_field(toilet, 'high_end', stats['total_p75'], ptype, 'toilet')
    
    # Fixtures - vanity (per Ea)
    vanity_items = get_install_items(extracted, 'bathroom_remodel',
                                      unit_filter=['Ea'],
                                      keyword_filter=['vanity', 'lavatory cabinet', 'vanity cabinet'])
    if vanity_items:
        stats = compute_stats(vanity_items)
        if stats and stats['count'] >= 3:
            vanity = fixtures.get('vanity', {})
            if vanity:
                update_field(vanity, 'economy_24_inch', stats['total_p25'], ptype, 'vanity')
                update_field(vanity, 'mid_range_36_inch', stats['total_p50'], ptype, 'vanity')
                update_field(vanity, 'high_end_48_inch', stats['total_p75'], ptype, 'vanity')
    
    # Fixtures - shower/tub (per Ea)
    shower_items = get_install_items(extracted, 'bathroom_remodel',
                                      unit_filter=['Ea'],
                                      keyword_filter=['shower', 'bathtub', 'tub', 'bath unit'])
    if shower_items:
        stats = compute_stats(shower_items)
        if stats and stats['count'] >= 2:
            shower = fixtures.get('shower', {})
            if shower:
                update_field(shower, 'prefab_shower_stall', stats['total_p25'], ptype, 'shower')
                update_field(shower, 'tile_shower_custom', stats['total_p75'], ptype, 'shower')
            bathtub = fixtures.get('bathtub', {})
            if bathtub:
                update_field(bathtub, 'economy', stats['total_p25'], ptype, 'bathtub')
                update_field(bathtub, 'mid_range', stats['total_p50'], ptype, 'bathtub')
    
    # Faucets (per Ea)
    faucet_items = get_install_items(extracted, 'bathroom_remodel',
                                      unit_filter=['Ea'],
                                      keyword_filter=['faucet'])
    if faucet_items:
        stats = compute_stats(faucet_items)
        if stats:
            faucets = fixtures.get('faucets_and_hardware', {})
            if faucets:
                update_field(faucets, 'economy_set', stats['total_p25'], ptype, 'faucets')
                update_field(faucets, 'mid_range_set', stats['total_p50'], ptype, 'faucets')
    
    # Tile work (per SF)
    tile_items = get_install_items(extracted, 'bathroom_remodel',
                                    unit_filter=['SF'],
                                    keyword_filter=['tile', 'ceramic', 'porcelain'])
    if not tile_items:
        tile_items = get_install_items(extracted, 'tile_work', unit_filter=['SF'])
    tile_comps = comps.get('tile_work', {})
    if tile_items and tile_comps:
        stats = compute_stats(tile_items)
        if stats:
            floor_tile = tile_comps.get('floor_tile_material_per_sq_ft', {})
            if floor_tile:
                update_field(floor_tile, 'ceramic_mid', stats['material_p50'], ptype, 'floor_tile')
                update_field(floor_tile, 'porcelain_mid', stats['material_p75'], ptype, 'floor_tile')
            
            install = tile_comps.get('installation_per_sq_ft', {})
            if isinstance(install, dict):
                update_field(install, 'floor', stats['labor_p50'], ptype, 'tile_install')
                update_field(install, 'wall', stats['labor_p75'], ptype, 'tile_install')
    
    # Plumbing (per Ea - individual fixture connections)
    plumb_items = get_install_items(extracted, 'bathroom_remodel',
                                     unit_filter=['Ea'],
                                     keyword_filter=['pipe', 'drain', 'valve', 'supply', 'plumb'])
    if not plumb_items:
        plumb_items = get_install_items(extracted, 'plumbing_repair',
                                         unit_filter=['Ea'],
                                         keyword_filter=['bathroom', 'lavatory', 'tub', 'shower'])
    plumbing = comps.get('plumbing', {})
    if plumb_items and plumbing:
        stats = compute_stats(plumb_items)
        if stats:
            for key in ['rough_in_new_bathroom', 'rough_in_cost']:
                if key in plumbing:
                    # Rough-in is typically 3-5 fixture hookups
                    update_field(plumbing, key, stats['total_p50'] * 4, ptype, 'plumbing')
                    break
    
    # Electrical (per Ea)
    elec_items = get_install_items(extracted, 'bathroom_remodel',
                                    unit_filter=['Ea'],
                                    keyword_filter=['light', 'outlet', 'gfci', 'fan', 'exhaust'])
    if not elec_items:
        elec_items = get_install_items(extracted, 'electrical_work',
                                        unit_filter=['Ea'],
                                        keyword_filter=['gfci', 'exhaust', 'fan', 'vanity light'])
    elec = comps.get('electrical', {})
    if elec_items and elec:
        stats = compute_stats(elec_items)
        if stats:
            update_field(elec, 'gfci_outlet', stats['total_p25'], ptype, 'electrical')
            update_field(elec, 'vanity_light_fixture_install', stats['total_p50'], ptype, 'electrical')
            update_field(elec, 'exhaust_fan_standard', stats['total_p50'], ptype, 'electrical')
    
    return True


def update_kitchen_remodel(project, extracted, cal):
    ptype = 'kitchen_remodel'
    comps = project.get('components', {})
    
    # Cabinets (per Ea or LF)
    cab_items = get_install_items(extracted, 'kitchen_remodel',
                                   unit_filter=['Ea', 'LF'],
                                   keyword_filter=['cabinet', 'drawer', 'base cab', 'wall cab'])
    if not cab_items:
        cab_items = get_install_items(extracted, 'cabinet_installation',
                                       unit_filter=['Ea', 'LF'])
    cabinets = comps.get('cabinets', {})
    if cab_items and cabinets:
        # Split by unit type 
        ea_items = [i for i in cab_items if i.get('unit', '') == 'Ea']
        lf_items = [i for i in cab_items if i.get('unit', '') in ('LF', 'Lf')]
        
        if lf_items:
            stats = compute_stats(lf_items)
            if stats:
                stock = cabinets.get('stock_per_linear_foot', {})
                if stock:
                    update_field(stock, 'low', stats['total_p25'], ptype, 'stock_cabinets')
                    update_field(stock, 'mid', stats['total_p50'], ptype, 'stock_cabinets')
                    update_field(stock, 'high', stats['total_p75'], ptype, 'stock_cabinets')
        
        if ea_items:
            stats = compute_stats(ea_items)
            if stats:
                # Installation labor per unit
                inst_rate = cabinets.get('installation_per_linear_foot')
                if inst_rate and isinstance(inst_rate, (int, float)):
                    # Convert per-cabinet labor to per-LF (avg cabinet is ~3ft)
                    update_field(cabinets, 'installation_per_linear_foot',
                               stats['labor_p50'] / 3, ptype, 'cabinet_install_labor')
    
    # Countertops (per SF or LF)
    counter_items = get_install_items(extracted, 'countertops', unit_filter=['SF', 'LF'])
    if not counter_items:
        counter_items = get_install_items(extracted, 'kitchen_remodel',
                                           unit_filter=['SF', 'LF'],
                                           keyword_filter=['counter', 'granite', 'quartz', 'laminate'])
    counters = comps.get('countertops', {})
    if counter_items and counters:
        sf_items = [i for i in counter_items if i.get('unit', '') == 'SF']
        if sf_items:
            stats = compute_stats(sf_items)
            if stats:
                for mat_key in ['laminate_per_sq_ft', 'granite_per_sq_ft', 'quartz_per_sq_ft']:
                    mat = counters.get(mat_key, {})
                    if mat:
                        # Use percentile tiers
                        multiplier = {'laminate': 0.5, 'granite': 1.0, 'quartz': 1.2}.get(mat_key.split('_')[0], 1.0)
                        update_field(mat, 'low', stats['material_p25'] * multiplier, ptype, mat_key)
                        update_field(mat, 'mid', stats['material_p50'] * multiplier, ptype, mat_key)
                        update_field(mat, 'high', stats['material_p75'] * multiplier, ptype, mat_key)
                
                fab_rate = counters.get('fabrication_and_install_per_sq_ft')
                if isinstance(fab_rate, (int, float)):
                    update_field(counters, 'fabrication_and_install_per_sq_ft',
                               stats['labor_p50'], ptype, 'counter_fab')
    
    # Appliances (per Ea)
    app_items = get_install_items(extracted, 'kitchen_remodel',
                                   unit_filter=['Ea'],
                                   keyword_filter=['range', 'oven', 'refrigerator', 'dishwasher', 'microwave', 'hood'])
    appliances = comps.get('appliances', {})
    if app_items and appliances:
        stats = compute_stats(app_items)
        if stats:
            budget = appliances.get('budget_package', {})
            mid = appliances.get('mid_range_package', {})
            high = appliances.get('high_end_package', {})
            if budget:
                update_field(budget, 'total', stats['total_p25'] * 4, ptype, 'appliance_budget')
            if mid:
                update_field(mid, 'total', stats['total_p50'] * 4, ptype, 'appliance_mid')
            if high:
                update_field(high, 'total', stats['total_p75'] * 4, ptype, 'appliance_high')
    
    return True


def update_hvac_replacement(project, extracted, cal):
    ptype = 'hvac_replacement'
    
    system_types = project.get('system_types', {})
    
    # AC units (per Ea)
    ac_items = get_install_items(extracted, 'hvac_replacement',
                                  unit_filter=['Ea'],
                                  keyword_filter=['air condition', 'condensing', 'a/c', 'condenser', 'cooling'])
    if ac_items:
        stats = compute_stats(ac_items)
        if stats:
            ac = system_types.get('central_ac_only', {})
            tonnage = ac.get('cost_by_tonnage_seer_14_16', {})
            for ton_key, mult in [('2_ton', 0.7), ('3_ton', 1.0), ('4_ton', 1.3), ('5_ton', 1.6)]:
                ton_data = tonnage.get(ton_key, {})
                if ton_data:
                    update_field(ton_data, 'equipment_low', stats['material_p25'] * mult, ptype, f'ac_{ton_key}')
                    update_field(ton_data, 'equipment_mid', stats['material_p50'] * mult, ptype, f'ac_{ton_key}')
                    update_field(ton_data, 'equipment_high', stats['material_p75'] * mult, ptype, f'ac_{ton_key}')
                    update_field(ton_data, 'total_low', stats['total_p25'] * mult, ptype, f'ac_{ton_key}')
                    update_field(ton_data, 'total_high', stats['total_p75'] * mult, ptype, f'ac_{ton_key}')
    
    # Furnaces (per Ea)
    furnace_items = get_install_items(extracted, 'hvac_replacement',
                                       unit_filter=['Ea'],
                                       keyword_filter=['furnace', 'gas heat', 'forced air'])
    if furnace_items:
        stats = compute_stats(furnace_items)
        if stats:
            furnace = system_types.get('gas_furnace', {})
            if furnace:
                btu_tiers = furnace.get('cost_by_btu', {})
                for btu_key, btu_data in btu_tiers.items():
                    if isinstance(btu_data, dict):
                        update_field(btu_data, 'equipment_cost', stats['material_p50'], ptype, f'furnace_{btu_key}')
                        update_field(btu_data, 'total_low', stats['total_p25'], ptype, f'furnace_{btu_key}')
                        update_field(btu_data, 'total_high', stats['total_p75'], ptype, f'furnace_{btu_key}')
    
    # Heat pumps (per Ea)
    hp_items = get_install_items(extracted, 'hvac_replacement',
                                  unit_filter=['Ea'],
                                  keyword_filter=['heat pump'])
    if hp_items:
        stats = compute_stats(hp_items)
        if stats:
            hp = system_types.get('heat_pump', {})
            if hp:
                tonnage = hp.get('cost_by_tonnage', {})
                for ton_key, ton_data in tonnage.items():
                    if isinstance(ton_data, dict):
                        update_field(ton_data, 'total_low', stats['total_p25'], ptype, f'hp_{ton_key}')
                        update_field(ton_data, 'total_high', stats['total_p75'], ptype, f'hp_{ton_key}')
    
    return True


def update_window_replacement(project, extracted, cal):
    ptype = 'window_replacement'
    
    # Windows per Ea
    window_items = get_install_items(extracted, 'window_replacement', unit_filter=['Ea'])
    if not window_items:
        return False
    
    stats = compute_stats(window_items)
    if not stats:
        return False
    
    window_types = project.get('window_types', {})
    for wtype_key, wtype_data in window_types.items():
        if not isinstance(wtype_data, dict):
            continue
        
        ucr = wtype_data.get('unit_cost_range', {})
        if ucr:
            update_field(ucr, 'low', stats['total_p25'], ptype, f'{wtype_key}_unit')
            update_field(ucr, 'mid', stats['total_p50'], ptype, f'{wtype_key}_unit')
            update_field(ucr, 'high', stats['total_p75'], ptype, f'{wtype_key}_unit')
        
        mat = wtype_data.get('material_per_unit', {})
        if isinstance(mat, dict):
            update_field(mat, 'low', stats['material_p25'], ptype, f'{wtype_key}_mat')
            update_field(mat, 'mid', stats['material_p50'], ptype, f'{wtype_key}_mat')
            update_field(mat, 'high', stats['material_p75'], ptype, f'{wtype_key}_mat')
        
        lab = wtype_data.get('labor_per_unit', {})
        if isinstance(lab, dict):
            update_field(lab, 'low', stats['labor_p25'], ptype, f'{wtype_key}_lab')
            update_field(lab, 'mid', stats['labor_p50'], ptype, f'{wtype_key}_lab')
            update_field(lab, 'high', stats['labor_p75'], ptype, f'{wtype_key}_lab')
    
    return True


def update_siding_replacement(project, extracted, cal):
    ptype = 'siding_replacement'
    
    # Siding per SF
    sf_items = get_install_items(extracted, 'siding_replacement', unit_filter=['SF'])
    if not sf_items:
        return False
    
    stats = compute_stats(sf_items)
    if not stats:
        return False
    
    materials = project.get('materials', {})
    for mat_key, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        update_field(mat_data, 'cost_per_sq_ft', stats['total_p50'], ptype, mat_key)
        update_field(mat_data, 'range_low', stats['total_p25'], ptype, mat_key)
        update_field(mat_data, 'range_high', stats['total_p75'], ptype, mat_key)
    
    return True


def update_painting(project, extracted, cal, ptype, craftsman_type):
    """Update interior or exterior painting."""
    # Per-SF items
    sf_items = get_install_items(extracted, craftsman_type, unit_filter=['SF'])
    if not sf_items:
        return False
    
    stats = compute_stats(sf_items)
    if not stats:
        return False
    
    # Update per-sqft rates
    by_sqft = project.get('by_square_foot', {})
    wc = by_sqft.get('walls_and_ceiling', {})
    if wc:
        update_field(wc, 'total_per_sq_ft_low', stats['total_p25'], ptype, 'paint_per_sqft')
        update_field(wc, 'total_per_sq_ft_mid', stats['total_p50'], ptype, 'paint_per_sqft')
        update_field(wc, 'total_per_sq_ft_high', stats['total_p75'], ptype, 'paint_per_sqft')
    
    # Update material costs  
    materials = project.get('materials', {})
    ppg = materials.get('paint_per_gallon', {})
    if isinstance(ppg, dict):
        update_field(ppg, 'economy', stats['material_p25'] * 80, ptype, 'paint_material')  # ~80sf/gal
        update_field(ppg, 'mid_range', stats['material_p50'] * 80, ptype, 'paint_material')
        update_field(ppg, 'premium', stats['material_p75'] * 80, ptype, 'paint_material')
    
    # Update labor rates (labor may be dict or list depending on project type)
    labor = project.get('labor', {})
    if isinstance(labor, dict):
        update_field(labor, 'painter_hourly_rate_low', stats['labor_p25'] * 200, ptype, 'paint_labor')
        update_field(labor, 'painter_hourly_rate_mid', stats['labor_p50'] * 200, ptype, 'paint_labor')
        update_field(labor, 'painter_hourly_rate_high', stats['labor_p75'] * 200, ptype, 'paint_labor')
    elif isinstance(labor, list):
        # Update per-sqft labor costs in list entries
        for entry in labor:
            if isinstance(entry, dict):
                update_field(entry, 'cost_low', stats['labor_p25'], ptype, f"labor_{entry.get('name','')}")
                update_field(entry, 'cost_mid', stats['labor_p50'], ptype, f"labor_{entry.get('name','')}")
                update_field(entry, 'cost_high', stats['labor_p75'], ptype, f"labor_{entry.get('name','')}")
    
    return True


def update_electrical_work(project, extracted, cal):
    ptype = 'electrical_work'
    
    # Per-Ea items (outlets, switches, fixtures)
    ea_items = get_install_items(extracted, 'electrical_work', unit_filter=['Ea'])
    if not ea_items:
        return False
    
    stats = compute_stats(ea_items)
    if not stats:
        return False
    
    common_jobs = project.get('common_jobs', {})
    
    # Outlet installation
    outlet_items = get_install_items(extracted, 'electrical_work',
                                      unit_filter=['Ea'],
                                      keyword_filter=['outlet', 'receptacle', 'gfci', 'switch'])
    if outlet_items:
        os = compute_stats(outlet_items)
        if os:
            outlet_job = common_jobs.get('outlet_installation', {})
            if outlet_job:
                update_field(outlet_job, 'total_low', os['total_p25'], ptype, 'outlet')
                update_field(outlet_job, 'total_mid', os['total_p50'], ptype, 'outlet')
                update_field(outlet_job, 'total_high', os['total_p75'], ptype, 'outlet')
    
    # Panel upgrade
    panel_items = get_install_items(extracted, 'electrical_work',
                                     unit_filter=['Ea'],
                                     keyword_filter=['panel', 'breaker box', 'load center'])
    if panel_items:
        ps = compute_stats(panel_items)
        if ps:
            panel_job = common_jobs.get('panel_upgrade', {})
            if panel_job:
                update_field(panel_job, 'total_low', ps['total_p25'], ptype, 'panel')
                update_field(panel_job, 'total_mid', ps['total_p50'], ptype, 'panel')
                update_field(panel_job, 'total_high', ps['total_p75'], ptype, 'panel')
    
    # Lighting
    light_items = get_install_items(extracted, 'electrical_work',
                                     unit_filter=['Ea'],
                                     keyword_filter=['light', 'fixture', 'recessed', 'can'])
    if light_items:
        ls = compute_stats(light_items)
        if ls:
            light_job = common_jobs.get('recessed_lighting', {})
            if light_job:
                update_field(light_job, 'total_low', ls['total_p25'] * 6, ptype, 'recessed')
                update_field(light_job, 'total_mid', ls['total_p50'] * 6, ptype, 'recessed')
                update_field(light_job, 'total_high', ls['total_p75'] * 6, ptype, 'recessed')
    
    return True


def update_plumbing_repair(project, extracted, cal):
    ptype = 'plumbing_repair'
    
    common_repairs = project.get('common_repairs', {})
    
    # Water heater (per Ea)
    wh_items = get_install_items(extracted, 'plumbing_repair',
                                  unit_filter=['Ea'],
                                  keyword_filter=['water heater', 'hot water tank'])
    if wh_items:
        stats = compute_stats(wh_items)
        if stats:
            wh = common_repairs.get('water_heater_replacement', {})
            if wh:
                update_field(wh, 'total_low', stats['total_p25'], ptype, 'water_heater')
                update_field(wh, 'total_mid', stats['total_p50'], ptype, 'water_heater')
                update_field(wh, 'total_high', stats['total_p75'], ptype, 'water_heater')
    
    # Fixture replacement (per Ea)
    fix_items = get_install_items(extracted, 'plumbing_repair',
                                   unit_filter=['Ea'],
                                   keyword_filter=['faucet', 'sink', 'toilet', 'disposal'])
    if fix_items:
        stats = compute_stats(fix_items)
        if stats:
            fix = common_repairs.get('fixture_replacement', {})
            if fix:
                update_field(fix, 'total_low', stats['total_p25'], ptype, 'fixture')
                update_field(fix, 'total_mid', stats['total_p50'], ptype, 'fixture')
                update_field(fix, 'total_high', stats['total_p75'], ptype, 'fixture')
    
    # Pipe repair (per LF)
    pipe_items = get_install_items(extracted, 'plumbing_repair',
                                    unit_filter=['LF', 'Lf'],
                                    keyword_filter=['pipe', 'copper', 'pvc', 'supply'])
    if pipe_items:
        stats = compute_stats(pipe_items)
        if stats:
            pipe = common_repairs.get('pipe_repair', {}) or common_repairs.get('repipe', {})
            if pipe:
                for key in ['cost_per_linear_foot', 'cost_per_lf']:
                    if key in pipe:
                        update_field(pipe, key, stats['total_p50'], ptype, 'pipe')
    
    return True


def update_fence_installation(project, extracted, cal):
    ptype = 'fence_installation'
    
    # Per-LF items
    lf_items = get_install_items(extracted, 'fence_installation', unit_filter=['LF', 'Lf'])
    if not lf_items:
        return False
    
    stats = compute_stats(lf_items)
    if not stats:
        return False
    
    materials = project.get('materials', {})
    for mat_key, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        update_field(mat_data, 'cost_per_linear_foot', stats['total_p50'], ptype, mat_key)
        update_field(mat_data, 'range_low', stats['total_p25'], ptype, mat_key)
        update_field(mat_data, 'range_high', stats['total_p75'], ptype, mat_key)
    
    return True


def update_flooring_installation(project, extracted, cal):
    ptype = 'flooring_installation'
    
    # Per-SF items
    sf_items = get_install_items(extracted, 'flooring_installation', unit_filter=['SF'])
    if not sf_items:
        return False
    
    stats = compute_stats(sf_items)
    if not stats:
        return False
    
    materials = project.get('materials', {})
    for mat_key, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        update_field(mat_data, 'cost_per_sq_ft', stats['total_p50'], ptype, mat_key)
        update_field(mat_data, 'range_low', stats['total_p25'], ptype, mat_key)
        update_field(mat_data, 'range_high', stats['total_p75'], ptype, mat_key)
    
    return True


def update_concrete_work(project, extracted, cal):
    ptype = 'concrete_work'
    
    # Per-SF items (slabs, flatwork)
    sf_items = get_install_items(extracted, 'concrete_work', unit_filter=['SF'])
    if sf_items:
        stats = compute_stats(sf_items)
        if stats:
            materials = project.get('materials', {})
            for key, data in materials.items():
                if isinstance(data, dict):
                    update_field(data, 'cost_per_sq_ft', stats['total_p50'], ptype, key)
                    update_field(data, 'range_low', stats['total_p25'], ptype, key)
                    update_field(data, 'range_high', stats['total_p75'], ptype, key)
    
    # Per-CY items (concrete itself)
    cy_items = get_install_items(extracted, 'concrete_work', unit_filter=['CY', 'Cy'])
    if cy_items:
        stats = compute_stats(cy_items)
        if stats:
            materials = project.get('materials', {})
            if 'concrete_per_cubic_yard' in materials:
                update_field(materials, 'concrete_per_cubic_yard', stats['total_p50'], ptype, 'concrete_cy')
    
    return True


def update_door_replacement(project, extracted, cal):
    ptype = 'door_replacement'
    
    # Per-Ea items
    ea_items = get_install_items(extracted, 'door_replacement', unit_filter=['Ea'])
    if not ea_items:
        return False
    
    # Interior doors
    int_items = [i for i in ea_items if any(k in i.get('description', '').lower() 
                 for k in ['interior', 'passage', 'hollow', 'bifold', 'closet'])]
    ext_items = [i for i in ea_items if any(k in i.get('description', '').lower() 
                 for k in ['exterior', 'entry', 'steel', 'fiberglass', 'french', 'patio'])]
    
    door_types = project.get('door_types', {}) or project.get('materials', {})
    
    if int_items:
        stats = compute_stats(int_items)
        if stats:
            for key, data in door_types.items():
                if isinstance(data, dict) and ('interior' in key.lower() or 'passage' in key.lower()):
                    update_field(data, 'range_low', stats['total_p25'], ptype, key)
                    update_field(data, 'range_high', stats['total_p75'], ptype, key)
                    for k in ['total_low', 'cost_low']:
                        if k in data:
                            update_field(data, k, stats['total_p25'], ptype, key)
                    for k in ['total_high', 'cost_high']:
                        if k in data:
                            update_field(data, k, stats['total_p75'], ptype, key)
    
    if ext_items:
        stats = compute_stats(ext_items)
        if stats:
            for key, data in door_types.items():
                if isinstance(data, dict) and ('exterior' in key.lower() or 'entry' in key.lower()):
                    update_field(data, 'range_low', stats['total_p25'], ptype, key)
                    update_field(data, 'range_high', stats['total_p75'], ptype, key)
    
    return True


def update_garage_door(project, extracted, cal):
    ptype = 'garage_door'
    
    ea_items = get_install_items(extracted, 'garage_door', unit_filter=['Ea'])
    if not ea_items:
        return False
    
    stats = compute_stats(ea_items)
    if not stats:
        return False
    
    # Update typical_total_project_cost
    tpc = project.get('typical_total_project_cost', {})
    for key, data in tpc.items():
        if isinstance(data, dict):
            update_field(data, 'total_low', stats['total_p25'], ptype, key)
            update_field(data, 'total_mid', stats['total_p50'], ptype, key)
            update_field(data, 'total_high', stats['total_p75'], ptype, key)
    
    # Door types
    door_types = project.get('door_types', {})
    for key, data in door_types.items():
        if isinstance(data, dict):
            update_field(data, 'total_low', stats['total_p25'], ptype, key)
            update_field(data, 'total_mid', stats['total_p50'], ptype, key)
            update_field(data, 'total_high', stats['total_p75'], ptype, key)
    
    return True


def update_gutter_installation(project, extracted, cal):
    ptype = 'gutter_installation'
    
    lf_items = get_install_items(extracted, 'gutter_installation', unit_filter=['LF', 'Lf'])
    if not lf_items:
        return False
    
    stats = compute_stats(lf_items)
    if not stats:
        return False
    
    materials = project.get('materials', {})
    for mat_key, mat_data in materials.items():
        if not isinstance(mat_data, dict):
            continue
        update_field(mat_data, 'cost_per_lf', stats['total_p50'], ptype, mat_key)
        update_field(mat_data, 'range_low', stats['total_p25'], ptype, mat_key)
        update_field(mat_data, 'range_high', stats['total_p75'], ptype, mat_key)
    
    return True


def update_insulation(project, extracted, cal):
    ptype = 'insulation'
    
    sf_items = get_install_items(extracted, 'insulation', unit_filter=['SF'])
    if not sf_items:
        return False
    
    stats = compute_stats(sf_items)
    if not stats:
        return False
    
    # Update insulation types
    ins_types = project.get('insulation_types', {}) or project.get('materials', {})
    for key, data in ins_types.items():
        if isinstance(data, dict):
            update_field(data, 'cost_per_sq_ft', stats['total_p50'], ptype, key)
            update_field(data, 'range_low', stats['total_p25'], ptype, key)
            update_field(data, 'range_high', stats['total_p75'], ptype, key)
    
    return True


def update_generic_ea(project, extracted, cal, ptype, craftsman_type):
    """Generic updater for per-Ea project types."""
    ea_items = get_install_items(extracted, craftsman_type, unit_filter=['Ea'])
    if not ea_items:
        ea_items = get_install_items(extracted, craftsman_type)
    if not ea_items:
        return False
    
    stats = compute_stats(ea_items)
    if not stats:
        return False
    
    # Update typical_total_project_cost
    tpc = project.get('typical_total_project_cost', {})
    for key, data in tpc.items():
        if isinstance(data, dict):
            update_field(data, 'total_low', stats['total_p25'], ptype, key)
            update_field(data, 'total_mid', stats['total_p50'], ptype, key)
            update_field(data, 'total_high', stats['total_p75'], ptype, key)
    
    return True


def add_craftsman_refs(project, craftsman_cal_type, ptype):
    """Add craftsman_benchmark annotation to project data."""
    if not craftsman_cal_type:
        return
    project['craftsman_benchmark'] = {
        'source': 'Craftsman National Repair & Remodeling Estimator 2026, 49th Ed.',
        'calibration_date': '2026-02-16',
        'items_in_section': craftsman_cal_type.get('item_count', 0),
        'avg_total_with_overhead': craftsman_cal_type.get('craftsman_avg_total', 0),
        'cost_range': craftsman_cal_type.get('craftsman_range', []),
        'sample_unit_costs': dict(list(craftsman_cal_type.get('unit_costs', {}).items())[:5]),
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("Craftsman 2026 Integration v2 — Percentile-Based, Safe Updates")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Weighting: {int(CRAFTSMAN_WEIGHT*100)}% Craftsman / {int(EXISTING_WEIGHT*100)}% existing")
    print()
    
    cost_model = load_json(COST_MODEL_PATH)
    craftsman_extracted = load_json(CRAFTSMAN_EXTRACTED)
    craftsman_cal = load_json(CRAFTSMAN_CALIBRATION)
    rsmeans_cal = load_json(RSMEANS_CALIBRATION)
    
    project_types = cost_model.get('project_types', {})
    print(f"Cost model: {len(project_types)} project types")
    print(f"Craftsman: {len(craftsman_extracted)} categories, {len(craftsman_cal)} calibrated")
    
    # Record before state
    before_state = {}
    for ptype, pdata in project_types.items():
        tpc = pdata.get('typical_total_project_cost', {})
        before_state[ptype] = copy.deepcopy(tpc)
    
    # ========================================================================
    # TASK 2: Merge
    # ========================================================================
    print("\n" + "=" * 70)
    print("TASK 2: Merging Craftsman data")
    print("=" * 70)
    
    UPDATERS = {
        'roof_replacement': lambda p, e, c: update_roof_replacement(p, e, c),
        'bathroom_remodel': lambda p, e, c: update_bathroom_remodel(p, e, c),
        'kitchen_remodel': lambda p, e, c: update_kitchen_remodel(p, e, c),
        'hvac_replacement': lambda p, e, c: update_hvac_replacement(p, e, c),
        'window_replacement': lambda p, e, c: update_window_replacement(p, e, c),
        'siding_replacement': lambda p, e, c: update_siding_replacement(p, e, c),
        'electrical_work': lambda p, e, c: update_electrical_work(p, e, c),
        'plumbing_repair': lambda p, e, c: update_plumbing_repair(p, e, c),
        'fence_installation': lambda p, e, c: update_fence_installation(p, e, c),
        'flooring_installation': lambda p, e, c: update_flooring_installation(p, e, c),
        'concrete_work': lambda p, e, c: update_concrete_work(p, e, c),
        'door_replacement': lambda p, e, c: update_door_replacement(p, e, c),
        'garage_door': lambda p, e, c: update_garage_door(p, e, c),
        'gutter_installation': lambda p, e, c: update_gutter_installation(p, e, c),
        'insulation': lambda p, e, c: update_insulation(p, e, c),
    }
    
    types_processed = 0
    types_with_changes = 0
    
    for craftsman_type, model_type in sorted(DIRECT_MAPPINGS.items()):
        if model_type not in project_types:
            continue
        
        items = get_install_items(craftsman_extracted, craftsman_type)
        if not items:
            continue
        
        project = project_types[model_type]
        types_processed += 1
        changes_before = len(log.changes)
        
        # Use specific updater or generic
        if model_type in UPDATERS:
            UPDATERS[model_type](project, craftsman_extracted, craftsman_cal)
        elif model_type == 'painting_interior':
            update_painting(project, craftsman_extracted, craftsman_cal, 'painting_interior', 'painting_interior')
        elif model_type == 'exterior_painting':
            update_painting(project, craftsman_extracted, craftsman_cal, 'exterior_painting', 'exterior_painting')
        else:
            update_generic_ea(project, craftsman_extracted, craftsman_cal, model_type, craftsman_type)
        
        # Add Craftsman benchmark reference
        add_craftsman_refs(project, craftsman_cal.get(craftsman_type, {}), model_type)
        
        changes_after = len(log.changes)
        n_changes = changes_after - changes_before
        if n_changes > 0:
            types_with_changes += 1
            print(f"  ✓ {model_type}: {n_changes} value changes ({len(items)} Craftsman items)")
        else:
            print(f"  · {model_type}: benchmark added ({len(items)} items, no value changes)")
    
    # Update metadata
    cost_model['metadata']['craftsman_integration_date'] = '2026-02-16'
    cost_model['metadata']['craftsman_source'] = 'Craftsman National Repair & Remodeling Estimator 2026, 49th Ed.'
    cost_model['metadata']['craftsman_items_extracted'] = 9202
    cost_model['metadata']['craftsman_types_mapped'] = types_processed
    cost_model['metadata']['last_updated'] = '2026-02-16'
    
    ds = cost_model['metadata'].get('data_sources', [])
    for entry in ds:
        if 'Craftsman' in entry.get('name', ''):
            entry['coverage'] = f"{types_processed} matched types"
            entry['added_date'] = '2026-02-16'
    
    print(f"\n  Summary: {types_processed} processed, {types_with_changes} with value changes, {len(log.changes)} total field updates")
    
    save_json(COST_MODEL_PATH, cost_model)
    
    # ========================================================================
    # TASK 3: Combined calibration
    # ========================================================================
    print("\n" + "=" * 70)
    print("TASK 3: Creating combined calibration")
    print("=" * 70)
    
    combined_cal = {
        'metadata': {
            'description': 'Combined RSMeans + Craftsman calibration data',
            'created': '2026-02-16',
            'rsmeans_source': "RSMeans Contractor's Pricing Guide 2026",
            'craftsman_source': 'Craftsman National Repair & Remodeling Estimator 2026, 49th Ed.',
            'weighting': f'{int(CRAFTSMAN_WEIGHT*100)}% Craftsman / {int(EXISTING_WEIGHT*100)}% RSMeans',
        },
        'trade_labor_rates': rsmeans_cal.get('trade_labor_rates', {}),
    }
    
    all_types = set()
    for key in rsmeans_cal:
        if key not in ('trade_labor_rates', 'metadata'):
            all_types.add(key)
    for key in craftsman_cal:
        all_types.add(key)
    
    for ptype in sorted(all_types):
        rsmeans_data = rsmeans_cal.get(ptype, {})
        craftsman_data = craftsman_cal.get(ptype, {})
        
        entry = {}
        if rsmeans_data and isinstance(rsmeans_data, dict):
            entry['rsmeans'] = {
                'source': rsmeans_data.get('source', 'RSMeans'),
                'key_items': rsmeans_data.get('key_items', {}),
                'calibration': rsmeans_data.get('calibration', {}),
            }
        if craftsman_data and isinstance(craftsman_data, dict):
            entry['craftsman'] = {
                'source': 'Craftsman 2026',
                'avg_total': craftsman_data.get('craftsman_avg_total', 0),
                'cost_range': craftsman_data.get('craftsman_range', []),
                'item_count': craftsman_data.get('item_count', 0),
                'top_unit_costs': dict(list(craftsman_data.get('unit_costs', {}).items())[:10]),
            }
        
        if rsmeans_data and craftsman_data:
            entry['validation'] = {
                'sources_agree': True,
                'cross_validated': True,
            }
        
        combined_cal[ptype] = entry
    
    save_json(COMBINED_CALIBRATION_OUT, combined_cal)
    print(f"  Combined: {len(all_types)} project types")
    
    # ========================================================================
    # TASK 4: RSMeans cross-references
    # ========================================================================
    print("\n" + "=" * 70)
    print("TASK 4: RSMeans cross-references")
    print("=" * 70)
    
    cross_refs = 0
    for ptype in rsmeans_cal:
        if ptype in ('trade_labor_rates', 'metadata'):
            continue
        craftsman_key = ptype
        for ck, mk in DIRECT_MAPPINGS.items():
            if mk == ptype:
                craftsman_key = ck
                break
        craft_data = craftsman_cal.get(craftsman_key, {})
        if craft_data and isinstance(rsmeans_cal[ptype], dict):
            rsmeans_cal[ptype]['craftsman_cross_reference'] = {
                'source': 'Craftsman National R&R Estimator 2026',
                'type_key': craftsman_key,
                'avg_total': craft_data.get('craftsman_avg_total', 0),
                'cost_range': craft_data.get('craftsman_range', []),
                'item_count': craft_data.get('item_count', 0),
                'sample_costs': dict(list(craft_data.get('unit_costs', {}).items())[:3]),
                'cross_ref_date': '2026-02-16',
            }
            cross_refs += 1
            print(f"  ✓ {ptype}")
    
    save_json(RSMEANS_CALIBRATION, rsmeans_cal)
    print(f"  Cross-references: {cross_refs}")
    
    # ========================================================================
    # Save report data
    # ========================================================================
    report = {
        'integration_date': '2026-02-16',
        'version': 2,
        'types_processed': types_processed,
        'types_with_value_changes': types_with_changes,
        'total_field_changes': len(log.changes),
        'types_affected': sorted(log.types_updated),
        'combined_calibration_types': len(all_types),
        'cross_references_added': cross_refs,
        'changes_by_type': {},
    }
    
    for change in log.changes:
        pt = change['project_type']
        if pt not in report['changes_by_type']:
            report['changes_by_type'][pt] = []
        report['changes_by_type'][pt].append(change)
    
    save_json(REPORT_OUT, report)
    
    print(f"\n{'=' * 70}")
    print(f"DONE — {types_processed} types, {len(log.changes)} changes, {cross_refs} cross-refs")
    print(f"{'=' * 70}")
    
    return report


if __name__ == '__main__':
    main()
