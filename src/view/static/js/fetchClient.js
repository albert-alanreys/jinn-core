var baseURL = "http://127.0.0.1:5000";

export async function getMode() {
  var response = await fetch(`${baseURL}/mode`);
  var result = await response.text();
  return result;
}

export async function getAlerts() {
  var response = await fetch(`${baseURL}/alerts`);
  var result = await response.json();
  return result;
}

export async function getAlertUpdates() {
  var response = await fetch(`${baseURL}/updates/alerts`);
  var result = await response.json();
  return result;
}

export async function getDataUpdates() {
  var response = await fetch(`${baseURL}/updates/data`);
  var result = await response.json();
  return result;
}

export async function getLiteData() {
  var response = await fetch(`${baseURL}/data/lite`);
  var result = await response.json();
  return result;
}

export async function getMainData(id) {
  var response = await fetch(`${baseURL}/data/main/${id}`);
  var result = await response.json();
  return result;
}

export async function updateData(id, parameter) {
  var response = await fetch(`${baseURL}/data/update/${id}/${parameter}`, {
    method: "POST",
  });
  var result = await response.json();
  return result;
}
