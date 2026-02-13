"""
GDPR R-15 — Do Not Track (DNT) Signal Handling

Middleware that inspects the DNT (Do Not Track) HTTP header.
When DNT=1:
  - Sets request.state.dnt = True so downstream code can skip analytics
  - Removes any non-essential analytics/tracking cookies from the response
  - Adds a Tk: N response header (tracking status: not tracking)

When DNT is absent or DNT=0:
  - Sets request.state.dnt = False
  - Adds Tk: ? header (tracking status: dynamic — depends on user prefs)

Note: While DNT is not legally mandated, honouring it demonstrates good-faith
privacy compliance and satisfies Art. 21 objection mechanisms in practice.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Cookie names that are considered non-essential / analytics / tracking.
# Add any future analytics cookies here.
_ANALYTICS_COOKIES = frozenset({
    "_ga",           # Google Analytics
    "_gid",          # Google Analytics
    "_gat",          # Google Analytics throttle
    "_fbp",          # Facebook Pixel
    "_gcl_au",       # Google Ads conversion linker
    "mp_mixpanel",   # Mixpanel
    "ajs_anonymous_id",  # Segment
})


class DNTMiddleware(BaseHTTPMiddleware):
    """
    Middleware that checks the DNT (Do Not Track) header and disables
    analytics/tracking cookies when the user has opted out.
    """

    async def dispatch(self, request: Request, call_next):
        dnt_value = request.headers.get("DNT", "").strip()
        is_dnt = dnt_value == "1"

        # Make the flag available to route handlers and other middleware
        request.state.dnt = is_dnt

        response = await call_next(request)

        if is_dnt:
            # Signal to the client that we are NOT tracking
            response.headers["Tk"] = "N"

            # Strip any analytics/tracking cookies from the response
            # (prevents setting new tracking cookies when DNT is on)
            if "set-cookie" in response.headers:
                # starlette MutableHeaders may have multiple set-cookie values
                # We need to filter them
                filtered_cookies = []
                for header_value in response.headers.getlist("set-cookie"):
                    cookie_name = header_value.split("=", 1)[0].strip()
                    if cookie_name.lower() not in {c.lower() for c in _ANALYTICS_COOKIES}:
                        filtered_cookies.append(header_value)
                # Remove all set-cookie headers and re-add filtered ones
                del response.headers["set-cookie"]
                for cookie in filtered_cookies:
                    response.headers.append("set-cookie", cookie)
        else:
            # Dynamic — tracking depends on user preferences / consent
            response.headers["Tk"] = "?"

        return response
