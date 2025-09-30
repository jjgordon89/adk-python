import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';

/**
 * Theme types
 */
export type Theme = 'light' | 'dark' | 'system';

interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

interface ThemeProviderState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

const initialState: ThemeProviderState = {
  theme: 'system',
  setTheme: () => null,
  resolvedTheme: 'light',
};

const ThemeProviderContext = createContext<ThemeProviderState>(initialState);

/**
 * ThemeProvider Component
 * 
 * Provides theme management functionality including:
 * - Light/dark mode switching
 * - System preference detection
 * - Theme persistence to localStorage
 * - CSS class management on root element
 */
export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'adk-gui-theme',
  ...props
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme
  );

  // Get the resolved theme (either 'light' or 'dark')
  const getResolvedTheme = (currentTheme: Theme): 'light' | 'dark' => {
    if (currentTheme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    }
    return currentTheme;
  };

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>(
    () => getResolvedTheme(theme)
  );

  useEffect(() => {
    const root = window.document.documentElement;
    const newResolvedTheme = getResolvedTheme(theme);
    
    setResolvedTheme(newResolvedTheme);
    
    // Remove both classes first
    root.classList.remove('light', 'dark');
    
    // Add the appropriate class
    root.classList.add(newResolvedTheme);
  }, [theme]);

  // Listen for system theme changes when theme is set to 'system'
  useEffect(() => {
    if (theme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      const newResolvedTheme = mediaQuery.matches ? 'dark' : 'light';
      setResolvedTheme(newResolvedTheme);
      
      const root = window.document.documentElement;
      root.classList.remove('light', 'dark');
      root.classList.add(newResolvedTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme);
    setThemeState(newTheme);
  };

  const value = {
    theme,
    setTheme,
    resolvedTheme,
  };

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  );
}

/**
 * useTheme Hook
 * 
 * Access theme state and setter from anywhere in the component tree
 * 
 * @returns ThemeProviderState with current theme, setTheme function, and resolvedTheme
 * @throws Error if used outside of ThemeProvider
 * 
 * @example
 * ```tsx
 * const { theme, setTheme, resolvedTheme } = useTheme();
 * 
 * // Change theme
 * setTheme('dark');
 * 
 * // Check current theme
 * console.log(theme); // 'light' | 'dark' | 'system'
 * console.log(resolvedTheme); // 'light' | 'dark'
 * ```
 */
export const useTheme = () => {
  const context = useContext(ThemeProviderContext);

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  return context;
};