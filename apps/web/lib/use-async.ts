"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { errorMessage } from "./errors";

interface AsyncState<T> {
  key: string;
  tick: number;
  data?: T;
  error?: string;
}

/**
 * İstemci tarafı veri çekme kancası. `key` değişince veya `reload()` çağrılınca yükleyici yeniden koşar.
 * Önceki veri yeniden yükleme sırasında korunur (tablo titremesin).
 */
export function useAsync<T>(loader: () => Promise<T>, key = "") {
  const [state, setState] = useState<AsyncState<T>>({ key: "__init__", tick: -1 });
  const [tick, setTick] = useState(0);
  const loaderRef = useRef(loader);

  useEffect(() => {
    loaderRef.current = loader;
  });

  useEffect(() => {
    let cancelled = false;
    loaderRef.current().then(
      (data) => {
        if (!cancelled) setState({ key, tick, data });
      },
      (err: unknown) => {
        if (!cancelled) setState({ key, tick, error: errorMessage(err) });
      },
    );
    return () => {
      cancelled = true;
    };
  }, [key, tick]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  const loading = state.key !== key || state.tick !== tick;

  return { data: state.data, error: loading ? undefined : state.error, loading, reload };
}
