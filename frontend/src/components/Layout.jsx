import TopBar from "./TopBar";
import BottomNav from "./BottomNav";

export default function Layout({ children, showNav = true, showTop = true }) {
  return (
    <div className="min-h-screen bg-[#FAFAFA] flex flex-col">
      {showTop && <TopBar />}
      <main className="flex-1 w-full">
        <div className="max-w-md mx-auto px-5 pt-5 pb-28">{children}</div>
      </main>
      {showNav && <BottomNav />}
    </div>
  );
}
