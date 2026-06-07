const ws = new WebSocket(process.env.CDP_WS);

let id = 0;
let evalId = 0;

function send(method, params = {}) {
  const message = { id: ++id, method, params };
  ws.send(JSON.stringify(message));
  return message.id;
}

ws.onerror = (event) => {
  console.log("WS_ERROR", event.message || String(event));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (
    message.method === "Runtime.exceptionThrown" ||
    message.method === "Runtime.consoleAPICalled"
  ) {
    console.log("EVENT", JSON.stringify(message));
  }

  if (message.id === evalId) {
    console.log("EVAL", JSON.stringify(message));
    setTimeout(() => process.exit(0), 500);
  }
};

ws.onopen = () => {
  console.log("OPEN");
  send("Runtime.enable");
  send("Page.enable");
  send("Page.reload");

  setTimeout(() => {
    evalId = send("Runtime.evaluate", {
      expression: `({
        root: document.getElementById("root")?.innerHTML,
        text: document.body.innerText,
        scripts: [...document.scripts].map((script) => script.src)
      })`,
      returnByValue: true,
    });
  }, 3000);
};

setTimeout(() => {
  console.log("TIMEOUT");
  process.exit(2);
}, 10000);
