/**
 * SSH client using native system SSH with multiplexing support
 */

import { spawn, execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import { dirname } from "path";
import { Config } from "./config.js";

export interface SSHResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exitCode: number;
}

export interface ConnectionStatus {
  connected: boolean;
  host: string;
  user: string;
  controlSocketExists: boolean;
  lastCommand?: string;
  lastCommandTime?: Date;
}

export class SSHClient {
  private config: Config;
  private lastCommand?: string;
  private lastCommandTime?: Date;

  constructor(config: Config) {
    this.config = config;
    this.ensureControlPathDirectory();
  }

  /**
   * Ensure the control socket directory exists
   */
  private ensureControlPathDirectory(): void {
    const controlDir = dirname(this.config.controlPath);
    if (!existsSync(controlDir)) {
      mkdirSync(controlDir, { recursive: true, mode: 0o700 });
    }
  }

  /**
   * Build SSH command arguments
   */
  private buildSSHArgs(command?: string): string[] {
    const args: string[] = [
      "-o", "BatchMode=yes",
      "-o", "StrictHostKeyChecking=accept-new",
      "-o", `ControlPath=${this.config.controlPath}`,
      "-o", "ControlMaster=auto",
      "-o", "ControlPersist=4h",
      "-o", "ServerAliveInterval=60",
      "-o", "ServerAliveCountMax=3",
      "-p", String(this.config.port),
      "-i", this.config.identityFile,
      `${this.config.user}@${this.config.host}`,
    ];

    if (command) {
      args.push("--", command);
    }

    return args;
  }

  /**
   * Execute SSH command and return result
   */
  async executeCommand(command: string, timeout?: number): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const effectiveTimeout = timeout || this.config.commandTimeout;

    try {
      const result = await this.runSSH(command, effectiveTimeout);
      this.lastCommand = command;
      this.lastCommandTime = new Date();

      if (result.success) {
        return {
          content: [{ type: "text", text: result.stdout || "(no output)" }],
        };
      } else {
        return {
          content: [{
            type: "text",
            text: `Command failed (exit ${result.exitCode}):\n${result.stderr || result.stdout}`,
          }],
          isError: true,
        };
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: "text", text: `SSH error: ${message}` }],
        isError: true,
      };
    }
  }

  /**
   * Run SSH command using native ssh binary
   */
  private runSSH(command: string, timeout: number): Promise<SSHResult> {
    return new Promise((resolve, reject) => {
      const args = this.buildSSHArgs(command);
      const ssh = spawn("ssh", args, {
        stdio: ["pipe", "pipe", "pipe"],
        timeout,
      });

      let stdout = "";
      let stderr = "";

      ssh.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      ssh.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      const timeoutId = setTimeout(() => {
        ssh.kill("SIGTERM");
        reject(new Error(`Command timed out after ${timeout}ms`));
      }, timeout);

      ssh.on("close", (code) => {
        clearTimeout(timeoutId);
        resolve({
          success: code === 0,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          exitCode: code || 0,
        });
      });

      ssh.on("error", (error) => {
        clearTimeout(timeoutId);
        reject(error);
      });
    });
  }

  /**
   * Check if control socket exists (connection likely active)
   */
  isConnected(): boolean {
    const controlSocket = this.config.controlPath
      .replace("%r", this.config.user)
      .replace("%h", this.config.host)
      .replace("%p", String(this.config.port));

    return existsSync(controlSocket);
  }

  /**
   * Establish SSH connection (creates control socket)
   */
  async connect(): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    try {
      // Test connection with simple command
      const result = await this.runSSH("echo 'MCP connection established'", this.config.connectionTimeout);

      if (result.success) {
        return {
          content: [{
            type: "text",
            text: `Connected to HiPerGator (${this.config.user}@${this.config.host}:${this.config.port})`,
          }],
        };
      } else {
        return {
          content: [{
            type: "text",
            text: `Connection failed: ${result.stderr}\n\nTroubleshooting:\n` +
              `1. Ensure SSH key exists: ${this.config.identityFile}\n` +
              `2. Complete Duo MFA if prompted\n` +
              `3. Check HiPerGator status: https://status.rc.ufl.edu/`,
          }],
          isError: true,
        };
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return {
        content: [{
          type: "text",
          text: `Connection error: ${message}\n\nEnsure:\n` +
            `1. SSH key is configured for HiPerGator\n` +
            `2. You've completed initial Duo MFA authentication\n` +
            `3. Network connectivity to hpg.rc.ufl.edu`,
        }],
        isError: true,
      };
    }
  }

  /**
   * Close SSH connection (removes control socket)
   */
  async disconnect(): Promise<{
    content: Array<{ type: string; text: string }>;
  }> {
    try {
      // Send exit command to control master
      execSync(`ssh -O exit -o ControlPath=${this.config.controlPath} ${this.config.user}@${this.config.host}`, {
        timeout: 5000,
      });
      return {
        content: [{ type: "text", text: "Disconnected from HiPerGator" }],
      };
    } catch {
      // Control socket may not exist
      return {
        content: [{ type: "text", text: "Connection closed (or was not active)" }],
      };
    }
  }

  /**
   * Get connection status
   */
  async getStatus(): Promise<{
    content: Array<{ type: string; text: string }>;
  }> {
    const status: ConnectionStatus = {
      connected: this.isConnected(),
      host: this.config.host,
      user: this.config.user,
      controlSocketExists: this.isConnected(),
      lastCommand: this.lastCommand,
      lastCommandTime: this.lastCommandTime,
    };

    // Test actual connectivity if socket exists
    if (status.controlSocketExists) {
      try {
        const result = await this.runSSH("echo ok", 5000);
        status.connected = result.success;
      } catch {
        status.connected = false;
      }
    }

    return {
      content: [{
        type: "text",
        text: JSON.stringify(status, null, 2),
      }],
    };
  }

  /**
   * Run SCP upload
   */
  async scpUpload(localPath: string, remotePath: string): Promise<SSHResult> {
    return new Promise((resolve, reject) => {
      const args = [
        "-o", `ControlPath=${this.config.controlPath}`,
        "-o", "ControlMaster=auto",
        "-P", String(this.config.port),
        "-i", this.config.identityFile,
        localPath,
        `${this.config.user}@${this.config.host}:${remotePath}`,
      ];

      const scp = spawn("scp", args, { stdio: ["pipe", "pipe", "pipe"] });

      let stdout = "";
      let stderr = "";

      scp.stdout.on("data", (data) => { stdout += data.toString(); });
      scp.stderr.on("data", (data) => { stderr += data.toString(); });

      scp.on("close", (code) => {
        resolve({
          success: code === 0,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          exitCode: code || 0,
        });
      });

      scp.on("error", reject);
    });
  }

  /**
   * Run SCP download
   */
  async scpDownload(remotePath: string, localPath: string): Promise<SSHResult> {
    return new Promise((resolve, reject) => {
      const args = [
        "-o", `ControlPath=${this.config.controlPath}`,
        "-o", "ControlMaster=auto",
        "-P", String(this.config.port),
        "-i", this.config.identityFile,
        `${this.config.user}@${this.config.host}:${remotePath}`,
        localPath,
      ];

      const scp = spawn("scp", args, { stdio: ["pipe", "pipe", "pipe"] });

      let stdout = "";
      let stderr = "";

      scp.stdout.on("data", (data) => { stdout += data.toString(); });
      scp.stderr.on("data", (data) => { stderr += data.toString(); });

      scp.on("close", (code) => {
        resolve({
          success: code === 0,
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          exitCode: code || 0,
        });
      });

      scp.on("error", reject);
    });
  }
}
