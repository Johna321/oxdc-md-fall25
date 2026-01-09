/**
 * SLURM job management tools for HiPerGator
 */

import { SSHClient } from "./ssh-client.js";
import { Config } from "./config.js";

export interface SlurmJob {
  jobId: string;
  name: string;
  user: string;
  state: string;
  partition: string;
  timeUsed: string;
  timeLimit: string;
  nodes: string;
  nodelist: string;
  submitTime?: string;
  startTime?: string;
  endTime?: string;
}

export interface JobSubmitResult {
  success: boolean;
  jobId?: string;
  message: string;
}

export class SlurmTools {
  private ssh: SSHClient;
  private config: Config;

  constructor(ssh: SSHClient, config: Config) {
    this.ssh = ssh;
    this.config = config;
  }

  /**
   * Submit a SLURM batch job
   */
  async submitJob(args: { script: string; workdir?: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { script, workdir } = args;

    // Build command with optional working directory
    let command = "";
    if (workdir) {
      command = `cd "${workdir}" && sbatch "${script}"`;
    } else {
      command = `sbatch "${script}"`;
    }

    const result = await this.ssh.executeCommand(command);

    // Parse job ID from sbatch output
    // Expected format: "Submitted batch job 12345678"
    const match = result.content[0]?.text?.match(/Submitted batch job (\d+)/);

    if (match) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: true,
            jobId: match[1],
            message: `Job ${match[1]} submitted successfully`,
            script: script,
          }, null, 2),
        }],
      };
    }

    return result;
  }

  /**
   * Get SLURM job queue
   */
  async getQueue(args: { user?: string; jobId?: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { user, jobId } = args;

    // Build squeue command with custom format
    let command = 'squeue --format="%.18i %.12P %.30j %.10u %.8T %.10M %.10l %.6D %R"';

    if (jobId) {
      command += ` -j ${jobId}`;
    } else if (user) {
      command += ` -u ${user}`;
    } else {
      command += ` -u ${this.config.user}`;
    }

    const result = await this.ssh.executeCommand(command);

    if (result.isError) {
      return result;
    }

    // Parse squeue output
    try {
      const jobs = this.parseSqueueOutput(result.content[0]?.text || "");
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            jobs: jobs,
            count: jobs.length,
            query: { user: user || this.config.user, jobId },
          }, null, 2),
        }],
      };
    } catch (e) {
      return result; // Return raw output if parsing fails
    }
  }

  /**
   * Parse squeue output into structured data
   */
  private parseSqueueOutput(output: string): SlurmJob[] {
    const lines = output.trim().split("\n");
    if (lines.length <= 1) return [];

    // Skip header line
    return lines.slice(1).map((line) => {
      const parts = line.trim().split(/\s+/);
      return {
        jobId: parts[0] || "",
        partition: parts[1] || "",
        name: parts[2] || "",
        user: parts[3] || "",
        state: parts[4] || "",
        timeUsed: parts[5] || "",
        timeLimit: parts[6] || "",
        nodes: parts[7] || "",
        nodelist: parts.slice(8).join(" ") || "",
      };
    }).filter((job) => job.jobId);
  }

  /**
   * Get job accounting information
   */
  async getJobAccounting(args: { jobId: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { jobId } = args;

    const command = `sacct -j ${jobId} --format=JobID,JobName,Partition,Account,AllocCPUS,State,ExitCode,Elapsed,MaxRSS,MaxVMSize,Submit,Start,End --noheader --parsable2`;

    const result = await this.ssh.executeCommand(command);

    if (result.isError) {
      return result;
    }

    // Parse sacct output
    try {
      const jobs = this.parseSacctOutput(result.content[0]?.text || "");
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            jobId: jobId,
            steps: jobs,
          }, null, 2),
        }],
      };
    } catch {
      return result;
    }
  }

  /**
   * Parse sacct parsable output
   */
  private parseSacctOutput(output: string): Record<string, string>[] {
    const lines = output.trim().split("\n");
    const fields = [
      "JobID", "JobName", "Partition", "Account", "AllocCPUS",
      "State", "ExitCode", "Elapsed", "MaxRSS", "MaxVMSize",
      "Submit", "Start", "End",
    ];

    return lines.map((line) => {
      const parts = line.split("|");
      const record: Record<string, string> = {};
      fields.forEach((field, i) => {
        record[field] = parts[i] || "";
      });
      return record;
    }).filter((r) => r.JobID);
  }

  /**
   * Cancel a SLURM job
   */
  async cancelJob(args: { jobId: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { jobId } = args;
    const command = `scancel ${jobId}`;

    const result = await this.ssh.executeCommand(command);

    // scancel doesn't output anything on success
    if (!result.isError && !result.content[0]?.text) {
      return {
        content: [{
          type: "text",
          text: `Job ${jobId} cancelled successfully`,
        }],
      };
    }

    return result;
  }

  /**
   * Get job output files
   */
  async getJobOutput(args: { jobId: string; outputType?: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { jobId, outputType = "both" } = args;

    // First, find the output files using scontrol
    const infoResult = await this.ssh.executeCommand(`scontrol show job ${jobId}`);

    if (infoResult.isError) {
      // Job might have completed, try to find output files in common patterns
      const findCommand = `find ${this.config.projectBase} -name "*${jobId}*.out" -o -name "*${jobId}*.err" 2>/dev/null | head -5`;
      return await this.ssh.executeCommand(findCommand);
    }

    // Parse stdout and stderr paths from scontrol output
    const stdoutMatch = infoResult.content[0]?.text?.match(/StdOut=(\S+)/);
    const stderrMatch = infoResult.content[0]?.text?.match(/StdErr=(\S+)/);

    const outputs: string[] = [];

    if ((outputType === "stdout" || outputType === "both") && stdoutMatch) {
      const stdout = await this.ssh.executeCommand(`tail -100 "${stdoutMatch[1]}"`);
      outputs.push(`=== STDOUT (${stdoutMatch[1]}) ===\n${stdout.content[0]?.text || "(empty)"}`);
    }

    if ((outputType === "stderr" || outputType === "both") && stderrMatch) {
      const stderr = await this.ssh.executeCommand(`tail -100 "${stderrMatch[1]}"`);
      outputs.push(`=== STDERR (${stderrMatch[1]}) ===\n${stderr.content[0]?.text || "(empty)"}`);
    }

    return {
      content: [{
        type: "text",
        text: outputs.join("\n\n") || "No output files found",
      }],
    };
  }

  /**
   * Check estimated start time for pending jobs
   */
  async getEstimatedStart(args: { jobId: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { jobId } = args;
    const command = `squeue -j ${jobId} --start --format="%.18i %.12P %.30j %.10u %.8T %S"`;
    return await this.ssh.executeCommand(command);
  }
}
