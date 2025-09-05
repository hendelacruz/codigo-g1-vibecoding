/**
 * StatsSection component for displaying todo statistics
 * Groups multiple StatsCard components in a responsive grid
 */

import { StatsCard } from "../../ui/StatsCard";

interface StatsSectionProps {
  todosCount: {
    total: number;
    completed: number;
    pending: number;
  };
}

export const StatsSection = ({ todosCount }: StatsSectionProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <StatsCard value={todosCount.total} label="Total" color="blue" />
      <StatsCard
        value={todosCount.completed}
        label="Completadas"
        color="green"
      />
      <StatsCard value={todosCount.pending} label="Pendientes" color="orange" />
    </div>
  );
};

export default StatsSection;
