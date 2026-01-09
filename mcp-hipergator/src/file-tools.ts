/**
 * File system tools for HiPerGator
 */

import { SSHClient } from "./ssh-client.js";
import { Config } from "./config.js";
import { posix } from "path";

export class FileTools {
  private ssh: SSHClient;
  private config: Config;

  constructor(ssh: SSHClient, config: Config) {
    this.ssh = ssh;
    this.config = config;
  }

  /**
   * Validate that a path is within allowed directories
   */
  private validatePath(path: string): boolean {
    const resolved = posix.resolve("/", path);
    const allowedBases = [
      this.config.projectBase,
      this.config.scratchBase,
      this.config.orangeBase,
      "/home",
    ];

    return allowedBases.some((base) => resolved.startsWith(base));
  }

  /**
   * Escape shell argument to prevent injection
   */
  private escapeArg(arg: string): string {
    // Use single quotes and escape any existing single quotes
    return `'${arg.replace(/'/g, "'\\''")}'`;
  }

  /**
   * List directory contents
   */
  async listDirectory(args: { path: string; options?: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { path, options = "-la" } = args;

    if (!this.validatePath(path)) {
      return {
        content: [{
          type: "text",
          text: `Path not allowed: ${path}\nAllowed paths: ${this.config.projectBase}, ${this.config.scratchBase}`,
        }],
        isError: true,
      };
    }

    const command = `ls ${options} ${this.escapeArg(path)}`;
    return await this.ssh.executeCommand(command);
  }

  /**
   * Read file content
   */
  async readFile(args: { path: string; lines?: number }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { path, lines } = args;

    if (!this.validatePath(path)) {
      return {
        content: [{
          type: "text",
          text: `Path not allowed: ${path}`,
        }],
        isError: true,
      };
    }

    // Check file size first to avoid reading huge files
    const sizeCheck = await this.ssh.executeCommand(`stat -c%s ${this.escapeArg(path)} 2>/dev/null || echo "0"`);
    const fileSize = parseInt(sizeCheck.content[0]?.text || "0");

    // Limit to 1MB
    if (fileSize > 1024 * 1024 && !lines) {
      return {
        content: [{
          type: "text",
          text: `File too large (${(fileSize / 1024 / 1024).toFixed(2)} MB). Use 'lines' parameter to read partial content.`,
        }],
        isError: true,
      };
    }

    let command: string;
    if (lines) {
      command = `tail -n ${lines} ${this.escapeArg(path)}`;
    } else {
      command = `cat ${this.escapeArg(path)}`;
    }

    return await this.ssh.executeCommand(command);
  }

  /**
   * Write content to file
   */
  async writeFile(args: { path: string; content: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { path, content } = args;

    if (!this.validatePath(path)) {
      return {
        content: [{
          type: "text",
          text: `Path not allowed: ${path}`,
        }],
        isError: true,
      };
    }

    // Use heredoc to write content safely
    // Escape any existing EOF markers in content
    const safeContent = content.replace(/^EOF$/gm, "E_O_F");
    const command = `cat > ${this.escapeArg(path)} << 'MCPEOF'\n${safeContent}\nMCPEOF`;

    const result = await this.ssh.executeCommand(command);

    if (!result.isError) {
      return {
        content: [{
          type: "text",
          text: `File written successfully: ${path} (${content.length} bytes)`,
        }],
      };
    }

    return result;
  }

  /**
   * Upload file via SCP
   */
  async uploadFile(args: { localPath: string; remotePath: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { localPath, remotePath } = args;

    if (!this.validatePath(remotePath)) {
      return {
        content: [{
          type: "text",
          text: `Remote path not allowed: ${remotePath}`,
        }],
        isError: true,
      };
    }

    const result = await this.ssh.scpUpload(localPath, remotePath);

    if (result.success) {
      return {
        content: [{
          type: "text",
          text: `File uploaded: ${localPath} -> ${remotePath}`,
        }],
      };
    }

    return {
      content: [{
        type: "text",
        text: `Upload failed: ${result.stderr}`,
      }],
      isError: true,
    };
  }

  /**
   * Download file via SCP
   */
  async downloadFile(args: { remotePath: string; localPath: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { remotePath, localPath } = args;

    if (!this.validatePath(remotePath)) {
      return {
        content: [{
          type: "text",
          text: `Remote path not allowed: ${remotePath}`,
        }],
        isError: true,
      };
    }

    const result = await this.ssh.scpDownload(remotePath, localPath);

    if (result.success) {
      return {
        content: [{
          type: "text",
          text: `File downloaded: ${remotePath} -> ${localPath}`,
        }],
      };
    }

    return {
      content: [{
        type: "text",
        text: `Download failed: ${result.stderr}`,
      }],
      isError: true,
    };
  }

  /**
   * Check if file exists
   */
  async fileExists(path: string): Promise<boolean> {
    const result = await this.ssh.executeCommand(`test -f ${this.escapeArg(path)} && echo "exists"`);
    return result.content[0]?.text?.includes("exists") || false;
  }

  /**
   * Get file info
   */
  async getFileInfo(args: { path: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { path } = args;

    if (!this.validatePath(path)) {
      return {
        content: [{
          type: "text",
          text: `Path not allowed: ${path}`,
        }],
        isError: true,
      };
    }

    const command = `stat ${this.escapeArg(path)}`;
    return await this.ssh.executeCommand(command);
  }
}
