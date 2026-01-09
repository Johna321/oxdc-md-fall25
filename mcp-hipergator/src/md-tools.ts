/**
 * Molecular Dynamics simulation-specific tools for AMBER workflows
 */

import { SSHClient } from "./ssh-client.js";
import { Config } from "./config.js";

export interface SimulationStatus {
  system: string;
  stage: "heating" | "eq1" | "eq2" | "production" | "unknown";
  progress: number; // 0-100
  currentStep: number;
  totalSteps: number;
  estimatedTimeRemaining: string;
  lastUpdate: string;
  files: {
    prmtop: boolean;
    inpcrd: boolean;
    heatRst7: boolean;
    eq1Rst7: boolean;
    eq2Rst7: boolean;
    prodNc: boolean;
    prodRst7: boolean;
  };
  errors: string[];
  warnings: string[];
}

export interface MdinfoData {
  currentStep: number;
  totalSteps: number;
  progress: number;
  temperature: number;
  pressure: number;
  density: number;
  totalEnergy: number;
  nsPerDay: number;
  estimatedTimeRemaining: string;
}

export class MDTools {
  private ssh: SSHClient;
  private config: Config;

  constructor(ssh: SSHClient, config: Config) {
    this.ssh = ssh;
    this.config = config;
  }

  /**
   * Check overall MD simulation status for a system
   */
  async checkSimulationStatus(args: { systemPath: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { systemPath } = args;

    // Check for expected files
    const fileChecks = await this.ssh.executeCommand(`
      cd "${systemPath}" 2>/dev/null || exit 1
      echo "=== File Status ==="
      for f in *.prmtop 5vg3_solv.inpcrd heat.cpu.rst7 eq1.cpu.rst7 eq2.cpu.rst7 prod.nc prod.rst7; do
        if [ -f "$f" ]; then
          echo "$f: EXISTS ($(ls -lh "$f" | awk '{print $5}'))"
        else
          echo "$f: MISSING"
        fi
      done

      echo ""
      echo "=== Latest mdinfo ==="
      for f in prod.mdinfo eq2.cpu.mdinfo eq1.cpu.mdinfo heat.cpu.mdinfo; do
        if [ -f "$f" ]; then
          echo "--- $f ---"
          cat "$f" | grep -E "NSTEP|Total steps|Completed|Remaining|ns/day"
          break
        fi
      done

      echo ""
      echo "=== Recent Errors ==="
      for f in *.out *.err; do
        if [ -f "$f" ]; then
          grep -i "error\\|fail\\|warning\\|vlimit" "$f" 2>/dev/null | tail -5
        fi
      done | head -20
    `);

    if (fileChecks.isError) {
      return fileChecks;
    }

    // Parse and structure the output
    const output = fileChecks.content[0]?.text || "";
    const status = this.parseSimulationStatus(output, systemPath);

    return {
      content: [{
        type: "text",
        text: JSON.stringify(status, null, 2),
      }],
    };
  }

  /**
   * Parse simulation status from file check output
   */
  private parseSimulationStatus(output: string, systemPath: string): SimulationStatus {
    const status: SimulationStatus = {
      system: systemPath.split("/").pop() || systemPath,
      stage: "unknown",
      progress: 0,
      currentStep: 0,
      totalSteps: 0,
      estimatedTimeRemaining: "unknown",
      lastUpdate: new Date().toISOString(),
      files: {
        prmtop: output.includes("prmtop: EXISTS"),
        inpcrd: output.includes("inpcrd: EXISTS"),
        heatRst7: output.includes("heat.cpu.rst7: EXISTS"),
        eq1Rst7: output.includes("eq1.cpu.rst7: EXISTS"),
        eq2Rst7: output.includes("eq2.cpu.rst7: EXISTS"),
        prodNc: output.includes("prod.nc: EXISTS"),
        prodRst7: output.includes("prod.rst7: EXISTS"),
      },
      errors: [],
      warnings: [],
    };

    // Determine stage
    if (status.files.prodNc) {
      status.stage = "production";
    } else if (status.files.eq2Rst7) {
      status.stage = "production"; // Ready for production
    } else if (status.files.eq1Rst7) {
      status.stage = "eq2";
    } else if (status.files.heatRst7) {
      status.stage = "eq1";
    } else {
      status.stage = "heating";
    }

    // Parse progress from mdinfo
    const stepMatch = output.match(/NSTEP\s*=\s*(\d+)/);
    const totalMatch = output.match(/Total steps:\s*(\d+)/);
    const completedMatch = output.match(/Completed:\s*(\d+)\s*\(\s*([\d.]+)%\)/);
    const remainingMatch = output.match(/Estimated time remaining:\s*(.+)/);

    if (stepMatch) status.currentStep = parseInt(stepMatch[1]);
    if (totalMatch) status.totalSteps = parseInt(totalMatch[1]);
    if (completedMatch) status.progress = parseFloat(completedMatch[2]);
    if (remainingMatch) status.estimatedTimeRemaining = remainingMatch[1].trim();

    // Parse errors/warnings
    const errorSection = output.split("=== Recent Errors ===")[1] || "";
    const errorLines = errorSection.split("\n").filter((l) => l.trim());
    status.errors = errorLines.filter((l) => /error|fail/i.test(l));
    status.warnings = errorLines.filter((l) => /warning|vlimit/i.test(l));

    return status;
  }

  /**
   * Analyze AMBER mdinfo file in detail
   */
  async analyzeMdinfo(args: { mdinfoPath: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { mdinfoPath } = args;

    const result = await this.ssh.executeCommand(`cat "${mdinfoPath}"`);

    if (result.isError) {
      return result;
    }

    const content = result.content[0]?.text || "";
    const data = this.parseMdinfo(content);

    return {
      content: [{
        type: "text",
        text: JSON.stringify(data, null, 2),
      }],
    };
  }

  /**
   * Parse AMBER mdinfo file content
   */
  private parseMdinfo(content: string): MdinfoData {
    const data: MdinfoData = {
      currentStep: 0,
      totalSteps: 0,
      progress: 0,
      temperature: 0,
      pressure: 0,
      density: 0,
      totalEnergy: 0,
      nsPerDay: 0,
      estimatedTimeRemaining: "unknown",
    };

    // Parse current step and temperature from energy block
    const stepMatch = content.match(/NSTEP\s*=\s*(\d+)/);
    const tempMatch = content.match(/TEMP\(K\)\s*=\s*([\d.]+)/);
    const pressMatch = content.match(/PRESS\s*=\s*([-\d.]+)/);
    const densityMatch = content.match(/Density\s*=\s*([\d.]+)/);
    const etotMatch = content.match(/Etot\s*=\s*([-\d.]+)/);

    // Parse timing info
    const totalMatch = content.match(/Total steps:\s*(\d+)/);
    const completedMatch = content.match(/Completed:\s*(\d+)\s*\(\s*([\d.]+)%\)/);
    const nsPerDayMatch = content.match(/ns\/day\s*=\s*([\d.]+)/);
    const remainingMatch = content.match(/Estimated time remaining:\s*(.+?)(?:\n|$)/);

    if (stepMatch) data.currentStep = parseInt(stepMatch[1]);
    if (tempMatch) data.temperature = parseFloat(tempMatch[1]);
    if (pressMatch) data.pressure = parseFloat(pressMatch[1]);
    if (densityMatch) data.density = parseFloat(densityMatch[1]);
    if (etotMatch) data.totalEnergy = parseFloat(etotMatch[1]);
    if (totalMatch) data.totalSteps = parseInt(totalMatch[1]);
    if (completedMatch) data.progress = parseFloat(completedMatch[2]);
    if (nsPerDayMatch) data.nsPerDay = parseFloat(nsPerDayMatch[1]);
    if (remainingMatch) data.estimatedTimeRemaining = remainingMatch[1].trim();

    return data;
  }

  /**
   * Validate restart file integrity
   */
  async validateRestart(args: { rst7Path: string; prmtopPath: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { rst7Path, prmtopPath } = args;

    // Use cpptraj to validate the restart file
    const command = `
      module load amber/25 2>/dev/null
      cpptraj -p "${prmtopPath}" << EOF
trajin "${rst7Path}"
trajinfo
EOF
    `;

    const result = await this.ssh.executeCommand(command, 30000);

    if (result.isError) {
      return result;
    }

    const output = result.content[0]?.text || "";

    // Check for common validation indicators
    const validation = {
      valid: !output.includes("Error") && !output.includes("error"),
      atomCount: 0,
      boxInfo: "",
      warnings: [] as string[],
    };

    const atomMatch = output.match(/(\d+)\s+atoms/i);
    if (atomMatch) validation.atomCount = parseInt(atomMatch[1]);

    const boxMatch = output.match(/Box:\s*(.+)/);
    if (boxMatch) validation.boxInfo = boxMatch[1].trim();

    if (output.includes("Warning")) {
      validation.warnings = output.match(/Warning:.+/g) || [];
    }

    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          file: rst7Path,
          ...validation,
          rawOutput: output,
        }, null, 2),
      }],
    };
  }

  /**
   * Quick RMSD check on trajectory
   */
  async quickRmsdCheck(args: { trajPath: string; prmtopPath: string; mask?: string }): Promise<{
    content: Array<{ type: string; text: string }>;
    isError?: boolean;
  }> {
    const { trajPath, prmtopPath, mask = ":1-357@CA" } = args;

    const command = `
      module load amber/25 2>/dev/null
      cpptraj -p "${prmtopPath}" << EOF
trajin "${trajPath}"
autoimage
rms first ${mask} out /tmp/rmsd_quick_$$.dat
run
quit
EOF
      echo "=== RMSD Statistics ==="
      awk 'NR>1 {sum+=$2; sumsq+=$2*$2; n++; if($2>max)max=$2; if(min==""||$2<min)min=$2}
           END {mean=sum/n; std=sqrt(sumsq/n-mean*mean);
                printf "Frames: %d\\nMean: %.3f A\\nStd: %.3f A\\nMin: %.3f A\\nMax: %.3f A\\n",
                       n, mean, std, min, max}' /tmp/rmsd_quick_$$.dat
      rm -f /tmp/rmsd_quick_$$.dat
    `;

    return await this.ssh.executeCommand(command, 120000);
  }
}
