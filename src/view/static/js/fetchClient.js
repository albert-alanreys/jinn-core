var URL = "http://127.0.0.1:5000";

export async function getMode() {
  var response = await fetch(`${URL}/mode`);
  var result = await response.text();
  return result;
}

export async function getAlerts() {
  var response = await fetch(`${URL}/alerts`);
  var result = await response.json();
  return result;
}

export async function getAlertUpdates() {
  var response = await fetch(`${URL}/updates/alerts`);
  var result = await response.json();
  return result;
}

export async function getDataUpdates() {
  var response = await fetch(`${URL}/updates/data`);
  var result = await response.json();
  return result;
}

export async function getLiteData() {
  var response = await fetch(`${URL}/data/lite`);
  var result = await response.json();
  return result;
}

export async function getMainData(strategy_id) {
  var response = await fetch(`${URL}/data/main/${strategy_id}`);
  var result = await response.json();
  return result;
}

export async function updateData(strategy_id, parameter) {
  var response = await fetch(
    `${URL}/data/update/${strategy_id}/${parameter}`,
    {
      method: "POST",
    }
  );
  var result = await response.json();
  return result;
}
