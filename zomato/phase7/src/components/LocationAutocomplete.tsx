"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { fetchLocations } from "@/lib/api";
import { ChevronDownIcon, MapPinIcon } from "@/components/Icons";

interface LocationAutocompleteProps {
  id?: string;
  value: string;
  disabled?: boolean;
  hasError?: boolean;
  onChange: (value: string) => void;
}

function fieldClass(hasError: boolean): string {
  const base =
    "w-full rounded-lg border bg-white py-2.5 pl-10 pr-10 text-base text-ink-primary transition-colors";
  return hasError ? `${base} border-error` : `${base} border-gray-200`;
}

export function LocationAutocomplete({
  id = "location",
  value,
  disabled = false,
  hasError = false,
  onChange,
}: LocationAutocompleteProps) {
  const [locations, setLocations] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;

    fetchLocations("Bangalore")
      .then((names) => {
        if (!cancelled) {
          setLocations(names);
          setLoadError(null);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadError("Could not load Bangalore locations.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const suggestions = useMemo(() => {
    const query = value.trim().toLowerCase();
    if (!query) {
      return locations.slice(0, 12);
    }
    return locations
      .filter((name) => name.toLowerCase().startsWith(query))
      .concat(
        locations.filter(
          (name) =>
            !name.toLowerCase().startsWith(query) &&
            name.toLowerCase().includes(query),
        ),
      )
      .slice(0, 12);
  }, [locations, value]);

  function selectLocation(name: string) {
    onChange(name);
    setOpen(false);
  }

  return (
    <div ref={containerRef} className="relative">
      <MapPinIcon className="pointer-events-none absolute left-3 top-1/2 z-10 h-4 w-4 -translate-y-1/2 text-gray-400" />
      <input
        id={id}
        type="text"
        role="combobox"
        aria-expanded={open}
        aria-controls={`${id}-listbox`}
        aria-autocomplete="list"
        autoComplete="off"
        className={fieldClass(hasError)}
        placeholder="Type a Bangalore locality"
        value={value}
        disabled={disabled}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Escape") {
            setOpen(false);
          }
        }}
      />
      <ChevronDownIcon className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />

      {open && !disabled && (
        <ul
          id={`${id}-listbox`}
          role="listbox"
          className="absolute z-20 mt-1 max-h-56 w-full overflow-auto rounded-lg border border-gray-200 bg-white py-1 shadow-card"
        >
          {suggestions.length === 0 ? (
            <li className="px-3 py-2 text-sm text-ink-secondary">
              {loadError ||
                (locations.length === 0
                  ? "Loading locations..."
                  : "No matching Bangalore localities")}
            </li>
          ) : (
            suggestions.map((name) => (
              <li key={name} role="option">
                <button
                  type="button"
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-ink-primary hover:bg-gray-50"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => selectLocation(name)}
                >
                  <MapPinIcon className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                  {name}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
