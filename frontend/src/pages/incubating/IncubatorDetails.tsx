import { useEffect, useState, type ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Egg,
  Thermometer,
  Droplets,
  Play,
  Trash2,
  CheckCircle2,
  AlertCircle,
  X,
  QrCode,
  RefreshCw,
  Wind,
  Clock3,
} from "lucide-react";
import {
  getIncubator,
  getIncubatorParameters,
  type Incubator,
  type IncubationParameters,
} from "../../services/incubators";

type MetricCardProps = {
  title: string;
  icon: ReactNode;
  target: number | null;
  targetLabel?: string;
  actual: number | null;
  unit: string;
  precision?: number;
  acceptableRange?: { min: number; max: number } | null;
};

function formatMetric(
  value: number | null,
  unit: string,
  precision: number,
): string {
  return value !== null && Number.isFinite(value)
    ? `${value.toFixed(precision)}${unit}`
    : "—";
}

function MetricCard({
  title,
  icon,
  target,
  targetLabel,
  actual,
  unit,
  precision = 1,
  acceptableRange,
}: MetricCardProps) {
  const hasActual = actual !== null && Number.isFinite(actual);
  const hasTarget = target !== null && Number.isFinite(target);
  const difference = hasTarget && hasActual ? actual - target : null;
  const inRange =
    acceptableRange && hasActual
      ? actual >= acceptableRange.min && actual <= acceptableRange.max
      : null;
  const isEqual = difference !== null && Math.abs(difference) < 0.000001;

  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
      <div className="mb-5 flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          {icon}
        </div>
        <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      </div>
      <p className="text-xs font-medium text-slate-500">Задане значення</p>
      <div className="mt-2 text-2xl font-bold text-slate-900">
        {targetLabel ?? formatMetric(target, unit, precision)}
      </div>
      <div className="my-4 border-t border-slate-100" />
      <p className="text-xs font-medium text-slate-500">Фактичне значення</p>
      <div className="mt-2 text-2xl font-bold text-blue-600">
        {formatMetric(actual, unit, precision)}
      </div>
      <div className="mt-4 min-h-5">
        {inRange !== null ? (
          <div
            className={`flex items-center gap-1 text-xs font-medium ${inRange ? "text-emerald-600" : "text-amber-600"}`}
          >
            {inRange ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
            <span>
              {inRange
                ? "У межах заданого діапазону"
                : "Поза заданим діапазоном"}
            </span>
          </div>
        ) : difference !== null ? (
          <div
            className={`flex items-center gap-1 text-xs font-medium ${isEqual ? "text-emerald-600" : "text-amber-600"}`}
          >
            {isEqual ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
            <span>
              {isEqual
                ? "Значення збігаються"
                : `Відхилення: ${difference > 0 ? "+" : ""}${difference.toFixed(precision)}${unit}`}
            </span>
          </div>
        ) : (
          <p className="text-xs text-slate-400">Немає даних для порівняння</p>
        )}
      </div>
    </div>
  );
}

type ParameterCardProps = {
  icon: ReactNode;
  label: string;
  value: string;
};

function ParameterCard({ icon, label, value }: ParameterCardProps) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center gap-2 text-blue-600">
        {icon}
        <span className="text-xs font-medium text-slate-500">{label}</span>
      </div>
      <p className="text-base font-semibold text-slate-900">{value}</p>
    </div>
  );
}

export default function IncubatorDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [device, setDevice] = useState<Incubator | null>(null);
  const [parameters, setParameters] = useState<IncubationParameters>({});
  const [loading, setLoading] = useState(true);
  const [parametersLoading, setParametersLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [parametersError, setParametersError] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    const incubatorId = Number(id);

    setDevice(null);
    setParameters({});
    setError(null);
    setParametersError(null);
    setLoading(true);
    setParametersLoading(true);

    if (!Number.isSafeInteger(incubatorId) || incubatorId <= 0) {
      setError("Некоректний ID інкубатора");
      setLoading(false);
      setParametersLoading(false);
      return;
    }

    async function load() {
      try {
        const result = await getIncubator(incubatorId);
        if (cancelled) return;
        setDevice(result);
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        setError(
          err instanceof Error
            ? err.message
            : "Не вдалося завантажити інкубатор",
        );
        setLoading(false);
        setParametersLoading(false);
        return;
      }

      try {
        const result = await getIncubatorParameters(incubatorId);
        if (!cancelled) setParameters(result);
      } catch (err) {
        if (!cancelled) {
          setParametersError(
            err instanceof Error
              ? err.message
              : "Не вдалося отримати параметри",
          );
        }
      } finally {
        if (!cancelled) setParametersLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl py-12 text-center text-sm text-slate-500">
        Завантаження інкубатора...
      </div>
    );
  }

  if (error || !device) {
    return (
      <div className="mx-auto max-w-2xl p-4">
        <h1 className="text-xl font-bold text-slate-900">
          {error ?? "Інкубатор не знайдено"}
        </h1>
        <button
          type="button"
          onClick={() => navigate("/incubator")}
          className="mt-4 text-blue-600"
        >
          Повернутися до списку
        </button>
      </div>
    );
  }

  const isIncubating = device.state === "incubating";
  const isAvailable = device.state === "available";
  const isBroken = device.state === "broken";
  const deviceType =
    device.device_type === "automatic"
      ? "Автоматичний"
      : device.device_type === "manual"
        ? "Ручний"
        : "Не вказано";

  const temperature = parameters.temperature ?? null;
  const humidity = parameters.humidity;
  const hasHumidityRange = humidity?.min != null && humidity?.max != null;
  const humidityRange = hasHumidityRange
    ? { min: humidity.min!, max: humidity.max! }
    : null;
  const humidityLabel = humidityRange
    ? `${humidityRange.min}–${humidityRange.max}%`
    : "—";

  return (
    <div className="mx-auto max-w-2xl pb-8 text-slate-900">
      <button
        type="button"
        onClick={() => navigate("/incubator")}
        className="mb-5 flex items-center gap-2 text-sm text-slate-500"
      >
        <ArrowLeft size={18} /> Усі інкубатори
      </button>

      <div className="mb-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-600">
          Smart Farm / Інкубація
        </p>
        <h1 className="mt-1 text-2xl font-bold">Інкубатор №{device.number}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
            {deviceType}
          </span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            ID: {device.id}
          </span>
          {device.capacity != null && (
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
              Місткість: {device.capacity}
            </span>
          )}
        </div>
      </div>

      {message && (
        <div
          role="status"
          className="mb-4 flex items-center justify-between gap-2 rounded-xl bg-blue-50 p-3 text-sm text-blue-900"
        >
          <span>{message}</span>
          <button
            type="button"
            aria-label="Закрити повідомлення"
            onClick={() => setMessage("")}
          >
            <X size={17} />
          </button>
        </div>
      )}

      {isIncubating ? (
        <div className="mb-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-600">
            <Egg size={18} /> Поточна інкубація
          </div>
          <div className="mt-3 text-3xl font-bold">
            {device.current_day != null
              ? `День ${device.current_day}${device.duration_days != null ? ` / ${device.duration_days}` : ""}`
              : "Інкубація триває"}
          </div>
          <p className="mt-2 text-sm text-slate-500">
            {device.activated_at
              ? `Запущено: ${new Date(device.activated_at).toLocaleString("uk-UA")}`
              : "Дата початку не вказана"}
          </p>
          <div className="mt-4 flex items-center justify-between gap-3 text-sm text-slate-500">
            <span>{device.eggs_amount ?? "—"} яєць</span>
            <span>{device.instruction_title ?? "Без інструкції"}</span>
          </div>
          {device.progress != null && device.duration_days != null ? (
            <div className="mt-5">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-slate-600">
                  Прогрес інкубації
                </span>
                <span className="font-semibold text-blue-600">
                  {device.progress.toFixed(1)}%
                </span>
              </div>
              <div
                className="h-2.5 overflow-hidden rounded-full bg-slate-100"
                role="progressbar"
                aria-valuenow={device.progress}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="h-full rounded-full bg-blue-600 transition-all"
                  style={{
                    width: `${Math.min(100, Math.max(0, device.progress))}%`,
                  }}
                />
              </div>
              <div className="mt-3 flex flex-wrap justify-between gap-2 text-xs text-slate-500">
                <span>
                  Завершення:{" "}
                  {device.estimated_end_at
                    ? new Date(device.estimated_end_at).toLocaleString("uk-UA")
                    : "—"}
                </span>
                <span>Залишилося: {device.days_remaining ?? "—"} дн.</span>
              </div>
            </div>
          ) : (
            <p className="mt-3 text-xs text-slate-400">
              Дані про тривалість інкубації відсутні в API або інструкції.
            </p>
          )}
        </div>
      ) : (
        <div className="mb-4 rounded-2xl border border-slate-100 bg-white p-6 text-center shadow-sm">
          {isBroken ? (
            <AlertCircle size={26} className="mx-auto mb-2 text-red-500" />
          ) : (
            <CheckCircle2 size={26} className="mx-auto mb-2 text-emerald-600" />
          )}
          <h2 className="font-semibold">
            {isBroken ? "Інкубатор несправний" : "Інкубатор вільний"}
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {isBroken
              ? "Наразі запуск недоступний."
              : "Можна розпочати нову інкубацію."}
          </p>
        </div>
      )}

      <div className="mb-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">
          Показники інкубатора
        </h2>
        {parametersLoading && (
          <p className="mb-3 text-sm text-slate-500">
            Завантаження заданих параметрів...
          </p>
        )}
        {parametersError && (
          <p
            role="alert"
            className="mb-3 rounded-xl bg-red-50 p-3 text-sm text-red-700"
          >
            Не вдалося завантажити задані параметри: {parametersError}
          </p>
        )}
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            title="Температура"
            icon={<Thermometer size={20} />}
            target={temperature}
            actual={device.actual_temperature ?? null}
            unit="°C"
          />
          <MetricCard
            title="Вологість"
            icon={<Droplets size={20} />}
            target={null}
            targetLabel={humidityLabel}
            actual={device.actual_humidity ?? null}
            unit="%"
            precision={0}
            acceptableRange={humidityRange}
          />
        </div>
      </div>

      <div className="mb-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">
          Параметри догляду
        </h2>
        <div className="grid grid-cols-2 gap-3">
          <ParameterCard
            icon={<RefreshCw size={18} />}
            label="Перевертання"
            value={
              parameters.turning_interval == null
                ? "Не задано"
                : parameters.turning_interval === 0
                  ? "Вимкнено"
                  : `Кожні ${parameters.turning_interval} год`
            }
          />
          <ParameterCard
            icon={<Wind size={18} />}
            label="Провітрювання"
            value={
              parameters.ventilation_count == null
                ? "Не задано"
                : parameters.ventilation_count === 0
                  ? "Вимкнено"
                  : `${parameters.ventilation_count} разів/добу`
            }
          />
          <ParameterCard
            icon={<Clock3 size={18} />}
            label="Тривалість провітрювання"
            value={
              parameters.ventilation_duration == null
                ? "Не задано"
                : `${parameters.ventilation_duration} хв`
            }
          />
        </div>
      </div>

      <div className="mb-4 rounded-xl bg-blue-50 p-4 text-sm text-blue-900">
        Задані параметри беруться з поточного стану інструкції інкубації.
        Фактичні показники надходять з датчиків або ручного введення, якщо вони
        підключені.
      </div>

      <button
        type="button"
        onClick={() => navigate(`/incubator/${device.id}/qr`)}
        className="mb-4 flex w-full items-center justify-center gap-3 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 font-semibold text-blue-700"
      >
        <QrCode size={20} /> Сформувати QR-код
      </button>

      {isAvailable && (
        <button
          type="button"
          onClick={() => navigate(`/incubator/${device.id}/start`)}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white"
        >
          <Play size={18} /> Почати інкубацію
        </button>
      )}

      {isIncubating && (
        <button
          type="button"
          disabled
          title="Потрібно підключити API завершення інкубації"
          className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 font-semibold text-slate-400"
        >
          Завершити інкубацію
        </button>
      )}

      {isAvailable && (
        <button
          type="button"
          disabled
          title="Потрібно підключити API видалення інкубатора"
          className="mt-5 flex w-full items-center justify-center gap-2 py-2 text-sm text-red-300"
        >
          <Trash2 size={17} /> Видалити інкубатор
        </button>
      )}
    </div>
  );
}
