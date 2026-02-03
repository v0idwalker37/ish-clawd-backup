#!/usr/bin/env python3
"""
Cost Model Validator - UnGouge
Validates contractor quote data for inconsistencies, anomalies, and potential errors

Usage:
    python cost-model-validator.py --quote quote.json
    python cost-model-validator.py --quote quote.json --market-data market-rates.json
    python cost-model-validator.py --batch quotes/*.json

Author: UnGouge Team
License: MIT
"""

import json
import argparse
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationResult:
    """Represents a validation check result"""
    check_name: str
    severity: Severity
    message: str
    line_item: str = None
    suggested_fix: str = None
    impact_amount: float = None


class CostModelValidator:
    """Validates contractor quote cost models for inconsistencies"""
    
    # Industry standard ranges (configurable)
    STANDARD_MARKUP_MIN = 0.20  # 20%
    STANDARD_MARKUP_MAX = 0.35  # 35%
    HIGH_MARKUP_THRESHOLD = 0.50  # 50%
    
    STANDARD_CONTINGENCY_MIN = 0.10  # 10%
    STANDARD_CONTINGENCY_MAX = 0.15  # 15%
    HIGH_CONTINGENCY_THRESHOLD = 0.20  # 20%
    
    STANDARD_PROFIT_MIN = 0.10  # 10%
    STANDARD_PROFIT_MAX = 0.20  # 20%
    
    MISC_ITEM_THRESHOLD = 500  # Flag "misc" items over $500
    
    def __init__(self, market_data: Dict = None):
        """Initialize validator with optional market data"""
        self.market_data = market_data or {}
        self.results: List[ValidationResult] = []
        
    def validate_quote(self, quote_data: Dict) -> List[ValidationResult]:
        """
        Run all validation checks on a quote
        
        Args:
            quote_data: Parsed quote JSON
            
        Returns:
            List of validation results
        """
        self.results = []
        
        # Structure validation
        self._validate_structure(quote_data)
        
        # Mathematical consistency
        self._validate_math(quote_data)
        
        # Line item analysis
        self._validate_line_items(quote_data)
        
        # Markup analysis
        self._validate_markups(quote_data)
        
        # Contingency analysis
        self._validate_contingency(quote_data)
        
        # Red flag detection
        self._detect_red_flags(quote_data)
        
        # Cross-reference with market data
        if self.market_data:
            self._validate_against_market(quote_data)
        
        return sorted(self.results, key=lambda x: (x.severity.value, x.line_item or ""))
    
    def _validate_structure(self, quote: Dict):
        """Validate quote has required fields"""
        required_fields = ['total', 'line_items', 'project_type']
        
        for field in required_fields:
            if field not in quote:
                self.results.append(ValidationResult(
                    check_name="structure_check",
                    severity=Severity.ERROR,
                    message=f"Missing required field: {field}",
                    suggested_fix=f"Add '{field}' to quote data"
                ))
        
        if 'line_items' in quote and not isinstance(quote['line_items'], list):
            self.results.append(ValidationResult(
                check_name="structure_check",
                severity=Severity.ERROR,
                message="'line_items' must be an array",
                suggested_fix="Convert line_items to array format"
            ))
    
    def _validate_math(self, quote: Dict):
        """Validate mathematical consistency"""
        if 'line_items' not in quote or 'total' not in quote:
            return
        
        # Sum all line items
        calculated_total = sum(
            item.get('amount', 0) for item in quote['line_items']
        )
        
        quoted_total = quote['total']
        
        # Allow for small rounding differences ($1)
        if abs(calculated_total - quoted_total) > 1.0:
            self.results.append(ValidationResult(
                check_name="math_check",
                severity=Severity.ERROR,
                message=f"Line items sum to ${calculated_total:,.2f} but total is ${quoted_total:,.2f}",
                impact_amount=abs(calculated_total - quoted_total),
                suggested_fix="Verify line item amounts and total"
            ))
        
        # Check for negative amounts
        for item in quote['line_items']:
            if item.get('amount', 0) < 0:
                self.results.append(ValidationResult(
                    check_name="math_check",
                    severity=Severity.ERROR,
                    message=f"Negative amount found: ${item['amount']}",
                    line_item=item.get('description', 'Unknown'),
                    suggested_fix="Amounts should be positive (or zero for free items)"
                ))
    
    def _validate_line_items(self, quote: Dict):
        """Validate individual line items"""
        if 'line_items' not in quote:
            return
        
        for item in quote['line_items']:
            description = item.get('description', '').lower()
            amount = item.get('amount', 0)
            
            # Check for vague descriptions
            vague_terms = ['miscellaneous', 'misc', 'other', 'various', 'etc']
            if any(term in description for term in vague_terms):
                if amount > self.MISC_ITEM_THRESHOLD:
                    self.results.append(ValidationResult(
                        check_name="line_item_vagueness",
                        severity=Severity.WARNING,
                        message=f"Vague line item '${amount:,.2f}' - should be itemized",
                        line_item=item.get('description'),
                        suggested_fix="Request detailed breakdown of miscellaneous costs",
                        impact_amount=amount
                    ))
            
            # Check for missing quantity/unit price
            if 'quantity' not in item and 'unit_price' not in item:
                if item.get('category') == 'materials':
                    self.results.append(ValidationResult(
                        check_name="line_item_detail",
                        severity=Severity.INFO,
                        message="Material item missing quantity/unit price",
                        line_item=item.get('description'),
                        suggested_fix="Request quantity and unit price for transparency"
                    ))
            
            # Check for suspiciously round numbers
            if amount > 1000 and amount % 1000 == 0:
                self.results.append(ValidationResult(
                    check_name="line_item_precision",
                    severity=Severity.INFO,
                    message=f"Very round number (${amount:,.0f}) - may be rough estimate",
                    line_item=item.get('description'),
                    suggested_fix="Confirm this is actual cost, not placeholder"
                ))
    
    def _validate_markups(self, quote: Dict):
        """Validate material markups"""
        if 'line_items' not in quote:
            return
        
        for item in quote['line_items']:
            if item.get('category') != 'materials':
                continue
            
            if 'cost' not in item or 'amount' not in item:
                continue
            
            cost = item['cost']
            amount = item['amount']
            
            if cost <= 0:
                continue
            
            markup = (amount - cost) / cost
            
            if markup < 0:
                self.results.append(ValidationResult(
                    check_name="markup_validation",
                    severity=Severity.ERROR,
                    message=f"Negative markup ({markup*100:.1f}%) - selling below cost?",
                    line_item=item.get('description'),
                    suggested_fix="Verify cost and price - may be data entry error"
                ))
            
            elif markup > self.HIGH_MARKUP_THRESHOLD:
                self.results.append(ValidationResult(
                    check_name="markup_validation",
                    severity=Severity.WARNING,
                    message=f"High markup ({markup*100:.1f}%) - standard is {self.STANDARD_MARKUP_MIN*100:.0f}-{self.STANDARD_MARKUP_MAX*100:.0f}%",
                    line_item=item.get('description'),
                    impact_amount=(markup - self.STANDARD_MARKUP_MAX) * cost,
                    suggested_fix="Ask contractor to explain high markup"
                ))
            
            elif markup < self.STANDARD_MARKUP_MIN:
                self.results.append(ValidationResult(
                    check_name="markup_validation",
                    severity=Severity.INFO,
                    message=f"Low markup ({markup*100:.1f}%) - very competitive pricing",
                    line_item=item.get('description')
                ))
    
    def _validate_contingency(self, quote: Dict):
        """Validate contingency percentage"""
        if 'contingency' not in quote or 'total' not in quote:
            return
        
        contingency = quote['contingency']
        total = quote['total']
        
        if total <= 0:
            return
        
        contingency_pct = contingency / total
        
        if contingency_pct > self.HIGH_CONTINGENCY_THRESHOLD:
            potential_savings = (contingency_pct - self.STANDARD_CONTINGENCY_MAX) * total
            self.results.append(ValidationResult(
                check_name="contingency_check",
                severity=Severity.WARNING,
                message=f"High contingency ({contingency_pct*100:.1f}%) - standard is {self.STANDARD_CONTINGENCY_MIN*100:.0f}-{self.STANDARD_CONTINGENCY_MAX*100:.0f}%",
                line_item="Contingency",
                impact_amount=potential_savings,
                suggested_fix=f"Negotiate down to {self.STANDARD_CONTINGENCY_MAX*100:.0f}% (saves ~${potential_savings:,.0f})"
            ))
        
        elif contingency_pct < self.STANDARD_CONTINGENCY_MIN:
            self.results.append(ValidationResult(
                check_name="contingency_check",
                severity=Severity.INFO,
                message=f"Low contingency ({contingency_pct*100:.1f}%) - may not cover unexpected costs",
                line_item="Contingency",
                suggested_fix="Ensure change order process is clearly defined"
            ))
    
    def _detect_red_flags(self, quote: Dict):
        """Detect common red flags in quotes"""
        
        # Check for missing insurance/licensing info
        if not quote.get('contractor_license'):
            self.results.append(ValidationResult(
                check_name="red_flag_license",
                severity=Severity.WARNING,
                message="No contractor license number provided",
                suggested_fix="Verify contractor is licensed in your state"
            ))
        
        if not quote.get('insurance_proof'):
            self.results.append(ValidationResult(
                check_name="red_flag_insurance",
                severity=Severity.WARNING,
                message="No insurance verification provided",
                suggested_fix="Request proof of liability and workers comp insurance"
            ))
        
        # Check payment terms
        if 'payment_schedule' in quote:
            first_payment = quote['payment_schedule'][0] if quote['payment_schedule'] else {}
            if first_payment.get('percentage', 0) > 0.50:
                self.results.append(ValidationResult(
                    check_name="red_flag_payment",
                    severity=Severity.CRITICAL,
                    message=f"First payment is {first_payment['percentage']*100:.0f}% - standard is 30-35%",
                    suggested_fix="Large upfront payments are risky - negotiate down to 30%"
                ))
        
        # Check for permits
        has_permit_line = any(
            'permit' in item.get('description', '').lower()
            for item in quote.get('line_items', [])
        )
        
        if not has_permit_line and quote.get('project_type') in ['addition', 'remodel', 'structural']:
            self.results.append(ValidationResult(
                check_name="red_flag_permits",
                severity=Severity.WARNING,
                message="No permit costs listed - permits may be required for this project",
                suggested_fix="Verify if permits are needed and who will obtain them"
            ))
    
    def _validate_against_market(self, quote: Dict):
        """Validate quote against market data"""
        project_type = quote.get('project_type')
        location = quote.get('location')
        
        if not project_type or not location:
            return
        
        market_key = f"{project_type}_{location}"
        
        if market_key not in self.market_data:
            self.results.append(ValidationResult(
                check_name="market_comparison",
                severity=Severity.INFO,
                message=f"No market data available for {project_type} in {location}",
                suggested_fix="Check regional pricing databases or get additional quotes"
            ))
            return
        
        market = self.market_data[market_key]
        quote_total = quote.get('total', 0)
        
        if quote_total < market['low']:
            self.results.append(ValidationResult(
                check_name="market_comparison",
                severity=Severity.WARNING,
                message=f"Quote (${quote_total:,.0f}) is below market range (${market['low']:,.0f}-${market['high']:,.0f})",
                suggested_fix="Verify scope is complete - unusually low pricing may indicate missing items"
            ))
        
        elif quote_total > market['high']:
            overage = quote_total - market['high']
            self.results.append(ValidationResult(
                check_name="market_comparison",
                severity=Severity.WARNING,
                message=f"Quote (${quote_total:,.0f}) is above market range (${market['low']:,.0f}-${market['high']:,.0f})",
                impact_amount=overage,
                suggested_fix=f"Negotiate or get second quote - potential ${overage:,.0f} overcharge"
            ))
    
    def print_results(self, verbose: bool = False):
        """Print validation results to console"""
        if not self.results:
            print("✅ No issues found - quote appears valid")
            return
        
        # Group by severity
        critical = [r for r in self.results if r.severity == Severity.CRITICAL]
        errors = [r for r in self.results if r.severity == Severity.ERROR]
        warnings = [r for r in self.results if r.severity == Severity.WARNING]
        info = [r for r in self.results if r.severity == Severity.INFO]
        
        print(f"\n{'='*80}")
        print(f"QUOTE VALIDATION RESULTS")
        print(f"{'='*80}\n")
        
        print(f"Summary: {len(critical)} critical, {len(errors)} errors, {len(warnings)} warnings, {len(info)} info\n")
        
        for severity_name, results_list, emoji in [
            ("CRITICAL ISSUES", critical, "🚨"),
            ("ERRORS", errors, "❌"),
            ("WARNINGS", warnings, "⚠️"),
            ("INFORMATION", info, "ℹ️")
        ]:
            if not results_list:
                continue
            
            print(f"{emoji} {severity_name}:\n")
            
            for result in results_list:
                print(f"  [{result.check_name}]")
                print(f"  {result.message}")
                if result.line_item:
                    print(f"  Line Item: {result.line_item}")
                if result.impact_amount:
                    print(f"  Potential Impact: ${result.impact_amount:,.2f}")
                if verbose and result.suggested_fix:
                    print(f"  → {result.suggested_fix}")
                print()
    
    def to_json(self) -> str:
        """Export results as JSON"""
        return json.dumps([
            {
                'check': r.check_name,
                'severity': r.severity.value,
                'message': r.message,
                'line_item': r.line_item,
                'suggested_fix': r.suggested_fix,
                'impact_amount': r.impact_amount
            }
            for r in self.results
        ], indent=2)


def load_quote(filepath: str) -> Dict:
    """Load quote from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Validate contractor quote for inconsistencies and red flags"
    )
    parser.add_argument('--quote', required=True, help='Path to quote JSON file')
    parser.add_argument('--market-data', help='Path to market data JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show suggested fixes')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Load quote
    quote = load_quote(args.quote)
    
    # Load market data if provided
    market_data = None
    if args.market_data:
        market_data = load_quote(args.market_data)
    
    # Run validation
    validator = CostModelValidator(market_data)
    results = validator.validate_quote(quote)
    
    # Output results
    if args.json:
        print(validator.to_json())
    else:
        validator.print_results(verbose=args.verbose)
        
        # Exit code based on highest severity
        if any(r.severity == Severity.CRITICAL for r in results):
            sys.exit(3)
        elif any(r.severity == Severity.ERROR for r in results):
            sys.exit(2)
        elif any(r.severity == Severity.WARNING for r in results):
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == '__main__':
    main()
