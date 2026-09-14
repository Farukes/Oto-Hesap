import type { Metadata } from "next";
import { OverviewView } from "@/components/views/OverviewView";

// Kök segment, layout ile aynı segmentte olduğu için `title.template` burada
// uygulanmaz; sekme adı diğer sayfalarla aynı kalsın diye tam yazılır.
export const metadata: Metadata = { title: "Genel Bakış · OtoHesap" };

export default function Page() {
  return <OverviewView />;
}
