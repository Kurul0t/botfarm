import { useNavigate } from "react-router-dom";
import "./Home.css";

function QuickAccessCard({
  icon,
  title,
  description,
  badge,
  iconBg,
  iconColor,
  onClick,
}: {
  icon: string;
  title: string;
  description: string;
  badge?: string;
  iconBg: string;
  iconColor: string;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="group w-full rounded-2xl bg-white p-4 shadow-sm text-left active:scale-[0.98] transition cursor-pointer"
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-11 h-11 rounded-xl ${iconBg} ${iconColor} flex items-center justify-center shrink-0`}
        >
          <span className="material-symbols-outlined text-[24px]">{icon}</span>
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[15px] text-[#191c1e] truncate">
              {title}
            </span>
            {badge && (
              <span className="px-2 py-0.5 rounded-full bg-[#0037b0] text-white text-[10px] font-semibold shrink-0">
                {badge}
              </span>
            )}
          </div>
          <p className="text-[12px] text-[#565e74] truncate mt-0.5">
            {description}
          </p>
        </div>

        <span className="material-symbols-outlined text-[20px] text-[#9aa0b0] shrink-0">
          chevron_right
        </span>
      </div>
    </button>
  );
}

export default function Home() {
  const navigate = useNavigate(); // Використовуємо роутер для переходу

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {/* Cards 
          <QuickAccessCard
            icon="insights"
            title="Аналітика"
            description="Звіти та статистика по компанії"
            badge="НОВЕ"
            iconBg="bg-[#e8ecff]"
            iconColor="text-[#0037b0]"
          />
          <QuickAccessCard
            icon="local_shipping"
            title="Трекінг замовлень"
            description="Зручне опрацювання замовлень"
            badge="НОВЕ"
            iconBg="bg-[#e8ecff]"
            iconColor="text-[#0037b0]"
          />
          <QuickAccessCard
            icon="point_of_sale"
            title="Мобільна каса"
            description="Створіть замовленя де завгодно"
            badge="НОВЕ"
            iconBg="bg-[#e8ecff]"
            iconColor="text-[#0037b0]"
          />
            
            */}
        <QuickAccessCard
          icon="egg"
          title="Smart-інкубатор"
          description="Керування інкубатором онлайн"
          badge="НОВЕ"
          iconBg="bg-[#e8ecff]"
          iconColor="text-[#0037b0]"
          onClick={() => navigate("/incubator")} // <--- Веде прямо на сторінку інкубатора в роутері
        />
      </div>
    </div>
  );
}
