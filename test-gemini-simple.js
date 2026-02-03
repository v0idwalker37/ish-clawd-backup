import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

try {
  const response = await ai.models.generateContent({
    model: "gemini-1.5-flash",
    contents: "Say hello",
  });
  console.log("✓ Text works:", response.text);
} catch (e) {
  console.log("✗ Error:", e.message);
}
