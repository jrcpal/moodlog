"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
    getEntries,
    createEntry,
    getTags,
    createTag,
    deleteTag,
    isLoggedIn,
    logout,
    Entry,
    Tag,
} from "@/lib/api";

export default function EntriesPage() {
    const router = useRouter();
    const [entries, setEntries] = useState<Entry[]>([]);
    const [tags, setTags] = useState<Tag[]>([]);
    const [text, setText] = useState("");
    const [mood, setMood] = useState(3);
    const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // Inline tag creation state
    const [showNewTagInput, setShowNewTagInput] = useState(false);
    const [newTagName, setNewTagName] = useState("");

    useEffect(() => {
        if (!isLoggedIn()) {
            router.push("/login");
            return;
        }
        loadData();
    }, [router]);

    async function loadData() {
        try {
            setLoading(true);
            const [entriesData, tagsData] = await Promise.all([
                getEntries(),
                getTags(),
            ]);
            setEntries(entriesData);
            setTags(tagsData);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load");
        } finally {
            setLoading(false);
        }
    }

    function toggleTag(id: number) {
        setSelectedTagIds((prev) =>
            prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
        );
    }

    async function handleCreateTag() {
        const name = newTagName.trim();
        if (!name) return;
        try {
            const newTag = await createTag(name);
            setTags((prev) => [...prev, newTag].sort((a, b) => a.name.localeCompare(b.name)));
            setSelectedTagIds((prev) => [...prev, newTag.id]); // auto-select it
            setNewTagName("");
            setShowNewTagInput(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create tag");
        }
    }

    async function handleDeleteTag(id: number) {
        if (!confirm("Archive this tag? It will be hidden from the tag picker but kept on past entries.")) return;
        try {
            await deleteTag(id);
            setTags((prev) => prev.filter((t) => t.id !== id));
            setSelectedTagIds((prev) => prev.filter((tid) => tid !== id));
            loadData(); // refresh entries to reflect tag removal
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete tag");
        }
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!text.trim()) return;
        try {
            await createEntry(text, mood, selectedTagIds);
            setText("");
            setMood(3);
            setSelectedTagIds([]);
            loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create entry");
        }
    }

    function handleLogout() {
        logout();
        router.push("/login");
    }

    return (
        <main className="max-w-2xl mx-auto p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">My entries</h1>
                <div className="flex gap-4 text-sm">
                    <Link href="/stats" className="underline">
                        Stats
                    </Link>
                    <button onClick={handleLogout} className="underline">
                        Log out
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3 mb-8 border-b pb-6">
                <textarea
                    placeholder="How was your day?"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                    rows={3}
                    required
                />

                <div className="flex items-center gap-3">
                    <label className="text-sm">Mood:</label>
                    <select
                        value={mood}
                        onChange={(e) => setMood(Number(e.target.value))}
                        className="border rounded px-2 py-1"
                    >
                        <option value={1}>1 - Terrible</option>
                        <option value={2}>2 - Bad</option>
                        <option value={3}>3 - Okay</option>
                        <option value={4}>4 - Good</option>
                        <option value={5}>5 - Great</option>
                    </select>
                </div>

                <div>
                    <p className="text-sm mb-1">Tags:</p>
                    <div className="flex flex-wrap items-center gap-2">
                        {tags.map((tag) => {
                            const selected = selectedTagIds.includes(tag.id);
                            return (
                                <span
                                    key={tag.id}
                                    className={`group inline-flex items-center text-xs rounded border overflow-hidden ${selected
                                        ? "bg-black text-white border-black"
                                        : "bg-white text-gray-700 border-gray-300"
                                        }`}
                                >
                                    <button
                                        type="button"
                                        onClick={() => toggleTag(tag.id)}
                                        className="px-2 py-1"
                                    >
                                        {tag.name}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => handleDeleteTag(tag.id)}
                                        className={`px-1.5 py-1 border-l ${selected
                                            ? "border-white/30 hover:bg-white/10"
                                            : "border-gray-300 hover:bg-gray-100"
                                            }`}
                                        title="Delete tag"
                                        aria-label={`Delete tag ${tag.name}`}
                                    >
                                        ×
                                    </button>
                                </span>
                            );
                        })}

                        {showNewTagInput ? (
                            <div className="inline-flex items-center gap-1">
                                <input
                                    autoFocus
                                    type="text"
                                    value={newTagName}
                                    onChange={(e) => setNewTagName(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") { e.preventDefault(); handleCreateTag(); }
                                    }}
                                    onBlur={() => {
                                        if (!newTagName.trim()) setShowNewTagInput(false);
                                    }}
                                    placeholder="tag name"
                                    className="text-xs border rounded px-2 py-1 w-24"
                                />
                                <button
                                    type="button"
                                    onClick={handleCreateTag}
                                    className="text-xs bg-black text-white px-2 py-1 rounded"
                                >
                                    Add
                                </button>
                            </div>
                        ) : (
                            <button
                                type="button"
                                onClick={() => setShowNewTagInput(true)}
                                className="text-xs px-2 py-1 rounded border border-dashed border-gray-400 text-gray-600 hover:bg-gray-50"
                            >
                                + New tag
                            </button>
                        )}
                    </div>
                </div>

                <button
                    type="submit"
                    className="bg-black text-white px-4 py-2 rounded"
                >
                    Add entry
                </button>
            </form>

            {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
            {loading ? (
                <p>Loading...</p>
            ) : entries.length === 0 ? (
                <p className="text-gray-500">No entries yet.</p>
            ) : (
                <ul className="space-y-4">
                    {entries.map((entry) => (
                        <li key={entry.id} className="border rounded p-4">
                            <div className="flex justify-between text-sm text-gray-500 mb-2">
                                <span>{new Date(entry.created_at).toLocaleString()}</span>
                                <span>Mood: {entry.mood}/5</span>
                            </div>
                            <p className="whitespace-pre-wrap">{entry.text}</p>
                            {entry.tags.length > 0 && (
                                <div className="mt-2 flex gap-2 flex-wrap">
                                    {entry.tags.map((tag) => (
                                        <span
                                            key={tag.id}
                                            className={`text-xs px-2 py-0.5 rounded ${tag.is_archived
                                                ? "bg-gray-100 text-gray-400 italic"
                                                : "bg-gray-100 text-gray-700"
                                                }`}
                                            title={tag.is_archived ? "Archived tag" : undefined}
                                        >
                                            {tag.name}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </main>
    );
}