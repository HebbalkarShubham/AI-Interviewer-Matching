// API client - all requests go to backend (use /api when proxied)
const BASE = '/api';

async function request(path, options = {}) {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Interviewers
export async function getInterviewers() {
  return request('/interviewers');
}

export async function getInterviewer(id) {
  return request(`/interviewers/${id}`);
}

export async function createInterviewer(data) {
  return request('/interviewers', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateInterviewer(id, data) {
  return request(`/interviewers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteInterviewer(id) {
  return request(`/interviewers/${id}`, { method: 'DELETE' });
}

// Candidates - upload returns candidate with extracted skills
// name and email are optional; sent as form fields for backend to store
export async function uploadResume(file, { name = '', email = '' } = {}) {
  const form = new FormData();
  form.append('file', file);
  if (name != null && String(name).trim()) form.append('name', String(name).trim());
  if (email != null && String(email).trim()) form.append('email', String(email).trim());
  const res = await fetch(`${BASE}/candidates/upload`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

export async function getCandidate(id) {
  return request(`/candidates/${id}`);
}

export async function getMatches(candidateId) {
  return request(`/candidates/${candidateId}/matches`);
}

// Select interviewer and send email (legacy)
export async function selectInterviewer(candidateId, interviewerId, sendEmail = true) {
  return request('/selection/select', {
    method: 'POST',
    body: JSON.stringify({
      candidate_id: candidateId,
      interviewer_id: interviewerId,
      send_email: sendEmail,
    }),
  });
}

// Schedule interview (date, time, optional message) and send email with Accept/Reject
export async function scheduleInterview(candidateId, interviewerId, date, time, customMessage = null) {
  return request('/selection/schedule', {
    method: 'POST',
    body: JSON.stringify({
      candidate_id: candidateId,
      interviewer_id: interviewerId,
      date,
      time,
      custom_message: customMessage || null,
    }),
  });
}
