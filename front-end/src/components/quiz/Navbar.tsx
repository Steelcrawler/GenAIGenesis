
import React from 'react';
import Link from 'next/link'

const Navbar: React.FC = () => {
  return (
    <nav className="p-6 w-full">
      <div className="container-fluid flex items-center justify-between">
        <Link 
            href="/courses" 
            className="text-lg font-medium tracking-tight hover:opacity-80 transition-opacity"
        >
            TempName
        </Link>
        <div className="flex items-center space-x-1">
        <Link 
            href="/courses" 
            className="px-4 py-2 rounded-full text-m font-medium hover:bg-secondary transition-colors"
        >
            Home
        </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;