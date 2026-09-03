import type { Metadata } from "next";
import "./styles.css";

export const metadata: Metadata = { title: "ClearFrame — NIGHT SHIFT", description: "Evidence-led clearance operations." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
