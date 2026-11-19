export interface QRData {
  v: number;
  type: string;
  id: string;
  action: string;
}

export function resolveQRCode(raw: string): QRData | null {
  try {
    const data: unknown = JSON.parse(raw);

    if (
      typeof data !== "object" ||
      data === null ||
      !("v" in data) ||
      !("type" in data) ||
      !("id" in data) ||
      !("action" in data)
    ) {
      return null;
    }

    if (
      data.v !== 1 ||
      data.type !== "incubator" ||
      data.action !== "details" ||
      typeof data.id !== "string" ||
      !/^\d{6}-\d{2}-\d{6}-\d$/.test(data.id)
    ) {
      return null;
    }

    return {
      v: 1,
      type: "incubator",
      id: data.id,
      action: "details",
    };
  } catch {
    return null;
  }
}
