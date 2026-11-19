const API_URL = import.meta.env.VITE_API_URL?.replace(/\/+$/, "");

if (!API_URL) {
  throw new Error("VITE_API_URL не налаштовано");
}

/* ==================================================
   TYPES
================================================== */

export type IncubatorState = "available" | "incubating" | "broken";

export type IncubatorType = "automatic" | "manual";

export interface IncubationParameters {
  temperature?: number | null;

  humidity?: {
    min: number | null;
    max: number | null;
  } | null;

  turning_interval?: number | null;
  ventilation_count?: number | null;
  ventilation_duration?: number | null;
}

export interface Incubator {
  id: number;
  device_code: string;
  company_id: number;
  number: number;

  device_type: IncubatorType;
  capacity: number | null;

  eggs_amount: number | null;
  activated_at: string | null;
  state: IncubatorState;
  instruction_id: number | null;

  // Задані показники (для сумісності)
  target_temperature?: number | null;
  target_humidity?: number | null;

  // Фактичні показники
  actual_temperature?: number | null;
  actual_humidity?: number | null;

  // Поточні рекомендовані параметри
  parameters?: IncubationParameters | null;

  // Прогрес інкубації
  duration_days: number | null;
  current_day: number | null;
  days_remaining: number | null;
  estimated_end_at: string | null;
  progress: number | null;
  instruction_title: string | null;
}

export interface IncubationParametersResponse {
  parameters: IncubationParameters;
}

/* ==================================================
   TELEGRAM AUTH
================================================== */

function getTelegramInitData(): string {
  const initData = window.Telegram?.WebApp?.initData;

  if (!initData) {
    throw new Error("Відкрийте застосунок через Telegram");
  }

  return initData;
}

function telegramHeaders(): HeadersInit {
  return {
    "X-Telegram-Init-Data": getTelegramInitData(),
  };
}

/* ==================================================
   GET ALL INCUBATORS
================================================== */

export async function getIncubators(): Promise<Incubator[]> {
  const response = await fetch(`${API_URL}/api/v1/incubators/`, {
    method: "GET",
    headers: telegramHeaders(),
  });

  if (!response.ok) {
    const error = await response.text();

    throw new Error(
      `Не вдалося отримати інкубатори (${response.status}): ${error}`,
    );
  }

  return response.json();
}

/* ==================================================
   GET INCUBATOR BY ID
================================================== */

export async function getIncubator(id: number): Promise<Incubator> {
  const response = await fetch(`${API_URL}/api/v1/incubators/${id}`, {
    method: "GET",
    headers: telegramHeaders(),
  });

  if (response.status === 404) {
    throw new Error("Інкубатор не знайдено");
  }

  if (!response.ok) {
    const error = await response.text();

    throw new Error(`Помилка API (${response.status}): ${error}`);
  }

  return response.json();
}

/* ==================================================
   GET CURRENT INCUBATION PARAMETERS
================================================== */

export async function getIncubatorParameters(
  id: number,
): Promise<IncubationParameters> {
  const response = await fetch(
    `${API_URL}/api/v1/incubators/${id}/parameters`,
    {
      method: "GET",
      headers: telegramHeaders(),
    },
  );

  if (response.status === 404) {
    throw new Error("Інкубатор не знайдено");
  }

  if (!response.ok) {
    const error = await response.text();

    throw new Error(
      `Помилка отримання параметрів (${response.status}): ${error}`,
    );
  }

  const data: IncubationParametersResponse = await response.json();

  return data.parameters;
}
