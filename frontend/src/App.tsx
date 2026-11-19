import { useEffect, useState } from "react";

import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";

import BottomNav from "./components/BottonNav";
import Home from "./pages/home/Home";
import IncubatorControl from "./pages/incubating/IncubatorControl";
import IncubatorDetails from "./pages/incubating/IncubatorDetails";
import AddIncubator from "./pages/incubating/AddIncubator";
import StartIncubation from "./pages/incubating/StartIncubation";
import Scanner from "./pages/scanner/Scanner";
import ScanResult from "./pages/scanner/ScannerResult";
import QRGenerator from "./pages/scanner/QRGenerator";

import { authTelegram, type AuthResponse } from "./services/auth";

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        platform: string;
        initData: string;

        initDataUnsafe: {
          user?: {
            id: number;
            first_name: string;
            last_name?: string;
            username?: string;
            language_code?: string;
          };
          start_param?: string;
        };

        ready: () => void;

        isVersionAtLeast: (version: string) => boolean;

        showScanQrPopup: (
          params: { text?: string },
          callback?: (text: string) => boolean | void,
        ) => void;

        closeScanQrPopup: () => void;

        showAlert: (message: string) => void;

        onEvent: (event: "scanQrPopupClosed", callback: () => void) => void;

        offEvent: (event: "scanQrPopupClosed", callback: () => void) => void;
      };
    };
  }
}

function AppContent() {
  const navigate = useNavigate();

  const [auth, setAuth] = useState<AuthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;

    if (!tg?.initData) {
      setAuthError("Відкрийте застосунок через Telegram");
      setLoading(false);
      return;
    }

    tg.ready();

    let cancelled = false;

    async function authenticate() {
      try {
        console.log("Початок Telegram-авторизації");

        const data = await authTelegram(tg!.initData);

        if (cancelled) return;

        setAuth(data);
        setAuthError(null);

        console.group("Smart Farm — Авторизація");
        console.log("Employee ID:", data.employee_id);
        console.log("Company ID:", data.company_id);
        console.log("Bot ID:", data.bot_id);
        console.log("Role:", data.role);
        console.groupEnd();
      } catch (error) {
        if (cancelled) return;

        console.error("Помилка авторизації:", error);

        setAuthError(
          error instanceof Error ? error.message : "Не вдалося авторизуватися",
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void authenticate();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleScanQR = () => {
    navigate("/scanner");
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Авторизація через Telegram...</p>
      </div>
    );
  }

  if (authError || !auth) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 p-6 text-center">
        <h1 className="text-xl font-semibold">Помилка авторизації</h1>

        <p className="text-sm text-red-600 break-words">
          {authError ?? "Доступ не підтверджено"}
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f7f9fb] text-[#191c1e] pb-24">
      {/* Верхня шапка */}
      <header className="sticky top-0 z-40 bg-[#f7f9fb]/90 backdrop-blur px-4 h-14 flex items-center justify-between border-b border-[#eef0f3]">
        <h1 className="text-xl font-semibold">Smart App</h1>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleScanQR}
            className="w-10 h-10 flex items-center justify-center rounded-full text-[#434655] active:bg-black/5"
          >
            <span className="material-symbols-outlined text-[24px]">
              qr_code_scanner
            </span>
          </button>

          <button
            type="button"
            className="w-10 h-10 flex items-center justify-center rounded-full text-[#434655]"
          >
            <span className="material-symbols-outlined text-[24px]">
              notifications
            </span>
          </button>

          <div className="w-8 h-8 rounded-full bg-[#0037b0] flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-[18px]">
              person
            </span>
          </div>
        </div>
      </header>

      <main className="px-4 pt-4">
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/incubator" element={<IncubatorControl />} />

          <Route path="/incubator/new" element={<AddIncubator />} />

          <Route path="/incubator/:id" element={<IncubatorDetails />} />

          <Route path="/incubator/:id/start" element={<StartIncubation />} />

          <Route path="/scanner" element={<Scanner />} />

          <Route path="/scan" element={<ScanResult />} />

          <Route path="/incubator/:id/qr" element={<QRGenerator />} />
        </Routes>
      </main>

      <BottomNav />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
