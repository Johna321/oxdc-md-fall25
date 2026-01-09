# HiPerGator MCP Server: Research & Design Journal

## Research Date: January 2026

---

## 1. Research Summary

### 1.1 MCP Protocol Overview

The Model Context Protocol (MCP) is an open standard that enables LLMs like Claude to interact with external tools, data sources, and systems through a standardized interface. Key components:

- **Server**: Exposes tools and resources via JSON-RPC over stdio
- **Transport**: Communication layer (stdio for local, HTTP/SSE for remote)
- **Tools**: Executable functions the model can invoke
- **Resources**: Read-only data sources for context

### 1.2 Existing SSH MCP Implementations Reviewed

| Project | Approach | Strengths | Limitations |
|---------|----------|-----------|-------------|
| [mcp-ssh (AiondaDotCom)](https://github.com/AiondaDotCom/mcp-ssh) | Native SSH commands | Uses system ssh/scp, auto-discovers hosts | No SLURM-specific tools |
| [ssh-mcp (tufantunc)](https://github.com/tufantunc/ssh-mcp) | Direct credentials | Simple setup | Password in config (insecure) |
| [SSH-MCP (mixelpixx)](https://github.com/mixelpixx/SSH-MCP) | Key-based | VPS management focus | Not HPC-oriented |

**Key Insight**: None of these are designed for HPC/SLURM workflows. A custom solution is needed.

### 1.3 HiPerGator Authentication Requirements

From [UFRC Documentation](https://docs.rc.ufl.edu/access/ssh_keys/):

1. **SSH Key Authentication**: Port 2222 for key-based auth, port 22 for password
2. **Recommended Key Type**: ED25519 (`ssh-keygen -o -a 100 -t ed25519`)
3. **MFA Requirement**: Duo MFA still required even with SSH keys
4. **SSH Multiplexing**: Reduces MFA prompts via ControlMaster

**Critical Design Decision**: Use SSH multiplexing with a persistent control socket to minimize MFA interruptions.

### 1.4 SLURM Job Management

From [simple-slurm](https://pypi.org/project/simple-slurm/) and [SLURM documentation](https://slurm.schedmd.com/):

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `sbatch` | Submit batch job | `--job-name`, `--output`, `--partition` |
| `squeue` | View job queue | `-u <user>`, `--start`, `--format` |
| `scancel` | Cancel job | `<jobid>` |
| `sacct` | Job accounting | `-j <jobid>`, `--format` |
| `scontrol` | Job control | `show job <jobid>` |

---

## 2. Architecture Design

### 2.1 Core Design Principles

1. **Security First**: Never store passwords; use SSH keys + agent forwarding
2. **Persistent Connections**: SSH multiplexing to avoid repeated MFA
3. **SLURM-Native**: Purpose-built tools for HPC job management
4. **Context-Aware**: Understand MD simulation workflows and file structures
5. **Robust Error Handling**: Graceful failures with actionable messages

### 2.2 Proposed Tool Set

```
┌─────────────────────────────────────────────────────────────────┐
│                    HiPerGator MCP Server                        │
├─────────────────────────────────────────────────────────────────┤
│  CONNECTION TOOLS                                               │
│  ├── hpg_connect        - Establish SSH connection              │
│  ├── hpg_disconnect     - Close connection                      │
│  └── hpg_status         - Check connection health               │
├─────────────────────────────────────────────────────────────────┤
│  FILE SYSTEM TOOLS                                              │
│  ├── hpg_ls             - List directory contents               │
│  ├── hpg_read_file      - Read remote file content              │
│  ├── hpg_write_file     - Write content to remote file          │
│  ├── hpg_upload         - Upload local file via SCP             │
│  └── hpg_download       - Download remote file via SCP          │
├─────────────────────────────────────────────────────────────────┤
│  SLURM JOB TOOLS                                                │
│  ├── hpg_sbatch         - Submit batch job                      │
│  ├── hpg_squeue         - Check job queue status                │
│  ├── hpg_sacct          - Get job accounting info               │
│  ├── hpg_scancel        - Cancel running job                    │
│  └── hpg_job_output     - Read job stdout/stderr                │
├─────────────────────────────────────────────────────────────────┤
│  MD SIMULATION TOOLS (Domain-Specific)                          │
│  ├── hpg_check_md_status - Check equilibration/production state │
│  ├── hpg_analyze_mdinfo  - Parse AMBER mdinfo for progress      │
│  └── hpg_validate_rst7   - Verify restart file integrity        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 SSH Configuration Strategy

```bash
# ~/.ssh/config for HiPerGator with multiplexing
Host hpg hpg.rc.ufl.edu
    User john.aitken
    HostName hpg.rc.ufl.edu
    Port 2222
    IdentityFile ~/.ssh/id_ed25519_hpg
    ControlPath ~/.ssh/sockets/hpg-%r@%h:%p
    ControlMaster auto
    ControlPersist 4h
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

**Key Features**:
- `ControlPersist 4h`: Keep connection alive for 4 hours after last use
- `ControlPath`: Reusable socket for connection multiplexing
- `ServerAliveInterval`: Prevent connection drops

### 2.4 Connection Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Claude Code │───▶│  MCP Server  │───▶│  HiPerGator  │
│              │    │  (Local)     │    │  (Remote)    │
└──────────────┘    └──────────────┘    └──────────────┘
       │                   │                    │
       │  Tool Request     │                    │
       │──────────────────▶│                    │
       │                   │  SSH (Multiplexed) │
       │                   │───────────────────▶│
       │                   │                    │  Execute
       │                   │◀───────────────────│  Command
       │  Tool Response    │                    │
       │◀──────────────────│                    │
```

---

## 3. Implementation Decisions

### 3.1 Language Choice: TypeScript

**Rationale**:
1. Official MCP SDK is TypeScript-first
2. Strong typing for reliable tool definitions
3. Native async/await for SSH operations
4. Easy integration with Claude Code

### 3.2 SSH Execution Strategy

**Option A: Native `ssh` command via child_process** ✓ CHOSEN
- Pros: Uses system SSH with full feature support (multiplexing, agent, ProxyJump)
- Cons: Relies on system configuration

**Option B: Node.js SSH library (ssh2)**
- Pros: Pure JavaScript, no system dependencies
- Cons: No SSH agent forwarding, complex key handling

**Decision**: Use native SSH commands for maximum compatibility with HiPerGator's authentication requirements.

### 3.3 Error Handling Strategy

```typescript
interface HPGError {
  code: 'CONNECTION_FAILED' | 'AUTH_FAILED' | 'COMMAND_FAILED' | 'TIMEOUT';
  message: string;
  recoverable: boolean;
  suggestion: string;
}

// Example error handling
try {
  await executeSSH(command);
} catch (e) {
  if (e.message.includes('Permission denied')) {
    return {
      code: 'AUTH_FAILED',
      message: 'SSH authentication failed',
      recoverable: true,
      suggestion: 'Check SSH key configuration and ensure Duo MFA is completed'
    };
  }
}
```

### 3.4 SLURM Output Parsing

```typescript
// Parse squeue output into structured data
interface SlurmJob {
  jobId: string;
  name: string;
  user: string;
  state: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  partition: string;
  timeUsed: string;
  timeLimit: string;
  nodes: number;
}

function parseSqueue(output: string): SlurmJob[] {
  // Parse tabular squeue output
  const lines = output.trim().split('\n').slice(1); // Skip header
  return lines.map(line => {
    const [jobId, partition, name, user, state, time, nodes, nodelist] =
      line.trim().split(/\s+/);
    return { jobId, partition, name, user, state, time, nodes: parseInt(nodes) };
  });
}
```

---

## 4. Security Considerations

### 4.1 Credential Handling

| Approach | Security Level | Implementation |
|----------|---------------|----------------|
| Password in config | ❌ NEVER | Rejected |
| SSH key (no passphrase) | ⚠️ Risky | Not recommended |
| SSH key + agent | ✅ Secure | Recommended |
| SSH key + passphrase + agent | ✅✅ Most Secure | Ideal |

### 4.2 Command Injection Prevention

```typescript
// UNSAFE - command injection risk
const cmd = `ssh hpg "ls ${userInput}"`;

// SAFE - escaped arguments
import { escapeShellArg } from './utils';
const cmd = `ssh hpg "ls ${escapeShellArg(userInput)}"`;

// SAFEST - use SSH command separation
const cmd = `ssh hpg -- ls ${escapeShellArg(userInput)}`;
```

### 4.3 Path Traversal Prevention

```typescript
function validatePath(path: string, allowedBase: string): boolean {
  const resolved = posix.resolve(allowedBase, path);
  return resolved.startsWith(allowedBase);
}

// Only allow operations within project directory
const PROJECT_BASE = '/blue/roitberg/john.aitken/oxdc-md-fall25';
if (!validatePath(targetPath, PROJECT_BASE)) {
  throw new Error('Path traversal detected');
}
```

---

## 5. Inspirational Code Snippets

### From mcp-ssh (Native SSH approach)

```typescript
// Execute command using system SSH
async function runRemoteCommand(host: string, command: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const ssh = spawn('ssh', [host, command], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    ssh.stdout.on('data', (data) => stdout += data);
    ssh.stderr.on('data', (data) => stderr += data);

    ssh.on('close', (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr || `Exit code ${code}`));
    });
  });
}
```

### SLURM Job Monitoring Pattern

```typescript
// Poll for job completion
async function waitForJob(jobId: string, pollInterval = 30000): Promise<JobResult> {
  while (true) {
    const status = await checkJobStatus(jobId);

    if (status.state === 'COMPLETED') {
      return { success: true, ...status };
    }
    if (status.state === 'FAILED' || status.state === 'CANCELLED') {
      return { success: false, ...status };
    }

    await sleep(pollInterval);
  }
}
```

---

## 6. Testing Strategy

### 6.1 Local Testing with MCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run server with inspector
npx mcp-inspector node dist/index.js
```

### 6.2 Integration Tests

```typescript
describe('HiPerGator MCP Server', () => {
  test('hpg_connect establishes connection', async () => {
    const result = await callTool('hpg_connect');
    expect(result.connected).toBe(true);
  });

  test('hpg_squeue returns job list', async () => {
    const result = await callTool('hpg_squeue', { user: 'john.aitken' });
    expect(Array.isArray(result.jobs)).toBe(true);
  });

  test('hpg_sbatch submits job', async () => {
    const result = await callTool('hpg_sbatch', {
      script: '/path/to/test.sbatch'
    });
    expect(result.jobId).toMatch(/^\d+$/);
  });
});
```

---

## 7. References

1. [MCP Official Documentation](https://modelcontextprotocol.io/docs/)
2. [mcp-ssh GitHub](https://github.com/AiondaDotCom/mcp-ssh)
3. [UFRC SSH Keys Documentation](https://docs.rc.ufl.edu/access/ssh_keys/)
4. [SLURM Quick Start Guide](https://slurm.schedmd.com/quickstart.html)
5. [simple-slurm Python Library](https://pypi.org/project/simple-slurm/)
6. [TypeScript MCP SDK Tutorial](https://dev.to/shadid12/how-to-build-mcp-servers-with-typescript-sdk-1c28)

---

## 8. Next Steps

1. [ ] Create project scaffold with TypeScript + MCP SDK
2. [ ] Implement SSH connection layer with multiplexing
3. [ ] Build SLURM tool set (sbatch, squeue, sacct, scancel)
4. [ ] Add file system tools (ls, read, write, upload, download)
5. [ ] Implement MD-specific tools for AMBER workflow
6. [ ] Write comprehensive tests
7. [ ] Package for easy installation via `claude mcp add`
