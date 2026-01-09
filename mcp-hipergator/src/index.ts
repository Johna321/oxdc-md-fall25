#!/usr/bin/env node
/**
 * MCP HiPerGator Server
 *
 * A Model Context Protocol server for accessing UF's HiPerGator HPC cluster.
 * Enables Claude Code to submit SLURM jobs, monitor progress, and manage files.
 *
 * @author John Aitken
 * @license MIT
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { SSHClient } from "./ssh-client.js";
import { SlurmTools } from "./slurm-tools.js";
import { FileTools } from "./file-tools.js";
import { MDTools } from "./md-tools.js";
import { toolDefinitions } from "./tool-definitions.js";
import { Config, loadConfig } from "./config.js";

// Initialize configuration
const config: Config = loadConfig();

// Initialize SSH client
const sshClient = new SSHClient(config);

// Initialize tool modules
const slurmTools = new SlurmTools(sshClient, config);
const fileTools = new FileTools(sshClient, config);
const mdTools = new MDTools(sshClient, config);

// Create MCP server
const server = new Server(
  {
    name: "mcp-hipergator",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// Register tool listing handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: toolDefinitions };
});

// Register tool execution handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      // Connection tools
      case "hpg_connect":
        return await sshClient.connect();

      case "hpg_disconnect":
        return await sshClient.disconnect();

      case "hpg_status":
        return await sshClient.getStatus();

      // SLURM tools
      case "hpg_sbatch":
        return await slurmTools.submitJob(args as { script: string; workdir?: string });

      case "hpg_squeue":
        return await slurmTools.getQueue(args as { user?: string; jobId?: string });

      case "hpg_sacct":
        return await slurmTools.getJobAccounting(args as { jobId: string });

      case "hpg_scancel":
        return await slurmTools.cancelJob(args as { jobId: string });

      case "hpg_job_output":
        return await slurmTools.getJobOutput(args as { jobId: string; outputType?: string });

      // File system tools
      case "hpg_ls":
        return await fileTools.listDirectory(args as { path: string; options?: string });

      case "hpg_read_file":
        return await fileTools.readFile(args as { path: string; lines?: number });

      case "hpg_write_file":
        return await fileTools.writeFile(args as { path: string; content: string });

      case "hpg_upload":
        return await fileTools.uploadFile(args as { localPath: string; remotePath: string });

      case "hpg_download":
        return await fileTools.downloadFile(args as { remotePath: string; localPath: string });

      case "hpg_exec":
        return await sshClient.executeCommand((args as { command: string }).command);

      // MD simulation tools
      case "hpg_check_md_status":
        return await mdTools.checkSimulationStatus(args as { systemPath: string });

      case "hpg_analyze_mdinfo":
        return await mdTools.analyzeMdinfo(args as { mdinfoPath: string });

      case "hpg_validate_rst7":
        return await mdTools.validateRestart(args as { rst7Path: string; prmtopPath: string });

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [{ type: "text", text: `Error: ${errorMessage}` }],
      isError: true,
    };
  }
});

// Register resource listing handler
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "hpg://config",
        name: "HiPerGator Configuration",
        description: "Current SSH and server configuration",
        mimeType: "application/json",
      },
      {
        uri: "hpg://queue",
        name: "SLURM Job Queue",
        description: "Current job queue for the configured user",
        mimeType: "application/json",
      },
    ],
  };
});

// Register resource reading handler
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  switch (uri) {
    case "hpg://config":
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({
              host: config.host,
              user: config.user,
              projectBase: config.projectBase,
              connected: sshClient.isConnected(),
            }, null, 2),
          },
        ],
      };

    case "hpg://queue":
      const queueResult = await slurmTools.getQueue({ user: config.user });
      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(queueResult, null, 2),
          },
        ],
      };

    default:
      throw new Error(`Unknown resource: ${uri}`);
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP HiPerGator server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
