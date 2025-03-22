import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { CourseProvider } from "@/context/CourseContext";
import  AuthProvider  from "@/context/AuthContext";

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
      <body className={inter.className}>
        <AuthProvider>
          <TooltipProvider>
            <CourseProvider>
              <Sonner />
              {children}
            </CourseProvider>
          </TooltipProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
