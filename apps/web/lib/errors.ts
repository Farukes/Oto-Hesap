// API hata tipi; gövde {detail:"Türkçe açıklama"} sözleşmesine göre.

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.detail;
  if (err instanceof Error && err.message) return err.message;
  return "Beklenmeyen bir hata oluştu.";
}

export function errorStatus(err: unknown): number | null {
  return err instanceof ApiError ? err.status : null;
}
