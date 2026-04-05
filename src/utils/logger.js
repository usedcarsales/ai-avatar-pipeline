// logger.js — Simple logging utility for the AI Avatar Pipeline

const timestamp = () => new Date().toISOString().replace('T', ' ').split('.')[0];

export const log = (message) => {
  console.log(`🔵 [${timestamp()}] ${message}`);
};

export const error = (message) => {
  console.error(`🔴 [${timestamp()}] ERROR: ${message}`);
};

export const success = (message) => {
  console.log(`✅ [${timestamp()}] ${message}`);
};

export const warn = (message) => {
  console.warn(`⚠️  [${timestamp()}] ${message}`);
};

export default { log, error, success, warn };
