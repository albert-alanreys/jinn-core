const URL = "http://127.0.0.1:5000";

export async function getMode() {
  try {
    const response = await fetch(`${URL}/mode`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.text();
    return result;
  } catch (error) {
    console.error("Failed to fetch mode:", error);
    throw error;
  }
}

export async function getAlerts() {
  try {
    const response = await fetch(`${URL}/alerts`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Failed to fetch alerts:", error);
    throw error;
  }
}

export async function getAlertUpdates() {
  try {
    const response = await fetch(`${URL}/updates/alerts`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Failed to fetch alert updates:", error);
    throw error;
  }
}

export async function getDataUpdates() {
  try {
    const response = await fetch(`${URL}/updates/data`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Failed to fetch data updates:", error);
    throw error;
  }
}

export async function getLiteData() {
  try {
    const response = await fetch(`${URL}/data/lite`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Failed to fetch lite data:", error);
    throw error;
  }
}

export async function getMainData(strategy_id) {
  try {
    const response = await fetch(`${URL}/data/main/${strategy_id}`);

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
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
    const response = await fetch(
      `${URL}/data/update/${strategy_id}/${parameter}`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Failed to update data:", error);
    throw error;
  }
}
