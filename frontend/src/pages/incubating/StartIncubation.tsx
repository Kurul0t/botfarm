import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ArrowLeft, Egg, CalendarDays, Play } from "lucide-react";

import { BIRDS, getDevice, updateDevice } from "./IncubatorStorage";

import type { Batch, Device } from "./IncubatorStorage";

export default function StartIncubation() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [device] = useState<Device | undefined>(() =>
    id ? getDevice(id) : undefined,
  );

  const [bird, setBird] = useState("Кури");
  const [eggs, setEggs] = useState(50);
  const [duration, setDuration] = useState(21);
  const [error, setError] = useState("");

  if (!device) {
    return (
      <div className="mx-auto max-w-2xl p-4">
        <h1 className="text-xl font-bold">Інкубатор не знайдено</h1>

        <button
          onClick={() => navigate("/incubator")}
          className="mt-4 text-blue-600"
        >
          Повернутися до списку
        </button>
      </div>
    );
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!device) return;

    // Повторно читаємо дані, щоб не перезаписати
    // інкубатор, який уже зайнятий.
    const current = getDevice(device.id);

    if (!current || current.status !== "available") {
      setError("Інкубатор уже недоступний.");
      return;
    }

    if (!Number.isInteger(eggs) || eggs < 1 || eggs > current.capacity) {
      setError("Некоректна кількість яєць.");
      return;
    }

    if (!Number.isInteger(duration) || duration < 1) {
      setError("Некоректна тривалість інкубації.");
      return;
    }

    const batch: Batch = {
      id: crypto.randomUUID(),
      bird,
      eggs,
      duration,
      startedAt: new Date().toISOString(),
    };

    try {
      updateDevice({
        ...current,
        status: "working",
        batch,
      });

      navigate(`/incubator/${current.id}`, {
        replace: true,
      });
    } catch {
      setError("Не вдалося зберегти інкубацію.");
    }
  }

  const inputClass =
    "mt-2 w-full rounded-xl border border-slate-200 " +
    "bg-white px-4 py-3 text-sm outline-none " +
    "focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

  return (
    <div className="mx-auto max-w-2xl pb-8 text-slate-900">
      <button
        type="button"
        onClick={() => navigate(`/incubator/${device.id}`)}
        className="mb-5 flex items-center gap-2 text-sm text-slate-500"
      >
        <ArrowLeft size={18} />
        {device.name}
      </button>

      <div className="mb-6">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-600">
          Smart Farm / Інкубація
        </p>

        <h1 className="mt-1 text-2xl font-bold">Нова інкубація</h1>

        <p className="mt-2 text-sm text-slate-500">
          Створення інкубаційної партії для інкубатора «{device.name}».
        </p>
      </div>

      {device.status !== "available" ? (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <h2 className="font-semibold text-amber-900">
            Інкубатор недоступний
          </h2>

          <p className="mt-2 text-sm text-amber-800">
            Нова інкубація можлива лише для вільного інкубатора.
          </p>

          <button
            type="button"
            onClick={() => navigate(`/incubator/${device.id}`)}
            className="mt-4 font-semibold text-blue-600"
          >
            Переглянути інкубатор
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
            <div className="mb-5 flex items-center gap-3">
              <div className="rounded-xl bg-blue-50 p-3 text-blue-600">
                <Egg size={23} />
              </div>

              <div>
                <h2 className="font-semibold">Інкубаційна партія</h2>

                <p className="text-xs text-slate-500">
                  Місткість: {device.capacity} яєць
                </p>
              </div>
            </div>

            <label className="block text-sm font-semibold">
              Вид птиці
              <select
                value={bird}
                onChange={(event) => {
                  const selectedBird = event.target.value;
                  setBird(selectedBird);
                  setDuration(BIRDS[selectedBird] ?? 21);
                }}
                className={inputClass}
              >
                {Object.keys(BIRDS).map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="mt-5 block text-sm font-semibold">
              Кількість яєць
              <input
                required
                type="number"
                min={1}
                max={device.capacity}
                step={1}
                value={eggs}
                onChange={(event) => setEggs(Number(event.target.value))}
                className={inputClass}
              />
            </label>

            <label className="mt-5 block text-sm font-semibold">
              <span className="flex items-center gap-2">
                <CalendarDays size={17} />
                Тривалість, днів
              </span>

              <input
                required
                type="number"
                min={1}
                step={1}
                value={duration}
                onChange={(event) => setDuration(Number(event.target.value))}
                className={inputClass}
              />
            </label>
          </div>

          <div className="rounded-xl bg-blue-50 p-4 text-sm text-blue-900">
            Запуск створює запис інкубації у браузері. Він не вмикає нагрівачі,
            двигуни або інші пристрої ESP32.
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-600">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            <Play size={18} />
            Почати інкубацію
          </button>
        </form>
      )}
    </div>
  );
}
