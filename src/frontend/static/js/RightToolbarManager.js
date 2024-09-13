import {
  getLiteData,
  updateData,
  getAlerts,
  getAlertUpdates,
} from "./fetchClient.js";

export default class RightToolbarManager {
  constructor(data, mode, renderUI) {
    this.data = data;
    this.renderUI = renderUI;

    this.manageStrategies();
    this.manageButtons();
    this.manageCursor();

    if (mode == "automation") {
      this.manageAlerts();
    }
  }

  manageStrategies() {
    var body = document.querySelector("#strategies-list .body");

    for (var key in this.data) {
      var button = document.createElement("button");
      button.setAttribute("data-strategy", key);
      button.setAttribute("data-status", "inactive");
      body.appendChild(button);

      var div = document.createElement("div");
      div.setAttribute("unselectable", "on");
      div.innerHTML = `${this.data[key].name}
      ${this.data[key].symbol}
      ${this.data[key].interval}`;
      button.appendChild(div);

      if (body.children.length == 1) {
        this.currentStrategy = key;
        button.setAttribute("data-status", "active");
        this.createDescription();
      }

      button.addEventListener("click", (event) => {
        if (event.target.dataset.strategy != this.currentStrategy) {
          document
            .querySelector(`button[data-strategy="${this.currentStrategy}"]`)
            .setAttribute("data-status", "inactive");
          event.target.setAttribute("data-status", "active");
          this.currentStrategy = event.target.dataset.strategy;
          this.renderUI(this.currentStrategy);
          this.createDescription();
        }
      });
    }
  }

  createDescription() {
    var body = document.querySelector("#strategy-description .body");
    var strategyData = this.data[this.currentStrategy];
    var oldData = Array.from(body.children);

    if (oldData.length > 0) {
      for (var item of oldData) {
        item.remove();
      }
    }

    var div = document.createElement("div");
    div.classList.add("title");
    div.innerText = "Общая информация";
    body.appendChild(div);

    var section = document.createElement("section");
    section.setAttribute("id", "general-info");
    body.appendChild(section);

    var outerDiv = document.createElement("div");
    outerDiv.classList.add("info");
    section.appendChild(outerDiv);

    var innerDiv1 = document.createElement("div");
    innerDiv1.innerText = "Стратегия";
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement("div");
    innerDiv2.innerText = strategyData.name;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement("div");
    outerDiv.classList.add("info");
    section.appendChild(outerDiv);

    var innerDiv1 = document.createElement("div");
    innerDiv1.innerText = "Биржа";
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement("div");
    innerDiv2.innerText = strategyData.exchange.toUpperCase();
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement("div");
    outerDiv.classList.add("info");
    section.appendChild(outerDiv);

    var innerDiv1 = document.createElement("div");
    innerDiv1.innerText = "Символ";
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement("div");
    innerDiv2.innerText = strategyData.symbol;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement("div");
    outerDiv.classList.add("info");
    section.appendChild(outerDiv);

    var innerDiv1 = document.createElement("div");
    innerDiv1.innerText = "Таймфрейм";
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement("div");
    innerDiv2.innerText = strategyData.interval;
    outerDiv.appendChild(innerDiv2);

    var outerDiv = document.createElement("div");
    outerDiv.classList.add("info");
    section.appendChild(outerDiv);

    var innerDiv1 = document.createElement("div");
    innerDiv1.innerText = "Размер тика";
    outerDiv.appendChild(innerDiv1);

    var innerDiv2 = document.createElement("div");
    innerDiv2.innerText = strategyData.mintick;
    outerDiv.appendChild(innerDiv2);

    var div = document.createElement("div");
    div.classList.add("title");
    div.innerText = "Параметры стратегии";
    body.appendChild(div);

    var section = document.createElement("section");
    section.setAttribute("id", "parameter-values");
    body.appendChild(section);

    for (var key in strategyData.parameters) {
      var parameter = strategyData.parameters[key];

      if (Array.isArray(parameter)) {
        for (var i = 0; i < parameter.length; i++) {
          var outerDiv = document.createElement("div");
          outerDiv.classList.add("info");
          section.appendChild(outerDiv);

          var innerDiv = document.createElement("div");
          innerDiv.innerText = `${key} #${i + 1}`;
          outerDiv.appendChild(innerDiv);

          var input = document.createElement("input");
          input.setAttribute("value", parameter[i]);
          input.setAttribute("data-parameter", `${key} #${i + 1}`);
          input.setAttribute("data-group", key);
          input.addEventListener("change", (event) => {
            this.changeParameter(event.target);
          });
          outerDiv.appendChild(input);
        }
      } else {
        var outerDiv = document.createElement("div");
        outerDiv.classList.add("info");
        section.appendChild(outerDiv);

        var innerDiv = document.createElement("div");
        innerDiv.innerText = key;
        outerDiv.appendChild(innerDiv);

        var input = document.createElement("input");
        input.setAttribute("value", parameter);
        input.setAttribute("data-parameter", key);
        input.addEventListener("change", (event) => {
          this.changeParameter(event.target);
        });
        outerDiv.appendChild(input);
      }
    }
  }

  changeParameter(target) {
    if (target.hasAttribute("data-group")) {
      var inputs = document.querySelectorAll(
        `input[data-group="${target.dataset.group}"]`
      );
      var parameter = JSON.stringify({
        [target.dataset.group]: [...inputs].map((input) => input.value),
      });
    } else {
      var parameter = JSON.stringify({
        [target.dataset.parameter]: target.value,
      });
    }

    updateData(this.currentStrategy, parameter).then((result) => {
      getLiteData().then((data) => {
        this.data = data;
        overwrite.bind(this)();

        if (result.status == "success") {
          this.renderUI(this.currentStrategy);
        } else {
          target.classList.add("animate-border");
          setTimeout(() => target.removeAttribute("class"), 1000);
        }
      });
    });

    function overwrite() {
      var strategyData = this.data[this.currentStrategy];

      for (var key in strategyData.parameters) {
        var parameter = strategyData.parameters[key];

        if (Array.isArray(parameter)) {
          for (var i = 0; i < parameter.length; i++) {
            var input = document.querySelector(
              `input[data-parameter="${key} #${i + 1}"]`
            );
            input.value = parameter[i];
          }
        } else {
          var input = document.querySelector(`input[data-parameter="${key}"]`);
          input.value = parameter;
        }
      }
    }
  }

  manageButtons() {
    var rightToolbar = document.getElementById("right-toolbar");
    var rightToolHandle = document.getElementById("right-toolbar-handle");
    var infoWrapper = document.getElementById("info-wrapper");
    var strategiesList = document.getElementById("strategies-list");
    var strategyDescription = document.getElementById("strategy-description");
    var alertsList = document.getElementById("alerts-list");
    var strategiesButton = document.getElementById("strategies-button");
    var descriptionButton = document.getElementById("description-button");
    var alertsButton = document.getElementById("alerts-button");
    var rightToolbarDefaultMinWidth = window
      .getComputedStyle(rightToolbar)
      .getPropertyValue("min-width");
    var rightToolbarLastFlex = window
      .getComputedStyle(rightToolbar)
      .getPropertyValue("flex");

    strategiesButton.addEventListener("click", () => {
      if (strategiesButton.dataset.status == "opened") {
        rightToolbarLastFlex = window
          .getComputedStyle(rightToolbar)
          .getPropertyValue("flex");

        rightToolbar.style.flex = "1 1 0%";
        rightToolbar.style.minWidth = "auto";
        rightToolHandle.style.pointerEvents = "none";
        infoWrapper.style.display = "none";

        strategiesButton.setAttribute("data-status", "closed");
      } else if (strategiesButton.dataset.status == "closed") {
        if (
          descriptionButton.dataset.status == "closed" &&
          alertsButton.dataset.status == "closed"
        ) {
          rightToolbar.style.flex = rightToolbarLastFlex;
        }

        rightToolbar.style.minWidth = rightToolbarDefaultMinWidth;
        rightToolHandle.style.pointerEvents = "auto";
        infoWrapper.style.display = "block";
        strategiesList.style.display = "flex";
        strategyDescription.style.display = "none";
        alertsList.style.display = "none";

        strategiesButton.setAttribute("data-status", "opened");
        descriptionButton.setAttribute("data-status", "closed");
        alertsButton.setAttribute("data-status", "closed");
      }
    });

    descriptionButton.addEventListener("click", () => {
      if (descriptionButton.dataset.status == "opened") {
        rightToolbarLastFlex = window
          .getComputedStyle(rightToolbar)
          .getPropertyValue("flex");

        rightToolbar.style.flex = "1 1 0%";
        rightToolbar.style.minWidth = "auto";
        rightToolHandle.style.pointerEvents = "none";
        infoWrapper.style.display = "none";

        descriptionButton.setAttribute("data-status", "closed");
      } else if (descriptionButton.dataset.status == "closed") {
        if (
          strategiesButton.dataset.status == "closed" &&
          alertsButton.dataset.status == "closed"
        ) {
          rightToolbar.style.flex = rightToolbarLastFlex;
        }

        rightToolbar.style.minWidth = rightToolbarDefaultMinWidth;
        rightToolHandle.style.pointerEvents = "auto";
        infoWrapper.style.display = "block";
        strategiesList.style.display = "none";
        strategyDescription.style.display = "flex";
        alertsList.style.display = "none";

        strategiesButton.setAttribute("data-status", "closed");
        descriptionButton.setAttribute("data-status", "opened");
        alertsButton.setAttribute("data-status", "closed");
      }
    });

    alertsButton.addEventListener("click", () => {
      if (alertsButton.dataset.status == "opened") {
        rightToolbarLastFlex = window
          .getComputedStyle(rightToolbar)
          .getPropertyValue("flex");

        rightToolbar.style.flex = "1 1 0%";
        rightToolbar.style.minWidth = "auto";
        rightToolHandle.style.pointerEvents = "none";
        infoWrapper.style.display = "none";

        alertsButton.setAttribute("data-status", "closed");
      } else if (alertsButton.dataset.status == "closed") {
        if (
          strategiesButton.dataset.status == "closed" &&
          descriptionButton.dataset.status == "closed"
        ) {
          rightToolbar.style.flex = rightToolbarLastFlex;
        }

        rightToolbar.style.minWidth = rightToolbarDefaultMinWidth;
        rightToolHandle.style.pointerEvents = "auto";
        infoWrapper.style.display = "block";
        strategiesList.style.display = "none";
        strategyDescription.style.display = "none";
        alertsList.style.display = "flex";

        strategiesButton.setAttribute("data-status", "closed");
        descriptionButton.setAttribute("data-status", "closed");
        alertsButton.setAttribute("data-status", "opened");
      }
    });
  }

  manageCursor() {
    var rightToolbar = document.getElementById("right-toolbar");
    var rightToolHandle = document.getElementById("right-toolbar-handle");
    var startOffset = NaN;
    var moving = false;

    rightToolHandle.addEventListener("mousedown", (event) => {
      startOffset = rightToolbar.offsetLeft - event.clientX;
      document.addEventListener("mousemove", onMouseMove);
      document.body.style.cursor = "ns-resize";
      moving = true;
    });

    document.addEventListener("mouseup", () => {
      if (moving) {
        document.removeEventListener("mousemove", onMouseMove);
        document.body.style.cursor = "default";
        moving = false;
      }
    });

    var onMouseMove = (event) => {
      var currentOffset = rightToolbar.offsetLeft - event.clientX;
      var newInfoPanelSize = `0 0 ${
        rightToolbar.offsetWidth + (currentOffset - startOffset)
      }px`;
      rightToolbar.style.flex = newInfoPanelSize;
    };
  }

  manageAlerts() {
    getAlerts().then((alerts) => {
      if (alerts.length > 0) {
        addAlerts.bind(this)(alerts);
      }
    });

    setInterval(() => {
      getAlertUpdates().then((alerts) => {
        if (alerts.length > 0) {
          addAlerts.bind(this)(alerts);
        }
      });
    }, 5000);

    function addAlerts(alerts) {
      var body = document.querySelector("#alerts-list .body");

      for (var alert of alerts) {
        var outerDiv = document.createElement("div");
        outerDiv.classList.add("alert");
        body.prepend(outerDiv);

        var header = document.createElement("div");
        header.classList.add("header");
        outerDiv.appendChild(header);

        var innerDiv1 = document.createElement("div");
        innerDiv1.innerText = alert.time;
        header.appendChild(innerDiv1);

        var innerDiv2 = document.createElement("div");
        innerDiv2.classList.add("target");
        innerDiv2.setAttribute("title", "Открыть стратегию");
        innerDiv2.setAttribute("data-strategy", alert.strategy);
        header.appendChild(innerDiv2);

        var hiddenСontent = document.createElement("div");
        hiddenСontent.classList.add("hidden-content");
        outerDiv.appendChild(hiddenСontent);

        var tr = document.createElement("div");
        tr.classList.add("tr");
        hiddenСontent.appendChild(tr);

        var td1 = document.createElement("div");
        td1.classList.add("td");
        td1.innerText = "Биржа";
        tr.appendChild(td1);

        var td2 = document.createElement("div");
        td2.classList.add("td");
        td2.innerText = alert.message.exchange;
        tr.appendChild(td2);

        if (!alert.message.hasOwnProperty("error")) {
          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Тип";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");
          td2.innerText = alert.message.type;
          tr.appendChild(td2);

          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Статус";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");

          if (alert.message.status == "исполнен") {
            var color = "#089981";
          } else if (alert.message.status == "ожидает исполнения") {
            var color = "#6a6d78";
          } else if (alert.message.status == "отменён") {
            var color = "#f23645";
          }

          td2.innerHTML = `<span style="color:
            ${color};">${alert.message.status}</span>`;
          tr.appendChild(td2);

          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Направление";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");

          if (alert.message.side == "покупка") {
            var color = "#089981";
          } else if (alert.message.side == "продажа") {
            var color = "#f23645";
          }

          td2.innerHTML = `<span style="color:
            ${color};">${alert.message.side}</span>`;
          tr.appendChild(td2);

          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Символ";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");
          td2.innerText = alert.message.symbol;
          tr.appendChild(td2);

          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Количество";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");
          td2.innerText = alert.message.qty;
          tr.appendChild(td2);

          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td1 = document.createElement("div");
          td1.classList.add("td");
          td1.innerText = "Цена";
          tr.appendChild(td1);

          var td2 = document.createElement("div");
          td2.classList.add("td");
          td2.innerText = alert.message.price;
          tr.appendChild(td2);
        } else {
          var tr = document.createElement("div");
          tr.classList.add("tr");
          hiddenСontent.appendChild(tr);

          var td = document.createElement("div");
          td.classList.add("td");
          td.innerHTML = `<span style="color:#f23645;">
            ${alert.message.error}</span>`;
          tr.appendChild(td);
        }

        outerDiv.addEventListener("click", (event) => {
          if (!event.target.classList.contains("target")) {
            var container = event.target.closest(".alert");

            if (
              window
                .getComputedStyle(container.lastChild)
                .getPropertyValue("display") == "none"
            ) {
              container.lastChild.style.display = "flex";
            } else {
              container.lastChild.style.display = "none";
            }
          }
        });

        innerDiv2.addEventListener("click", (event) => {
          if (event.target.dataset.strategy != this.currentStrategy) {
            document
              .querySelector(`button[data-strategy="${this.currentStrategy}"]`)
              .setAttribute("data-status", "inactive");
            this.currentStrategy = event.target.dataset.strategy;
            document
              .querySelector(`button[data-strategy="${this.currentStrategy}"]`)
              .setAttribute("data-status", "active");

            this.renderUI(this.currentStrategy, true);
            this.createDescription();
          }
        });
      }
    }
  }
}
