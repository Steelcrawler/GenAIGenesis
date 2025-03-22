'use client';

import React, { useState, useEffect } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from './SideBar';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);

  return (
    <div className="h-screen flex overflow-hidden">
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
        
        <main 
          className={cn(
            "flex-1 flex flex-col overflow-y-auto transition-all duration-300 ease-in-out",
          )}
        >
          <header className="md:hidden sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b p-4">
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(true)}
                className="mr-2"
              >
                <Menu className="h-5 w-5" />
              </Button>
              <h1 className="font-semibold text-lg">Courses</h1>
            </div>
          </header>

          <div className="flex-1 p-4 md:p-8 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;