import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { QRCodeCanvas } from "qrcode.react";

import { ArrowLeft, Send, QrCode, Loader2, CheckCircle2 } from "lucide-react";

import { getIncubator, type Incubator } from "../../services/incubators";

export default function QRGenerator() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  const [device, setDevice] = useState<Incubator | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  // ==========================================
  // ОТРИМАННЯ ІНКУБАТОРА
  // ==========================================

  useEffect(() => {
    let cancelled = false;

    async function loadDevice() {
      setLoading(true);
      setError(null);
      setDevice(null);
      setSent(false);

      const deviceId = Number(id);

      if (!Number.isSafeInteger(deviceId) || deviceId <= 0) {
        setError("Некоректний ID інкубатора");
        setLoading(false);
        return;
      }

      try {
        const result = await getIncubator(deviceId);

        if (!cancelled) {
          setDevice(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : "Не вдалося завантажити інкубатор",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDevice();

    return () => {
      cancelled = true;
    };
  }, [id]);

  // ==========================================
  // НАДСИЛАННЯ PNG У TELEGRAM
  // ==========================================

  const sendQR = async () => {
    if (!device || sending) return;

    setSending(true);
    setSent(false);

    try {
      const tg = window.Telegram?.WebApp;

      const initData = tg?.initData;

      if (!initData) {
        throw new Error("Відкрийте застосунок через Telegram");
      }

      const response = await fetch(`/api/v1/incubators/${device.id}/send-qr`, {
        method: "POST",
        headers: {
          "X-Telegram-Init-Data": initData,
        },
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : `Помилка надсилання (${response.status})`,
        );
      }

      setSent(true);

      const message = "QR-код успішно надіслано в чат із ботом!";

      if (tg?.showAlert) {
        tg.showAlert(message);
      } else {
        window.alert(message);
      }
    } catch (err) {
      console.error("Send QR error:", err);

      const message =
        err instanceof Error ? err.message : "Не вдалося надіслати QR-код";

      const tg = window.Telegram?.WebApp;

      if (tg?.showAlert) {
        tg.showAlert(message);
      } else {
        window.alert(message);
      }
    } finally {
      setSending(false);
    }
  };

  // ==========================================
  // LOADING
  // ==========================================

  if (loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-3">
        <Loader2 size={28} className="animate-spin text-blue-600" />

        <p className="text-sm text-gray-500">Завантаження інкубатора...</p>
      </div>
    );
  }

  // ==========================================
  // ERROR
  // ==========================================

  if (error || !device) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4 p-6">
        <p className="text-center text-gray-600">
          {error ?? "Інкубатор не знайдено"}
        </p>

        <button
          type="button"
          onClick={() => navigate("/incubators")}
          className="font-medium text-blue-600"
        >
          Повернутися до інкубаторів
        </button>
      </div>
    );
  }

  // ==========================================
  // DEVICE CODE CHECK
  // ==========================================

  if (!device.device_code) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-4 p-6">
        <p className="text-center text-red-600">
          У інкубатора відсутній device_code.
        </p>

        <button
          type="button"
          onClick={() => navigate(`/incubator/${device.id}`)}
          className="font-medium text-blue-600"
        >
          Повернутися до інкубатора
        </button>
      </div>
    );
  }

  // ==========================================
  // QR DATA
  // ==========================================

  const qrData = JSON.stringify({
    v: 1,
    type: "incubator",
    id: device.device_code,
    action: "details",
  });

  // ==========================================
  // INTERFACE
  // ==========================================

  return (
    <div className="flex min-h-[80vh] flex-col">
      {/* HEADER */}
      <div className="mb-8 flex items-center gap-3">
        <button
          type="button"
          onClick={() => navigate(`/incubator/${device.id}`)}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm"
        >
          <ArrowLeft size={22} />
        </button>

        <div>
          <h1 className="text-xl font-semibold">QR-код інкубатора</h1>

          <p className="text-sm text-gray-500">Інкубатор №{device.number}</p>
        </div>
      </div>

      {/* QR CARD */}
      <div className="flex flex-col items-center rounded-3xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
          <QrCode className="text-blue-600" size={26} />
        </div>

        <h2 className="mb-2 text-lg font-semibold">
          Інкубатор №{device.number}
        </h2>

        <p className="mb-6 text-center text-sm text-gray-500">
          Відскануйте QR-код у Smart Farm, щоб відкрити цей інкубатор.
        </p>

        <div className="rounded-2xl border border-gray-100 bg-white p-4">
          <QRCodeCanvas value={qrData} size={300} level="M" marginSize={4} />
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-400">Унікальний код пристрою</p>

          <p className="mt-1 break-all font-mono text-sm font-semibold text-gray-700">
            {device.device_code}
          </p>
        </div>
      </div>

      {/* SEND BUTTON */}
      <button
        type="button"
        onClick={() => void sendQR()}
        disabled={sending}
        className="mt-6 flex w-full items-center justify-center gap-3 rounded-2xl bg-[#0037b0] py-4 font-semibold text-white transition-transform active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
      >
        {sending ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            Надсилання...
          </>
        ) : sent ? (
          <>
            <CheckCircle2 size={20} />
            Надіслати ще раз
          </>
        ) : (
          <>
            <Send size={20} />
            Надіслати QR у Telegram
          </>
        )}
      </button>

      {sent && (
        <p className="mt-4 text-center text-sm text-green-600">
          QR-код надіслано в особистий чат із ботом.
        </p>
      )}

      <p className="mt-4 text-center text-xs text-gray-400">
        Бот надішле PNG-файл, який можна зберегти або роздрукувати.
      </p>
    </div>
  );
}
