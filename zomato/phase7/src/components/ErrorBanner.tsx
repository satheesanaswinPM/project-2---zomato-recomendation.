interface ErrorBannerProps {
  message: string;
  isError?: boolean;
}

export function ErrorBanner({ message, isError = true }: ErrorBannerProps) {
  const classes = isError
    ? "border-error-border bg-error-bg text-error"
    : "border-notice-info-border bg-notice-info-bg text-ink-primary";

  return (
    <p className={`mb-4 rounded-lg border px-4 py-3 text-sm ${classes}`}>
      {message}
    </p>
  );
}
