const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function sendChatMessage(message, conversationHistory = [], profile = {}, language = 'en', sessionId = null) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      conversation_history: conversationHistory,
      profile,
      language
    })
  });
  if (!res.ok) {
    throw new Error(`Chat API error: ${res.statusText}`);
  }
  return res.json();
}

export async function getRecommendations(profile) {
  const res = await fetch(`${API_BASE_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile)
  });
  if (!res.ok) {
    throw new Error(`Recommendation API error: ${res.statusText}`);
  }
  return res.json();
}

export async function getFeasibility(businessId, profile) {
  const res = await fetch(`${API_BASE_URL}/feasibility`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      business_id: businessId,
      profile
    })
  });
  if (!res.ok) {
    throw new Error(`Feasibility API error: ${res.statusText}`);
  }
  return res.json();
}

export async function getFinancialPlan(financialInputs) {
  const res = await fetch(`${API_BASE_URL}/financial`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(financialInputs)
  });
  if (!res.ok) {
    throw new Error(`Financial API error: ${res.statusText}`);
  }
  return res.json();
}

export async function matchSchemes(profile, businessId = null, businessCategory = null, projectCost = null) {
  const res = await fetch(`${API_BASE_URL}/schemes/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      profile,
      business_id: businessId,
      business_category: businessCategory,
      project_cost: projectCost
    })
  });
  if (!res.ok) {
    throw new Error(`Schemes API error: ${res.statusText}`);
  }
  return res.json();
}

export async function generateReport(profile, selectedBusinessId = null, customProjectCost = null) {
  const res = await fetch(`${API_BASE_URL}/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      profile,
      selected_business_id: selectedBusinessId,
      custom_project_cost: customProjectCost
    })
  });
  if (!res.ok) {
    throw new Error(`Report API error: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchBusinesses(domain = '', search = '') {
  const params = new URLSearchParams();
  if (domain && domain !== 'All') params.append('domain', domain);
  if (search) params.append('search', search);

  const res = await fetch(`${API_BASE_URL}/businesses?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch businesses');
  return res.json();
}

export async function fetchSchemes() {
  const res = await fetch(`${API_BASE_URL}/schemes`);
  if (!res.ok) throw new Error('Failed to fetch schemes');
  return res.json();
}

export async function fetchTrainStatus() {
  const res = await fetch(`${API_BASE_URL}/train/status`);
  if (!res.ok) throw new Error('Failed to fetch training status');
  return res.json();
}

export async function triggerModelTraining(filePath = null) {
  const res = await fetch(`${API_BASE_URL}/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Training failed');
  }
  return res.json();
}

export async function uploadAndTrainFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/businesses/import`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'File upload failed');
  }
  return res.json();
}

export async function fetchEquipment(businessName, scale = 'small') {
  const enc = encodeURIComponent(businessName);
  const res = await fetch(`${API_BASE_URL}/equipment/${enc}?scale=${scale}`);
  if (!res.ok) throw new Error('Failed to fetch required equipment');
  return res.json();
}

export async function searchSuppliers(params) {
  const res = await fetch(`${API_BASE_URL}/suppliers/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error('Failed to search suppliers');
  return res.json();
}

export async function recommendSuppliers(params) {
  const res = await fetch(`${API_BASE_URL}/suppliers/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  if (!res.ok) throw new Error('Failed to fetch supplier recommendations');
  return res.json();
}
