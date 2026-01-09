/**
 * Configuration management for MCP HiPerGator server
 */

import { homedir } from "os";
import { join } from "path";
import { existsSync, readFileSync } from "fs";

export interface Config {
  // SSH configuration
  host: string;
  user: string;
  port: number;
  identityFile: string;
  controlPath: string;

  // HiPerGator paths
  projectBase: string;
  scratchBase: string;
  orangeBase: string;

  // Timeouts (in milliseconds)
  connectionTimeout: number;
  commandTimeout: number;
  longCommandTimeout: number;

  // SLURM defaults
  defaultPartition: string;
  defaultAccount: string;
  defaultQos: string;
}

const DEFAULT_CONFIG: Config = {
  host: "hpg.rc.ufl.edu",
  user: process.env.HPG_USER || "",
  port: 2222,
  identityFile: join(homedir(), ".ssh", "id_ed25519_hpg"),
  controlPath: join(homedir(), ".ssh", "sockets", "hpg-%r@%h:%p"),

  projectBase: "/blue/roitberg/john.aitken",
  scratchBase: "/red/roitberg/john.aitken",
  orangeBase: "/orange/roitberg/john.aitken",

  connectionTimeout: 30000,
  commandTimeout: 60000,
  longCommandTimeout: 600000,

  defaultPartition: "hpg-default",
  defaultAccount: "roitberg",
  defaultQos: "roitberg",
};

export function loadConfig(): Config {
  // Try to load from config file
  const configPaths = [
    join(process.cwd(), "hpg-config.json"),
    join(homedir(), ".config", "mcp-hipergator", "config.json"),
    join(homedir(), ".mcp-hipergator.json"),
  ];

  for (const configPath of configPaths) {
    if (existsSync(configPath)) {
      try {
        const fileConfig = JSON.parse(readFileSync(configPath, "utf-8"));
        return { ...DEFAULT_CONFIG, ...fileConfig };
      } catch (e) {
        console.error(`Warning: Failed to parse config at ${configPath}`);
      }
    }
  }

  // Use environment variables as overrides
  const envConfig: Partial<Config> = {};

  if (process.env.HPG_HOST) envConfig.host = process.env.HPG_HOST;
  if (process.env.HPG_USER) envConfig.user = process.env.HPG_USER;
  if (process.env.HPG_PORT) envConfig.port = parseInt(process.env.HPG_PORT);
  if (process.env.HPG_IDENTITY_FILE) envConfig.identityFile = process.env.HPG_IDENTITY_FILE;
  if (process.env.HPG_PROJECT_BASE) envConfig.projectBase = process.env.HPG_PROJECT_BASE;

  return { ...DEFAULT_CONFIG, ...envConfig };
}

export function validateConfig(config: Config): string[] {
  const errors: string[] = [];

  if (!config.user) {
    errors.push("HPG_USER not set. Set via environment variable or config file.");
  }

  if (!existsSync(config.identityFile)) {
    errors.push(`SSH identity file not found: ${config.identityFile}`);
  }

  return errors;
}
