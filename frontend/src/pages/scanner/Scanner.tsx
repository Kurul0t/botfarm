import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Html5Qrcode, Html5QrcodeSupportedFormats } from "html5-qrcode";
import { X, Camera, ScanLine } from "lucide-react";

export default function Scanner() {
  const navigate = useNavigate();

  const scannedRef = useRef(false);

  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let disposed = false;
    let cleanupPromise: Promise<void> | null = null;

    scannedRef.current = false;

    const scanner = new Html5Qrcode("scanner-camera", {
      formatsToSupport: [
        Html5QrcodeSupportedFormats.QR_CODE,
        Html5QrcodeSupportedFormats.EAN_13,
        Html5QrcodeSupportedFormats.EAN_8,
        Html5QrcodeSupportedFormats.CODE_128,
        Html5QrcodeSupportedFormats.CODE_39,
        Html5QrcodeSupportedFormats.UPC_A,
        Html5QrcodeSupportedFormats.UPC_E,
      ],
      verbose: false,
    });

    const startPromise = scanner.start(
      { facingMode: "environment" },
      {
        fps: 10,
        aspectRatio: 1,
        disableFlip: true,
      },
      (decodedText) => {
        if (disposed || scannedRef.current) return;

        scannedRef.current = true;

        void (async () => {
          await stopScanner();

          if (!disposed) {
            navigate(`/scan?code=${encodeURIComponent(decodedText)}`, {
              replace: true,
            });
          }
        })();
      },
      () => {
        // QR-код не знайдено в поточному кадрі
      },
    );

    const stopScanner = (): Promise<void> => {
      if (cleanupPromise) {
        return cleanupPromise;
      }

      cleanupPromise = (async () => {
        try {
          // Чекаємо завершення запуску камери
          await startPromise;

          // Спочатку зупиняємо сканування
          if (scanner.isScanning) {
            await scanner.stop();
          }

          // Очищаємо тільки після зупинки
          scanner.clear();
        } catch (err) {
          console.error("Scanner cleanup error:", err);
        }
      })();

      return cleanupPromise;
    };

    startPromise
      .then(() => {
        if (!disposed && !scannedRef.current) {
          setReady(true);
        }
      })
      .catch((err) => {
        console.error("Scanner start error:", err);

        if (!disposed) {
          setError("Не вдалося запустити камеру.");
        }
      });

    return () => {
      disposed = true;
      void stopScanner();
    };
  }, [navigate]);

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-[#0b1220] text-white">
      {/* Верхня панель */}
      <header className="flex items-center justify-between px-5 pt-6 pb-4">
        <button
          type="button"
          onClick={() => navigate(-1)}
          aria-label="Закрити сканер"
          className="flex h-10 w-10 items-center justify-center rounded-full bg-white/10 text-white"
        >
          <X size={22} />
        </button>

        <h1 className="text-lg font-semibold text-white">Сканування коду</h1>

        <ScanLine size={22} className="text-blue-400" />
      </header>

      {/* Основна область */}
      <main className="flex flex-1 flex-col items-center justify-center px-5">
        {/* Контейнер камери */}
        <div className="relative aspect-square w-full max-w-sm overflow-hidden rounded-3xl bg-black">
          {/* Відеопотік */}
          <div id="scanner-camera" className="absolute inset-0 h-full w-full" />

          {/* Власна рамка */}
          {ready && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <div className="scanner-frame relative h-[180px] w-[80%] max-w-[280px]">
                {/* Анімована лінія */}
                <div className="scanner-line" />
              </div>
            </div>
          )}

          {/* Завантаження */}
          {!ready && !error && (
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/40">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
            </div>
          )}
        </div>

        {/* Повідомлення */}
        {error ? (
          <p role="alert" className="mt-6 text-center text-sm text-red-400">
            {error}
          </p>
        ) : (
          <>
            <h2 className="mt-8 text-center text-lg font-semibold text-white">
              Наведіть камеру на код
            </h2>

            <p className="mt-2 text-center text-sm text-slate-400">
              QR-коди та штрихкоди
              <br />
              розпізнаються автоматично
            </p>
          </>
        )}
      </main>

      {/* Нижня панель */}
      <footer className="flex items-center justify-center gap-2 px-5 pb-10 text-sm text-slate-400">
        <Camera size={18} />
        {ready
          ? "Камера активна"
          : error
            ? "Камера недоступна"
            : "Запуск камери..."}
      </footer>

      {/* Стилі */}
      <style>{`
        #scanner-camera {
          width: 100%;
          height: 100%;
          overflow: hidden;
        }

        #scanner-camera video {
          display: block !important;
          width: 100% !important;
          height: 100% !important;
          object-fit: cover !important;
          border-radius: 0 !important;
        }

        #scanner-camera canvas {
          display: none !important;
        }

        .scanner-frame {
          border: 3px solid #60a5fa;
          border-radius: 18px;
          box-shadow:
            0 0 20px rgba(59, 130, 246, 0.3),
            inset 0 0 15px rgba(59, 130, 246, 0.1);
          overflow: hidden;
        }

        .scanner-line {
          position: absolute;
          left: 5%;
          right: 5%;
          height: 2px;
          background: #60a5fa;
          box-shadow: 0 0 12px #60a5fa;
          animation: scanMove 2s ease-in-out infinite alternate;
        }

        @keyframes scanMove {
          from {
            top: 8%;
          }

          to {
            top: 90%;
          }
        }
      `}</style>
    </div>
  );
}
