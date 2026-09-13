"use client";

import { useSyncExternalStore } from "react";

// "mock veri" rozeti için küçük dış store.
// unknown: henüz istek yok · live: gerçek API yanıt verdi (HTTP hatası olsa bile) · mock: fetch ağ hatası → mock veri.
export type ApiState = "unknown" | "live" | "mock";

let state: ApiState = "unknown";
const listeners = new Set<() => void>();

export function setMockMode(mock: boolean): void {
  const next: ApiState = mock ? "mock" : "live";
  if (state === next) return;
  state = next;
  listeners.forEach((l) => l());
}

export function getApiState(): ApiState {
  return state;
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getServerSnapshot(): ApiState {
  return "unknown";
}

export function useApiState(): ApiState {
  return useSyncExternalStore(subscribe, getApiState, getServerSnapshot);
}

export function useMockMode(): boolean {
  return useApiState() === "mock";
}
