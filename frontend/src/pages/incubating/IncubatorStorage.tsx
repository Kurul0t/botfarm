export type DeviceType = "manual" | "automatic";

export type DeviceStatus = "available" | "working" | "maintenance";

export interface Batch {
  id: string;
  bird: string;
  eggs: number;
  startedAt: string;
  duration: number;
}

export interface Device {
  id: string;
  uuid: string;
  name: string;
  type: DeviceType;
  status: DeviceStatus;
  capacity: number;
  temperature?: number;
  humidity?: number;
  batch?: Batch;
}

export const BIRDS: Record<string, number> = {
  Кури: 21,
  Качки: 28,
  Гуси: 30,
  Індики: 28,
};

const STORAGE_KEY = "smart-farm-incubators-v2";

// Генерація UUID
export function generateUUID(): string {
  return crypto.randomUUID();
}

function createDemoDevices(): Device[] {
  return [
    {
      id: "demo-1",
      uuid: "550e8400-e29b-41d4-a716-446655440001",
      name: "Інкубатор №1",
      type: "automatic",
      status: "working",
      capacity: 500,
      temperature: 37.6,
      humidity: 56,
      batch: {
        id: "batch-1",
        bird: "Кури",
        eggs: 280,
        startedAt: new Date(Date.now() - 11 * 86400000).toISOString(),
        duration: 21,
      },
    },
    {
      id: "demo-2",
      uuid: "550e8400-e29b-41d4-a716-446655440000",
      name: "Інкубатор №2",
      type: "manual",
      status: "working",
      capacity: 200,
      batch: {
        id: "batch-2",
        bird: "Качки",
        eggs: 120,
        startedAt: new Date(Date.now() - 6 * 86400000).toISOString(),
        duration: 28,
      },
    },
    {
      id: "demo-3",
      uuid: "550e8400-e29b-41d4-a716-446655440003",
      name: "Інкубатор №3",
      type: "automatic",
      status: "available",
      capacity: 300,
    },
  ];
}

// Збереження інкубаторів
export function saveDevices(devices: Device[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(devices));
}

// Отримання інкубаторів + міграція UUID
export function getDevices(): Device[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (saved === null) {
      const initial = createDemoDevices();
      saveDevices(initial);
      return initial;
    }

    const parsed: unknown = JSON.parse(saved);

    if (!Array.isArray(parsed)) {
      return [];
    }

    let changed = false;

    const devices: Device[] = (parsed as Device[]).map((device) => {
      if (device.uuid) {
        return device;
      }

      changed = true;

      return {
        ...device,
        uuid: generateUUID(),
      };
    });

    // Зберігаємо нові UUID лише один раз
    if (changed) {
      saveDevices(devices);
    }

    return devices;
  } catch (error) {
    console.error("Помилка читання інкубаторів:", error);
    return [];
  }
}

// Пошук за звичайним ID
export function getDevice(id: string): Device | undefined {
  return getDevices().find((device) => device.id === id);
}

// Пошук за UUID із QR-коду
export function getDeviceByUUID(uuid: string): Device | undefined {
  return getDevices().find((device) => device.uuid === uuid);
}

// Створення інкубатора
export function addDevice(
  device: Omit<Device, "uuid"> & {
    uuid?: string;
  },
): void {
  const devices = getDevices();

  const newDevice: Device = {
    ...device,
    uuid: device.uuid || generateUUID(),
  };

  saveDevices([...devices, newDevice]);
}

// Оновлення інкубатора
export function updateDevice(updated: Device): void {
  const devices = getDevices();

  saveDevices(
    devices.map((device) =>
      device.id === updated.id
        ? {
            ...updated,
            // UUID не змінюємо під час редагування
            uuid: device.uuid,
          }
        : device,
    ),
  );
}

// Видалення інкубатора
export function deleteDevice(id: string): void {
  saveDevices(getDevices().filter((device) => device.id !== id));
}

// Прогрес інкубації
export function getProgress(batch: Batch) {
  const elapsed = Math.max(
    0,
    Math.floor((Date.now() - new Date(batch.startedAt).getTime()) / 86400000),
  );

  return {
    day: Math.min(batch.duration, elapsed + 1),

    percent: Math.min(100, Math.round((elapsed / batch.duration) * 100)),

    remaining: Math.max(0, batch.duration - elapsed),
  };
}
