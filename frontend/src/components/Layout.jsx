import { useState } from "react";
import TopBar from "./TopBar";
import BottomNav from "./BottomNav";
import Tutorial from "./Tutorial";

export default function Layout({ children, showNav = true, showTop = true }) {
  const [tutOpen, setTutOpen] = useState(false);
  return (
    <div className="min-h-screen flex flex-col">
      {showTop && <TopBar onHelp={() => setTutOpen(true)} />}
      <main className="flex-1 w-full">
        <div className="max-w-md mx-auto px-5 pt-5 pb-28">{children}</div>
      </main>
      {showNav && <BottomNav />}
      <Tutorial open={tutOpen} onClose={() => setTutOpen(false)} />
    </div>
  );
}
