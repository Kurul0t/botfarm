import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Cpu, Hand, Plus } from "lucide-react";

import { addDevice } from "./IncubatorStorage";

import type { Device, DeviceType } from "./IncubatorStorage";

export default function AddIncubator() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [type, setType] = useState<DeviceType>("manual");
  const [capacity, setCapacity] = useState(120);
  const [error, setError] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim()) {
      setError("Введіть назву інкубатора.");
      return;
    }

    if (!Number.isInteger(capacity) || capacity < 1) {
      setError("Місткість має бути додатним цілим числом.");
      return;
    }

    const device: Omit<Device, "uuid"> = {
      id: crypto.randomUUID(),
      name: name.trim(),
      type,
      capacity,
      status: "available",
    };

    try {
      addDevice(device);
      navigate(`/incubator/${device.id}`, {
        replace: true,
      });
    } catch {
      setError("Не вдалося зберегти інкубатор.");
    }
  }

  const inputClass =
    "mt-2 w-full rounded-xl border border-slate-200 " +
    "bg-white px-4 py-3 text-sm text-slate-900 " +
    "outline-none focus:border-blue-500 " +
    "focus:ring-2 focus:ring-blue-100";

  return (
    <div className="mx-auto max-w-2xl pb-8 text-slate-900">
      <button
        type="button"
        onClick={() => navigate("/incubator")}
        className="mb-5 flex items-center gap-2 text-sm text-slate-500"
      >
        <ArrowLeft size={18} />
        Мої інкубатори
      </button>

      <div className="mb-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-600">
          Smart Farm / Обладнання
        </p>

        <h1 className="mt-1 text-2xl font-bold">Новий інкубатор</h1>

        <p className="mt-2 text-sm text-slate-500">
          Додайте інкубатор для подальшого керування інкубаційними партіями.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <label
            htmlFor="incubator-name"
            className="block text-sm font-semibold"
          >
            Назва інкубатора
          </label>

          <input
            id="incubator-name"
            required
            maxLength={80}
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Наприклад, Інкубатор №4"
            className={inputClass}
          />

          <label
            htmlFor="incubator-capacity"
            className="mt-5 block text-sm font-semibold"
          >
            Місткість, яєць
          </label>

          <input
            id="incubator-capacity"
            required
            type="number"
            min={1}
            step={1}
            value={capacity}
            onChange={(event) => setCapacity(Number(event.target.value))}
            className={inputClass}
          />
        </div>

        <div>
          <h2 className="mb-3 text-base font-semibold">Тип керування</h2>

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              aria-pressed={type === "manual"}
              onClick={() => setType("manual")}
              className={`rounded-2xl border p-4 text-left transition ${
                type === "manual"
                  ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                  : "border-slate-200 bg-white"
              }`}
            >
              <Hand
                size={24}
                className={
                  type === "manual" ? "text-blue-600" : "text-slate-500"
                }
              />

              <div className="mt-3 font-semibold">Ручний</div>

              <p className="mt-1 text-xs text-slate-500">
                Самостійне внесення температури та вологості
              </p>
            </button>

            <button
              type="button"
              aria-pressed={type === "automatic"}
              onClick={() => setType("automatic")}
              className={`rounded-2xl border p-4 text-left transition ${
                type === "automatic"
                  ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                  : "border-slate-200 bg-white"
              }`}
            >
              <Cpu
                size={24}
                className={
                  type === "automatic" ? "text-blue-600" : "text-slate-500"
                }
              />

              <div className="mt-3 font-semibold">Автоматизований</div>

              <p className="mt-1 text-xs text-slate-500">
                Для майбутнього підключення ESP32
              </p>
            </button>
          </div>
        </div>

        {type === "automatic" && (
          <div className="rounded-xl bg-amber-50 p-4 text-sm text-amber-900">
            Підключення ESP32 ще не реалізоване. Створення цього запису не
            підключає фізичний пристрій.
          </div>
        )}

        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}

        <button
          type="submit"
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-700"
        >
          <Plus size={19} />
          Створити інкубатор
        </button>
      </form>
    </div>
  );
}
