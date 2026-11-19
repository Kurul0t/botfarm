import { Link, useLocation } from "react-router-dom";

export default function BottomNav() {
  const location = useLocation();
  const currentPath = location.pathname;

  const items = [
    { path: "/", label: "Головна", icon: "home" },
    { path: "/explore", label: "Огляд", icon: "explore" },
    { path: "/messages", label: "Повідомлення", icon: "chat" },
    { path: "/settings", label: "Налаштування", icon: "settings" },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur border-t border-[#eef0f3] pb-[env(safe-area-inset-bottom,0px)]">
      <div className="flex justify-around items-center h-16">
        {items.map((item) => {
          const active = currentPath === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center min-w-[64px] ${
                active ? "text-[#0037b0]" : "text-[#8b90a0]"
              }`}
            >
              <div
                className={`w-12 h-8 rounded-full flex items-center justify-center ${
                  active ? "bg-[#dae2fd]" : ""
                }`}
              >
                <span className="material-symbols-outlined text-[24px]">
                  {item.icon}
                </span>
              </div>
              <span className="text-[11px] font-medium mt-0.5">
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
