import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const prompt = `Create a dense, data-heavy executive dashboard mockup for a web application.

Layout: Command Center style (2x2 grid with dense information)

Header: "COMMAND CENTER" with date "Feb 3, 2026"

Four quadrants:

TOP LEFT - FINANCIAL:
- MTD: $1,247
- QTD: $3,891
- YTD: $3,891
- MRR: $2,100 (est)
- CAC: $9.30
- LTV: $19.99
- Q1 GOAL: Progress bar 78% ($3,891 / $5,000)

TOP RIGHT - METRICS:
- Traffic bars with numbers (3,247 visits, 1,892 uniques, 14% conv)
- Content Performance:
  * YouTube: 1.2K subs (+89)
  * Blog: 8 posts, 2.1K views
  * Reddit: 2.9K karma, 47 posts
  * Twitter: 892 followers (+23)

BOTTOM LEFT - ACTION ITEMS:
- 🔴 Blog #3 (today)
- 🔴 Video render
- 🟡 Cost model v2
- 🟢 Email template
- 🟢 Reddit posts
- "⏰ OVERDUE: None"
- "✅ DONE TODAY (3)"

BOTTOM RIGHT - CALENDAR:
- TODAY: 10:00 AM - Summer clothes
- THIS WEEK: Wed: Pizza pickup, Fri: YouTube launch
- NEXT WEEK: Mon: Q1 checkpoint, Tue: Dentist 3 PM

BOTTOM BANNER:
- "🧠 AI OVERNIGHT WORK (1:00-4:00 AM)"
- Brief summary line

Style: Dense professional dashboard, dark header, lots of data visualization, progress bars, color-coded priorities (red/yellow/green), terminal/analyst aesthetic. Like a Bloomberg terminal but modern. High information density.`;

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
    fs.writeFileSync("dashboard-concept-3-command-center.png", Buffer.from(part.inlineData.data, "base64"));
    console.log("✓ Dashboard 3 (Command Center) generated");
  }
}
