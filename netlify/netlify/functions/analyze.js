// netlify/functions/analyze.js
const PRIMARY_MODEL = "gemini-3.6-flash";
const FALLBACK_MODEL = "gemini-2.5-flash";
const GEMINI_ENDPOINT = (model) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

const RESPONSE_SCHEMA = {
  type: "OBJECT",
  properties: {
    empresa: { type: "STRING" },
    monto_total: { type: "STRING" },
    puntos_criticos: { type: "ARRAY", items: { type: "STRING" } },
    nivel_riesgo: { type: "INTEGER" },
    riesgo_categoria: { type: "STRING", enum: ["bajo", "medio", "alto"] },
    evaluacion_legal: { type: "STRING" },
    carta_reclamo: { type: "STRING" },
  },
  required: ["empresa","monto_total","puntos_criticos","nivel_riesgo","riesgo_categoria","evaluacion_legal","carta_reclamo"],
};

function buildPrompt() {
  return `Actuás como asistente de análisis para consumidores en Argentina, con base en la Ley 24.240 de Defensa del Consumidor y normativa complementaria vigente.

Analizá la imagen de la factura o comprobante adjunto y devolvé la información en el formato JSON solicitado.

Campos:
- empresa: nombre de la empresa o proveedor del servicio.
- monto_total: monto total facturado, con moneda.
- puntos_criticos: lista de ítems, cargos o cláusulas que ameriten revisión. Si no hay nada irregular, lista vacía.
- nivel_riesgo: entero 0 a 100 (0-30 bajo, 31-65 medio, 66-100 alto).
- riesgo_categoria: "bajo", "medio" o "alto", coherente con nivel_riesgo.
- evaluacion_legal: 2 a 3 oraciones en tono informativo y prudente. Usá "podría constituir base para un reclamo", NUNCA "esto es ilegal" o "tenés un caso ganado". Aclará que no reemplaza asesoramiento legal profesional.
- carta_reclamo: carta formal completa, lista para copiar, con variables entre corchetes como [Nombre del Cliente], citando artículos de la Ley 24.240, tono firme pero profesional.

Si la imagen no es una factura legible, devolvé empresa: "No identificado", puntos_criticos vacío, nivel_riesgo: 0, riesgo_categoria: "bajo", y explicá en evaluacion_legal que no se pudo leer el documento.`;
}

async function callGemini(model, apiKey, prompt, imageBase64, mimeType) {
  const res = await fetch(GEMINI_ENDPOINT(model), {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: prompt }, { inline_data: { mime_type: mimeType, data: imageBase64 } }] }],
      generationConfig: { responseMimeType: "application/json", responseSchema: RESPONSE_SCHEMA, temperature: 0.3 },
    }),
  });
  if (!res.ok) { const errText = await res.text(); throw new Error(`Gemini (${model}) respondió ${res.status}: ${errText}`); }
  const data = await res.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error(`Respuesta vacía del modelo ${model}`);
  return JSON.parse(text);
}

exports.handler = async (event) => {
  const headers = { "Content-Type": "application/json" };
  if (event.httpMethod !== "POST") return { statusCode: 405, headers, body: JSON.stringify({ error: "Método no permitido." }) };

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return { statusCode: 500, headers, body: JSON.stringify({ error: "Falta configurar GEMINI_API_KEY en las variables de entorno de Netlify." }) };

  let payload;
  try { payload = JSON.parse(event.body || "{}"); }
  catch { return { statusCode: 400, headers, body: JSON.stringify({ error: "Body inválido." }) }; }

  const { imageBase64, mimeType } = payload;
  if (!imageBase64 || !mimeType) return { statusCode: 400, headers, body: JSON.stringify({ error: "Falta la imagen a analizar." }) };

  const prompt = buildPrompt();
  try {
    const result = await callGemini(PRIMARY_MODEL, apiKey, prompt, imageBase64, mimeType);
    return { statusCode: 200, headers, body: JSON.stringify(result) };
  } catch (primaryErr) {
    console.error("Modelo principal falló:", primaryErr.message);
    try {
      const result = await callGemini(FALLBACK_MODEL, apiKey, prompt, imageBase64, mimeType);
      return { statusCode: 200, headers, body: JSON.stringify(result) };
    } catch (fallbackErr) {
      console.error("Modelo de respaldo también falló:", fallbackErr.message);
      return { statusCode: 502, headers, body: JSON.stringify({ error: "No pudimos completar la auditoría. Probá de nuevo en unos minutos." }) };
    }
  }
};q
