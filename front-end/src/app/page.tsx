'use client'

import { useRouter } from "next/navigation";

// page not in use
export default function Home() {
  const router = useRouter();

  return (
    <button onClick={() => router.push('/login')}>Login</button>
  );
}
