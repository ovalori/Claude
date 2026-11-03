// See all configuration options: https://remotion.dev/docs/config
// Each option also is available as a CLI flag: https://remotion.dev/docs/cli

// Note: When using the Node.JS APIs, the config file doesn't apply. Instead, pass options directly to the APIs

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Cloud sessions can't download Remotion's Chrome, so use the preinstalled one.
// On your own computer this path doesn't exist and Remotion downloads Chrome itself.
import { existsSync } from "node:fs";
const cloudChrome =
  "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
if (existsSync(cloudChrome)) {
  Config.setBrowserExecutable(cloudChrome);
}
