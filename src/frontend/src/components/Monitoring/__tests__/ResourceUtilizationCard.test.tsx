import React from "react";
import { render, screen } from "@testing-library/react";
import { ThemeProvider, createTheme } from "@mui/material";
import ResourceUtilizationCard from "../ResourceUtilizationCard";
import type { SystemMetrics, MetricData } from "../../../services/monitoring";

const theme = createTheme();

const mockSystemMetrics: SystemMetrics = {
  cpu: 75,
  memory: 60,
  storage: 45,
  network: 30,
};

const generateHistoricalData = (hours: number): MetricData[] => {
  const now = Date.now();
  return Array.from({ length: hours }, (_, i) => ({
    timestamp: now - (hours - i) * 3600000,
    value: 50 + Math.sin(i) * 20,
  }));
};

const mockHistoricalData = {
  cpu: generateHistoricalData(24),
  memory: generateHistoricalData(24),
  storage: generateHistoricalData(24),
  network: generateHistoricalData(24),
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(<ThemeProvider theme={theme}>{component}</ThemeProvider>);
};

describe("ResourceUtilizationCard", () => {
  it("displays resource utilization data correctly", () => {
    renderWithTheme(
      <ResourceUtilizationCard
        currentMetrics={mockSystemMetrics}
        historicalData={mockHistoricalData}
        isLoading={false}
      />,
    );

    // Check title and section headers
    expect(screen.getByText("Resource Utilization")).toBeInTheDocument();
    expect(screen.getByText("Current Usage")).toBeInTheDocument();

    // Check each resource's display
    Object.entries(mockSystemMetrics).forEach(([key, value]) => {
      // Convert 'cpu' to 'CPU', 'memory' to 'Memory', etc.
      const label = `${key.toUpperCase()} Usage`;
      expect(screen.getByText(label)).toBeInTheDocument();
      expect(screen.getByText(`${value}%`)).toBeInTheDocument();

      // Check progress bar
      const progressBar = screen.getByRole("progressbar", {
        name: `${value}% utilized`,
      });
      expect(progressBar).toBeInTheDocument();
      expect(progressBar).toHaveAttribute("aria-valuenow", value.toString());
    });

    // Verify chart is rendered
    expect(
      screen.getByTestId("resource-utilization-chart"),
    ).toBeInTheDocument();
  });

  it("applies correct color coding based on utilization levels", () => {
    const highUtilizationMetrics: SystemMetrics = {
      cpu: 95, // Should show error color (>= 90)
      memory: 75, // Should show warning color (>= 70)
      storage: 45, // Should show success color (< 70)
      network: 30, // Should show success color (< 70)
    };

    renderWithTheme(
      <ResourceUtilizationCard
        currentMetrics={highUtilizationMetrics}
        historicalData={mockHistoricalData}
        isLoading={false}
      />,
    );

    // CPU should have error color
    const cpuProgress = screen.getByRole("progressbar", {
      name: "95% utilized",
    });
    expect(cpuProgress).toHaveClass("MuiLinearProgress-colorError");

    // Memory should have warning color
    const memoryProgress = screen.getByRole("progressbar", {
      name: "75% utilized",
    });
    expect(memoryProgress).toHaveClass("MuiLinearProgress-colorWarning");

    // Storage and Network should have success color
    const storageProgress = screen.getByRole("progressbar", {
      name: "45% utilized",
    });
    const networkProgress = screen.getByRole("progressbar", {
      name: "30% utilized",
    });
    expect(storageProgress).toHaveClass("MuiLinearProgress-colorSuccess");
    expect(networkProgress).toHaveClass("MuiLinearProgress-colorSuccess");
  });

  it("handles empty historical data gracefully", () => {
    renderWithTheme(
      <ResourceUtilizationCard
        currentMetrics={mockSystemMetrics}
        historicalData={{}}
        isLoading={false}
      />,
    );

    // Should still render the chart container
    expect(
      screen.getByTestId("resource-utilization-chart"),
    ).toBeInTheDocument();

    // All current metrics should still be displayed
    Object.entries(mockSystemMetrics).forEach(([key, value]) => {
      const label = `${key.toUpperCase()} Usage`;
      expect(screen.getByText(label)).toBeInTheDocument();
      expect(screen.getByText(`${value}%`)).toBeInTheDocument();
    });
  });

  it("shows utilization tooltips on progress bars", () => {
    renderWithTheme(
      <ResourceUtilizationCard
        currentMetrics={mockSystemMetrics}
        historicalData={mockHistoricalData}
        isLoading={false}
      />,
    );

    // Each progress bar should have a tooltip with the correct utilization text
    Object.values(mockSystemMetrics).forEach((value) => {
      const progressBar = screen.getByRole("progressbar", {
        name: `${value}% utilized`,
      });
      expect(progressBar).toHaveAttribute("aria-label", `${value}% utilized`);
    });
  });
});
