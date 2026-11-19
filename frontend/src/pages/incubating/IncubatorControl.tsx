import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Plus, Cpu, ChevronRight, RefreshCw } from "lucide-react";

import { getIncubators, type IncubatorState } from "../../services/incubators";

type Filter = "all" | "incubating" | "available";

// Тимчасові показники
const STATIC_METRICS = {
  temperature: 37.8,
  humidity: 60,
  bird: "Курка",
};

const statusLabels: Record<IncubatorState, string> = {
  available: "Вільний",
  incubating: "Інкубація триває",
  broken: "Несправний",
};

const statusColors: Record<IncubatorState, string> = {
  available: "bg-blue-50 text-blue-700",
  incubating: "bg-emerald-50 text-emerald-700",
  broken: "bg-red-50 text-red-700",
};

export default function IncubatorControl() {
  const navigate = useNavigate();

  const [filter, setFilter] = useState<Filter>("all");

  // ==========================================
  // TANSTACK QUERY
  // ==========================================

  const {
    data: devices = [],
    isLoading,
    isFetching,
    error,
    refetch,
  } = useQuery({
    queryKey: ["incubators"],
    queryFn: getIncubators,
    staleTime: 60_000,
  });

  // ==========================================
  // STATISTICS
  // ==========================================

  const active = devices.filter(
    (device) => device.state === "incubating",
  ).length;

  const available = devices.filter(
    (device) => device.state === "available",
  ).length;

  const visible = devices.filter(
    (device) => filter === "all" || device.state === filter,
  );

  // ==========================================
  // INTERFACE
  // ==========================================

  return (
    <div className="mx-auto max-w-2xl pb-8 text-slate-900">
      {/* HEADER */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-600">
            Smart Farm / Інкубація
          </p>

          <h1 className="mt-1 text-2xl font-bold">Мої інкубатори</h1>
        </div>

        <div className="flex items-center gap-2">
          {/* REFRESH */}
          <button
            type="button"
            aria-label="Оновити інкубатори"
            onClick={() => void refetch()}
            disabled={isFetching}
            className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-100 text-slate-600 disabled:opacity-50"
          >
            <RefreshCw size={19} className={isFetching ? "animate-spin" : ""} />
          </button>

          {/* ADD */}
          <button
            type="button"
            aria-label="Додати інкубатор"
            onClick={() => navigate("/incubator/new")}
            className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-white"
          >
            <Plus size={22} />
          </button>
        </div>
      </div>

      {/* STATISTICS */}
      <div className="mb-5 grid grid-cols-3 gap-2">
        {[
          { label: "Усього", value: devices.length },
          { label: "Активні", value: active },
          { label: "Вільні", value: available },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-2xl border border-slate-100 bg-white p-3 shadow-sm"
          >
            <div className="text-2xl font-bold">{item.value}</div>

            <div className="mt-1 text-xs text-slate-500">{item.label}</div>
          </div>
        ))}
      </div>

      {/* FILTERS */}
      <div className="mb-4 flex rounded-xl bg-slate-100 p-1">
        {(
          [
            ["all", "Усі"],
            ["incubating", "Активні"],
            ["available", "Вільні"],
          ] as const
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`flex-1 rounded-lg py-2 text-sm font-medium ${
              filter === value
                ? "bg-white text-blue-700 shadow-sm"
                : "text-slate-500"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ERROR */}
      {error && (
        <div className="mb-4 rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-700">
          {error instanceof Error
            ? error.message
            : "Помилка завантаження інкубаторів"}
        </div>
      )}

      {/* LOADING */}
      {isLoading && (
        <div className="py-10 text-center text-sm text-slate-500">
          Завантаження інкубаторів...
        </div>
      )}

      {/* INCUBATORS */}
      <div className="space-y-3">
        {visible.map((device) => {
          const isIncubating = device.state === "incubating";

          return (
            <button
              key={device.id}
              type="button"
              onClick={() => navigate(`/incubator/${device.id}`)}
              className="w-full rounded-2xl border border-slate-100 bg-white p-4 text-left shadow-sm transition active:scale-[0.99]"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className="rounded-xl bg-slate-100 p-2.5 text-slate-600">
                    <Cpu size={21} />
                  </div>

                  <div>
                    <h2 className="font-semibold">
                      Інкубатор №{device.number}
                    </h2>

                    <p className="mt-0.5 text-xs text-slate-500">
                      Автоматизований · ESP32
                    </p>
                  </div>
                </div>

                <ChevronRight size={18} className="mt-2 text-slate-400" />
              </div>

              <div className="mt-4 flex items-center justify-between gap-2">
                <span
                  className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                    statusColors[device.state]
                  }`}
                >
                  {statusLabels[device.state]}
                </span>

                {isIncubating && device.activated_at && (
                  <span className="text-xs text-slate-500">
                    Запущено{" "}
                    {new Date(device.activated_at).toLocaleDateString("uk-UA")}
                  </span>
                )}
              </div>

              {isIncubating && (
                <div className="mt-3 flex justify-between gap-2 text-xs text-slate-500">
                  <span>
                    {device.eggs_amount ?? 0} яєць
                    {" · "}
                    {STATIC_METRICS.bird}
                  </span>

                  <span>
                    {STATIC_METRICS.temperature}°C
                    {" · "}
                    {STATIC_METRICS.humidity}%
                  </span>
                </div>
              )}
            </button>
          );
        })}

        {!isLoading && !error && visible.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-200 p-8 text-center text-sm text-slate-500">
            Інкубаторів у цій категорії немає.
          </div>
        )}
      </div>

      {/* ADD INCUBATOR */}
      <button
        type="button"
        onClick={() => navigate("/incubator/new")}
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white"
      >
        <Plus size={18} />
        Додати інкубатор
      </button>
    </div>
  );
}
