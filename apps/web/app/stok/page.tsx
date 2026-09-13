import type { Metadata } from "next";
import { StockView } from "@/components/views/StockView";

export const metadata: Metadata = { title: "Stok" };

export default function Page() {
  return <StockView />;
}
