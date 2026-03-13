const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function fetchAPI(endpoint: string, options: FetchOptions = {}) {
  const { token, headers, ...rest } = options;

  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...rest,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return res.json();
}

// Auth
export async function signup(email: string, password: string) {
  return fetchAPI("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string) {
  return fetchAPI("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function authGoogle(email: string, name?: string, photo_url?: string) {
  return fetchAPI("/auth/google", {
    method: "POST",
    body: JSON.stringify({ email, name, photo_url }),
  });
}

export async function getMe(token: string) {
  return fetchAPI("/auth/me", { token });
}

export async function setRole(token: string, role: "job_seeker" | "recruiter") {
  return fetchAPI("/auth/role", {
    method: "PUT",
    token,
    body: JSON.stringify({ role }),
  });
}

// Job Seeker Profile
export async function getJobSeekerProfile(token: string) {
  return fetchAPI("/profile/jobseeker/", { token });
}

export async function createJobSeekerProfile(token: string, data: {
  name: string;
  age?: number;
  location?: string;
  skills?: string[];
  experience?: string;
  preferred_roles?: string[];
  expected_salary?: string;
  resume_url?: string;
}) {
  return fetchAPI("/profile/jobseeker/", {
    method: "POST",
    token,
    body: JSON.stringify(data),
  });
}

export async function updateJobSeekerProfile(token: string, data: {
  name?: string;
  age?: number;
  location?: string;
  skills?: string[];
  experience?: string;
  preferred_roles?: string[];
  expected_salary?: string;
  resume_url?: string;
}) {
  return fetchAPI("/profile/jobseeker/", {
    method: "PUT",
    token,
    body: JSON.stringify(data),
  });
}

// Recruiter Profile
export async function getRecruiterProfile(token: string) {
  return fetchAPI("/profile/recruiter/", { token });
}

export async function createRecruiterProfile(token: string, data: {
  company_name: string;
  industry?: string;
  company_size?: string;
}) {
  return fetchAPI("/profile/recruiter/", {
    method: "POST",
    token,
    body: JSON.stringify(data),
  });
}

export async function updateRecruiterProfile(token: string, data: {
  company_name?: string;
  industry?: string;
  company_size?: string;
}) {
  return fetchAPI("/profile/recruiter/", {
    method: "PUT",
    token,
    body: JSON.stringify(data),
  });
}

// Jobs
export async function createJob(token: string, data: {
  title: string;
  description: string;
  skills_required?: string[];
  salary_range?: string;
  experience_required?: string;
  location?: string;
}) {
  return fetchAPI("/jobs/create", {
    method: "POST",
    token,
    body: JSON.stringify(data),
  });
}

export async function listJobs(skip = 0, limit = 20) {
  return fetchAPI(`/jobs/list?skip=${skip}&limit=${limit}`);
}

export async function getJob(jobId: string) {
  return fetchAPI(`/jobs/${jobId}`);
}

export async function getMyJobs(token: string) {
  return fetchAPI("/jobs/my-jobs", { token });
}

// Chat & Messaging
export async function getConversations(token: string) {
  return fetchAPI("/chat/conversations", { token });
}

export async function getMessages(token: string, conversationId: string) {
  return fetchAPI(`/chat/messages/${conversationId}`, { token });
}

export async function startConversation(token: string, jobId: string) {
  return fetchAPI(`/chat/conversations/start?job_id=${jobId}`, {
    method: "POST",
    token,
  });
}
