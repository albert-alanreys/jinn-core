export async function getAlerts() {
  try {
    var response = await fetch(`${API_URL}/alerts`);

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

export async function getAlertUpdates() {
  try {
    var response = await fetch(`${API_URL}/updates/alerts`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to fetch alert updates:', error);
    throw error;
  }
}

export async function getDataUpdates() {
  try {
    var response = await fetch(`${API_URL}/updates/data`);

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

export async function getLiteData() {
  try {
    var response = await fetch(`${API_URL}/data/lite`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to fetch lite data:', error);
    throw error;
  }
}

export async function getMainData(strategy_id) {
  try {
    var response = await fetch(`${API_URL}/data/main/${strategy_id}`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error(
      `Failed to fetch main data for strategy ${strategy_id}:`,
      error
    );
    throw error;
  }
}

export async function updateData(strategy_id, parameter) {
  try {
    var parsed = JSON.parse(parameter);

    var response = await fetch(`${API_URL}/data/update/${strategy_id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        param: Object.keys(parsed)[0],
        value: Object.values(parsed)[0],
      }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    var result = await response.json();
    return result;
  } catch (error) {
    console.error('Failed to update data:', error);
    throw error;
  }
}
