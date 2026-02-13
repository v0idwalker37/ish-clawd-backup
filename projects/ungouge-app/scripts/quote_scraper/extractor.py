"""Extract structured quote data from unstructured text."""

import re
import hashlib
from datetime import datetime
from typing import List, Optional, Tuple

from .models import RawQuote, ExtractedQuote
from .config import PROJECT_TYPES, US_STATES, STATE_NAME_TO_ABBR, MAJOR_CITIES


def extract_quotes(raw: RawQuote) -> List[ExtractedQuote]:
    """Extract one or more quotes from a raw text post/comment.
    
    Returns a list because one post might contain multiple quotes.
    """
    text = raw.raw_text
    if not text or len(text.strip()) < 20:
        return []

    # Find all dollar amounts in the text
    amounts = extract_dollar_amounts(text)
    if not amounts:
        return []

    # Extract shared context
    project_type, type_confidence = detect_project_type(text)
    state, city = detect_location(text)
    year = detect_year(text, raw.date_posted)
    sqft = detect_square_footage(text)
    scope = extract_scope(text)

    results = []
    
    # If there are multiple dollar amounts, try to create line items
    if len(amounts) > 1:
        line_items = []
        for amt, context in amounts:
            line_items.append({
                "amount": amt,
                "context": context[:200],
            })
        
        # Use the largest amount as the primary (often the total)
        # But filter out unreasonably small amounts (likely not quotes)
        valid_amounts = [(a, c) for a, c in amounts if a >= 100]
        if not valid_amounts:
            return []
        
        # Take the max as the primary quote amount
        primary_amount, primary_context = max(valid_amounts, key=lambda x: x[0])
        
        # Calculate confidence
        confidence = calculate_confidence(
            primary_amount, project_type, state, city, type_confidence
        )
        
        if confidence >= 0.2:  # minimum threshold
            eq = ExtractedQuote(
                raw=raw,
                dollar_amount=primary_amount,
                project_type=project_type,
                location_state=state,
                location_city=city,
                year=year,
                square_footage=sqft,
                scope=scope,
                confidence=confidence,
                line_items=line_items,
            )
            results.append(eq)
    else:
        amount, context = amounts[0]
        if amount < 100:
            return []
        
        confidence = calculate_confidence(
            amount, project_type, state, city, type_confidence
        )
        
        if confidence >= 0.2:
            eq = ExtractedQuote(
                raw=raw,
                dollar_amount=amount,
                project_type=project_type,
                location_state=state,
                location_city=city,
                year=year,
                square_footage=sqft,
                scope=scope,
                confidence=confidence,
                line_items=[],
            )
            results.append(eq)

    return results


def extract_dollar_amounts(text: str) -> List[Tuple[float, str]]:
    """Find dollar amounts in text. Returns list of (amount, surrounding_context)."""
    amounts = []
    
    # Pattern 1: $X,XXX or $X,XXX,XXX or $X.XX
    pattern1 = r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b'
    for m in re.finditer(pattern1, text):
        try:
            val = float(m.group(1).replace(",", ""))
            context = text[max(0, m.start() - 50):m.end() + 50]
            amounts.append((val, context))
        except ValueError:
            pass

    # Pattern 2: $XXk or $XX.Xk
    pattern2 = r'\$\s*(\d+(?:\.\d+)?)\s*[kK]\b'
    for m in re.finditer(pattern2, text):
        try:
            val = float(m.group(1)) * 1000
            context = text[max(0, m.start() - 50):m.end() + 50]
            amounts.append((val, context))
        except ValueError:
            pass

    # Pattern 3: "X thousand" or "XX thousand"
    pattern3 = r'(\d+(?:\.\d+)?)\s+thousand\s+(?:dollars?)?'
    for m in re.finditer(pattern3, text, re.IGNORECASE):
        try:
            val = float(m.group(1)) * 1000
            context = text[max(0, m.start() - 50):m.end() + 50]
            amounts.append((val, context))
        except ValueError:
            pass

    # Pattern 4: "quoted X,XXX" or "quoted XXXX" (without $ sign)
    pattern4 = r'(?:quoted|charged|cost|bid|estimate[d]?)\s+(?:us\s+)?(?:at\s+)?(\d{1,3}(?:,\d{3})+)\b'
    for m in re.finditer(pattern4, text, re.IGNORECASE):
        try:
            val = float(m.group(1).replace(",", ""))
            context = text[max(0, m.start() - 50):m.end() + 50]
            # Avoid duplicate if we already found this amount with $
            if not any(abs(a - val) < 1 for a, _ in amounts):
                amounts.append((val, context))
        except ValueError:
            pass

    # Filter: contractor quotes are typically $100 - $500,000
    amounts = [(a, c) for a, c in amounts if 100 <= a <= 500000]
    
    return amounts


def detect_project_type(text: str) -> Tuple[str, float]:
    """Detect the project type from text. Returns (type, confidence)."""
    text_lower = text.lower()
    
    best_type = "general_remodel"
    best_score = 0
    
    for ptype, keywords in PROJECT_TYPES.items():
        score = 0
        for kw in keywords:
            if kw.lower() in text_lower:
                # Longer keywords are more specific, worth more
                score += len(kw.split())
        
        if score > best_score:
            best_score = score
            best_type = ptype
    
    # Confidence based on score
    if best_score >= 3:
        confidence = 0.9
    elif best_score >= 2:
        confidence = 0.7
    elif best_score >= 1:
        confidence = 0.5
    else:
        confidence = 0.2
    
    return best_type, confidence


def detect_location(text: str) -> Tuple[str, str]:
    """Detect state and city from text."""
    text_lower = text.lower()
    state = ""
    city = ""
    
    # Check for city names first (they often include state context)
    for city_name, state_abbr in MAJOR_CITIES.items():
        if city_name in text_lower:
            city = city_name.title()
            state = state_abbr
            return state, city
    
    # Check for state abbreviations (need word boundaries)
    # Look for patterns like ", TX" or "in TX" or "(TX)"
    for abbr in US_STATES:
        patterns = [
            r',\s*' + abbr + r'\b',
            r'\bin\s+' + abbr + r'\b',
            r'\(' + abbr + r'\)',
            r'\b' + abbr + r'\s+area\b',
        ]
        for pat in patterns:
            if re.search(pat, text):
                state = abbr
                break
        if state:
            break
    
    # Check for full state names
    if not state:
        for name, abbr in STATE_NAME_TO_ABBR.items():
            # Use word boundary to avoid false matches
            if re.search(r'\b' + re.escape(name) + r'\b', text_lower):
                state = abbr
                break
    
    # Check for ZIP codes
    if not state:
        zip_match = re.search(r'\b(\d{5})(?:-\d{4})?\b', text)
        if zip_match:
            zipcode = zip_match.group(1)
            # Basic ZIP->state mapping (first digit)
            zip_first = int(zipcode[0])
            zip_state_map = {
                0: "CT",  # 0xxxx = CT/MA/ME/NH/NJ/RI/VT
                1: "NY",  # 1xxxx = DE/NY/PA
                2: "VA",  # 2xxxx = DC/MD/NC/SC/VA/WV
                3: "GA",  # 3xxxx = AL/FL/GA/MS/TN
                4: "OH",  # 4xxxx = IN/KY/MI/OH
                5: "MN",  # 5xxxx = IA/MN/MT/ND/NE/SD/WI
                6: "TX",  # 6xxxx = IL/KS/MO/NE (partial)/TX (partial)
                7: "TX",  # 7xxxx = AR/LA/OK/TX
                8: "CO",  # 8xxxx = AZ/CO/ID/NM/NV/UT/WY
                9: "CA",  # 9xxxx = AK/CA/HI/OR/WA
            }
            state = zip_state_map.get(zip_first, "")
    
    return state, city


def detect_year(text: str, date_posted: str) -> int:
    """Detect what year the quote is from."""
    # Look for explicit year mentions
    year_match = re.search(r'\b(202[0-6]|201[5-9])\b', text)
    if year_match:
        return int(year_match.group(1))
    
    # Fall back to post date
    if date_posted:
        try:
            if "T" in date_posted:
                dt = datetime.fromisoformat(date_posted.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(date_posted[:10], "%Y-%m-%d")
            return dt.year
        except (ValueError, IndexError):
            pass
    
    return datetime.now().year


def detect_square_footage(text: str) -> Optional[float]:
    """Extract square footage from text."""
    patterns = [
        r'(\d{1,5}(?:,\d{3})?)\s*(?:sq\.?\s*ft\.?|square\s*feet|sqft|sf)\b',
        r'(\d{1,5}(?:,\d{3})?)\s*(?:square\s*foot)\b',
    ]
    
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(",", ""))
                if 10 <= val <= 100000:  # reasonable range
                    return val
            except ValueError:
                pass
    
    return None


def extract_scope(text: str) -> str:
    """Extract a summary of what's included in the quote."""
    # Look for scope-related phrases
    scope_phrases = []
    
    scope_patterns = [
        r'(?:includes?|including|included)\s+(.{10,150}?)(?:\.|$)',
        r'(?:for|covers?|covering)\s+(.{10,150}?)(?:\.|$)',
        r'(?:scope|work)\s*(?:is|includes?|:)\s*(.{10,150}?)(?:\.|$)',
    ]
    
    for pat in scope_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            cleaned = m.strip()
            if len(cleaned) > 10:
                scope_phrases.append(cleaned)
    
    if scope_phrases:
        return "; ".join(scope_phrases[:3])  # max 3 scope phrases
    
    # Fall back: take the first 200 chars of meaningful text
    cleaned = re.sub(r'\s+', ' ', text).strip()
    if len(cleaned) > 200:
        cleaned = cleaned[:200] + "..."
    return cleaned


def calculate_confidence(
    amount: float,
    project_type: str,
    state: str,
    city: str,
    type_confidence: float,
) -> float:
    """Calculate overall confidence score for an extracted quote."""
    score = 0.0
    
    # Has a dollar amount (required, so base score)
    score += 0.3
    
    # Project type confidence
    score += type_confidence * 0.3
    
    # Has location
    if state:
        score += 0.15
    if city:
        score += 0.1
    
    # Amount in reasonable range for home improvement
    if 500 <= amount <= 200000:
        score += 0.15
    elif 100 <= amount <= 500000:
        score += 0.05
    
    return min(score, 1.0)


def content_hash(source: str, dollar_amount: float, project_type: str, location: str) -> str:
    """Generate a content hash for deduplication."""
    content = f"{source}|{dollar_amount:.0f}|{project_type}|{location}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
