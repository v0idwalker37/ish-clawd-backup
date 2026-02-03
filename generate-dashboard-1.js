import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const prompt = `Create a clean, modern executive dashboard mockup for a web application.

Layout: Single-pane dashboard (minimalist style)

Top section:
- Header: "UnGouge.ai Executive Dashboard" with date "Feb 3, 2026"

Main sections (vertical layout):
1. REVENUE section with 3 metric cards side-by-side:
   - "This Month: $1,247 / 62 reports / +18% MoM" (green indicator)
   - "Quarter: $3,891 / 195 reports / Goal: 78%" (green indicator)  
   - "Year: $3,891 / 195 reports / Goal: 6%" (yellow indicator)

2. GOALS section:
   - Large progress bar showing "78% to Q1 goal"
   - Text: "195 / 250 reports ($5K target)"

3. TRACTION section with 4 metrics:
   - YouTube Subs: 1,247 (+89 this week)
   - Email List: 423 subscribers
   - Reddit Karma: 2,891
   - Twitter Followers: 892

4. ATTENTION NEEDED section (warning/orange):
   - "Blog post #3 due today"
   - "YouTube video rendering (87% complete)"

5. COMPLETED TODAY section (success/green):
   - 3 checkmark items

Style: Modern SaaS dashboard, clean white background, professional typography, subtle shadows, blue/green accent colors, data visualization friendly. Make it look like a real web app screenshot.`;

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
    fs.writeFileSync("dashboard-concept-1-minimalist.png", Buffer.from(part.inlineData.data, "base64"));
    console.log("✓ Dashboard 1 (Minimalist) generated");
  }
}
