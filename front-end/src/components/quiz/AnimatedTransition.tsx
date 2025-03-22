
import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface AnimatedTransitionProps {
  show: boolean;
  children: React.ReactNode;
  duration?: number;
  className?: string;
  animation?: 'fade' | 'slide' | 'scale';
}

const AnimatedTransition: React.FC<AnimatedTransitionProps> = ({
  show,
  children,
  duration = 300,
  className,
  animation = 'fade'
}) => {
  const [shouldRender, setShouldRender] = useState(show);

  useEffect(() => {
    if (show) setShouldRender(true);
    else {
      const timer = setTimeout(() => {
        setShouldRender(false);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [show, duration]);

  const animationClasses = {
    fade: show ? 'animate-fade-in' : 'animate-fade-out',
    slide: show ? 'animate-slide-in' : 'animate-slide-out',
    scale: show ? 'animate-scale-in' : 'animate-scale-out'
  };

  return shouldRender ? (
    <div 
      className={cn(
        animationClasses[animation],
        className
      )}
      style={{ animationDuration: `${duration}ms` }}
    >
      {children}
    </div>
  ) : null;
};

export default AnimatedTransition;
