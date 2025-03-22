'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('http://localhost:8000/api/status/', {
          method: 'GET',
          credentials: 'include',
        });
        const data = await res.json();

        if (!data.logged_in) {
           
            if (pathname !== '/login' && pathname !== '/signup') {
              router.push('/login');
            }
          } else {
            
            if (pathname === '/login' || pathname === '/signup') {
               router.push('/courses');
            }
          }


        
      } catch (err) {
        console.error(err);
        if (pathname !== '/login') {
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [pathname, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
}
