const GITHUB_DISPATCH_URL =
  "https://api.github.com/repos/cutecubeandy/JxJ_Stock_Watcher/dispatches";

export default {
  async scheduled(_controller, env, ctx) {
    ctx.waitUntil(triggerGitHub(env));
  },
};

async function triggerGitHub(env) {
  if (!env.GITHUB_TOKEN) {
    throw new Error("Missing GITHUB_TOKEN secret");
  }

  const response = await fetch(GITHUB_DISPATCH_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "jxj-stock-scheduler",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      event_type: "jxj-stock-check",
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(
      `GitHub dispatch failed: ${response.status} ${response.statusText} - ${body}`
    );
  }

  console.log("Triggered GitHub repository_dispatch: jxj-stock-check");
}
