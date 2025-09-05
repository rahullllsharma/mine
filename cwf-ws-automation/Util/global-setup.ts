import path from "path";
import os from "os";
import rimraf from "rimraf";

async function globalSetup() {
  // Cleanup temp directories
  const tmpDirPath = path.join(os.tmpdir(), "pw");
  rimraf.sync(tmpDirPath);
}

export default globalSetup;
