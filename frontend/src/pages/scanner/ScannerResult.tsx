import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Loader2, AlertCircle } from "lucide-react";

import { resolveQRCode } from "./ScannerResolver";

import { getIncubators } from "../../services/incubators";

export default function ScanResult() {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const [message, setMessage] = useState("Обробка QR-коду...");

  const [loading, setLoading] = useState(true);

  const code = params.get("code");

  useEffect(() => {
    let cancelled = false;

    async function processQRCode() {
      setLoading(true);
      setMessage("Обробка QR-коду...");

      // 1. Перевіряємо наявність QR-коду
      if (!code) {
        setMessage("Помилка: QR-код не передано");
        setLoading(false);
        return;
      }

      // 2. Розбираємо QR-код
      const result = resolveQRCode(code);

      if (!result) {
        setMessage("Помилка: неправильний формат QR-коду");
        setLoading(false);
        return;
      }

      try {
        setMessage("Пошук інкубатора...");

        // 3. Отримуємо інкубатори з backend
        const incubators = await getIncubators();

        if (cancelled) return;

        // 4. Знаходимо інкубатор за device_code
        const device = incubators.find(
          (incubator) => incubator.device_code === result.id,
        );

        if (!device) {
          setMessage(`Інкубатор не знайдено: ${result.id}`);
          return;
        }

        // 5. Переходимо на сторінку інкубатора
        navigate(`/incubator/${device.id}`, {
          replace: true,
        });
      } catch (error) {
        if (cancelled) return;

        console.error("QR scan error:", error);

        setMessage(
          error instanceof Error
            ? error.message
            : "Не вдалося знайти інкубатор",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void processQRCode();

    return () => {
      cancelled = true;
    };
  }, [code, navigate]);

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center gap-4 p-6 text-center">
      {loading ? (
        <Loader2 size={40} className="animate-spin text-blue-600" />
      ) : (
        <AlertCircle size={40} className="text-red-500" />
      )}

      <h1 className="text-xl font-bold">
        {loading ? "Сканування QR-коду" : "Помилка сканування"}
      </h1>

      <p className="max-w-sm break-all text-sm text-gray-600">{message}</p>

      {!loading && (
        <button
          type="button"
          onClick={() => navigate("/incubator")}
          className="mt-4 rounded-xl bg-blue-600 px-5 py-3 font-medium text-white"
        >
          До інкубаторів
        </button>
      )}
    </div>
  );
}
