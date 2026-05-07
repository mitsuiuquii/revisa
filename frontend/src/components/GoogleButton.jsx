// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
export default function GoogleButton({ testId = "google-login-btn", label = "Entrar com Google" }) {
  const handleClick = () => {
    const redirectUrl = window.location.origin + "/auth/callback";
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };
  return (
    <button
      type="button"
      onClick={handleClick}
      data-testid={testId}
      className="btn-tactile btn-secondary-revisa w-full flex items-center justify-center gap-3 text-base"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.4-1.6 4.1-5.5 4.1-3.3 0-6-2.7-6-6.1s2.7-6.1 6-6.1c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.9 3.5 14.7 2.5 12 2.5 6.8 2.5 2.6 6.7 2.6 12s4.2 9.5 9.4 9.5c5.4 0 9-3.8 9-9.1 0-.6-.1-1.1-.1-1.7H12z"/>
        <path fill="#34A853" d="M3.9 7.6l3.2 2.3C8 8.1 9.9 6.9 12 6.9c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.9 3.5 14.7 2.5 12 2.5 8.2 2.5 5 4.6 3.9 7.6z" opacity="0"/>
        <path fill="#FBBC05" d="M3.9 7.6C2.8 9.6 2.6 11.6 2.6 12c0 .4.2 2.4 1.3 4.4l3.2-2.5c-.3-.9-.5-1.8-.5-2.9 0-1.1.2-2 .5-2.9L3.9 7.6z" opacity="0"/>
        <path fill="#4285F4" d="M12 21.5c2.7 0 5-1 6.7-2.6l-3.2-2.5c-.9.6-2 1-3.5 1-2.6 0-4.9-1.8-5.7-4.1L3 15.8c1.5 3.4 4.9 5.7 9 5.7z" opacity="0"/>
      </svg>
      {label}
    </button>
  );
}
