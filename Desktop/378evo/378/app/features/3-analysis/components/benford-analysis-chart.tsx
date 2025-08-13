
"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import type { BenfordAnalysisPoint } from "@/types/types";

interface BenfordAnalysisChartProps {
  data: BenfordAnalysisPoint[];
}

export function BenfordAnalysisChart({ data }: BenfordAnalysisChartProps) {
  if (!data || data.length === 0) {
    return null;
  }
  
  const chartConfig = {
    actual: {
      label: "Actual",
      color: "hsl(var(--chart-1))",
    },
    expected: {
      label: "Expected (Benford's Law)",
      color: "hsl(var(--chart-2))",
    },
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Benford's Law Analysis</CardTitle>
        <CardDescription>
          This chart compares the frequency of leading digits in your debit transactions against the expected distribution according to Benford's Law. Significant deviations can indicate data anomalies.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="min-h-[200px] w-full">
            <BarChart data={data} accessibilityLayer>
                <CartesianGrid vertical={false} />
                <XAxis
                    dataKey="digit"
                    tickLine={false}
                    tickMargin={10}
                    axisLine={false}
                    tickFormatter={(value) => `Digit ${value}`}
                />
                <YAxis 
                    tickFormatter={(value) => `${value}%`}
                />
                <ChartTooltip
                    cursor={false}
                    content={<ChartTooltipContent indicator="dot" />}
                />
                <Legend />
                <Bar dataKey="actual" fill="var(--color-actual)" radius={4} />
                <Bar dataKey="expected" fill="var(--color-expected)" radius={4} />
            </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
