"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getStats, isLoggedIn, Stats } from "@/lib/api";

const MOOD_LABELS: Record<number, string> = {
  1: "Terrible",
  2: "Bad",
  3: "Okay",
  4: "Good",
  5: "Great",
};

export default function StatsPage() {
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) {
      router.push("/login");
      return;
    }
    loadStats();
  }, [router]);

  async function loadStats() {
    try {
      setLoading(true);
      const data = await getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stats");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p>Loading...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-red-600">{error}</p>
      </main>
    );
  }

  if (!stats) return null;

  const hasData = stats.total_entries > 0;

  return (
    <main className="max-w-3xl mx-auto p-8 space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Stats</h1>
        <Link href="/entries" className="text-sm underline">
          Back to entries
        </Link>
      </div>

      {!hasData ? (
        <p className="text-gray-500">No entries yet. Write something first.</p>
      ) : (
        <>
          {/* Big numbers */}
          <div className="grid grid-cols-2 gap-4">
            <Card label="Total entries" value={stats.total_entries.toString()} />
            <Card
              label="Average mood"
              value={
                stats.average_mood !== null
                  ? `${stats.average_mood.toFixed(1)} / 5`
                  : "—"
              }
              hint={
                stats.average_mood !== null
                  ? MOOD_LABELS[Math.round(stats.average_mood)]
                  : undefined
              }
            />
          </div>

          {/* Mood over time */}
          <section>
            <h2 className="text-lg font-semibold mb-3">Mood over time</h2>
            <div className="border rounded p-4">
              <ResponsiveContainer width="100%" height={240}>
                <LineChart
                  data={stats.mood_over_time}
                  margin={{ top: 5, right: 10, bottom: 5, left: -20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(d) =>
                      new Date(d).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                      })
                    }
                  />
                  <YAxis
                    domain={[1, 5]}
                    ticks={[1, 2, 3, 4, 5]}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip
                    formatter={(value) => [typeof value === "number" ? value.toFixed(2) : value, "Avg mood"]}
                    labelFormatter={(d) => new Date(d).toLocaleDateString()}
                  />
                  <Line
                    type="monotone"
                    dataKey="average_mood"
                    stroke="#000"
                    strokeWidth={2}
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Tag frequency */}
          {stats.tag_frequency.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-3">Tag frequency</h2>
              <div className="border rounded p-4">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart
                    data={stats.tag_frequency}
                    margin={{ top: 5, right: 10, bottom: 5, left: -20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="tag" tick={{ fontSize: 12 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#000" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          )}

          {/* Mood by tag */}
          {stats.mood_by_tag.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-3">Mood by tag</h2>
              <div className="border rounded divide-y">
                {stats.mood_by_tag.map((row) => (
                  <div
                    key={row.tag}
                    className="flex items-center gap-4 px-4 py-3"
                  >
                    <span className="w-24 text-sm font-medium truncate">
                      {row.tag}
                    </span>
                    <div className="flex-1 h-2 bg-gray-100 rounded overflow-hidden">
                      <div
                        className="h-full bg-black"
                        style={{
                          width: `${(row.average_mood / 5) * 100}%`,
                        }}
                      />
                    </div>
                    <span className="text-sm tabular-nums w-16 text-right">
                      {row.average_mood.toFixed(2)}
                    </span>
                    <span className="text-xs text-gray-500 w-12 text-right">
                      n={row.count}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}

function Card({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="border rounded p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-semibold mt-1">{value}</p>
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}