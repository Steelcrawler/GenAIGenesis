import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import AuthProvider from "@/context/AuthContext";
import { SyncedProvider } from "@/components/SyncedProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Course Management App",
  description: "Manage your courses effectively",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <SyncedProvider>
            {children}
          </SyncedProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
