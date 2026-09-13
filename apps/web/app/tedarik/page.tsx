import type { Metadata } from "next";
import { SupplyView } from "@/components/views/SupplyView";

export const metadata: Metadata = { title: "Tedarik" };

export default function Page() {
  return <SupplyView />;
}
