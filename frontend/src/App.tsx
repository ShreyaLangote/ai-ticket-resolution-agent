import { useState } from "react";
import { Bell, RefreshCw, Settings, User, Clock, AlertTriangle } from "lucide-react"; // icons

export default function App() {
  const [tickets] = useState([
    { id: 1, title: "Login not working", priority: "High", status: "Open" },
    { id: 2, title: "Payment gateway error", priority: "Medium", status: "In Progress" },
    { id: 3, title: "UI bug on dashboard", priority: "Low", status: "Resolved" },
  ]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-mono flex flex-col">
      {/* 🔹 Top Navbar */}
      <header className="flex items-center justify-between px-6 h-16 bg-gray-900/80 border-b border-cyan-400/20 backdrop-blur-md">
        <div className="flex items-center gap-6">
          <h1 className="text-2xl font-extrabold tracking-wide text-cyan-400">
            PriorityOps
          </h1>
          <select className="bg-gray-800 px-2 py-1 rounded-md border border-gray-700 text-sm">
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
          </select>
          <select className="bg-gray-800 px-2 py-1 rounded-md border border-gray-700 text-sm">
            <option>All Teams</option>
            <option>Support</option>
            <option>Engineering</option>
          </select>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs">Critical</span>
            <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs">High</span>
            <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Medium</span>
            <span className="px-2 py-1 bg-gray-500/20 text-gray-300 rounded text-xs">Low</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button className="flex items-center gap-1 text-sm text-gray-300 hover:text-cyan-400">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
          <span className="text-xs text-green-400">● Live</span>
          <Bell className="w-5 h-5 text-gray-400 hover:text-cyan-400" />
          <Settings className="w-5 h-5 text-gray-400 hover:text-cyan-400" />
          <User className="w-6 h-6 text-cyan-400" />
        </div>
      </header>

      {/* 🔹 Dashboard Section */}
      <main className="p-6 space-y-6 flex-1">
        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard label="Active Tickets" value="44" icon="🎫" color="blue" />
          <StatCard label="Avg Resolution Time" value="3.4 hrs" icon="⏱️" color="green" />
          <StatCard label="SLA Compliance" value="88.9%" icon="🎯" color="orange" />
          <StatCard label="AI Accuracy" value="82.9%" icon="🧠" color="cyan" />
        </div>

        {/* Ticket Flow & Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart Placeholder */}
          <div className="col-span-2 bg-gray-900/70 border border-cyan-400/20 rounded-xl p-6">
            <h2 className="text-cyan-400 text-lg mb-4">Real-Time Ticket Flow</h2>
            <div className="h-64 flex items-center justify-center text-gray-500">
              📊 Chart goes here
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-gray-900/70 border border-cyan-400/20 rounded-xl p-6 space-y-4">
            <h2 className="text-cyan-400 text-lg">Quick Stats</h2>
            <p>Tickets Today: <span className="text-white font-bold">23</span></p>
            <p>Resolved Today: <span className="text-green-400 font-bold">18</span></p>
            <p>Escalated: <span className="text-red-400 font-bold">3</span></p>
            <p>Avg Response: <span className="text-cyan-400 font-bold">18m</span></p>
          </div>
        </div>

        {/* Tickets Table */}
        <div className="bg-gray-900/70 border border-cyan-400/20 rounded-xl p-6">
          <h2 className="text-cyan-400 text-lg mb-4">Tickets</h2>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-gray-400 text-sm border-b border-cyan-400/20">
                <th className="py-2">ID</th>
                <th className="py-2">Title</th>
                <th className="py-2">Priority</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t) => (
                <tr key={t.id} className="hover:bg-gray-800/50 transition">
                  <td className="py-2">{t.id}</td>
                  <td className="py-2">{t.title}</td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded text-xs 
                      ${t.priority === "High" ? "bg-red-500/20 text-red-400" : 
                        t.priority === "Medium" ? "bg-yellow-500/20 text-yellow-400" : 
                        "bg-green-500/20 text-green-400"}`}>
                      {t.priority}
                    </span>
                  </td>
                  <td className="py-2">
                    <span className={`px-2 py-1 rounded text-xs 
                      ${t.status === "Open" ? "bg-blue-500/20 text-blue-400" : 
                        t.status === "In Progress" ? "bg-yellow-500/20 text-yellow-400" : 
                        "bg-green-500/20 text-green-400"}`}>
                      {t.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

/* 🔹 Reusable Stat Card */
function StatCard({ label, value, icon, color }: { label: string; value: string; icon: string; color: string }) {
  const colors: Record<string, string> = {
    blue: "text-blue-400 border-blue-400/20",
    green: "text-green-400 border-green-400/20",
    orange: "text-orange-400 border-orange-400/20",
    cyan: "text-cyan-400 border-cyan-400/20",
  };

  return (
    <div className={`bg-gray-900/70 border ${colors[color]} rounded-xl p-6 shadow-lg`}>
      <div className="flex items-center justify-between">
        <span className="text-lg">{label}</span>
        <span>{icon}</span>
      </div>
      <p className={`text-3xl font-bold mt-2 ${colors[color]}`}>{value}</p>
    </div>
  );
}
