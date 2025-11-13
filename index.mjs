import axios from "axios";

const DEFAULT_WEBHOOK_URL = process.env.WEBHOOK_URL || "https://example.com/webhook";
const DEFAULT_DURATION_MINUTES = parseFloat(process.env.DURATION_MINUTES || "1");
const INTERVAL_SECONDS = parseFloat(process.env.INTERVAL_SECONDS || "5");

const USER_ID = process.env.USER_ID || "anonymous";
const JOB_ID = process.env.JOB_ID || process.env.AWS_BATCH_JOB_ID || "local-run";

const startTime = Date.now();
const endTime = startTime + DEFAULT_DURATION_MINUTES * 60 * 1000;

console.log("========================================");
console.log("📡 Webhook Sender Started");
console.log("----------------------------------------");
console.log(`Webhook URL       : ${DEFAULT_WEBHOOK_URL}`);
console.log(`User ID           : ${USER_ID}`);
console.log(`Job ID            : ${JOB_ID}`);
console.log(`Duration (minutes): ${DEFAULT_DURATION_MINUTES}`);
console.log(`Interval (seconds): ${INTERVAL_SECONDS}`);
console.log("----------------------------------------");

const sendEvent = async (count) => {
  const payload = {
    eventType: "JOB_PROGRESS",
    userId: USER_ID,
    jobId: JOB_ID,
    count,
    timestamp: new Date().toISOString(),
  };

  try {
    const res = await axios.post(DEFAULT_WEBHOOK_URL, payload);
    console.log(`[${new Date().toISOString()}] ✅ Event #${count} sent (status ${res.status})`);
  } catch (err) {
    console.error(`[${new Date().toISOString()}] ❌ Failed to send event #${count}:`, err.message);
  }
};

const loop = async () => {
  let count = 1;
  while (Date.now() < endTime) {
    await sendEvent(count++);
    await new Promise((r) => setTimeout(r, INTERVAL_SECONDS * 1000));
  }

  // Final completion event
  await axios.post(DEFAULT_WEBHOOK_URL, {
    eventType: "JOB_COMPLETED",
    userId: USER_ID,
    jobId: JOB_ID,
    totalEvents: count - 1,
    finishedAt: new Date().toISOString(),
  });

  console.log("========================================");
  console.log(`✅ Job Completed (${DEFAULT_DURATION_MINUTES} min total)`);
  console.log("========================================");
};

loop();
