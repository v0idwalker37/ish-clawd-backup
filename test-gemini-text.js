import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

try {
  const response = await ai.models.generateContent({
    model: "gemini-2.0-flash-exp",
    contents: "Say hello in one sentence",
  });
  console.log("✓ Text model works:", response.text);
} catch (e) {
  console.log("✗ Error:", e.message);
}
