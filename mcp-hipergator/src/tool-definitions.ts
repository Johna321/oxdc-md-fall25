/**
 * MCP Tool definitions for HiPerGator server
 */

import { Tool } from "@modelcontextprotocol/sdk/types.js";

export const toolDefinitions: Tool[] = [
  // ============================================
  // CONNECTION TOOLS
  // ============================================
  {
    name: "hpg_connect",
    description: "Establish SSH connection to HiPerGator. Uses SSH key authentication with multiplexing for persistent connections. May require Duo MFA on first connection.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "hpg_disconnect",
    description: "Close the SSH connection to HiPerGator and clean up control socket.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "hpg_status",
    description: "Check current connection status to HiPerGator including control socket state and last command info.",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },

  // ============================================
  // SLURM JOB TOOLS
  // ============================================
  {
    name: "hpg_sbatch",
    description: "Submit a SLURM batch job script. Returns the job ID on success.",
    inputSchema: {
      type: "object",
      properties: {
        script: {
          type: "string",
          description: "Path to the SLURM batch script (.sbatch file) on HiPerGator",
        },
        workdir: {
          type: "string",
          description: "Optional working directory to cd into before submitting",
        },
      },
      required: ["script"],
    },
  },
  {
    name: "hpg_squeue",
    description: "Check SLURM job queue. Shows job status, partition, time used, and node allocation.",
    inputSchema: {
      type: "object",
      properties: {
        user: {
          type: "string",
          description: "Filter by username (defaults to configured user)",
        },
        jobId: {
          type: "string",
          description: "Filter by specific job ID",
        },
      },
      required: [],
    },
  },
  {
    name: "hpg_sacct",
    description: "Get detailed job accounting information including resource usage, exit codes, and timing.",
    inputSchema: {
      type: "object",
      properties: {
        jobId: {
          type: "string",
          description: "The SLURM job ID to query",
        },
      },
      required: ["jobId"],
    },
  },
  {
    name: "hpg_scancel",
    description: "Cancel a running or pending SLURM job.",
    inputSchema: {
      type: "object",
      properties: {
        jobId: {
          type: "string",
          description: "The SLURM job ID to cancel",
        },
      },
      required: ["jobId"],
    },
  },
  {
    name: "hpg_job_output",
    description: "Read the stdout and/or stderr output from a SLURM job.",
    inputSchema: {
      type: "object",
      properties: {
        jobId: {
          type: "string",
          description: "The SLURM job ID",
        },
        outputType: {
          type: "string",
          enum: ["stdout", "stderr", "both"],
          description: "Which output to retrieve (default: both)",
        },
      },
      required: ["jobId"],
    },
  },

  // ============================================
  // FILE SYSTEM TOOLS
  // ============================================
  {
    name: "hpg_ls",
    description: "List directory contents on HiPerGator. Supports standard ls options.",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Directory path to list",
        },
        options: {
          type: "string",
          description: "ls options (default: -la)",
        },
      },
      required: ["path"],
    },
  },
  {
    name: "hpg_read_file",
    description: "Read file contents from HiPerGator. Limited to 1MB unless using lines parameter.",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Path to the file to read",
        },
        lines: {
          type: "number",
          description: "Number of lines to read from the end of file (uses tail)",
        },
      },
      required: ["path"],
    },
  },
  {
    name: "hpg_write_file",
    description: "Write content to a file on HiPerGator. Creates or overwrites the file.",
    inputSchema: {
      type: "object",
      properties: {
        path: {
          type: "string",
          description: "Path to the file to write",
        },
        content: {
          type: "string",
          description: "Content to write to the file",
        },
      },
      required: ["path", "content"],
    },
  },
  {
    name: "hpg_upload",
    description: "Upload a local file to HiPerGator via SCP.",
    inputSchema: {
      type: "object",
      properties: {
        localPath: {
          type: "string",
          description: "Path to the local file to upload",
        },
        remotePath: {
          type: "string",
          description: "Destination path on HiPerGator",
        },
      },
      required: ["localPath", "remotePath"],
    },
  },
  {
    name: "hpg_download",
    description: "Download a file from HiPerGator to local machine via SCP.",
    inputSchema: {
      type: "object",
      properties: {
        remotePath: {
          type: "string",
          description: "Path to the file on HiPerGator",
        },
        localPath: {
          type: "string",
          description: "Local destination path",
        },
      },
      required: ["remotePath", "localPath"],
    },
  },
  {
    name: "hpg_exec",
    description: "Execute an arbitrary command on HiPerGator. Use for commands not covered by other tools.",
    inputSchema: {
      type: "object",
      properties: {
        command: {
          type: "string",
          description: "The shell command to execute",
        },
      },
      required: ["command"],
    },
  },

  // ============================================
  // MD SIMULATION TOOLS
  // ============================================
  {
    name: "hpg_check_md_status",
    description: "Check the overall status of an AMBER MD simulation system. Reports file existence, current stage, progress, and any errors.",
    inputSchema: {
      type: "object",
      properties: {
        systemPath: {
          type: "string",
          description: "Path to the MD system directory (e.g., /blue/roitberg/.../systems/BiOx+2)",
        },
      },
      required: ["systemPath"],
    },
  },
  {
    name: "hpg_analyze_mdinfo",
    description: "Parse and analyze an AMBER mdinfo file to get detailed simulation progress including step count, temperature, energy, and timing.",
    inputSchema: {
      type: "object",
      properties: {
        mdinfoPath: {
          type: "string",
          description: "Path to the .mdinfo file",
        },
      },
      required: ["mdinfoPath"],
    },
  },
  {
    name: "hpg_validate_rst7",
    description: "Validate an AMBER restart file (.rst7) using cpptraj. Checks atom count, box dimensions, and integrity.",
    inputSchema: {
      type: "object",
      properties: {
        rst7Path: {
          type: "string",
          description: "Path to the restart file (.rst7)",
        },
        prmtopPath: {
          type: "string",
          description: "Path to the topology file (.prmtop)",
        },
      },
      required: ["rst7Path", "prmtopPath"],
    },
  },
];
