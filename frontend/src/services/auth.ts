export interface AuthResponse {
  employee_id: number;
  telegram_user_id: number;
  company_id: number;
  role: string;
  bot_id: number;
}

const API_URL = import.meta.env.VITE_API_URL;

export async function authTelegram(initData: string): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/telegram`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      init_data: initData,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Помилка авторизації (${response.status}): ${error}`);
  }

  return response.json();
}
