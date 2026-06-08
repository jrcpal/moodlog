const API_URL = process.env.NEXT_PUBLIC_API_URL;

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Token ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API ${response.status}: ${errorBody}`);
  }

  // Some endpoints (like DELETE) return no body
  if (response.status === 204) return null as T;
  return response.json();
}

// Auth
export async function login(username: string, password: string) {
  const data = await request<{ token: string }>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (typeof window !== "undefined") {
    localStorage.setItem("token", data.token);
  }
  return data.token;
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
  }
}

export function isLoggedIn(): boolean {
  return !!getToken();
}

// Entries
export interface Tag {
  id: number;
  name: string;
  is_archived: boolean;
  created_at: string;
}

export interface Entry {
  id: number;
  text: string;
  mood: number;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export async function getEntries(): Promise<Entry[]> {
  return request<Entry[]>("/entries/");
}

export async function createEntry(
  text: string,
  mood: number,
  tagIds: number[] = []
): Promise<Entry> {
  return request<Entry>("/entries/", {
    method: "POST",
    body: JSON.stringify({ text, mood, tag_ids: tagIds }),
  });
}

// Tags
export async function getTags(): Promise<Tag[]> {
  return request<Tag[]>("/tags/");
}

export async function createTag(name: string): Promise<Tag> {
    return request<Tag>("/tags/", {
        method: "POST",
        body: JSON.stringify({name}),
    });
}

export async function restoreTag(id: number): Promise<Tag> {
  return request<Tag>(`/tags/${id}/restore/`, {
    method: "POST",
  });
}

export async function getArchivedTags(): Promise<Tag[]> {
  return request<Tag[]>("/tags/?include_archived=true");
}

export async function deleteTag(id: number): Promise<void> {
    await request<void>(`/tags/${id}/`, {
        method: "DELETE"
    });
}

// Stats
export interface MoodOverTimePoint {
  date: string;
  average_mood: number;
  count: number;
}

export interface TagFrequencyPoint {
  tag: string;
  count: number;
}

export interface MoodByTagPoint {
  tag: string;
  average_mood: number;
  count: number;
}

export interface Stats {
  total_entries: number;
  average_mood: number | null;
  mood_over_time: MoodOverTimePoint[];
  tag_frequency: TagFrequencyPoint[];
  mood_by_tag: MoodByTagPoint[];
}

export async function getStats(): Promise<Stats> {
  return request<Stats>("/stats/");
}