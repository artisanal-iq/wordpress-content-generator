import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { FiHome, FiFileText, FiTarget, FiSettings, FiMenu, FiX } from "react-icons/fi";
import Image from "next/image";
import { useState, useEffect } from "react";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WordPress Content Generator Dashboard",
  description: "Dashboard for managing automated WordPress content generation",
};

function SidebarLink({ href, icon, children, isMobileMenuOpen, setMobileMenuOpen }: { 
  href: string; 
  icon: React.ReactNode; 
  children: React.ReactNode;
  isMobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}) {
  return (
    <Link 
      href={href}
      className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors dark:text-gray-200 dark:hover:bg-gray-800"
      onClick={() => isMobileMenuOpen && setMobileMenuOpen(false)}
    >
      <span className="text-xl">{icon}</span>
      <span>{children}</span>
    </Link>
  );
}

function Sidebar({ isMobileMenuOpen, setMobileMenuOpen }: { 
  isMobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}) {
  return (
    <>
      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-30 h-full w-64 bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out
        dark:bg-gray-900 dark:border-gray-700
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo and close button */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <Link href="/" className="flex items-center gap-2">
              <div className="relative w-8 h-8">
                <Image
                  src="/wp-logo.svg"
                  alt="WordPress Logo"
                  fill
                  style={{ objectFit: "contain" }}
                />
              </div>
              <span className="font-semibold text-gray-800 dark:text-white">Content Generator</span>
            </Link>
            <button 
              className="p-1 rounded-md text-gray-500 hover:bg-gray-100 lg:hidden dark:text-gray-400 dark:hover:bg-gray-800"
              onClick={() => setMobileMenuOpen(false)}
            >
              <FiX size={24} />
            </button>
          </div>
          
          {/* Navigation links */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            <SidebarLink href="/" icon={<FiHome />} isMobileMenuOpen={isMobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen}>
              Dashboard
            </SidebarLink>
            <SidebarLink href="/content" icon={<FiFileText />} isMobileMenuOpen={isMobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen}>
              Content
            </SidebarLink>
            <SidebarLink href="/plans" icon={<FiTarget />} isMobileMenuOpen={isMobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen}>
              Strategic Plans
            </SidebarLink>
            <SidebarLink href="/settings" icon={<FiSettings />} isMobileMenuOpen={isMobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen}>
              Settings
            </SidebarLink>
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-gray-200 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400">
            <p>© {new Date().getFullYear()} WordPress Content Generator</p>
          </div>
        </div>
      </aside>
    </>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // State for mobile menu
  const [isMobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Close menu when pressing escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setMobileMenuOpen(false);
      }
    };
    
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-gray-50 dark:bg-gray-950`}>
        <Providers>
          {/* Mobile menu button */}
          <button 
            className="fixed top-4 left-4 z-10 p-2 rounded-md bg-white shadow-md lg:hidden dark:bg-gray-800"
            onClick={() => setMobileMenuOpen(true)}
          >
            <FiMenu size={24} className="text-gray-700 dark:text-gray-200" />
          </button>
          
          {/* Sidebar */}
          <Sidebar isMobileMenuOpen={isMobileMenuOpen} setMobileMenuOpen={setMobileMenuOpen} />
          
          {/* Main content */}
          <main className="lg:ml-64 min-h-screen transition-all duration-300">
            <div className="container mx-auto p-4 sm:p-6">
              {children}
            </div>
          </main>
        </Providers>
      </body>
    </html>
  );
}
