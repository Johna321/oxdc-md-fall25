# MCP HiPerGator Server

A Model Context Protocol (MCP) server for accessing UF's HiPerGator HPC cluster from Claude Code. Enables AI-assisted molecular dynamics simulation workflows with SLURM job management.

## Features

- **SSH Connection Management**: Persistent connections with multiplexing to minimize MFA prompts
- **SLURM Job Control**: Submit, monitor, and cancel batch jobs
- **File Operations**: Read, write, upload, and download files
- **MD Simulation Tools**: AMBER-specific tools for checking simulation status and analyzing results

## Prerequisites

1. **SSH Key Setup for HiPerGator**

   Generate an ED25519 key (recommended by UFRC):
   ```bash
   ssh-keygen -o -a 100 -t ed25519 -f ~/.ssh/id_ed25519_hpg -C "HiPerGator MCP"
   ```

   Copy to HiPerGator:
   ```bash
   ssh-copy-id -i ~/.ssh/id_ed25519_hpg john.aitken@hpg.rc.ufl.edu
   ```

2. **SSH Config for Multiplexing**

   Add to `~/.ssh/config`:
   ```
   Host hpg hpg.rc.ufl.edu
       User john.aitken
       HostName hpg.rc.ufl.edu
       Port 2222
       IdentityFile ~/.ssh/id_ed25519_hpg
       ControlPath ~/.ssh/sockets/hpg-%r@%h:%p
       ControlMaster auto
       ControlPersist 4h
       ServerAliveInterval 60
   ```

   Create socket directory:
   ```bash
   mkdir -p ~/.ssh/sockets
   chmod 700 ~/.ssh/sockets
   ```

3. **Initial MFA Authentication**

   Before using the MCP server, establish an initial connection to complete Duo MFA:
   ```bash
   ssh hpg
   # Complete Duo authentication
   # This creates the control socket that the MCP server will reuse
   ```

## Installation

### Option 1: Install from npm (when published)
```bash
npm install -g mcp-hipergator
```

### Option 2: Install from source
```bash
cd mcp-hipergator
npm install
npm run build
```

## Configuration

Create a config file at `~/.mcp-hipergator.json`:

```json
{
  "host": "hpg.rc.ufl.edu",
  "user": "john.aitken",
  "port": 2222,
  "identityFile": "~/.ssh/id_ed25519_hpg",
  "projectBase": "/blue/roitberg/john.aitken",
  "defaultAccount": "roitberg",
  "defaultQos": "roitberg"
}
```

Or use environment variables:
```bash
export HPG_USER="john.aitken"
export HPG_PROJECT_BASE="/blue/roitberg/john.aitken"
```

## Adding to Claude Code

```bash
claude mcp add mcp-hipergator -- node /path/to/mcp-hipergator/dist/index.js
```

Or add to your Claude Code settings manually:
```json
{
  "mcpServers": {
    "hipergator": {
      "command": "node",
      "args": ["/path/to/mcp-hipergator/dist/index.js"],
      "env": {
        "HPG_USER": "john.aitken"
      }
    }
  }
}
```

## Available Tools

### Connection Tools
| Tool | Description |
|------|-------------|
| `hpg_connect` | Establish SSH connection to HiPerGator |
| `hpg_disconnect` | Close SSH connection |
| `hpg_status` | Check connection status |

### SLURM Tools
| Tool | Description |
|------|-------------|
| `hpg_sbatch` | Submit a batch job |
| `hpg_squeue` | Check job queue |
| `hpg_sacct` | Get job accounting info |
| `hpg_scancel` | Cancel a job |
| `hpg_job_output` | Read job stdout/stderr |

### File Tools
| Tool | Description |
|------|-------------|
| `hpg_ls` | List directory contents |
| `hpg_read_file` | Read file content |
| `hpg_write_file` | Write file content |
| `hpg_upload` | Upload file via SCP |
| `hpg_download` | Download file via SCP |
| `hpg_exec` | Execute arbitrary command |

### MD Simulation Tools
| Tool | Description |
|------|-------------|
| `hpg_check_md_status` | Check simulation status |
| `hpg_analyze_mdinfo` | Parse AMBER mdinfo file |
| `hpg_validate_rst7` | Validate restart file |

## Example Usage with Claude Code

```
User: Check the status of my BiOx+2 MD simulation

Claude: I'll check the simulation status on HiPerGator.
[Uses hpg_connect, then hpg_check_md_status]

The BiOx+2 system is currently in eq1 stage:
- Progress: 59.6% (149000/250000 steps)
- Estimated time remaining: 4.0 hours
- Files present: heat.cpu.rst7, eq1.cpu.rst7
- Missing: eq2.cpu.rst7 (will be created after eq1 completes)

User: Submit the production job once eq2 is done

Claude: I'll monitor and submit when ready.
[Uses hpg_squeue to check eq job, then hpg_sbatch when complete]
```

## Security Considerations

- **Never stores passwords**: Uses SSH key authentication only
- **SSH agent integration**: Supports passphrase-protected keys via ssh-agent
- **Path validation**: Restricts file operations to allowed directories
- **Command escaping**: Prevents shell injection attacks
- **Control socket**: Reuses authenticated connections to minimize MFA prompts

## Troubleshooting

### Connection Fails
1. Ensure SSH key exists: `ls -la ~/.ssh/id_ed25519_hpg`
2. Test manual connection: `ssh hpg`
3. Check control socket: `ls ~/.ssh/sockets/`
4. Complete Duo MFA manually first

### Jobs Not Submitting
1. Check account/QOS: `sacctmgr show associations user=<username>`
2. Verify partition access: `sinfo`
3. Check script permissions: `chmod +x script.sbatch`

### Timeout Errors
Increase timeout in config:
```json
{
  "commandTimeout": 120000,
  "longCommandTimeout": 600000
}
```

## Development

```bash
# Run in development mode
npm run dev

# Test with MCP Inspector
npm run inspect

# Run tests
npm test
```

## License

MIT

## References

- [MCP Documentation](https://modelcontextprotocol.io/docs/)
- [UFRC HiPerGator Docs](https://help.rc.ufl.edu/)
- [SLURM Documentation](https://slurm.schedmd.com/)
- [AMBER Manual](https://ambermd.org/Manuals.php)
