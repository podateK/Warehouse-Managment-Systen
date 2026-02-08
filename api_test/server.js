const http = require("http");
const fs = require("fs");
const path = require("path");

const clients = [];
const serveFile = (res, filePath, contentType) => {
  fs.readFile(filePath, (err, content) => {
    if (err) {
      res.writeHead(500);
      res.end("Error loading file");
    } else {
      res.writeHead(200, { "Content-Type": contentType });
      res.end(content);
    }
  });
};

const broadcast = (data) => {
  clients.forEach((client) => client.write(`data: ${data}\n\n`));
};

const server = http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/") {
    serveFile(res, path.join(__dirname, "index.html"), "text/html");
  } else if (req.method === "GET" && req.url === "/events") {
    res.writeHead(200, {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    });
    clients.push(res);
    req.on("close", () => {
      clients.splice(clients.indexOf(res), 1);
    });
  } else if (req.method === "POST" && req.url === "/api") {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
    });
    req.on("end", () => {
      console.log("Received:", body);
      broadcast(body);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "success", received: body }));
    });
  } else {
    res.writeHead(404);
    res.end("Not Found");
  }
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
