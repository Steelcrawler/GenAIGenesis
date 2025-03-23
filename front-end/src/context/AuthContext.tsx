"use client";

import React, { useState, useEffect, useContext, createContext } from "react";
import { useRouter, usePathname } from "next/navigation";

export interface AuthState {
  loggedIn: boolean;
  userId: number | null;
  username: string | null;
}

const AuthContext = createContext<AuthState>({
  loggedIn: false,
  userId: null,
  username: null,
});

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [authState, setAuthState] = useState<AuthState>({
    loggedIn: false,
    userId: null,
    username: null,
  });

  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/api/status/", {
          method: "GET",
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          setAuthState({
            loggedIn: data.logged_in,
            userId: data.user_id,
            username: data.username,
          });

          if (!data.logged_in) {
            if (pathname !== "/login" && pathname !== "/signup") {
              router.push("/login");
            }
          } else {
            if (pathname === "/login" || pathname === "/signup") {
              router.push("/courses");
            }
          }
        } else {
          if (pathname !== "/login") {
            router.push("/login");
          }
        }
      } catch (err) {
        console.error("Error checking auth status:", err);
        if (pathname !== "/login") {
          router.push("/login");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [pathname, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
