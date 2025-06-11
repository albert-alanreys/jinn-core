export async function fetchAlerts() {
  try {
    var response = await fetch(`${SERVER_URL}/api/data/alerts`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to fetch alerts:', error);
    throw error;
  }
}

export async function fetchSummary() {
  try {
    var response = await fetch(`${SERVER_URL}/api/data/summary`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to fetch summary:', error);
    throw error;
  }
}

export async function fetchUpdates() {
  try {
    var response = await fetch(`${SERVER_URL}/api/data/updates`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to fetch data updates:', error);
    throw error;
  }
}

export async function fetchDetails(context_id) {
  try {
    var response = await fetch(`${SERVER_URL}/api/data/details/${context_id}`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error(`Failed to fetch details for ${context_id}:`, error);
    throw error;
  }
}

export async function updateContext(context_id, param) {
  try {
    var parsed = JSON.parse(param);

    var response = await fetch(
      `${SERVER_URL}/api/data/contexts/${context_id}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          param: Object.keys(parsed)[0],
          value: Object.values(parsed)[0],
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error(`Failed to update context for ${context_id}:`, error);
    throw error;
  }
}
