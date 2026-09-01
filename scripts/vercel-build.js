const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const root = process.cwd();
const frontend = fs.existsSync(path.join(root, "frontend", "package.json"))
  ? path.join(root, "frontend")
  : root;
const dest = path.join(root, "build");

function hasIndex(dir) {
  return Boolean(dir) && fs.existsSync(path.join(dir, "index.html"));
}

console.log("[vercel-build] cwd=", root);
console.log("[vercel-build] frontend=", frontend);
console.log("[vercel-build] dest=", dest);

execSync("yarn build", {
  cwd: frontend,
  stdio: "inherit",
  env: {
    ...process.env,
    BUILD_PATH: dest,
  },
});

const found = [dest, path.join(frontend, "build"), path.join(root, "frontend", "build")].find(
  hasIndex
);

if (!found) {
  console.error("[vercel-build] index.html not found after CRA build");
  console.error("[vercel-build] root entries:", fs.readdirSync(root).join(", "));
  if (frontend !== root && fs.existsSync(frontend)) {
    console.error("[vercel-build] frontend entries:", fs.readdirSync(frontend).join(", "));
  }
  process.exit(1);
}

if (path.resolve(found) !== path.resolve(dest)) {
  fs.cpSync(found, dest, { recursive: true });
}

if (!hasIndex(dest)) {
  console.error("[vercel-build] missing index.html in", dest);
  process.exit(1);
}

console.log("[vercel-build] static output ready at", dest);
