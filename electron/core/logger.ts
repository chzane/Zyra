import log from "electron-log";
import path from "path";

log.transports.file.level = "info";
log.transports.file.maxSize = 10 * 1024 * 1024;
log.transports.file.fileName = `zyra_${Date.now()}.log`;
log.transports.file.resolvePath = () =>
    path.join(__dirname, "../../logs", log.transports.file.fileName);

Object.assign(console, log.functions);

export default log;