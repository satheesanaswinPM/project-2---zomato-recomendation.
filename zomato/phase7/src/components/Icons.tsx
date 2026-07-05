export function CompassLogo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <circle cx="16" cy="16" r="15" fill="#E23744" />
      <path d="M16 6L18.5 16L16 26L13.5 16L16 6Z" fill="white" />
      <path d="M6 16L16 13.5L26 16L16 18.5L6 16Z" fill="white" fillOpacity="0.9" />
      <circle cx="16" cy="16" r="2.5" fill="white" />
    </svg>
  );
}

export function MapPinIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden>
      <path
        fillRule="evenodd"
        d="M9.69 18.933l.003.001C9.89 19.02 10 19 10 19s.11.02.308-.066l.002-.001.006-.003.018-.008a5.741 5.741 0 00.281-.14c.186-.096.446-.24.757-.433.62-.384 1.445-.966 2.274-1.765C13.304 14.988 15 12.494 15 9.5a6 6 0 10-12 0c0 3.013 1.696 5.508 3.355 7.09.83.799 1.654 1.38 2.274 1.765.311.193.571.337.757.433a5.74 5.74 0 00.281.14l.018.008.006.003zM10 11.25a1.75 1.75 0 100-3.5 1.75 1.75 0 000 3.5z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function UtensilsIcon({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden>
      <path d="M3 2a1 1 0 011 1v5.5a2.5 2.5 0 005 0V3a1 1 0 112 0v5.5a4.5 4.5 0 01-9 0V3a1 1 0 011-1zM14 2a1 1 0 00-1 1v12.05A3.5 3.5 0 0013.5 18h1a3.5 3.5 0 003.5-3.5V3a1 1 0 00-1-1h-3z" />
    </svg>
  );
}

export function SearchIcon({ className = "h-5 w-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden>
      <path
        fillRule="evenodd"
        d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function ChevronDownIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden>
      <path
        fillRule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.94a.75.75 0 111.08 1.04l-4.24 4.5a.75.75 0 01-1.08 0l-4.24-4.5a.75.75 0 01.02-1.06z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function WalletIcon({ className = "h-3.5 w-3.5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden>
      <path d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm10 6a2 2 0 100-4 2 2 0 000 4z" />
    </svg>
  );
}
