import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const prompt = `Create a clean, modern executive dashboard mockup for a web application.

Layout: Morning briefing style dashboard (conversational)

Top banner:
- "Good morning, Jason! ☕️"
- "Tuesday, Feb 3, 2026 — 6:00 AM EST"

Sections (clean card layout):
1. WEATHER card: "Clear, 1°F (feels -4°F). Very cold — bundle up."

2. YOUR DAY card: "10:00 AM - Summer clothes (1 hour)"

3. INBOX card: "2 unread, 0 urgent" with 2 email previews

4. UNGOUGE STATUS card:
   - Revenue: $3,891 QTD (78% to goal)
   - Yesterday: +$247 (12 reports)
   - Traction: 1.2K YouTube subs, 423 email subscribers

5. WHAT I DID OVERNIGHT card (AI work summary):
   - "10 deliverables: 2 blog posts, social templates, SEO"
   - "Documentation: Your background, partnership framework"
   - "Moltbook: API down, built strategic docs instead"

6. NEEDS ATTENTION card (warning):
   - "Blog post #3 draft by EOD today"
   - "YouTube video rendering (87% complete)"

7. AMAZING AI NEWS card:
   - 3 bullet points with tech news

Style: Clean, friendly, conversational UI. Like a personal morning briefing. White background, soft cards with subtle shadows, friendly icons, blue and orange accent colors. Modern SaaS aesthetic.`;

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash-image",
  contents: prompt,
  config: {
    responseModalities: ["IMAGE"],
    generationConfig: {
      imageConfig: {
        aspectRatio: "16:9"
      }
    }
  }
});

const parts = response.candidates?.[0]?.content?.parts ?? [];
for (const part of parts) {
  if (part.inlineData?.data) {
    fs.writeFileSync("dashboard-concept-2-briefing.png", Buffer.from(part.inlineData.data, "base64"));
    console.log("✓ Dashboard 2 (Morning Briefing) generated");
  }
}
