import { app } from "./app.js";
import { env } from "./config/index.js";

const port = env.PORT;

app.listen(port, () => {
  console.log(`🚀 Aegis Forge Express Server listening on port ${port}`);
  console.log(`👉 Environment: ${env.NODE_ENV}`);
});
